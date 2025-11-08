"""
Statistics calculation service
"""
from typing import List, Dict
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.models import (
    Bruker, Muskel, BrukerMuskelStatus, AntagonistiskPar,
    OvelseUtfort, Ovelse, OvelseMuskel
)


# ============================================================================
# MUSCLE VOLUME (HEATMAP DATA)
# ============================================================================

def beregn_muskel_volum(
    db: Session,
    bruker_id: int
) -> List[Dict]:
    """
    Calculate volume statistics for all muscles.

    Used for heatmap visualization.

    Returns:
        List of dicts with muscle info and volume stats
    """
    # Get all muscle status records for user
    status_records = db.query(BrukerMuskelStatus, Muskel).join(
        Muskel,
        BrukerMuskelStatus.muskel_id == Muskel.muskel_id
    ).filter(
        BrukerMuskelStatus.bruker_id == bruker_id
    ).all()

    result = []
    for status, muskel in status_records:
        result.append({
            "muskel_navn": muskel.muskel_navn,
            "hovedkategori": muskel.hovedkategori,
            "underkategori": muskel.underkategori,
            "total_volum": status.total_volum or Decimal(0),
            "antall_ganger_trent": status.antall_ganger_trent or 0,
            "sist_trent_dato": status.sist_trent_dato
        })

    # Include muscles that haven't been trained yet
    all_muskler = db.query(Muskel).all()
    trained_muskel_ids = {status.muskel_id for status, _ in status_records}

    for muskel in all_muskler:
        if muskel.muskel_id not in trained_muskel_ids:
            result.append({
                "muskel_navn": muskel.muskel_navn,
                "hovedkategori": muskel.hovedkategori,
                "underkategori": muskel.underkategori,
                "total_volum": Decimal(0),
                "antall_ganger_trent": 0,
                "sist_trent_dato": None
            })

    return result


# ============================================================================
# ANTAGONISTIC BALANCE
# ============================================================================

def beregn_antagonistisk_balanse(
    db: Session,
    bruker_id: int
) -> List[Dict]:
    """
    Calculate antagonistic muscle balance.

    Compares volume between opposing muscle groups.

    Returns:
        List of dicts with balance information for each pair
    """
    # Get all antagonistic pairs
    par_liste = db.query(AntagonistiskPar).all()

    result = []
    for par in par_liste:
        # Get muscle names
        muskel_1 = db.query(Muskel).get(par.muskel_1_id)
        muskel_2 = db.query(Muskel).get(par.muskel_2_id)

        # Get volume for each muscle
        status_1 = db.query(BrukerMuskelStatus).filter(
            and_(
                BrukerMuskelStatus.bruker_id == bruker_id,
                BrukerMuskelStatus.muskel_id == par.muskel_1_id
            )
        ).first()

        status_2 = db.query(BrukerMuskelStatus).filter(
            and_(
                BrukerMuskelStatus.bruker_id == bruker_id,
                BrukerMuskelStatus.muskel_id == par.muskel_2_id
            )
        ).first()

        volum_1 = status_1.total_volum if status_1 and status_1.total_volum else Decimal(0)
        volum_2 = status_2.total_volum if status_2 and status_2.total_volum else Decimal(0)

        # Calculate ratio
        if volum_2 > 0:
            faktisk_ratio = volum_1 / volum_2
        else:
            faktisk_ratio = Decimal(0) if volum_1 == 0 else Decimal(999)  # Infinity-like value

        onsket_ratio = par.onsket_ratio

        # Determine balance status
        TOLERANCE = Decimal('0.3')  # 30% tolerance
        min_ratio = onsket_ratio * (Decimal('1') - TOLERANCE)
        max_ratio = onsket_ratio * (Decimal('1') + TOLERANCE)

        if volum_1 == 0 and volum_2 == 0:
            balanse_status = "balanced"  # Neither trained yet
            avvik_prosent = 0.0
        elif min_ratio <= faktisk_ratio <= max_ratio:
            balanse_status = "balanced"
            avvik_prosent = abs(float((faktisk_ratio - onsket_ratio) / onsket_ratio * 100))
        elif faktisk_ratio < min_ratio:
            balanse_status = "muskel_1_needs_work"
            avvik_prosent = abs(float((faktisk_ratio - onsket_ratio) / onsket_ratio * 100))
        else:
            balanse_status = "muskel_2_needs_work"
            avvik_prosent = abs(float((faktisk_ratio - onsket_ratio) / onsket_ratio * 100))

        result.append({
            "muskel_1_navn": muskel_1.muskel_navn,
            "muskel_2_navn": muskel_2.muskel_navn,
            "muskel_1_volum": volum_1,
            "muskel_2_volum": volum_2,
            "faktisk_ratio": faktisk_ratio,
            "onsket_ratio": onsket_ratio,
            "balanse_status": balanse_status,
            "avvik_prosent": avvik_prosent
        })

    return result


