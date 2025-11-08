"""
Equipment profile API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app.models import Bruker, Utstyr, BrukerUtstyrProfil
from app.schemas import (
    UtstyrResponse,
    UtstyrProfilCreate,
    UtstyrProfilUpdate,
    UtstyrProfilResponse,
    MessageResponse
)
from app.utils.security import get_current_user


router = APIRouter()


# ============================================================================
# GET ALL EQUIPMENT
# ============================================================================

@router.get("/alle", response_model=List[UtstyrResponse])
async def get_alle_utstyr(
    current_user: Bruker = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of all available equipment types.

    Useful for building equipment selection UI.
    """
    utstyr = db.query(Utstyr).order_by(
        Utstyr.kategori,
        Utstyr.utstyr_navn
    ).all()

    return utstyr


# ============================================================================
# GET USER'S EQUIPMENT PROFILES
# ============================================================================

@router.get("/profiler", response_model=List[UtstyrProfilResponse])
async def get_profiler(
    current_user: Bruker = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all equipment profiles for current user.

    Returns list of profiles with their equipment items.
    """
    profiler = db.query(BrukerUtstyrProfil).filter(
        BrukerUtstyrProfil.bruker_id == current_user.bruker_id
    ).all()

    result = []
    for profil in profiler:
        # Get equipment details
        utstyr_list = db.query(Utstyr).filter(
            Utstyr.utstyr_id.in_(profil.utstyr_ids)
        ).all()

        result.append({
            "profil_id": profil.profil_id,
            "bruker_id": profil.bruker_id,
            "profil_navn": profil.profil_navn,
            "utstyr_ids": profil.utstyr_ids,
            "aktiv": profil.aktiv,
            "utstyr": utstyr_list
        })

    return result


# ============================================================================
# GET ACTIVE EQUIPMENT PROFILE
# ============================================================================

@router.get("/profiler/aktiv", response_model=UtstyrProfilResponse)
async def get_aktiv_profil(
    current_user: Bruker = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the currently active equipment profile.

    This profile is used for exercise recommendations.
    """
    profil = db.query(BrukerUtstyrProfil).filter(
        and_(
            BrukerUtstyrProfil.bruker_id == current_user.bruker_id,
            BrukerUtstyrProfil.aktiv == True
        )
    ).first()

    if not profil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active equipment profile found"
        )

    # Get equipment details
    utstyr_list = db.query(Utstyr).filter(
        Utstyr.utstyr_id.in_(profil.utstyr_ids)
    ).all()

    return {
        "profil_id": profil.profil_id,
        "bruker_id": profil.bruker_id,
        "profil_navn": profil.profil_navn,
        "utstyr_ids": profil.utstyr_ids,
        "aktiv": profil.aktiv,
        "utstyr": utstyr_list
    }


# ============================================================================
# CREATE EQUIPMENT PROFILE
# ============================================================================

