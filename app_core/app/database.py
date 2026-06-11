import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

from .config import settings


Base = declarative_base()


def get_database_url():
    db_host = os.getenv("DB_HOST", settings.ENCRYPTION_SERVICE_HOST)
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "helios")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "")

    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def create_db_engine():
    database_url = get_database_url()

    engine = create_engine(
        database_url,
        poolclass=NullPool,
        echo=os.getenv("SQL_ECHO", "false").lower() == "true",
        future=True,
    )

    return engine


def create_session_factory(engine):
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    return SessionLocal


engine = create_db_engine()
SessionLocal = create_session_factory(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(app):
    with app.app_context():
        Base.metadata.create_all(bind=engine)


def drop_db(app):
    with app.app_context():
        Base.metadata.drop_all(bind=engine)