# ============================================================================
# VOLUME OVER TIME
# ============================================================================

def beregn_volum_over_tid(
    db: Session,
    bruker_id: int,
    dager: int = 30
) -> List[Dict]:
    """
    Calculate total volume per day over specified time period.

    Args:
        db: Database session
        bruker_id: User ID
        dager: Number of days to look back (default 30)

    Returns:
        List of dicts with date, total_volum, antall_ovelser
    """
    # Calculate start date
    start_date = datetime.utcnow() - timedelta(days=dager)

    # Get all exercises in time period
    utforte = db.query(OvelseUtfort).filter(
        and_(
            OvelseUtfort.bruker_id == bruker_id,
            OvelseUtfort.tidspunkt >= start_date
        )
    ).all()

    # Group by date
    daily_volum = {}
    for utfort in utforte:
        date_str = utfort.tidspunkt.strftime("%Y-%m-%d")

        if date_str not in daily_volum:
            daily_volum[date_str] = {
                "volum": Decimal(0),
                "ovelser": set()
            }

        # Calculate volume
        volum = Decimal(utfort.sett) * Decimal(utfort.repetisjoner) * utfort.vekt
        daily_volum[date_str]["volum"] += volum
        daily_volum[date_str]["ovelser"].add(utfort.ovelse_id)

    # Build result
    result = []
    for date_str in sorted(daily_volum.keys()):
        result.append({
            "dato": date_str,
            "total_volum": daily_volum[date_str]["volum"],
            "antall_ovelser": len(daily_volum[date_str]["ovelser"])
        })

    return result


# ============================================================================
# MUSCLE DETAILS
# ============================================================================

def hent_muskel_detaljer(
    db: Session,
    bruker_id: int,
    muskel_id: int
) -> Dict:
    """
    Get detailed statistics for a specific muscle.

    Includes:
    - Volume and training frequency
    - List of exercises used for this muscle
    - Usage count per exercise

    Args:
        db: Database session
        bruker_id: User ID
        muskel_id: Muscle ID

    Returns:
        Dict with muscle details and exercise breakdown
    """
    # Get muscle info
    muskel = db.query(Muskel).get(muskel_id)

    if not muskel:
        return None

    # Get muscle status
    status = db.query(BrukerMuskelStatus).filter(
        and_(
            BrukerMuskelStatus.bruker_id == bruker_id,
            BrukerMuskelStatus.muskel_id == muskel_id
        )
    ).first()

    # Get exercises used for this muscle
    # Query all exercises logged by user that involve this muscle
    ovelser_brukt = db.query(
        Ovelse.ovelse_navn,
        func.count(OvelseUtfort.utfort_id).label('antall')
    ).join(
        OvelseMuskel,
        Ovelse.ovelse_id == OvelseMuskel.ovelse_id
    ).join(
        OvelseUtfort,
        Ovelse.ovelse_id == OvelseUtfort.ovelse_id
    ).filter(
        and_(
            OvelseMuskel.muskel_id == muskel_id,
            OvelseUtfort.bruker_id == bruker_id
        )
    ).group_by(
        Ovelse.ovelse_navn
    ).order_by(
        func.count(OvelseUtfort.utfort_id).desc()
    ).all()

    ovelser_list = [
        {
            "ovelse_navn": ovelse_navn,
            "antall_ganger_brukt": antall
        }
        for ovelse_navn, antall in ovelser_brukt
    ]

    return {
        "muskel_id": muskel.muskel_id,
        "muskel_navn": muskel.muskel_navn,
        "hovedkategori": muskel.hovedkategori,
        "underkategori": muskel.underkategori,
        "total_volum": status.total_volum if status else Decimal(0),
        "antall_ganger_trent": status.antall_ganger_trent if status else 0,
        "sist_trent_dato": status.sist_trent_dato if status else None,
        "ovelser_brukt": ovelser_list
    }