@router.post("/profiler", response_model=UtstyrProfilResponse, status_code=status.HTTP_201_CREATED)
async def create_profil(
    profil_data: UtstyrProfilCreate,
    current_user: Bruker = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new equipment profile.

    Args:
        profil_data: Profile name and equipment IDs
    """
    # Verify all equipment IDs exist
    existing_utstyr = db.query(Utstyr).filter(
        Utstyr.utstyr_id.in_(profil_data.utstyr_ids)
    ).all()

    if len(existing_utstyr) != len(profil_data.utstyr_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more equipment IDs are invalid"
        )

    # Check if profile name already exists for this user
    existing_profil = db.query(BrukerUtstyrProfil).filter(
        and_(
            BrukerUtstyrProfil.bruker_id == current_user.bruker_id,
            BrukerUtstyrProfil.profil_navn == profil_data.profil_navn
        )
    ).first()

    if existing_profil:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile with this name already exists"
        )

    # Create new profile
    ny_profil = BrukerUtstyrProfil(
        bruker_id=current_user.bruker_id,
        profil_navn=profil_data.profil_navn,
        utstyr_ids=profil_data.utstyr_ids,
        aktiv=False  # New profiles start as inactive
    )

    db.add(ny_profil)
    db.commit()
    db.refresh(ny_profil)

    # Get equipment details
    utstyr_list = db.query(Utstyr).filter(
        Utstyr.utstyr_id.in_(ny_profil.utstyr_ids)
    ).all()

    return {
        "profil_id": ny_profil.profil_id,
        "bruker_id": ny_profil.bruker_id,
        "profil_navn": ny_profil.profil_navn,
        "utstyr_ids": ny_profil.utstyr_ids,
        "aktiv": ny_profil.aktiv,
        "utstyr": utstyr_list
    }


# ============================================================================
# UPDATE EQUIPMENT PROFILE
# ============================================================================

@router.put("/profiler/{profil_id}", response_model=UtstyrProfilResponse)
async def update_profil(
    profil_id: int,
    profil_data: UtstyrProfilUpdate,
    current_user: Bruker = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing equipment profile.

    Can update:
    - Profile name
    - Equipment list
    - Active status
    """
    # Get profile
    profil = db.query(BrukerUtstyrProfil).filter(
        and_(
            BrukerUtstyrProfil.profil_id == profil_id,
            BrukerUtstyrProfil.bruker_id == current_user.bruker_id
        )
    ).first()

    if not profil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    # Update fields if provided
    if profil_data.profil_navn is not None:
        # Check if new name conflicts with existing profile
        existing = db.query(BrukerUtstyrProfil).filter(
            and_(
                BrukerUtstyrProfil.bruker_id == current_user.bruker_id,
                BrukerUtstyrProfil.profil_navn == profil_data.profil_navn,
                BrukerUtstyrProfil.profil_id != profil_id
            )
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Profile with this name already exists"
            )

        profil.profil_navn = profil_data.profil_navn

    if profil_data.utstyr_ids is not None:
        # Verify all equipment IDs exist
        existing_utstyr = db.query(Utstyr).filter(
            Utstyr.utstyr_id.in_(profil_data.utstyr_ids)
        ).all()

        if len(existing_utstyr) != len(profil_data.utstyr_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more equipment IDs are invalid"
            )

        profil.utstyr_ids = profil_data.utstyr_ids

    if profil_data.aktiv is not None:
        # If setting this profile as active, deactivate others
        if profil_data.aktiv:
            db.query(BrukerUtstyrProfil).filter(
                and_(
                    BrukerUtstyrProfil.bruker_id == current_user.bruker_id,
                    BrukerUtstyrProfil.profil_id != profil_id
                )
            ).update({"aktiv": False})

        profil.aktiv = profil_data.aktiv

    db.commit()
    db.refresh(profil)

    # Get equipment details
    utstyr_list = db.query(Utstyr).filter(
        Utstyr.utstyr_id.in_(profil.utstyr_ids)
    ).all()

    return {
        "profil_id": profil.profil_id,
        "bruker_id": profil.bruker_id,
        "profil_navn": profil.profil_navn,
        "utstyr_ids": profil.utstyr_ids,
        "aktiv": profil.aktiv,
        "utstyr": utstyr_list
    }


# ============================================================================
# DELETE EQUIPMENT PROFILE
# ============================================================================

@router.delete("/profiler/{profil_id}", response_model=MessageResponse)
async def delete_profil(
    profil_id: int,
    current_user: Bruker = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an equipment profile.
    """
    profil = db.query(BrukerUtstyrProfil).filter(
        and_(
            BrukerUtstyrProfil.profil_id == profil_id,
            BrukerUtstyrProfil.bruker_id == current_user.bruker_id
        )
    ).first()

    if not profil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    db.delete(profil)
    db.commit()

    return {"message": "Profile deleted successfully"}


# ============================================================================
# ACTIVATE EQUIPMENT PROFILE
# ============================================================================

@router.post("/profiler/{profil_id}/aktivere", response_model=UtstyrProfilResponse)
async def aktivere_profil(
    profil_id: int,
    current_user: Bruker = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Set a profile as active (deactivates all other profiles).

    The active profile is used for exercise recommendations.
    """
    profil = db.query(BrukerUtstyrProfil).filter(
        and_(
            BrukerUtstyrProfil.profil_id == profil_id,
            BrukerUtstyrProfil.bruker_id == current_user.bruker_id
        )
    ).first()

    if not profil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    # Deactivate all other profiles
    db.query(BrukerUtstyrProfil).filter(
        and_(
            BrukerUtstyrProfil.bruker_id == current_user.bruker_id,
            BrukerUtstyrProfil.profil_id != profil_id
        )
    ).update({"aktiv": False})

    # Activate this profile
    profil.aktiv = True

    db.commit()
    db.refresh(profil)

    # Get equipment details
    utstyr_list = db.query(Utstyr).filter(
        Utstyr.utstyr_id.in_(profil.utstyr_ids)
    ).all()

    return {
        "profil_id": profil.profil_id,
        "bruker_id": profil.bruker_id,
        "profil_navn": profil.profil_navn,
        "utstyr_ids": profil.utstyr_ids,
        "aktiv": profil.aktiv,
        "utstyr": utstyr_list
    }
