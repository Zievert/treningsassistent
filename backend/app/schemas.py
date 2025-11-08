"""
Pydantic schemas for API request/response validation
"""
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field, validator


# ============================================================================
# AUTHENTICATION SCHEMAS
# ============================================================================

class BrukerRegistrer(BaseModel):
    """Schema for user registration"""
    brukernavn: str = Field(..., min_length=3, max_length=50, description="Username")
    epost: EmailStr = Field(..., description="Email address")
    passord: str = Field(..., min_length=8, max_length=100, description="Password (min 8 characters)")
    invitasjonskode: str = Field(..., min_length=1, description="Invitation code required for registration")


class BrukerLogin(BaseModel):
    """Schema for user login"""
    brukernavn: str = Field(..., description="Username")
    passord: str = Field(..., description="Password")


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"


class BrukerResponse(BaseModel):
    """Schema for user information response (without password)"""
    bruker_id: int
    brukernavn: str
    epost: str
    opprettet_dato: datetime
    aktiv: bool
    rolle: str

    class Config:
        from_attributes = True


# ============================================================================
# MUSKEL SCHEMAS
# ============================================================================

class MuskelBase(BaseModel):
    """Base schema for muscle"""
    muskel_id: int
    muskel_navn: str
    hovedkategori: str
    underkategori: Optional[str] = None

    class Config:
        from_attributes = True


class MuskelResponse(MuskelBase):
    """Schema for muscle response"""
    pass


class MuskelPrioritetResponse(MuskelBase):
    """Schema for muscle with priority score"""
    prioritet_score: float = Field(..., description="Priority score for this muscle (higher = needs training more)")
    dager_siden_trent: Optional[int] = Field(None, description="Days since muscle was last trained")
    total_volum: Optional[Decimal] = Field(None, description="Total volume trained for this muscle")


# ============================================================================
# UTSTYR SCHEMAS
# ============================================================================

class UtstyrBase(BaseModel):
    """Base schema for equipment"""
    utstyr_id: int
    utstyr_navn: str
    kategori: Optional[str] = None

    class Config:
        from_attributes = True


class UtstyrResponse(UtstyrBase):
    """Schema for equipment response"""
    pass


class UtstyrProfilCreate(BaseModel):
    """Schema for creating equipment profile"""
    profil_navn: str = Field(..., min_length=1, max_length=50, description="Profile name")
    utstyr_ids: List[int] = Field(..., min_items=1, description="List of equipment IDs available in this profile")


class UtstyrProfilUpdate(BaseModel):
    """Schema for updating equipment profile"""
    profil_navn: Optional[str] = Field(None, min_length=1, max_length=50, description="Profile name")
    utstyr_ids: Optional[List[int]] = Field(None, min_items=1, description="List of equipment IDs")
    aktiv: Optional[bool] = Field(None, description="Whether profile is active")


class UtstyrProfilResponse(BaseModel):
    """Schema for equipment profile response"""
    profil_id: int
    bruker_id: int
    profil_navn: str
    utstyr_ids: List[int]
    aktiv: bool
    # Include equipment details
    utstyr: List[UtstyrResponse] = Field(default_factory=list, description="Equipment items in this profile")

    class Config:
        from_attributes = True


# ============================================================================
# OVELSE SCHEMAS
# ============================================================================

class OvelseMuskelResponse(BaseModel):
    """Schema for muscle involvement in an exercise"""
    muskel_id: int
    muskel_navn: str
    muskel_type: str  # 'primar' or 'sekundar'

    class Config:
        from_attributes = True


class OvelseBase(BaseModel):
    """Base schema for exercise"""
    ovelse_id: int
    ovelse_navn: str
    force: Optional[str] = None
    level: Optional[str] = None
    mechanic: Optional[str] = None
    category: Optional[str] = None
    bilde_1_url: Optional[str] = None
    bilde_2_url: Optional[str] = None
    kilde_id: Optional[str] = None

    class Config:
        from_attributes = True


class OvelseResponse(OvelseBase):
    """Schema for detailed exercise response"""
    instruksjoner: Optional[str] = Field(None, description="JSON string of instructions")
    # Related data
    muskler: List[OvelseMuskelResponse] = Field(default_factory=list, description="Muscles involved in this exercise")
    utstyr: List[UtstyrResponse] = Field(default_factory=list, description="Equipment required for this exercise")


class OvelseListItem(OvelseBase):
    """Schema for exercise in list view (lighter version)"""
    primary_muscles: List[str] = Field(default_factory=list, description="List of primary muscle names")
    secondary_muscles: List[str] = Field(default_factory=list, description="List of secondary muscle names")
    equipment: Optional[str] = Field(None, description="Equipment name")


