from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from app.core import database
from app.core.database import Base
from sqlalchemy import create_engine, inspect, text


def test_initial_migration_upgrades_and_downgrades_sqlite(tmp_path: Path) -> None:
    database_path = tmp_path / "migration-test.sqlite"
    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    config = Config(str(Path(__file__).resolve().parents[2] / "alembic.ini"))

    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, "head")
        tables = set(inspect(connection).get_table_names())
        assert {
            "agents",
            "skills",
            "agent_skills",
            "tool_registry",
            "knowledge_packs",
            "evaluations",
            "certificates",
            "agent_permissions",
            "approvals",
            "audit_records",
            "missions",
            "mission_events",
            "system_agents",
        } <= tables

        command.downgrade(config, "base")
        remaining_tables = set(inspect(connection).get_table_names())
        assert remaining_tables <= {"alembic_version"}

    engine.dispose()


def test_existing_complete_schema_is_stamped_without_recreation(monkeypatch) -> None:
    engine = create_engine("sqlite://")
    config = Config(str(Path(__file__).resolve().parents[2] / "alembic.ini"))
    Base.metadata.create_all(engine)
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL PRIMARY KEY)"
        )
    monkeypatch.setattr(database, "engine", engine)

    database.create_schema()

    with engine.connect() as connection:
        current_head = ScriptDirectory.from_config(config).get_current_head()
        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == current_head
    engine.dispose()