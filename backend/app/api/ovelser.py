"""
Exercise API endpoints
"""
import json
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app.models import (
    Bruker, Ovelse, OvelseMuskel, OvelseUtstyr, Muskel, Utstyr,
    OvelseUtfort, BrukerOvelseHistorikk
)
from app.schemas import (
    OvelseResponse, OvelseListItem, OvelseLogg, OvelseUtfortResponse,
    AnbefalingResponse, OvelseMuskelResponse, UtstyrResponse
)
from app.utils.security import get_current_user
from app.services.ai_forslag import hent_neste_anbefaling, oppdater_muskel_status_etter_logg


router = APIRouter()


# ============================================================================
# GET NEXT RECOMMENDATION
# ============================================================================

@router.get("/neste-anbefaling", response_model=AnbefalingResponse)
async def get_neste_anbefaling(
    current_user: Bruker = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the next recommended exercise based on muscle priorities and balance.

    Algorithm considers:
    - Muscles that haven't been trained recently
    - Antagonistic muscle balance
    - Available equipment from user's active profile
    """
    ovelse, grunn, prioritert_muskel, prioritet_score = hent_neste_anbefaling(
        db, current_user.bruker_id
    )

    if not ovelse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=grunn
        )

    # Build full exercise response with related data
    ovelse_response = build_ovelse_response(db, ovelse)

    return {
        "ovelse": ovelse_response,
        "grunn": grunn,
        "prioritert_muskel": prioritert_muskel,
        "prioritet_score": prioritet_score
    }


# ============================================================================
# GET ALL EXERCISES
# ============================================================================

@router.get("/alle", response_model=List[OvelseListItem])
async def get_alle_ovelser(
    current_user: Bruker = Depends(get_current_user),
    db: Session = Depends(get_db),
    muskel: Optional[str] = Query(None, description="Filter by muscle name"),
    level: Optional[str] = Query(None, description="Filter by difficulty level"),
    force: Optional[str] = Query(None, description="Filter by force type (push/pull/static)"),
    limit: int = Query(100, le=500, description="Maximum number of results")
):
    """
    Get all exercises with optional filters.

    Filters:
    - muskel: Filter by muscle name (e.g., 'chest', 'quadriceps')
    - level: Filter by difficulty (beginner, intermediate, expert)
    - force: Filter by force type (push, pull, static)
    - limit: Maximum results (default 100, max 500)
    """
    query = db.query(Ovelse)

    # Filter by muscle if specified
    if muskel:
        query = query.join(
            OvelseMuskel,
            Ovelse.ovelse_id == OvelseMuskel.ovelse_id
        ).join(
            Muskel,
            OvelseMuskel.muskel_id == Muskel.muskel_id
        ).filter(
            Muskel.muskel_navn == muskel
        )

    # Filter by level
    if level:
        query = query.filter(Ovelse.level == level)

    # Filter by force
    if force:
        query = query.filter(Ovelse.force == force)

    # Limit results
    ovelser = query.limit(limit).all()

    # Build list items
    result = []
    for ovelse in ovelser:
        item = build_ovelse_list_item(db, ovelse)
        result.append(item)

    return result


@router.get("/tilgjengelige", response_model=List[OvelseListItem])
async def get_tilgjengelige_ovelser(
    current_user: Bruker = Depends(get_current_user),
    db: Session = Depends(get_db),
    muskel: Optional[str] = Query(None, description="Filter by muscle name"),
    level: Optional[str] = Query(None, description="Filter by difficulty level"),
    force: Optional[str] = Query(None, description="Filter by force type (push/pull/static)"),
    limit: int = Query(100, le=500, description="Maximum number of results")
):
    """
    Get exercises filtered by user's active equipment profile.

    Automatically filters exercises based on the user's active equipment profile.
    Only returns exercises that can be performed with the available equipment.

    Additional filters:
    - muskel: Filter by muscle name (e.g., 'chest', 'quadriceps')
    - level: Filter by difficulty (beginner, intermediate, expert)
    - force: Filter by force type (push, pull, static)
    - limit: Maximum results (default 100, max 500)
    """
    from app.models import BrukerUtstyrProfil

    # Get user's active equipment profile
    utstyr_profil = db.query(BrukerUtstyrProfil).filter(
        and_(
            BrukerUtstyrProfil.bruker_id == current_user.bruker_id,
            BrukerUtstyrProfil.aktiv == True
        )
    ).first()

    # Start building query
    query = db.query(Ovelse)

    # Filter by equipment if user has active profile
    if utstyr_profil and utstyr_profil.utstyr_ids:
        query = query.join(
            OvelseUtstyr,
            Ovelse.ovelse_id == OvelseUtstyr.ovelse_id
        ).filter(
            OvelseUtstyr.utstyr_id.in_(utstyr_profil.utstyr_ids)
        )

    # Filter by muscle if specified
    if muskel:
        query = query.join(
            OvelseMuskel,
            Ovelse.ovelse_id == OvelseMuskel.ovelse_id
        ).join(
            Muskel,
            OvelseMuskel.muskel_id == Muskel.muskel_id
        ).filter(
            Muskel.muskel_navn == muskel
        )

    # Filter by level
    if level:
        query = query.filter(Ovelse.level == level)

    # Filter by force
    if force:
        query = query.filter(Ovelse.force == force)

    # Deduplicate exercises (same exercise might match multiple equipment)
    query = query.distinct()

    # Limit results
    ovelser = query.limit(limit).all()

    # Build list items
    result = []
    for ovelse in ovelser:
        item = build_ovelse_list_item(db, ovelse)
        result.append(item)

    return result


# ============================================================================
# GET SPECIFIC EXERCISE
# ============================================================================

@router.get("/{ovelse_id}", response_model=OvelseResponse)
async def get_ovelse(
    ovelse_id: int,
    current_user: Bruker = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific exercise.

    Includes:
    - Exercise details
    - Primary and secondary muscles
    - Required equipment
    - Instructions
    - Image URLs
    """
    ovelse = db.query(Ovelse).filter(Ovelse.ovelse_id == ovelse_id).first()

    if not ovelse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )

    return build_ovelse_response(db, ovelse)


