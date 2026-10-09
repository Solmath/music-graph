from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

# One local file next to where you run the commands. Delete it to start over.
engine = create_engine("sqlite:///graph.db")


def init_db() -> None:
    """Create the tables if they don't exist yet.

    create_all() is fine while the schema is still changing and the data can be
    re-fetched. Introduce Alembic once the DB holds data you don't want to lose.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    """FastAPI dependency: one DB session per request."""
    with Session(engine) as session:
        yield session
