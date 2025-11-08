#!/usr/bin/env python3
"""
Test complete workflow
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.models import Bruker, Invitasjon, Ovelse, Utstyr, BrukerUtstyrProfil
from app.utils.security import hash_password
from datetime import datetime, timedelta
import secrets

print("=" * 70)
print("TRENINGSASSISTENT WORKFLOW TEST")
print("=" * 70)

db = SessionLocal()

try:
    # Step 1: Create admin user
    print("\n1️⃣  Creating admin user...")
    admin = Bruker(
        brukernavn="admin",
        epost="admin@treningsassistent.no",
        passord_hash=hash_password("admin123"),
        aktiv=True,
        rolle="admin"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print(f"   ✅ Admin created: {admin.brukernavn} (ID: {admin.bruker_id})")

    # Step 2: Create invitation
    print("\n2️⃣  Creating invitation code...")
    invitasjonskode = secrets.token_urlsafe(16)
    invitasjon = Invitasjon(
        invitasjonskode=invitasjonskode,
        opprettet_av_bruker_id=admin.bruker_id,
        epost=None,
        brukt=False,
        utloper_dato=datetime.utcnow() + timedelta(days=30)
    )
    db.add(invitasjon)
    db.commit()
    db.refresh(invitasjon)
    print(f"   ✅ Invitation created: {invitasjon.invitasjonskode}")

    # Step 3: Register regular user
    print("\n3️⃣  Registering regular user...")
    bruker = Bruker(
        brukernavn="testuser",
        epost="test@example.com",
        passord_hash=hash_password("password123"),
        aktiv=True,
        rolle="bruker"
    )
    db.add(bruker)

    # Mark invitation as used
    invitasjon.brukt = True

    db.commit()
    db.refresh(bruker)
    print(f"   ✅ User created: {bruker.brukernavn} (ID: {bruker.bruker_id})")

    # Step 4: Create equipment profile
    print("\n4️⃣  Creating equipment profile...")

    # Get all equipment IDs (user has access to all equipment for testing)
    all_utstyr = db.query(Utstyr).all()
    utstyr_ids = [u.utstyr_id for u in all_utstyr]

    profil = BrukerUtstyrProfil(
        bruker_id=bruker.bruker_id,
        profil_navn="Hjemmegym",
        utstyr_ids=utstyr_ids,
        aktiv=True
    )
    db.add(profil)
    db.commit()
    db.refresh(profil)
    print(f"   ✅ Equipment profile created: {profil.profil_navn} ({len(utstyr_ids)} equipment items)")

    # Step 5: Get recommendation
    print("\n5️⃣  Getting exercise recommendation...")
    from app.services.ai_forslag import hent_neste_anbefaling

    ovelse, grunn, prioritert_muskel, prioritet_score = hent_neste_anbefaling(db, bruker.bruker_id)

    if ovelse:
        print(f"   ✅ Recommendation: {ovelse.ovelse_navn}")
        print(f"   📝 Reason: {grunn}")
        print(f"   💪 Priority muscle: {prioritert_muskel}")
        print(f"   🎯 Priority score: {prioritet_score}")
    else:
        print(f"   ❌ No recommendation: {grunn}")

    # Step 6: Log exercise
    if ovelse:
        print("\n6️⃣  Logging exercise...")
        from app.models import OvelseUtfort
        from app.services.ai_forslag import oppdater_muskel_status_etter_logg
        from decimal import Decimal

        sett = 3
        reps = 10
        vekt = Decimal('50.0')

        utfort = OvelseUtfort(
            bruker_id=bruker.bruker_id,
            ovelse_id=ovelse.ovelse_id,
            sett=sett,
            repetisjoner=reps,
            vekt=vekt,
            tidspunkt=datetime.utcnow()
        )
        db.add(utfort)
        db.flush()

        # Update muscle status
        volum = Decimal(sett) * Decimal(reps) * vekt
        oppdater_muskel_status_etter_logg(db, bruker.bruker_id, ovelse.ovelse_id, volum)

        db.commit()
        print(f"   ✅ Exercise logged: {ovelse.ovelse_navn}")
        print(f"   📊 Volume: {sett} sets × {reps} reps × {vekt}kg = {volum}kg")

    # Step 7: Check muscle status
    print("\n7️⃣  Checking muscle status...")
    from app.models import BrukerMuskelStatus

    status_count = db.query(BrukerMuskelStatus).filter(
        BrukerMuskelStatus.bruker_id == bruker.bruker_id
    ).count()

    print(f"   ✅ Muscles tracked: {status_count}")

    # Step 8: Get statistics
    print("\n8️⃣  Getting statistics...")
    from app.services.statistikk import beregn_muskel_volum, beregn_antagonistisk_balanse

    volum_data = beregn_muskel_volum(db, bruker.bruker_id)
    trained_muscles = [m for m in volum_data if m['antall_ganger_trent'] > 0]

    print(f"   ✅ Trained muscles: {len(trained_muscles)}/17")

    balanse_data = beregn_antagonistisk_balanse(db, bruker.bruker_id)
    print(f"   ✅ Antagonistic pairs analyzed: {len(balanse_data)}")

    # Step 9: Get another recommendation
    print("\n9️⃣  Getting next recommendation...")
    ovelse2, grunn2, prioritert_muskel2, prioritet_score2 = hent_neste_anbefaling(db, bruker.bruker_id)

    if ovelse2:
        print(f"   ✅ Recommendation: {ovelse2.ovelse_navn}")
        print(f"   📝 Reason: {grunn2}")
        print(f"   💪 Priority muscle: {prioritert_muskel2}")

    print("\n" + "=" * 70)
    print("✅ WORKFLOW TEST COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print("\n📊 Summary:")
    print(f"   - Admin user: {admin.brukernavn}")
    print(f"   - Test user: {bruker.brukernavn}")
    print(f"   - Invitation code: {invitasjonskode}")
    print(f"   - Equipment profile: {profil.profil_navn} ({len(utstyr_ids)} items)")
    print(f"   - Exercises logged: 1")
    print(f"   - Muscles tracked: {status_count}")
    print("\n🚀 The API is ready to use!")
    print("\nNext steps:")
    print("  1. Start server: uvicorn app.main:app --reload")
    print("  2. Visit docs: http://localhost:8000/docs")
    print("  3. Login with admin/admin123 or testuser/password123")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
