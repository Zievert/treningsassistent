"""
SQLAlchemy database models for Treningsassistent
"""
from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, TIMESTAMP, ForeignKey, Text, ARRAY, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


# ============================================================================
# GLOBALE TABELLER (deles av alle brukere)
# ============================================================================

class Muskel(Base):
    """
    Muskelgrupper (17 totalt)
    Eksempel: Pectoralis major, Latissimus dorsi, Biceps, etc.
    """
    __tablename__ = "muskler"

    muskel_id = Column(Integer, primary_key=True, index=True)
    muskel_navn = Column(String(100), nullable=False, unique=True)
    hovedkategori = Column(String(50), nullable=False)  # overkropp_push, overkropp_pull, ben, core
    underkategori = Column(String(50))  # bryst, rygg, armer, skulder, etc.

    # Relationships
    antagonist_par_1 = relationship("AntagonistiskPar", foreign_keys="[AntagonistiskPar.muskel_1_id]", back_populates="muskel_1")
    antagonist_par_2 = relationship("AntagonistiskPar", foreign_keys="[AntagonistiskPar.muskel_2_id]", back_populates="muskel_2")
    ovelse_muskler = relationship("OvelseMuskel", back_populates="muskel")
    bruker_muskel_status = relationship("BrukerMuskelStatus", back_populates="muskel")


class AntagonistiskPar(Base):
    """
    Muskelpar for antagonistisk balanse tracking
    Eksempel: Pectoralis ↔ Latissimus (1:1), Quadriceps ↔ Hamstrings (1:1)
    """
    __tablename__ = "antagonistiske_par"

    par_id = Column(Integer, primary_key=True, index=True)
    muskel_1_id = Column(Integer, ForeignKey("muskler.muskel_id"), nullable=False)
    muskel_2_id = Column(Integer, ForeignKey("muskler.muskel_id"), nullable=False)
    onsket_ratio = Column(DECIMAL, default=1.0)  # Ønsket balanse (1.0 = 1:1)

    # Relationships
    muskel_1 = relationship("Muskel", foreign_keys=[muskel_1_id], back_populates="antagonist_par_1")
    muskel_2 = relationship("Muskel", foreign_keys=[muskel_2_id], back_populates="antagonist_par_2")


class Utstyr(Base):
    """
    Treningsutstyr (12 typer)
    Eksempel: Kroppsvekt, Vektstang, Dumbbells, Benk, etc.
    """
    __tablename__ = "utstyr"

    utstyr_id = Column(Integer, primary_key=True, index=True)
    utstyr_navn = Column(String(100), nullable=False, unique=True)
    kategori = Column(String(50))  # fri_vekt, maskin, kroppsvekt, kabel, etc.

    # Relationships
    ovelse_utstyr = relationship("OvelseUtstyr", back_populates="utstyr")


class Ovelse(Base):
    """
    Øvelsesdatabase (873 øvelser fra free-exercise-db)
    Eksempel: Barbell Bench Press, Pull-ups, Squats, etc.
    """
    __tablename__ = "ovelser"

    ovelse_id = Column(Integer, primary_key=True, index=True)
    ovelse_navn = Column(String(200), nullable=False, unique=True)

    # Metadata fra free-exercise-db
    force = Column(String(20))  # push, pull, static, NULL
    level = Column(String(20))  # beginner, intermediate, expert
    mechanic = Column(String(20))  # compound, isolation, NULL
    category = Column(String(50))  # strength, stretching, cardio, etc.

    # Media URLs
    gif_url = Column(Text)
    video_url = Column(Text)
    bilde_1_url = Column(Text)
    bilde_2_url = Column(Text)

    # Instructions and tips
    instruksjoner = Column(Text)  # JSON array as TEXT
    tips = Column(ARRAY(Text))  # PostgreSQL array
    vanlige_feil = Column(ARRAY(Text))  # PostgreSQL array

    # Original ID fra datakilde
    kilde_id = Column(String(100))  # Original ID fra free-exercise-db

    # Relationships
    ovelse_muskler = relationship("OvelseMuskel", back_populates="ovelse", cascade="all, delete-orphan")
    ovelse_utstyr = relationship("OvelseUtstyr", back_populates="ovelse", cascade="all, delete-orphan")
    bruker_ovelse_historikk = relationship("BrukerOvelseHistorikk", back_populates="ovelse")
    ovelser_utfort = relationship("OvelseUtfort", back_populates="ovelse")


class OvelseMuskel(Base):
    """
    Junction table: Kobler øvelser til muskler (primære/sekundære)
    """
    __tablename__ = "ovelse_muskler"

    ovelse_id = Column(Integer, ForeignKey("ovelser.ovelse_id", ondelete="CASCADE"), primary_key=True)
    muskel_id = Column(Integer, ForeignKey("muskler.muskel_id"), primary_key=True)
    muskel_type = Column(String(20), nullable=False)  # 'primar' eller 'sekundar'

    # Relationships
    ovelse = relationship("Ovelse", back_populates="ovelse_muskler")
    muskel = relationship("Muskel", back_populates="ovelse_muskler")


class OvelseUtstyr(Base):
    """
    Junction table: Kobler øvelser til utstyr
    """
    __tablename__ = "ovelse_utstyr"

    ovelse_id = Column(Integer, ForeignKey("ovelser.ovelse_id", ondelete="CASCADE"), primary_key=True)
    utstyr_id = Column(Integer, ForeignKey("utstyr.utstyr_id"), primary_key=True)

    # Relationships
    ovelse = relationship("Ovelse", back_populates="ovelse_utstyr")
    utstyr = relationship("Utstyr", back_populates="ovelse_utstyr")


