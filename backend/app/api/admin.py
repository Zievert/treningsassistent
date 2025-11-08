"""
Admin API endpoints
"""
from typing import List
from datetime import datetime, timedelta
import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Bruker, Invitasjon
from app.schemas import (
    InvitasjonCreate,
    InvitasjonResponse,
    BrukerAdminResponse,
    MessageResponse
)
from app.utils.security import get_current_active_admin


router = APIRouter()


# ============================================================================
# INVITATION MANAGEMENT
# ============================================================================

@router.post("/invitasjoner", response_model=InvitasjonResponse, status_code=status.HTTP_201_CREATED)
async def create_invitasjon(
    inv_data: InvitasjonCreate,
    current_admin: Bruker = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new invitation code.

    Only admins can create invitations.

    Args:
        inv_data: Optional email and expiration date
    """
    # Generate secure random invitation code
    invitasjonskode = secrets.token_urlsafe(16)

    # Set default expiration (30 days from now)
    if not inv_data.utloper_dato:
        utloper_dato = datetime.utcnow() + timedelta(days=30)
    else:
        utloper_dato = inv_data.utloper_dato

    # Create invitation
    invitasjon = Invitasjon(
        invitasjonskode=invitasjonskode,
        opprettet_av_bruker_id=current_admin.bruker_id,
        epost=inv_data.epost,
        brukt=False,
        utloper_dato=utloper_dato
    )

    db.add(invitasjon)
    db.commit()
    db.refresh(invitasjon)

    return invitasjon


@router.get("/invitasjoner", response_model=List[InvitasjonResponse])
async def get_alle_invitasjoner(
    current_admin: Bruker = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """
    Get all invitation codes.

    Only admins can view invitations.
    """
    invitasjoner = db.query(Invitasjon).order_by(
        Invitasjon.opprettet_dato.desc()
    ).all()

    return invitasjoner


@router.get("/invitasjoner/{invitasjon_id}", response_model=InvitasjonResponse)
async def get_invitasjon(
    invitasjon_id: int,
    current_admin: Bruker = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """
    Get details for a specific invitation.

    Only admins can view invitation details.
    """
    invitasjon = db.query(Invitasjon).filter(
        Invitasjon.invitasjon_id == invitasjon_id
    ).first()

    if not invitasjon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found"
        )

    return invitasjon


@router.delete("/invitasjoner/{invitasjon_id}", response_model=MessageResponse)
async def delete_invitasjon(
    invitasjon_id: int,
    current_admin: Bruker = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """
    Delete an invitation code.

    Only admins can delete invitations.
    Can only delete unused invitations.
    """
    invitasjon = db.query(Invitasjon).filter(
        Invitasjon.invitasjon_id == invitasjon_id
    ).first()

    if not invitasjon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found"
        )

    if invitasjon.brukt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete used invitation"
        )

    db.delete(invitasjon)
    db.commit()

    return {"message": "Invitation deleted successfully"}


# ============================================================================
# USER MANAGEMENT
# ============================================================================

@router.get("/brukere", response_model=List[BrukerAdminResponse])
async def get_alle_brukere(
    current_admin: Bruker = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """
    Get list of all users.

    Only admins can view user list.
    """
    brukere = db.query(Bruker).order_by(
        Bruker.opprettet_dato.desc()
    ).all()

    return brukere


@router.get("/brukere/{bruker_id}", response_model=BrukerAdminResponse)
async def get_bruker(
    bruker_id: int,
    current_admin: Bruker = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """
    Get details for a specific user.

    Only admins can view user details.
    """
    bruker = db.query(Bruker).filter(Bruker.bruker_id == bruker_id).first()

    if not bruker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return bruker


@router.post("/brukere/{bruker_id}/deaktiver", response_model=MessageResponse)
async def deaktiver_bruker(
    bruker_id: int,
    current_admin: Bruker = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """
    Deactivate a user account.

    Only admins can deactivate users.
    Cannot deactivate admin accounts.
    """
    bruker = db.query(Bruker).filter(Bruker.bruker_id == bruker_id).first()

    if not bruker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if bruker.rolle == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate admin accounts"
        )

    bruker.aktiv = False
    db.commit()

    return {"message": f"User {bruker.brukernavn} deactivated successfully"}


@router.post("/brukere/{bruker_id}/aktiver", response_model=MessageResponse)
async def aktiver_bruker(
    bruker_id: int,
    current_admin: Bruker = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """
    Activate a user account.

    Only admins can activate users.
    """
    bruker = db.query(Bruker).filter(Bruker.bruker_id == bruker_id).first()

    if not bruker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    bruker.aktiv = True
    db.commit()

    return {"message": f"User {bruker.brukernavn} activated successfully"}


@router.post("/brukere/{bruker_id}/gjor-admin", response_model=MessageResponse)
async def gjor_admin(
    bruker_id: int,
    current_admin: Bruker = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """
    Promote a user to admin role.

    Only admins can promote users.
    """
    bruker = db.query(Bruker).filter(Bruker.bruker_id == bruker_id).first()

    if not bruker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if bruker.rolle == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already an admin"
        )

    bruker.rolle = "admin"
    db.commit()

    return {"message": f"User {bruker.brukernavn} promoted to admin"}


# ============================================================================
# SYSTEM STATISTICS
# ============================================================================

@router.get("/stats")
async def get_system_stats(
    current_admin: Bruker = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """
    Get system statistics.

    Only admins can view system stats.
    """
    from app.models import Ovelse, Muskel, Utstyr, OvelseUtfort

    stats = {
        "total_brukere": db.query(Bruker).count(),
        "aktive_brukere": db.query(Bruker).filter(Bruker.aktiv == True).count(),
        "admin_brukere": db.query(Bruker).filter(Bruker.rolle == "admin").count(),
        "total_invitasjoner": db.query(Invitasjon).count(),
        "ubrukte_invitasjoner": db.query(Invitasjon).filter(Invitasjon.brukt == False).count(),
        "total_ovelser": db.query(Ovelse).count(),
        "total_muskler": db.query(Muskel).count(),
        "total_utstyr": db.query(Utstyr).count(),
        "total_loggede_ovelser": db.query(OvelseUtfort).count(),
    }

    return stats
