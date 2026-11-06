import os
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from database.models import Base

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")

# Build DATABASE_URL only if password is available (tests use SQLite via monkeypatch)
if POSTGRES_PASSWORD:
    DATABASE_URL = (
        f"postgresql+psycopg://data_engineer:"
        f"{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/ai_platform"
    )
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        echo=False
    )
else:
    # Fallback SQLite for test environments (overridden by monkeypatch)
    engine = create_engine("sqlite:///:memory:")

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


def get_db_session():
    """Create and provide a database session."""

    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


def test_connection():
    """Check PostgreSQL connectivity."""

    if not POSTGRES_PASSWORD:
        logger.warning("POSTGRES_PASSWORD is not configured")
        return False

    from sqlalchemy import text

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        logger.info("PostgreSQL connection successful")
        return True

    except Exception:
        logger.exception("PostgreSQL connection failed")
        return False


def create_tables():
    """Create database tables if they do not exist."""

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True

    except Exception:
        logger.exception("Failed to create database tables")
        return False
