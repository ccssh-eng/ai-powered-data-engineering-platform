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

if not POSTGRES_PASSWORD:
    raise ValueError("POSTGRES_PASSWORD is not configured")

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")

DATABASE_URL = (
    f"postgresql+psycopg://data_engineer:"
    f"{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/ai_platform"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False
)

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


