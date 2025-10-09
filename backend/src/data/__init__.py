from sqlmodel import create_engine, SQLModel

# noinspection PyUnusedImports
import entities.call
# noinspection PyUnusedImports
import entities.member
# noinspection PyUnusedImports
import entities.training
# noinspection PyUnusedImports
import entities.youth

def new_engine():
    # TODO: replace with actual database
    return create_engine("postgresql+psycopg://postgres:postgres@localhost:5432/postgres", echo=True)

engine = new_engine()

SQLModel.metadata.create_all(engine)
