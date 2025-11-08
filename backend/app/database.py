"""
Database setup og session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Last inn environment variables
load_dotenv()

# Database URL fra environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://treningsuser:password@localhost:5432/treningsapp"
)

# Opprett database engine
engine = create_engine(DATABASE_URL, echo=False)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency for å få database session.
    Brukes i FastAPI endpoints.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
