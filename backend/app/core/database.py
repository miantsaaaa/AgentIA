import os
from collections.abc import Generator
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session


class Base(DeclarativeBase):
    pass


database_url = os.getenv("AGENTIA_DATABASE_URL", "sqlite:///./data/agentia.db")
engine = create_engine(
    database_url,
    connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {},
)


def create_schema() -> None:
    from app import models  # noqa: F401

    config = Config(str(Path(__file__).resolve().parents[3] / "alembic.ini"))
    with engine.begin() as connection:
        existing_tables = set(inspect(connection).get_table_names())
        expected_tables = set(Base.metadata.tables)
        version_row = (
            connection.scalar(text("SELECT version_num FROM alembic_version LIMIT 1"))
            if "alembic_version" in existing_tables
            else None
        )
        has_migration_version = version_row is not None
        application_tables = existing_tables - {"alembic_version"}
        if not has_migration_version and application_tables:
            if expected_tables <= application_tables:
                config.attributes["connection"] = connection
                command.stamp(config, "head")
                return
            missing_tables = sorted(expected_tables - application_tables)
            raise RuntimeError(
                "Base SQLite non versionnée et incomplète. Sauvegarder les données, "
                f"puis prévoir une migration dédiée. Tables manquantes : {missing_tables}"
            )
        config.attributes["connection"] = connection
        command.upgrade(config, "head")


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session