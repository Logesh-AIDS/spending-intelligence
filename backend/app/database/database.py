import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Use DATABASE_URL from environment if set, otherwise default to local SQLite
_DATABASE_URL = os.getenv("DATABASE_URL")

if not _DATABASE_URL:
    # Absolute path — works regardless of working directory
    _DB_PATH = Path(__file__).parent.parent.parent / "spending.db"
    _DATABASE_URL = f"sqlite:///{_DB_PATH}"

DATABASE_URL = _DATABASE_URL

# SQLite needs check_same_thread=False; PostgreSQL does not
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=_connect_args,
    pool_pre_ping=True,   # verify connections before use (important for PostgreSQL)
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base = declarative_base()
