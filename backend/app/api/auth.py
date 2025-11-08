"""
Authentication API endpoints
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Bruker, Invitasjon
from app.schemas import BrukerRegistrer, BrukerLogin, Token, BrukerResponse, MessageResponse
from app.utils.security import hash_password, authenticate_user, create_access_token, get_current_user


router = APIRouter()


# ============================================================================
# REGISTRATION
# ============================================================================

@router.post("/register", response_model=BrukerResponse, status_code=status.HTTP_201_CREATED)
async def register(
    bruker_data: BrukerRegistrer,
    db: Session = Depends(get_db)
):
    """
    Register a new user with an invitation code.

    - Validates invitation code
    - Checks that username and email are unique
    - Creates new user account
    - Marks invitation as used
    """
    # Validate invitation code
    invitasjon = db.query(Invitasjon).filter(
        Invitasjon.invitasjonskode == bruker_data.invitasjonskode
    ).first()

    if not invitasjon:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid invitation code"
        )

    if invitasjon.brukt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation code has already been used"
        )

    if invitasjon.utloper_dato and invitasjon.utloper_dato < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation code has expired"
        )

    # Validate email matches invitation (if invitation has specific email)
    if invitasjon.epost and invitasjon.epost != bruker_data.epost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation code is for a different email address"
        )

    # Check if username already exists
    existing_bruker = db.query(Bruker).filter(
        Bruker.brukernavn == bruker_data.brukernavn
    ).first()

    if existing_bruker:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    # Check if email already exists
    existing_email = db.query(Bruker).filter(
        Bruker.epost == bruker_data.epost
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = hash_password(bruker_data.passord)

    ny_bruker = Bruker(
        brukernavn=bruker_data.brukernavn,
        epost=bruker_data.epost,
        passord_hash=hashed_password,
        aktiv=True,
        rolle="bruker"  # Default role
    )

    db.add(ny_bruker)

    # Mark invitation as used
    invitasjon.brukt = True

    db.commit()
    db.refresh(ny_bruker)

    return ny_bruker


# ============================================================================
# LOGIN
# ============================================================================

@router.post("/login", response_model=Token)
async def login(
    login_data: BrukerLogin,
    db: Session = Depends(get_db)
):
    """
    Login with username and password.

    Returns JWT access token on success.
    """
    bruker = authenticate_user(db, login_data.brukernavn, login_data.passord)

    if not bruker:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not bruker.aktiv:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Create JWT token
    access_token = create_access_token(data={"sub": str(bruker.bruker_id)})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ============================================================================
# CURRENT USER
# ============================================================================

@router.get("/me", response_model=BrukerResponse)
async def get_me(
    current_user: Bruker = Depends(get_current_user)
):
    """
    Get current authenticated user information.

    Requires valid JWT token in Authorization header.
    """
    return current_user


# ============================================================================
# LOGOUT (client-side only)
# ============================================================================

@router.post("/logout", response_model=MessageResponse)
async def logout():
    """
    Logout endpoint (for API consistency).

    Since we use stateless JWT tokens, actual logout happens client-side
    by deleting the token. This endpoint exists for API consistency
    and to allow future server-side token revocation if needed.
    """
    return {"message": "Logged out successfully. Delete your token client-side."}
