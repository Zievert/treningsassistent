#!/usr/bin/env python3
"""
Management CLI tool for Treningsassistent

Usage:
    python manage.py create-admin          # Create first admin user
    python manage.py create-invitation     # Create invitation code
    python manage.py list-users            # List all users
"""
import sys
import os
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.models import Bruker, Invitasjon
from app.utils.security import hash_password
from datetime import datetime, timedelta
import secrets
import getpass


def create_admin():
    """Create the first admin user"""
    print("=" * 70)
    print("CREATE ADMIN USER")
    print("=" * 70)

    db = SessionLocal()

    try:
        # Check if any admin already exists
        existing_admin = db.query(Bruker).filter(Bruker.rolle == "admin").first()

        if existing_admin:
            print(f"\n⚠️  Warning: Admin user already exists: {existing_admin.brukernavn}")
            response = input("Create another admin anyway? (y/N): ")
            if response.lower() != 'y':
                print("Cancelled.")
                return

        # Get user input
        print("\nEnter admin user details:")
        brukernavn = input("Username: ").strip()

        if not brukernavn:
            print("❌ Username cannot be empty")
            return

        # Check if username exists
        existing = db.query(Bruker).filter(Bruker.brukernavn == brukernavn).first()
        if existing:
            print(f"❌ Username '{brukernavn}' already exists")
            return

        epost = input("Email: ").strip()

        if not epost:
            print("❌ Email cannot be empty")
            return

        # Check if email exists
        existing = db.query(Bruker).filter(Bruker.epost == epost).first()
        if existing:
            print(f"❌ Email '{epost}' already exists")
            return

        # Get password (hidden input)
        passord = getpass.getpass("Password (min 8 characters): ")

        if len(passord) < 8:
            print("❌ Password must be at least 8 characters")
            return

        passord_confirm = getpass.getpass("Confirm password: ")

        if passord != passord_confirm:
            print("❌ Passwords do not match")
            return

        # Create admin user
        passord_hash = hash_password(passord)

        admin = Bruker(
            brukernavn=brukernavn,
            epost=epost,
            passord_hash=passord_hash,
            aktiv=True,
            rolle="admin"
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("\n" + "=" * 70)
        print("✅ ADMIN USER CREATED SUCCESSFULLY")
        print("=" * 70)
        print(f"Username: {admin.brukernavn}")
        print(f"Email: {admin.epost}")
        print(f"User ID: {admin.bruker_id}")
        print(f"Role: {admin.rolle}")
        print("\nYou can now login with these credentials.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


def create_invitation():
    """Create an invitation code"""
    print("=" * 70)
    print("CREATE INVITATION CODE")
    print("=" * 70)

    db = SessionLocal()

    try:
        # Check if any admin exists
        admin_count = db.query(Bruker).filter(Bruker.rolle == "admin").count()

        if admin_count == 0:
            print("\n❌ No admin users exist. Create an admin first with:")
            print("   python manage.py create-admin")
            return

        # Get admin user
        print("\nAvailable admins:")
        admins = db.query(Bruker).filter(Bruker.rolle == "admin").all()

        for idx, admin in enumerate(admins, 1):
            print(f"  {idx}. {admin.brukernavn} (ID: {admin.bruker_id})")

        admin_choice = input("\nSelect admin (1-{}) or press Enter for first: ".format(len(admins))).strip()

        if admin_choice:
            try:
                admin_idx = int(admin_choice) - 1
                if admin_idx < 0 or admin_idx >= len(admins):
                    print("❌ Invalid selection")
                    return
                selected_admin = admins[admin_idx]
            except ValueError:
                print("❌ Invalid input")
                return
        else:
            selected_admin = admins[0]

        # Get invitation details
        epost = input("\nEmail address (optional, press Enter to skip): ").strip() or None

        dagen_str = input("Valid for how many days? (default 30): ").strip()
        try:
            dagen = int(dagen_str) if dagen_str else 30
        except ValueError:
            print("❌ Invalid number")
            return

        # Generate invitation code
        invitasjonskode = secrets.token_urlsafe(16)
        utloper_dato = datetime.utcnow() + timedelta(days=dagen)

        invitasjon = Invitasjon(
            invitasjonskode=invitasjonskode,
            opprettet_av_bruker_id=selected_admin.bruker_id,
            epost=epost,
            brukt=False,
            utloper_dato=utloper_dato
        )

        db.add(invitasjon)
        db.commit()
        db.refresh(invitasjon)

        print("\n" + "=" * 70)
        print("✅ INVITATION CODE CREATED")
        print("=" * 70)
        print(f"Code: {invitasjon.invitasjonskode}")
        print(f"Email: {invitasjon.epost or 'Any'}")
        print(f"Expires: {invitasjon.utloper_dato.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Created by: {selected_admin.brukernavn}")
        print("\nShare this code with the user for registration.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


def list_users():
    """List all users"""
    print("=" * 70)
    print("USER LIST")
    print("=" * 70)

    db = SessionLocal()

    try:
        brukere = db.query(Bruker).order_by(Bruker.bruker_id).all()

        if not brukere:
            print("\nNo users found.")
            return

        print(f"\nTotal users: {len(brukere)}\n")

        for bruker in brukere:
            status = "✓ Active" if bruker.aktiv else "✗ Inactive"
            role_emoji = "👑" if bruker.rolle == "admin" else "👤"

            print(f"{role_emoji} [{bruker.bruker_id}] {bruker.brukernavn}")
            print(f"   Email: {bruker.epost}")
            print(f"   Role: {bruker.rolle}")
            print(f"   Status: {status}")
            print(f"   Created: {bruker.opprettet_dato.strftime('%Y-%m-%d %H:%M:%S')}")
            print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        db.close()


def list_invitations():
    """List all invitation codes"""
    print("=" * 70)
    print("INVITATION CODES")
    print("=" * 70)

    db = SessionLocal()

    try:
        invitasjoner = db.query(Invitasjon).order_by(Invitasjon.opprettet_dato.desc()).all()

        if not invitasjoner:
            print("\nNo invitations found.")
            return

        print(f"\nTotal invitations: {len(invitasjoner)}\n")

        for inv in invitasjoner:
            status = "✓ Used" if inv.brukt else "○ Available"

            # Check if expired
            if not inv.brukt and inv.utloper_dato and inv.utloper_dato < datetime.utcnow():
                status = "✗ Expired"

            print(f"[{inv.invitasjon_id}] {inv.invitasjonskode}")
            print(f"   Status: {status}")
            print(f"   Email: {inv.epost or 'Any'}")
            print(f"   Created: {inv.opprettet_dato.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Expires: {inv.utloper_dato.strftime('%Y-%m-%d %H:%M:%S')}")
            print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        db.close()


def show_help():
    """Show help message"""
    print("=" * 70)
    print("TRENINGSASSISTENT MANAGEMENT CLI")
    print("=" * 70)
    print("\nAvailable commands:")
    print("  create-admin         Create a new admin user")
    print("  create-invitation    Create an invitation code")
    print("  list-users           List all users")
    print("  list-invitations     List all invitation codes")
    print("  help                 Show this help message")
    print("\nUsage:")
    print("  python manage.py <command>")
    print("\nExamples:")
    print("  python manage.py create-admin")
    print("  python manage.py create-invitation")
    print()


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    commands = {
        'create-admin': create_admin,
        'create-invitation': create_invitation,
        'list-users': list_users,
        'list-invitations': list_invitations,
        'help': show_help,
    }

    if command in commands:
        commands[command]()
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python manage.py help' for available commands.")


if __name__ == "__main__":
    main()
