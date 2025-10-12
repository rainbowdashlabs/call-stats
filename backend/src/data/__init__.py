from sqlmodel import create_engine, SQLModel, Session


def new_engine():
    # TODO: replace with actual database
    return create_engine("postgresql+psycopg://postgres:postgres@localhost:5432/postgres", echo=True)


engine = new_engine()

# noinspection PyUnusedImports
import entities.call
# noinspection PyUnusedImports
import entities.member
# noinspection PyUnusedImports
import entities.exercise
# noinspection PyUnusedImports
import entities.youth
# noinspection PyUnusedImports
import entities.qualification

SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