# ============================================================================
# LOG EXERCISE
# ============================================================================

@router.post("/logg", response_model=OvelseUtfortResponse, status_code=status.HTTP_201_CREATED)
async def logg_ovelse(
    logg_data: OvelseLogg,
    current_user: Bruker = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log a completed exercise.

    Updates:
    - ovelser_utfort table (log entry)
    - bruker_muskel_status (muscle training stats)
    - bruker_ovelse_historikk (exercise usage tracking)

    Args:
        logg_data: Exercise log data (ovelse_id, sett, reps, vekt)
    """
    # Verify exercise exists
    ovelse = db.query(Ovelse).filter(Ovelse.ovelse_id == logg_data.ovelse_id).first()

    if not ovelse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )

    # Create log entry
    utfort = OvelseUtfort(
        bruker_id=current_user.bruker_id,
        ovelse_id=logg_data.ovelse_id,
        sett=logg_data.sett,
        repetisjoner=logg_data.repetisjoner,
        vekt=logg_data.vekt,
        tidspunkt=datetime.utcnow()
    )

    db.add(utfort)
    db.flush()  # Get utfort_id

    # Calculate volume
    volum = Decimal(logg_data.sett) * Decimal(logg_data.repetisjoner) * logg_data.vekt

    # Update muscle status
    oppdater_muskel_status_etter_logg(
        db, current_user.bruker_id, logg_data.ovelse_id, volum
    )

    # Update exercise usage history
    oppdater_ovelse_historikk(db, current_user.bruker_id, logg_data.ovelse_id)

    db.commit()
    db.refresh(utfort)

    # Build response
    return {
        "utfort_id": utfort.utfort_id,
        "bruker_id": utfort.bruker_id,
        "ovelse_id": utfort.ovelse_id,
        "ovelse_navn": ovelse.ovelse_navn,
        "sett": utfort.sett,
        "repetisjoner": utfort.repetisjoner,
        "vekt": utfort.vekt,
        "tidspunkt": utfort.tidspunkt
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def build_ovelse_response(db: Session, ovelse: Ovelse) -> OvelseResponse:
    """
    Build full exercise response with related data.
    """
    # Get muscles
    ovelse_muskler = db.query(OvelseMuskel, Muskel).join(
        Muskel,
        OvelseMuskel.muskel_id == Muskel.muskel_id
    ).filter(
        OvelseMuskel.ovelse_id == ovelse.ovelse_id
    ).all()

    muskler = [
        {
            "muskel_id": muskel.muskel_id,
            "muskel_navn": muskel.muskel_navn,
            "muskel_type": ovelse_muskel.muskel_type
        }
        for ovelse_muskel, muskel in ovelse_muskler
    ]

    # Get equipment
    ovelse_utstyr = db.query(OvelseUtstyr, Utstyr).join(
        Utstyr,
        OvelseUtstyr.utstyr_id == Utstyr.utstyr_id
    ).filter(
        OvelseUtstyr.ovelse_id == ovelse.ovelse_id
    ).all()

    utstyr = [
        {
            "utstyr_id": utstyr_obj.utstyr_id,
            "utstyr_navn": utstyr_obj.utstyr_navn,
            "kategori": utstyr_obj.kategori
        }
        for _, utstyr_obj in ovelse_utstyr
    ]

    return {
        "ovelse_id": ovelse.ovelse_id,
        "ovelse_navn": ovelse.ovelse_navn,
        "force": ovelse.force,
        "level": ovelse.level,
        "mechanic": ovelse.mechanic,
        "category": ovelse.category,
        "bilde_1_url": ovelse.bilde_1_url,
        "bilde_2_url": ovelse.bilde_2_url,
        "kilde_id": ovelse.kilde_id,
        "instruksjoner": ovelse.instruksjoner,
        "muskler": muskler,
        "utstyr": utstyr
    }


def build_ovelse_list_item(db: Session, ovelse: Ovelse) -> OvelseListItem:
    """
    Build lighter exercise list item.
    """
    # Get muscles
    ovelse_muskler = db.query(OvelseMuskel, Muskel).join(
        Muskel,
        OvelseMuskel.muskel_id == Muskel.muskel_id
    ).filter(
        OvelseMuskel.ovelse_id == ovelse.ovelse_id
    ).all()

    primary_muscles = [
        muskel.muskel_navn
        for ovelse_muskel, muskel in ovelse_muskler
        if ovelse_muskel.muskel_type == 'primar'
    ]

    secondary_muscles = [
        muskel.muskel_navn
        for ovelse_muskel, muskel in ovelse_muskler
        if ovelse_muskel.muskel_type == 'sekundar'
    ]

    # Get equipment (just first one for list view)
    ovelse_utstyr = db.query(Utstyr).join(
        OvelseUtstyr,
        Utstyr.utstyr_id == OvelseUtstyr.utstyr_id
    ).filter(
        OvelseUtstyr.ovelse_id == ovelse.ovelse_id
    ).first()

    equipment = ovelse_utstyr.utstyr_navn if ovelse_utstyr else None

    return {
        "ovelse_id": ovelse.ovelse_id,
        "ovelse_navn": ovelse.ovelse_navn,
        "force": ovelse.force,
        "level": ovelse.level,
        "mechanic": ovelse.mechanic,
        "category": ovelse.category,
        "bilde_1_url": ovelse.bilde_1_url,
        "bilde_2_url": ovelse.bilde_2_url,
        "kilde_id": ovelse.kilde_id,
        "primary_muscles": primary_muscles,
        "secondary_muscles": secondary_muscles,
        "equipment": equipment
    }


def oppdater_ovelse_historikk(db: Session, bruker_id: int, ovelse_id: int):
    """
    Update exercise usage history for user.
    """
    historikk = db.query(BrukerOvelseHistorikk).filter(
        and_(
            BrukerOvelseHistorikk.bruker_id == bruker_id,
            BrukerOvelseHistorikk.ovelse_id == ovelse_id
        )
    ).first()

    if not historikk:
        # Create new history entry
        historikk = BrukerOvelseHistorikk(
            bruker_id=bruker_id,
            ovelse_id=ovelse_id,
            sist_brukt_dato=datetime.utcnow(),
            antall_ganger_brukt=1
        )
        db.add(historikk)
    else:
        # Update existing
        historikk.sist_brukt_dato = datetime.utcnow()
        historikk.antall_ganger_brukt += 1

    # Note: commit happens in main endpoint function
