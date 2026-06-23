"""
PostgreSQL Connection Management
Provides connection pool and session management
"""

import os
from contextlib import contextmanager
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

load_dotenv()

# PostgreSQL Configuration
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "car_valuation")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")

# Connection URL
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Global engine instance
_engine: Engine | None = None
_SessionLocal: sessionmaker | None = None


def get_engine() -> Engine:
    """Get or create SQLAlchemy engine with connection pooling"""
    global _engine
    
    if _engine is None:
        _engine = create_engine(
            DATABASE_URL,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # Verify connections before using
            echo=False  # Set to True for SQL query logging
        )
    
    return _engine


def get_session_factory() -> sessionmaker:
    """Get or create session factory"""
    global _SessionLocal
    
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return _SessionLocal


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions
    
    Usage:
        with get_session() as session:
            session.query(MarketPrice).all()
    """
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def test_connection() -> bool:
    """Test PostgreSQL connection"""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        print("✅ PostgreSQL connection successful")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False


def create_all_tables():
    """Create all tables defined in models"""
    from database.models import Base
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully")


def drop_all_tables():
    """Drop all tables (use with caution!)"""
    from database.models import Base
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)
    print("⚠️  All tables dropped")
