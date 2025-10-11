from sqlmodel import create_engine, SQLModel


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

SQLModel.metadata.create_all(engine)
