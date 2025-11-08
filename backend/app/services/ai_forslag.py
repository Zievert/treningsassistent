"""
AI-powered exercise recommendation service

Core algorithm:
1. Calculate muscle priority based on days since last trained
2. Consider antagonistic muscle balance
3. Filter exercises by available equipment
4. Return exercise targeting highest-priority muscle
"""
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.models import (
    Bruker, Muskel, Ovelse, OvelseMuskel, OvelseUtstyr,
    BrukerMuskelStatus, BrukerUtstyrProfil, AntagonistiskPar,
    OvelseUtfort
)


# ============================================================================
# PRIORITY CALCULATION
# ============================================================================

def beregn_prioritet(
    db: Session,
    bruker_id: int,
    muskel_id: int
) -> float:
    """
    Calculate priority score for a muscle.

    Priority is based on:
    - Days since last trained (higher = more priority)
    - Never trained muscles get highest priority

    Args:
        db: Database session
        bruker_id: User ID
        muskel_id: Muscle ID

    Returns:
        Priority score (float). Higher = needs training more.
        - Never trained: 1000.0
        - Recently trained: low score
        - Long time since trained: high score
    """
    # Get muscle status for this user
    status = db.query(BrukerMuskelStatus).filter(
        and_(
            BrukerMuskelStatus.bruker_id == bruker_id,
            BrukerMuskelStatus.muskel_id == muskel_id
        )
    ).first()

    # If never trained, give highest priority
    if not status or not status.sist_trent_dato:
        return 1000.0

    # Calculate days since last trained
    dager_siden = (datetime.utcnow() - status.sist_trent_dato).days

    # Priority score = days since trained
    # (Simple linear formula for MVP - can be enhanced with exponential decay)
    prioritet = float(dager_siden)

    return prioritet


def beregn_alle_prioriteter(
    db: Session,
    bruker_id: int
) -> List[Tuple[int, str, float]]:
    """
    Calculate priority scores for all muscles.

    Args:
        db: Database session
        bruker_id: User ID

    Returns:
        List of tuples: (muskel_id, muskel_navn, prioritet_score)
        Sorted by priority (highest first)
    """
    # Get all muscles
    muskler = db.query(Muskel).all()

    prioriteter = []
    for muskel in muskler:
        prioritet = beregn_prioritet(db, bruker_id, muskel.muskel_id)
        prioriteter.append((muskel.muskel_id, muskel.muskel_navn, prioritet))

    # Sort by priority (highest first)
    prioriteter.sort(key=lambda x: x[2], reverse=True)

    return prioriteter


# ============================================================================
# ANTAGONISTIC BALANCE
# ============================================================================

