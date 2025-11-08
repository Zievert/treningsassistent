"""
Comprehensive data import script for Treningsassistent
Imports all global data: muskler, utstyr, antagonistiske_par, ovelser, and junction tables
"""
import json
import os
import sys
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.append(str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import Muskel, Utstyr, AntagonistiskPar, Ovelse, OvelseMuskel, OvelseUtstyr
from sqlalchemy.exc import IntegrityError


# ============================================================================
# DATA DEFINITIONS (from data_mapping.md)
# ============================================================================

MUSKLER_DATA = [
    # Format: (muskel_navn, hovedkategori, underkategori)
    ("chest", "overkropp_push", "bryst"),
    ("shoulders", "overkropp_push", "skulder"),
    ("triceps", "overkropp_push", "armer"),
    ("lats", "overkropp_pull", "rygg"),
    ("middle back", "overkropp_pull", "rygg"),
    ("lower back", "overkropp_pull", "rygg"),
    ("biceps", "overkropp_pull", "armer"),
    ("forearms", "overkropp_pull", "armer"),
    ("traps", "overkropp_pull", "skulder"),
    ("neck", "overkropp_pull", "nakke"),
    ("quadriceps", "ben", "lår"),
    ("hamstrings", "ben", "lår"),
    ("glutes", "ben", "sete"),
    ("calves", "ben", "legg"),
    ("adductors", "ben", "lår"),
    ("abductors", "ben", "hofte"),
    ("abdominals", "core", "abs"),
]

UTSTYR_DATA = [
    # Format: (utstyr_navn, kategori)
    ("body only", "kroppsvekt"),
    ("barbell", "fri_vekt"),
    ("dumbbell", "fri_vekt"),
    ("kettlebells", "fri_vekt"),
    ("e-z curl bar", "fri_vekt"),
    ("cable", "kabel"),
    ("machine", "maskin"),
    ("bands", "annet"),
    ("exercise ball", "annet"),
    ("foam roll", "annet"),
    ("medicine ball", "annet"),
    ("other", "annet"),
]

# Antagonistic muscle pairs (muskel_1_navn, muskel_2_navn, onsket_ratio)
ANTAGONISTISKE_PAR_DATA = [
    ("chest", "lats", 1.0),
    ("quadriceps", "hamstrings", 1.0),
    ("biceps", "triceps", 1.0),
    ("shoulders", "middle back", 1.0),  # Simplified for MVP
    ("abdominals", "lower back", 1.0),
]


# ============================================================================
# IMPORT FUNCTIONS
# ============================================================================

def populate_muskler(db):
    """Populate muskler table"""
    print("\n📊 Populating muskler table...")

    count = db.query(Muskel).count()
    if count > 0:
        print(f"   ℹ️  Muskler table already contains {count} entries. Skipping.")
        return

    for muskel_navn, hovedkategori, underkategori in MUSKLER_DATA:
        muskel = Muskel(
            muskel_navn=muskel_navn,
            hovedkategori=hovedkategori,
            underkategori=underkategori
        )
        db.add(muskel)

    db.commit()
    print(f"   ✅ Inserted {len(MUSKLER_DATA)} muskler")


def populate_utstyr(db):
    """Populate utstyr table"""
    print("\n🏋️  Populating utstyr table...")

    count = db.query(Utstyr).count()
    if count > 0:
        print(f"   ℹ️  Utstyr table already contains {count} entries. Skipping.")
        return

    for utstyr_navn, kategori in UTSTYR_DATA:
        utstyr = Utstyr(
            utstyr_navn=utstyr_navn,
            kategori=kategori
        )
        db.add(utstyr)

    db.commit()
    print(f"   ✅ Inserted {len(UTSTYR_DATA)} utstyr")


def populate_antagonistiske_par(db):
    """Populate antagonistiske_par table"""
    print("\n⚖️  Populating antagonistiske_par table...")

    count = db.query(AntagonistiskPar).count()
    if count > 0:
        print(f"   ℹ️  Antagonistiske_par table already contains {count} entries. Skipping.")
        return

    # Build muskel name -> ID mapping
    muskler = db.query(Muskel).all()
    muskel_map = {m.muskel_navn: m.muskel_id for m in muskler}

    for muskel_1_navn, muskel_2_navn, onsket_ratio in ANTAGONISTISKE_PAR_DATA:
        if muskel_1_navn not in muskel_map or muskel_2_navn not in muskel_map:
            print(f"   ⚠️  Warning: Could not find muscle '{muskel_1_navn}' or '{muskel_2_navn}'. Skipping pair.")
            continue

        par = AntagonistiskPar(
            muskel_1_id=muskel_map[muskel_1_navn],
            muskel_2_id=muskel_map[muskel_2_navn],
            onsket_ratio=onsket_ratio
        )
        db.add(par)

    db.commit()
    print(f"   ✅ Inserted {len(ANTAGONISTISKE_PAR_DATA)} antagonistic pairs")


def populate_ovelser(db, exercises_json_path):
    """Populate ovelser, ovelse_muskler, and ovelse_utstyr tables from exercises.json"""
    print(f"\n💪 Populating ovelser from {exercises_json_path}...")

    # Check if ovelser already populated
    count = db.query(Ovelse).count()
    if count > 0:
        print(f"   ℹ️  Ovelser table already contains {count} entries. Skipping.")
        return

    # Load exercises.json
    if not os.path.exists(exercises_json_path):
        print(f"   ❌ Error: exercises.json not found at {exercises_json_path}")
        return

    with open(exercises_json_path, 'r', encoding='utf-8') as f:
        exercises = json.load(f)

    print(f"   📖 Loaded {len(exercises)} exercises from JSON")

    # Build lookup maps
    muskler = db.query(Muskel).all()
    muskel_map = {m.muskel_navn: m.muskel_id for m in muskler}

    utstyr_list = db.query(Utstyr).all()
    utstyr_map = {u.utstyr_navn: u.utstyr_id for u in utstyr_list}

    # Track statistics
    ovelser_inserted = 0
    ovelse_muskler_inserted = 0
    ovelse_utstyr_inserted = 0
    skipped_exercises = []

    for idx, ex in enumerate(exercises, 1):
        try:
            # Create Ovelse
            ovelse = Ovelse(
                ovelse_navn=ex['name'],
                force=ex.get('force'),
                level=ex.get('level'),
                mechanic=ex.get('mechanic'),
                category=ex.get('category'),
                instruksjoner=json.dumps(ex.get('instructions', [])),
                kilde_id=ex['id'],
                # Image URLs (from GitHub raw)
                bilde_1_url=f"https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/{ex['id']}/0.jpg" if ex.get('images') and len(ex['images']) > 0 else None,
                bilde_2_url=f"https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/{ex['id']}/1.jpg" if ex.get('images') and len(ex['images']) > 1 else None,
            )
            db.add(ovelse)
            db.flush()  # Get ovelse_id

            # Track which muscles have been added to avoid duplicates
            # (some exercises list same muscle as both primary and secondary)
            added_muscles = set()

            # Add primary muscles
            for muscle_name in ex.get('primaryMuscles', []):
                if muscle_name in muskel_map:
                    muskel_id = muskel_map[muscle_name]
                    if muskel_id not in added_muscles:
                        ovelse_muskel = OvelseMuskel(
                            ovelse_id=ovelse.ovelse_id,
                            muskel_id=muskel_id,
                            muskel_type='primar'
                        )
                        db.add(ovelse_muskel)
                        ovelse_muskler_inserted += 1
                        added_muscles.add(muskel_id)
                else:
                    print(f"   ⚠️  Unknown muscle '{muscle_name}' in exercise '{ex['name']}'")

            # Add secondary muscles (skip if already added as primary)
            for muscle_name in ex.get('secondaryMuscles', []):
                if muscle_name in muskel_map:
                    muskel_id = muskel_map[muscle_name]
                    if muskel_id not in added_muscles:
                        ovelse_muskel = OvelseMuskel(
                            ovelse_id=ovelse.ovelse_id,
                            muskel_id=muskel_id,
                            muskel_type='sekundar'
                        )
                        db.add(ovelse_muskel)
                        ovelse_muskler_inserted += 1
                        added_muscles.add(muskel_id)
                else:
                    print(f"   ⚠️  Unknown muscle '{muscle_name}' in exercise '{ex['name']}'")

            # Add equipment
            equipment_name = ex.get('equipment')
            if equipment_name and equipment_name in utstyr_map:
                ovelse_utstyr = OvelseUtstyr(
                    ovelse_id=ovelse.ovelse_id,
                    utstyr_id=utstyr_map[equipment_name]
                )
                db.add(ovelse_utstyr)
                ovelse_utstyr_inserted += 1
            elif equipment_name:
                print(f"   ⚠️  Unknown equipment '{equipment_name}' in exercise '{ex['name']}'")

            # CRITICAL: Commit after each successful exercise
            # This prevents rollback from affecting previous exercises
            db.commit()
            ovelser_inserted += 1

            # Progress indicator every 100 exercises
            if idx % 100 == 0:
                print(f"   📈 Progress: {idx}/{len(exercises)} exercises processed...")

        except IntegrityError as e:
            db.rollback()
            skipped_exercises.append(ex['name'])
            # Don't print for every duplicate, just count them
            continue
        except Exception as e:
            db.rollback()
            skipped_exercises.append(ex['name'])
            print(f"   ❌ Error processing '{ex['name']}': {str(e)}")
            continue

    print(f"\n   ✅ Inserted {ovelser_inserted} ovelser")
    print(f"   ✅ Inserted {ovelse_muskler_inserted} ovelse_muskler relations")
    print(f"   ✅ Inserted {ovelse_utstyr_inserted} ovelse_utstyr relations")

    if skipped_exercises:
        print(f"   ⚠️  Skipped {len(skipped_exercises)} exercises")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main import function"""
    print("="*70)
    print("🚀 TRENINGSASSISTENT DATA IMPORT")
    print("="*70)

    # Find exercises.json
    exercises_json_path = Path(__file__).parent.parent.parent / "exercises.json"

    if not exercises_json_path.exists():
        print(f"\n❌ ERROR: exercises.json not found at {exercises_json_path}")
        print("   Please ensure exercises.json is in the project root directory.")
        sys.exit(1)

    # Create database session
    db = SessionLocal()

    try:
        # Import in correct order (respecting foreign key dependencies)
        populate_muskler(db)
        populate_utstyr(db)
        populate_antagonistiske_par(db)
        populate_ovelser(db, str(exercises_json_path))

        print("\n" + "="*70)
        print("✅ DATA IMPORT COMPLETED SUCCESSFULLY")
        print("="*70)

        # Print summary
        print("\n📊 Database Summary:")
        print(f"   - Muskler: {db.query(Muskel).count()}")
        print(f"   - Utstyr: {db.query(Utstyr).count()}")
        print(f"   - Antagonistiske par: {db.query(AntagonistiskPar).count()}")
        print(f"   - Ovelser: {db.query(Ovelse).count()}")
        print(f"   - Ovelse-muskel relations: {db.query(OvelseMuskel).count()}")
        print(f"   - Ovelse-utstyr relations: {db.query(OvelseUtstyr).count()}")

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {str(e)}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
