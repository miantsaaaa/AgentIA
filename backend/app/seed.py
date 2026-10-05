import argparse

from app.core.database import Session, create_schema, engine
from app.services.registry import seed_agents


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--app-dir", help=argparse.SUPPRESS)
    parser.parse_args()
    create_schema()
    with Session(engine) as session:
        print(f"Agents ajoutés : {seed_agents(session)}")


if __name__ == "__main__":
    main()