def sjekk_antagonistisk_balanse(
    db: Session,
    bruker_id: int,
    muskel_id: int
) -> Tuple[bool, Optional[str]]:
    """
    Check if training this muscle would create antagonistic imbalance.

    Args:
        db: Database session
        bruker_id: User ID
        muskel_id: Muscle ID to check

    Returns:
        Tuple of (should_avoid, reason)
        - should_avoid: True if muscle should be avoided due to imbalance
        - reason: Explanation string (None if balanced)
    """
    # Find antagonistic pairs involving this muscle
    antagonistiske_par = db.query(AntagonistiskPar).filter(
        or_(
            AntagonistiskPar.muskel_1_id == muskel_id,
            AntagonistiskPar.muskel_2_id == muskel_id
        )
    ).all()

    if not antagonistiske_par:
        # No antagonistic pair defined for this muscle
        return False, None

    for par in antagonistiske_par:
        # Determine which is the current muscle and which is the opposing muscle
        if par.muskel_1_id == muskel_id:
            current_muskel_id = par.muskel_1_id
            opposing_muskel_id = par.muskel_2_id
            is_muskel_1 = True
        else:
            current_muskel_id = par.muskel_2_id
            opposing_muskel_id = par.muskel_1_id
            is_muskel_1 = False

        # Get volume for both muscles
        current_status = db.query(BrukerMuskelStatus).filter(
            and_(
                BrukerMuskelStatus.bruker_id == bruker_id,
                BrukerMuskelStatus.muskel_id == current_muskel_id
            )
        ).first()

        opposing_status = db.query(BrukerMuskelStatus).filter(
            and_(
                BrukerMuskelStatus.bruker_id == bruker_id,
                BrukerMuskelStatus.muskel_id == opposing_muskel_id
            )
        ).first()

        current_volum = current_status.total_volum if current_status and current_status.total_volum else Decimal(0)
        opposing_volum = opposing_status.total_volum if opposing_status and opposing_status.total_volum else Decimal(0)

        # If opposing muscle has no volume, it's fine to train current muscle
        if opposing_volum == 0:
            continue

        # Calculate actual ratio
        if is_muskel_1:
            actual_ratio = float(current_volum / opposing_volum) if opposing_volum > 0 else 0
        else:
            actual_ratio = float(opposing_volum / current_volum) if current_volum > 0 else 0

        onsket_ratio = float(par.onsket_ratio)

        # Check if current muscle is significantly over-trained compared to opposing
        # Allow 30% deviation from desired ratio
        TOLERANCE = 0.3
        max_ratio = onsket_ratio * (1 + TOLERANCE)

        if actual_ratio > max_ratio:
            # Current muscle is over-trained relative to opposing muscle
            muskel_1_navn = db.query(Muskel).get(par.muskel_1_id).muskel_navn
            muskel_2_navn = db.query(Muskel).get(par.muskel_2_id).muskel_navn

            opposing_navn = muskel_2_navn if is_muskel_1 else muskel_1_navn

            reason = f"Antagonistic imbalance: train {opposing_navn} first (ratio: {actual_ratio:.2f}, desired: {onsket_ratio:.2f})"
            return True, reason

    return False, None


# ============================================================================
# EXERCISE FINDING
# ============================================================================

def finn_ovelse_for_muskel(
    db: Session,
    bruker_id: int,
    muskel_id: int,
    utstyr_ids: Optional[List[int]] = None
) -> Optional[Ovelse]:
    """
    Find an appropriate exercise for a given muscle.

    Prioritizes:
    1. Exercises the user hasn't done recently
    2. Exercises with the muscle as primary target
    3. Exercises available with user's equipment

    Args:
        db: Database session
        bruker_id: User ID
        muskel_id: Target muscle ID
        utstyr_ids: List of available equipment IDs (None = all equipment)

    Returns:
        Ovelse object or None if no suitable exercise found
    """
    # Build base query for exercises targeting this muscle
    query = db.query(Ovelse).join(
        OvelseMuskel,
        Ovelse.ovelse_id == OvelseMuskel.ovelse_id
    ).filter(
        OvelseMuskel.muskel_id == muskel_id
    )

    # Filter by equipment if specified
    if utstyr_ids:
        query = query.join(
            OvelseUtstyr,
            Ovelse.ovelse_id == OvelseUtstyr.ovelse_id
        ).filter(
            OvelseUtstyr.utstyr_id.in_(utstyr_ids)
        )

    # Prioritize primary muscle exercises
    # Subquery for exercises with this muscle as primary
    primary_exercises = query.filter(
        OvelseMuskel.muskel_type == 'primar'
    ).all()

    if primary_exercises:
        # Pick least recently used exercise (or random if never used)
        # For MVP, just pick first one - can enhance with usage tracking later
        return primary_exercises[0]

    # Fall back to secondary muscle exercises
    secondary_exercises = query.filter(
        OvelseMuskel.muskel_type == 'sekundar'
    ).all()

    if secondary_exercises:
        return secondary_exercises[0]

    return None


# ============================================================================
# MAIN RECOMMENDATION FUNCTION
# ============================================================================

