import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from .config import settings


db = SQLAlchemy()


def get_database_url():
    db_host = os.getenv("DB_HOST", settings.DB_HOST)
    db_port = os.getenv("DB_PORT", settings.DB_PORT)
    db_name = os.getenv("DB_NAME", settings.DB_NAME)
    db_user = os.getenv("DB_USER", settings.DB_USER)
    db_password = os.getenv("DB_PASSWORD", settings.DB_PASSWORD)

    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def create_db_engine():
    database_url = get_database_url()

    engine = create_engine(
        database_url,
        poolclass=NullPool,
        echo=settings.SQL_ECHO,
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
    from flask import current_app
    with current_app.app_context():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()