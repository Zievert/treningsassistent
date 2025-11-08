"""
Muscle API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Bruker, Muskel, BrukerMuskelStatus
from app.schemas import MuskelResponse, MuskelPrioritetResponse
from app.utils.security import get_current_user
from app.services.ai_forslag import beregn_prioritet


router = APIRouter()


# ============================================================================
# GET ALL MUSCLES
# ============================================================================

@router.get("/", response_model=List[MuskelResponse])
async def get_alle_muskler(
    current_user: Bruker = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of all muscles.

    Returns all muscles in the system with their categories.
    """
    muskler = db.query(Muskel).order_by(
        Muskel.hovedkategori,
        Muskel.underkategori,
        Muskel.muskel_navn
    ).all()

    return muskler


# ============================================================================
# GET MUSCLE PRIORITIES
# ============================================================================

@router.get("/prioritet", response_model=List[MuskelPrioritetResponse])
async def get_muskel_prioriteter(
    current_user: Bruker = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all muscles with their priority scores.

    Priority indicates how much each muscle needs training.
    Higher score = needs training more.

    Useful for:
    - Dashboard visualization
    - Understanding which muscles are neglected
    - Planning workout focus
    """
    muskler = db.query(Muskel).all()

    result = []
    for muskel in muskler:
        # Calculate priority
        prioritet_score = beregn_prioritet(db, current_user.bruker_id, muskel.muskel_id)

        # Get muscle status for additional info
        status = db.query(BrukerMuskelStatus).filter(
            BrukerMuskelStatus.bruker_id == current_user.bruker_id,
            BrukerMuskelStatus.muskel_id == muskel.muskel_id
        ).first()

        # Calculate days since trained
        dager_siden_trent = None
        if status and status.sist_trent_dato:
            from datetime import datetime
            dager_siden_trent = (datetime.utcnow() - status.sist_trent_dato).days

        result.append({
            "muskel_id": muskel.muskel_id,
            "muskel_navn": muskel.muskel_navn,
            "hovedkategori": muskel.hovedkategori,
            "underkategori": muskel.underkategori,
            "prioritet_score": prioritet_score,
            "dager_siden_trent": dager_siden_trent,
            "total_volum": status.total_volum if status else None
        })

    # Sort by priority (highest first)
    result.sort(key=lambda x: x["prioritet_score"], reverse=True)

    return result


# ============================================================================
# GET SPECIFIC MUSCLE DETAILS
# ============================================================================

@router.get("/{muskel_id}", response_model=MuskelPrioritetResponse)
async def get_muskel(
    muskel_id: int,
    current_user: Bruker = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific muscle.

    Includes:
    - Muscle info (name, categories)
    - Priority score
    - Days since last trained
    - Total volume
    """
    from fastapi import HTTPException, status

    muskel = db.query(Muskel).filter(Muskel.muskel_id == muskel_id).first()

    if not muskel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Muscle not found"
        )

    # Calculate priority
    prioritet_score = beregn_prioritet(db, current_user.bruker_id, muskel.muskel_id)

    # Get muscle status
    from datetime import datetime
    status = db.query(BrukerMuskelStatus).filter(
        BrukerMuskelStatus.bruker_id == current_user.bruker_id,
        BrukerMuskelStatus.muskel_id == muskel.muskel_id
    ).first()

    dager_siden_trent = None
    if status and status.sist_trent_dato:
        dager_siden_trent = (datetime.utcnow() - status.sist_trent_dato).days

    return {
        "muskel_id": muskel.muskel_id,
        "muskel_navn": muskel.muskel_navn,
        "hovedkategori": muskel.hovedkategori,
        "underkategori": muskel.underkategori,
        "prioritet_score": prioritet_score,
        "dager_siden_trent": dager_siden_trent,
        "total_volum": status.total_volum if status else None
    }
