import logging
import os

import sqlalchemy
from sqlmodel import create_engine, SQLModel, Session
log = logging.getLogger(__name__)

def new_engine():
    # TODO: replace with actual database
    username = os.getenv("DB_USERNAME", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres")
    schema = os.getenv("DB_SCHEMA", "public")
    database = os.getenv("DB_DATABASE", "postgres")
    port = os.getenv("DB_PORT", "5432")
    host = os.getenv("DB_HOST", "localhost")

    connection_string = f"postgresql+psycopg://{username}:{password}@{host}:{port}/{database}?"
    log.info(f"Connecting to database: {connection_string}")
    return create_engine(connection_string, echo=True, connect_args={'options': '-c search_path={}'.format(schema)})


engine = new_engine()

# Ensure the schema exists, create tables, and deploy SQL functions
with engine.connect() as conn:
    schema = os.getenv("DB_SCHEMA", "public")
    conn.execute(sqlalchemy.text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
    conn.commit()

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

def _split_functions(sql: str) -> list[str]:
    """Split functions.sql into one statement per function body, dropping the header
    comments that precede each one. A line ending in `$$;` closes a definition."""
    statements = []
    current = []
    for line in sql.split('\n'):
        stripped = line.strip()
        if not current and (not stripped or stripped.startswith('--')):
            continue
        current.append(line)
        if stripped.endswith('$$;'):
            statements.append('\n'.join(current))
            current = []
    return statements


_functions_sql = os.path.join(os.path.dirname(__file__), "functions.sql")
if os.path.exists(_functions_sql):
    with engine.connect() as conn:
        with open(_functions_sql) as f:
            sql = f.read().replace("{{schema}}", schema)
        statements = _split_functions(sql)
        for statement in statements:
            conn.execute(sqlalchemy.text(statement))
        conn.commit()
    log.info(f"Deployed {len(statements)} SQL functions")

def get_session():
    with Session(engine) as session:
        yield session