# ============================================================================
# BRUKER-TABELLER
# ============================================================================

class Bruker(Base):
    """
    Brukerkontoer
    """
    __tablename__ = "brukere"

    bruker_id = Column(Integer, primary_key=True, index=True)
    brukernavn = Column(String(50), nullable=False, unique=True, index=True)
    passord_hash = Column(String(255), nullable=False)
    epost = Column(String(255), nullable=False, unique=True, index=True)
    opprettet_dato = Column(TIMESTAMP, server_default=func.now())
    aktiv = Column(Boolean, default=True)
    rolle = Column(String(20), default="bruker")  # 'admin' eller 'bruker'

    # Relationships
    invitasjoner_opprettet = relationship("Invitasjon", back_populates="opprettet_av_bruker")
    bruker_muskel_status = relationship("BrukerMuskelStatus", back_populates="bruker")
    bruker_ovelse_historikk = relationship("BrukerOvelseHistorikk", back_populates="bruker")
    ovelser_utfort = relationship("OvelseUtfort", back_populates="bruker")
    utstyr_profiler = relationship("BrukerUtstyrProfil", back_populates="bruker")


class Invitasjon(Base):
    """
    Invitasjonskoder for registrering (invite-only system)
    """
    __tablename__ = "invitasjoner"

    invitasjon_id = Column(Integer, primary_key=True, index=True)
    invitasjonskode = Column(String(50), nullable=False, unique=True, index=True)
    opprettet_av_bruker_id = Column(Integer, ForeignKey("brukere.bruker_id"))
    epost = Column(String(255))
    brukt = Column(Boolean, default=False)
    opprettet_dato = Column(TIMESTAMP, server_default=func.now())
    utloper_dato = Column(TIMESTAMP)

    # Relationships
    opprettet_av_bruker = relationship("Bruker", back_populates="invitasjoner_opprettet")


class BrukerMuskelStatus(Base):
    """
    Tracker hvilke muskler en bruker har trent og når
    Brukes for å beregne muskel-prioritet
    """
    __tablename__ = "bruker_muskel_status"

    status_id = Column(Integer, primary_key=True, index=True)
    bruker_id = Column(Integer, ForeignKey("brukere.bruker_id"), nullable=False)
    muskel_id = Column(Integer, ForeignKey("muskler.muskel_id"), nullable=False)
    sist_trent_dato = Column(TIMESTAMP)
    antall_ganger_trent = Column(Integer, default=0)
    total_volum = Column(DECIMAL, default=0)  # Akkumulert volum (sett × reps × vekt), vektet for primær/sekundær

    __table_args__ = (
        UniqueConstraint('bruker_id', 'muskel_id', name='uq_bruker_muskel'),
    )

    # Relationships
    bruker = relationship("Bruker", back_populates="bruker_muskel_status")
    muskel = relationship("Muskel", back_populates="bruker_muskel_status")


class BrukerOvelseHistorikk(Base):
    """
    Tracker hvilke øvelser en bruker har gjort og når
    Brukes for øvelsesrotasjon
    """
    __tablename__ = "bruker_ovelse_historikk"

    historikk_id = Column(Integer, primary_key=True, index=True)
    bruker_id = Column(Integer, ForeignKey("brukere.bruker_id"), nullable=False)
    ovelse_id = Column(Integer, ForeignKey("ovelser.ovelse_id"), nullable=False)
    sist_brukt_dato = Column(TIMESTAMP)
    antall_ganger_brukt = Column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint('bruker_id', 'ovelse_id', name='uq_bruker_ovelse'),
    )

    # Relationships
    bruker = relationship("Bruker", back_populates="bruker_ovelse_historikk")
    ovelse = relationship("Ovelse", back_populates="bruker_ovelse_historikk")


class OvelseUtfort(Base):
    """
    Logg av alle utførte øvelser
    Brukes for historikk og statistikk
    """
    __tablename__ = "ovelser_utfort"

    utfort_id = Column(Integer, primary_key=True, index=True)
    bruker_id = Column(Integer, ForeignKey("brukere.bruker_id"), nullable=False)
    ovelse_id = Column(Integer, ForeignKey("ovelser.ovelse_id"), nullable=False)
    sett = Column(Integer, nullable=False)
    repetisjoner = Column(Integer, nullable=False)
    vekt = Column(DECIMAL, nullable=False)
    tidspunkt = Column(TIMESTAMP, server_default=func.now(), index=True)

    # Relationships
    bruker = relationship("Bruker", back_populates="ovelser_utfort")
    ovelse = relationship("Ovelse", back_populates="ovelser_utfort")


class BrukerUtstyrProfil(Base):
    """
    Utstyrsprofiler per bruker (Gym, Hjemme, Reise, etc.)
    Brukes for å filtrere øvelser basert på tilgjengelig utstyr
    """
    __tablename__ = "bruker_utstyr_profiler"

    profil_id = Column(Integer, primary_key=True, index=True)
    bruker_id = Column(Integer, ForeignKey("brukere.bruker_id"), nullable=False)
    profil_navn = Column(String(50), nullable=False)  # 'Gym', 'Hjemme', 'Reise'
    utstyr_ids = Column(ARRAY(Integer), nullable=False)  # Array av utstyr_ids
    aktiv = Column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint('bruker_id', 'profil_navn', name='uq_bruker_profil'),
    )

    # Relationships
    bruker = relationship("Bruker", back_populates="utstyr_profiler")
