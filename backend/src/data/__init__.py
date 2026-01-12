import logging
import os

from sqlmodel import create_engine, SQLModel, Session
log = logging.getLogger(__name__)

def new_engine():
    # TODO: replace with actual database
    username = os.getenv("DB_USERNAME", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres")
    schema = os.getenv("DB_SCHEMA", "public")
    database = os.getenv("DB_DATABASE", "postgres")
    port = os.getenv("DB_PORT", "5432")

    connection_string = f"postgresql+psycopg://{username}:{password}@localhost:{port}/{database}?"
    log.info(f"Connecting to database: {connection_string}")
    return create_engine(connection_string, echo=True, connect_args={'options': '-c search_path={}'.format(schema)})


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
