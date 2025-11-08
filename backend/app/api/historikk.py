"""
Workout history API endpoints
"""
from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.database import get_db
from app.models import Bruker, OvelseUtfort, Ovelse, OvelseMuskel, Muskel
from app.schemas import HistorikkResponse, OvelseUtfortResponse, TreningsoktResponse
from app.utils.security import get_current_user


router = APIRouter()


# ============================================================================
# GET WORKOUT HISTORY
# ============================================================================

@router.get("/", response_model=List[HistorikkResponse])
async def get_historikk(
    current_user: Bruker = Depends(get_current_user),
    db: Session = Depends(get_db),
    dager: int = Query(30, ge=1, le=365, description="Number of days of history to retrieve (default 30)")
):
    """
    Get workout history grouped by date.

    Returns exercises logged in the last N days, grouped by date.

    Args:
        dager: Number of days of history (default 30, max 365)
    """
    # Calculate start date
    start_date = datetime.utcnow() - timedelta(days=dager)

    # Get all exercises logged since start_date
    utforte = db.query(OvelseUtfort, Ovelse).join(
        Ovelse,
        OvelseUtfort.ovelse_id == Ovelse.ovelse_id
    ).filter(
        and_(
            OvelseUtfort.bruker_id == current_user.bruker_id,
            OvelseUtfort.tidspunkt >= start_date
        )
    ).order_by(
        OvelseUtfort.tidspunkt.desc()
    ).all()

    # Group by date
    grouped = {}
    for utfort, ovelse in utforte:
        # Get date string (YYYY-MM-DD)
        date_str = utfort.tidspunkt.strftime("%Y-%m-%d")

        if date_str not in grouped:
            grouped[date_str] = []

        # Get muscles for this exercise
        muskler = db.query(Muskel.muskel_navn).join(
            OvelseMuskel,
            Muskel.muskel_id == OvelseMuskel.muskel_id
        ).filter(
            OvelseMuskel.ovelse_id == utfort.ovelse_id
        ).all()

        involverte_muskler = [muskel.muskel_navn for muskel in muskler]

        grouped[date_str].append({
            "utfort_id": utfort.utfort_id,
            "bruker_id": utfort.bruker_id,
            "ovelse_id": utfort.ovelse_id,
            "ovelse_navn": ovelse.ovelse_navn,
            "sett": utfort.sett,
            "repetisjoner": utfort.repetisjoner,
            "vekt": utfort.vekt,
            "tidspunkt": utfort.tidspunkt,
            "involverte_muskler": involverte_muskler
        })

    # Build response
    result = [
        {
            "dato": date_str,
            "ovelser": ovelser
        }
        for date_str, ovelser in sorted(grouped.items(), reverse=True)
    ]

    return result


# ============================================================================
# GET SPECIFIC WORKOUT SESSION
# ============================================================================

@router.get("/treningsokt/{dato}", response_model=TreningsoktResponse)
async def get_treningsokt(
    dato: str,
    current_user: Bruker = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details for a specific workout session by date.

    Args:
        dato: Date in format YYYY-MM-DD

    Returns:
        Workout session with statistics and exercises
    """
    # Parse date
    try:
        dato_obj = datetime.strptime(dato, "%Y-%m-%d")
    except ValueError:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )

    # Get date range (whole day)
    start_datetime = dato_obj.replace(hour=0, minute=0, second=0, microsecond=0)
    end_datetime = start_datetime + timedelta(days=1)

    # Get exercises for this date
    utforte = db.query(OvelseUtfort, Ovelse).join(
        Ovelse,
        OvelseUtfort.ovelse_id == Ovelse.ovelse_id
    ).filter(
        and_(
            OvelseUtfort.bruker_id == current_user.bruker_id,
            OvelseUtfort.tidspunkt >= start_datetime,
            OvelseUtfort.tidspunkt < end_datetime
        )
    ).order_by(
        OvelseUtfort.tidspunkt
    ).all()

    if not utforte:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No workout found for this date"
        )

    # Build exercise list
    ovelser = []
    total_volum = 0
    total_sett = 0

    for utfort, ovelse in utforte:
        ovelser.append({
            "utfort_id": utfort.utfort_id,
            "bruker_id": utfort.bruker_id,
            "ovelse_id": utfort.ovelse_id,
            "ovelse_navn": ovelse.ovelse_navn,
            "sett": utfort.sett,
            "repetisjoner": utfort.repetisjoner,
            "vekt": utfort.vekt,
            "tidspunkt": utfort.tidspunkt
        })

        # Calculate volume
        volum = utfort.sett * utfort.repetisjoner * utfort.vekt
        total_volum += volum
        total_sett += utfort.sett

    # Count unique exercises
    unique_ovelser = len(set(utfort.ovelse_id for utfort, _ in utforte))

    return {
        "dato": utforte[0][0].tidspunkt,  # Use first exercise timestamp
        "total_ovelser": unique_ovelser,
        "total_sett": total_sett,
        "total_volum": total_volum,
        "ovelser": ovelser
    }


# ============================================================================
# GET RECENT ACTIVITY
# ============================================================================

@router.get("/siste", response_model=List[OvelseUtfortResponse])
async def get_siste_ovelser(
    current_user: Bruker = Depends(get_current_user),
    db: Session = Depends(get_db),
    antall: int = Query(10, ge=1, le=50, description="Number of recent exercises to retrieve (default 10, max 50)")
):
    """
    Get most recent logged exercises.

    Args:
        antall: Number of exercises to return (default 10, max 50)
    """
    utforte = db.query(OvelseUtfort, Ovelse).join(
        Ovelse,
        OvelseUtfort.ovelse_id == Ovelse.ovelse_id
    ).filter(
        OvelseUtfort.bruker_id == current_user.bruker_id
    ).order_by(
        OvelseUtfort.tidspunkt.desc()
    ).limit(antall).all()

    result = []
    for utfort, ovelse in utforte:
        result.append({
            "utfort_id": utfort.utfort_id,
            "bruker_id": utfort.bruker_id,
            "ovelse_id": utfort.ovelse_id,
            "ovelse_navn": ovelse.ovelse_navn,
            "sett": utfort.sett,
            "repetisjoner": utfort.repetisjoner,
            "vekt": utfort.vekt,
            "tidspunkt": utfort.tidspunkt
        })

    return result
