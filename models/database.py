from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config.settings import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Yield a database session, ensuring it's closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session():
    """Return a new database session (caller must close)."""
    return SessionLocal()