def hent_neste_anbefaling(
    db: Session,
    bruker_id: int
) -> Tuple[Optional[Ovelse], str, Optional[str], Optional[float]]:
    """
    Get the next recommended exercise for a user.

    Algorithm:
    1. Get user's active equipment profile
    2. Calculate priority for all muscles
    3. Check antagonistic balance
    4. Find exercise for highest-priority balanced muscle

    Args:
        db: Database session
        bruker_id: User ID

    Returns:
        Tuple of (ovelse, grunn, prioritert_muskel_navn, prioritet_score)
        - ovelse: Recommended exercise (None if no recommendation)
        - grunn: Reason for recommendation
        - prioritert_muskel_navn: Name of prioritized muscle
        - prioritet_score: Priority score
    """
    # Get user's active equipment profile
    utstyr_profil = db.query(BrukerUtstyrProfil).filter(
        and_(
            BrukerUtstyrProfil.bruker_id == bruker_id,
            BrukerUtstyrProfil.aktiv == True
        )
    ).first()

    utstyr_ids = utstyr_profil.utstyr_ids if utstyr_profil else None

    # Calculate priorities for all muscles
    prioriteter = beregn_alle_prioriteter(db, bruker_id)

    # Iterate through muscles by priority and find first one that:
    # 1. Doesn't create antagonistic imbalance
    # 2. Has available exercises with user's equipment
    for muskel_id, muskel_navn, prioritet_score in prioriteter:
        # Check antagonistic balance
        should_avoid, balance_reason = sjekk_antagonistisk_balanse(db, bruker_id, muskel_id)

        if should_avoid:
            # Skip this muscle due to imbalance
            continue

        # Find exercise for this muscle
        ovelse = finn_ovelse_for_muskel(db, bruker_id, muskel_id, utstyr_ids)

        if ovelse:
            # Found suitable exercise!
            if prioritet_score >= 1000.0:
                grunn = f"Never trained {muskel_navn} before - great time to start!"
            else:
                dager = int(prioritet_score)
                grunn = f"{muskel_navn} hasn't been trained in {dager} day{'s' if dager != 1 else ''}"

            return ovelse, grunn, muskel_navn, prioritet_score

    # No suitable exercise found
    return None, "No exercises available with your current equipment profile", None, None


# ============================================================================
# EXERCISE LOGGING (updates muscle status)
# ============================================================================

def oppdater_muskel_status_etter_logg(
    db: Session,
    bruker_id: int,
    ovelse_id: int,
    volum: Decimal
):
    """
    Update muscle status after logging an exercise.

    Updates:
    - sist_trent_dato
    - antall_ganger_trent
    - total_volum (weighted by muscle involvement)

    Args:
        db: Database session
        bruker_id: User ID
        ovelse_id: Exercise ID that was logged
        volum: Volume (sett × reps × vekt)
    """
    # Get muscles involved in this exercise
    ovelse_muskler = db.query(OvelseMuskel).filter(
        OvelseMuskel.ovelse_id == ovelse_id
    ).all()

    now = datetime.utcnow()

    for ovelse_muskel in ovelse_muskler:
        muskel_id = ovelse_muskel.muskel_id
        muskel_type = ovelse_muskel.muskel_type

        # Calculate weighted volume
        # Primary muscles: 100% of volume
        # Secondary muscles: 50% of volume
        if muskel_type == 'primar':
            weighted_volum = volum
        else:  # sekundar
            weighted_volum = volum * Decimal('0.5')

        # Get or create muscle status
        status = db.query(BrukerMuskelStatus).filter(
            and_(
                BrukerMuskelStatus.bruker_id == bruker_id,
                BrukerMuskelStatus.muskel_id == muskel_id
            )
        ).first()

        if not status:
            # Create new status
            status = BrukerMuskelStatus(
                bruker_id=bruker_id,
                muskel_id=muskel_id,
                sist_trent_dato=now,
                antall_ganger_trent=1,
                total_volum=weighted_volum
            )
            db.add(status)
        else:
            # Update existing status
            status.sist_trent_dato = now
            status.antall_ganger_trent += 1
            status.total_volum = (status.total_volum or Decimal(0)) + weighted_volum

    db.commit()
