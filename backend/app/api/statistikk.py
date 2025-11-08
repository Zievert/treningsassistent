"""
Statistics API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Bruker
from app.schemas import (
    MuskelVolumResponse,
    AntagonistiskBalanseResponse,
    MuskelDetaljerResponse,
    VolumOvertidResponse
)
from app.utils.security import get_current_user
from app.services.statistikk import (
    beregn_muskel_volum,
    beregn_antagonistisk_balanse,
    beregn_volum_over_tid,
    hent_muskel_detaljer
)


router = APIRouter()


# ============================================================================
# MUSCLE VOLUME HEATMAP
# ============================================================================

@router.get("/heatmap", response_model=List[MuskelVolumResponse])
async def get_heatmap(
    current_user: Bruker = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get muscle volume data for heatmap visualization.

    Returns volume statistics for all muscles, useful for:
    - Visual heatmap of muscle training
    - Identifying neglected muscle groups
    - Understanding training distribution
    """
    volum_data = beregn_muskel_volum(db, current_user.bruker_id)
    return volum_data


# ============================================================================
# ANTAGONISTIC BALANCE
# ============================================================================

@router.get("/antagonistisk-balanse", response_model=List[AntagonistiskBalanseResponse])
async def get_antagonistisk_balanse(
    current_user: Bruker = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get antagonistic muscle balance analysis.

    Compares volume between opposing muscle pairs to identify imbalances.

    Balance status:
    - 'balanced': Ratio within acceptable range
    - 'muskel_1_needs_work': First muscle needs more training
    - 'muskel_2_needs_work': Second muscle needs more training
    """
    balanse_data = beregn_antagonistisk_balanse(db, current_user.bruker_id)
    return balanse_data


# ============================================================================
# VOLUME OVER TIME
# ============================================================================

@router.get("/volum-over-tid", response_model=List[VolumOvertidResponse])
async def get_volum_over_tid(
    current_user: Bruker = Depends(get_current_user),
    db: Session = Depends(get_db),
    dager: int = Query(30, ge=1, le=365, description="Number of days to analyze (default 30, max 365)")
):
    """
    Get daily volume statistics over time.

    Useful for:
    - Progress tracking
    - Identifying training frequency patterns
    - Volume trend analysis

    Args:
        dager: Number of days to look back (default 30, max 365)
    """
    volum_data = beregn_volum_over_tid(db, current_user.bruker_id, dager)
    return volum_data


# ============================================================================
# MUSCLE DETAILS
# ============================================================================

@router.get("/muskel/{muskel_id}", response_model=MuskelDetaljerResponse)
async def get_muskel_detaljer(
    muskel_id: int,
    current_user: Bruker = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed statistics for a specific muscle.

    Includes:
    - Total volume and training frequency
    - Last trained date
    - List of exercises used for this muscle
    - Usage count per exercise

    Args:
        muskel_id: ID of the muscle to analyze
    """
    detaljer = hent_muskel_detaljer(db, current_user.bruker_id, muskel_id)

    if not detaljer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Muscle not found"
        )

    return detaljer


# ============================================================================
# DASHBOARD SUMMARY
# ============================================================================

@router.get("/dashboard")
async def get_dashboard_summary(
    current_user: Bruker = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get summary statistics for dashboard.

    Returns:
    - Total workouts logged
    - Total exercises logged
    - Total volume
    - Recent activity
    - Balance overview
    """
    from app.models import OvelseUtfort
    from sqlalchemy import func
    from datetime import datetime, timedelta

    # Total stats
    total_utfort = db.query(OvelseUtfort).filter(
        OvelseUtfort.bruker_id == current_user.bruker_id
    ).count()

    # Total volume
    total_volum_result = db.query(
        func.sum(OvelseUtfort.sett * OvelseUtfort.repetisjoner * OvelseUtfort.vekt)
    ).filter(
        OvelseUtfort.bruker_id == current_user.bruker_id
    ).scalar()

    total_volum = float(total_volum_result) if total_volum_result else 0.0

    # Recent activity (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_count = db.query(OvelseUtfort).filter(
        OvelseUtfort.bruker_id == current_user.bruker_id,
        OvelseUtfort.tidspunkt >= seven_days_ago
    ).count()

    # Count unique exercises used
    from app.models import BrukerOvelseHistorikk
    unique_ovelser = db.query(BrukerOvelseHistorikk).filter(
        BrukerOvelseHistorikk.bruker_id == current_user.bruker_id
    ).count()

    # Antagonistic balance summary
    balanse_data = beregn_antagonistisk_balanse(db, current_user.bruker_id)
    imbalanced_pairs = [b for b in balanse_data if b["balanse_status"] != "balanced"]

    return {
        "total_utforte_ovelser": total_utfort,
        "total_volum": total_volum,
        "unike_ovelser_brukt": unique_ovelser,
        "siste_7_dager": recent_count,
        "antagonistisk_balanse": {
            "total_par": len(balanse_data),
            "balanserte_par": len(balanse_data) - len(imbalanced_pairs),
            "ubalanserte_par": len(imbalanced_pairs)
        }
    }