class OvelseLogg(BaseModel):
    """Schema for logging a completed exercise"""
    ovelse_id: int = Field(..., description="Exercise ID")
    sett: int = Field(..., ge=1, le=20, description="Number of sets (1-20)")
    repetisjoner: int = Field(..., ge=1, le=100, description="Number of repetitions per set (1-100)")
    vekt: Decimal = Field(..., ge=0, description="Weight used in kg (0 for bodyweight)")

    @validator('vekt')
    def validate_vekt(cls, v):
        """Ensure weight has max 2 decimal places"""
        if v is not None:
            return round(v, 2)
        return v


class OvelseUtfortResponse(BaseModel):
    """Schema for completed exercise response"""
    utfort_id: int
    bruker_id: int
    ovelse_id: int
    ovelse_navn: str
    sett: int
    repetisjoner: int
    vekt: Decimal
    tidspunkt: datetime

    class Config:
        from_attributes = True


# ============================================================================
# ANBEFALING SCHEMAS
# ============================================================================

class AnbefalingResponse(BaseModel):
    """Schema for exercise recommendation"""
    ovelse: OvelseResponse = Field(..., description="Recommended exercise")
    grunn: str = Field(..., description="Reason why this exercise was recommended")
    prioritert_muskel: Optional[str] = Field(None, description="The muscle that needs training most")
    prioritet_score: Optional[float] = Field(None, description="Priority score for the muscle")


# ============================================================================
# HISTORIKK SCHEMAS
# ============================================================================

class HistorikkResponse(BaseModel):
    """Schema for workout history response"""
    dato: str = Field(..., description="Date (YYYY-MM-DD)")
    ovelser: List[OvelseUtfortResponse] = Field(..., description="Exercises completed on this date")


class TreningsoktResponse(BaseModel):
    """Schema for single workout session"""
    dato: datetime
    total_ovelser: int = Field(..., description="Number of different exercises")
    total_sett: int = Field(..., description="Total number of sets")
    total_volum: Decimal = Field(..., description="Total volume (sett × reps × vekt)")
    ovelser: List[OvelseUtfortResponse]


# ============================================================================
# STATISTIKK SCHEMAS
# ============================================================================

class MuskelVolumResponse(BaseModel):
    """Schema for muscle volume (for heatmap)"""
    muskel_navn: str
    hovedkategori: str
    underkategori: Optional[str] = None
    total_volum: Decimal = Field(..., description="Total weighted volume for this muscle")
    antall_ganger_trent: int = Field(..., description="Number of times this muscle was trained")
    sist_trent_dato: Optional[datetime] = Field(None, description="Last time this muscle was trained")


class AntagonistiskBalanseResponse(BaseModel):
    """Schema for antagonistic muscle pair balance"""
    muskel_1_navn: str
    muskel_2_navn: str
    muskel_1_volum: Decimal
    muskel_2_volum: Decimal
    faktisk_ratio: Decimal = Field(..., description="Actual volume ratio (muskel_1 / muskel_2)")
    onsket_ratio: Decimal = Field(..., description="Desired ratio")
    balanse_status: str = Field(..., description="'balanced', 'muskel_1_needs_work', or 'muskel_2_needs_work'")
    avvik_prosent: float = Field(..., description="Percentage deviation from desired ratio")


class MuskelDetaljerResponse(BaseModel):
    """Schema for detailed muscle statistics"""
    muskel_id: int
    muskel_navn: str
    hovedkategori: str
    underkategori: Optional[str] = None
    total_volum: Decimal
    antall_ganger_trent: int
    sist_trent_dato: Optional[datetime] = None
    ovelser_brukt: List[dict] = Field(default_factory=list, description="List of exercises used for this muscle with counts")


class VolumOvertidResponse(BaseModel):
    """Schema for volume over time"""
    dato: str = Field(..., description="Date (YYYY-MM-DD)")
    total_volum: Decimal = Field(..., description="Total volume on this date")
    antall_ovelser: int = Field(..., description="Number of exercises on this date")


# ============================================================================
# ADMIN SCHEMAS
# ============================================================================

class InvitasjonCreate(BaseModel):
    """Schema for creating invitation"""
    epost: Optional[EmailStr] = Field(None, description="Email address to send invitation to (optional)")
    utloper_dato: Optional[datetime] = Field(None, description="Expiration date (optional)")


class InvitasjonResponse(BaseModel):
    """Schema for invitation response"""
    invitasjon_id: int
    invitasjonskode: str
    opprettet_av_bruker_id: Optional[int] = None
    epost: Optional[str] = None
    brukt: bool
    opprettet_dato: datetime
    utloper_dato: Optional[datetime] = None

    class Config:
        from_attributes = True


class BrukerAdminResponse(BrukerResponse):
    """Schema for user information in admin context"""
    pass


# ============================================================================
# GENERIC RESPONSE SCHEMAS
# ============================================================================

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str


class ErrorResponse(BaseModel):
    """Generic error response"""
    detail: str
