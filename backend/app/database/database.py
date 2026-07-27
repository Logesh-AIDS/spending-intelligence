from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Absolute path — works regardless of working directory or script location
_DB_PATH = Path(__file__).parent.parent.parent / "spending.db"
DATABASE_URL = f"sqlite:///{_DB_PATH}"


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
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