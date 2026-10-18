import logging
import os
import re

import sqlalchemy
from sqlmodel import create_engine, SQLModel, Session

from data.timezone import APP_TIMEZONE_NAME

log = logging.getLogger(__name__)

def new_engine():
    # TODO: replace with actual database
    username = os.getenv("DB_USERNAME", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres")
    schema = os.getenv("DB_SCHEMA", "public")
    database = os.getenv("DB_DATABASE", "postgres")
    port = os.getenv("DB_PORT", "5432")
    host = os.getenv("DB_HOST", "localhost")

    echo = os.getenv("DB_ECHO", "false").lower() in ("1", "true", "yes")

    connection_string = f"postgresql+psycopg://{username}:{password}@{host}:{port}/{database}?"
    log.info(f"Connecting to database {database} at {host}:{port}")
    # The session zone only matters for the statistics, which cut TIMESTAMPTZ values into
    # the brigade's local days and hours; everything else is an instant.
    options = f"-c search_path={schema} -c timezone={APP_TIMEZONE_NAME}"
    return create_engine(connection_string, echo=echo, connect_args={'options': options})


engine = new_engine()

def ensure_schema(name: str) -> None:
    """Creates the schema unless it is already there.

    `CREATE SCHEMA` checks for the CREATE privilege on the *database* before `IF NOT EXISTS`
    can short-circuit, so issuing it unconditionally fails for a role that only holds rights
    inside an already existing schema. Looking first keeps such a role from needing a privilege
    it never uses.
    """
    with engine.connect() as conn:
        exists = conn.execute(sqlalchemy.text("SELECT 1 FROM pg_namespace WHERE nspname = :name"),
                              {"name": name}).first()
        if exists:
            return
        conn.execute(sqlalchemy.text(f"CREATE SCHEMA IF NOT EXISTS {name}"))
        conn.commit()
        log.info(f"Created schema {name}")


schema = os.getenv("DB_SCHEMA", "public")
ensure_schema(schema)

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

_SCHEMA_UPGRADES = [
    "ALTER TABLE {schema}.subject ADD COLUMN IF NOT EXISTS archived BOOLEAN NOT NULL DEFAULT false",
    "ALTER TABLE {schema}.member ADD COLUMN IF NOT EXISTS joined DATE",
    # Call times used to be naive timestamps holding UTC wall-clock time (the backend ran with
    # a UTC clock and inserted UTC instants). Reading them back as UTC loses nothing and gives
    # the instants a type that says what they are. Guarded by the column type, so it runs once.
    # Views built on the call table by hand are not managed here, but PostgreSQL refuses to
    # change a column they use, so they are dropped first and recreated from their saved
    # definitions once the columns have their new type.
    """
    DO $$
    DECLARE
        dependents OID[];
        pending    TEXT[];
        retry      TEXT[];
        statement  TEXT;
        progressed BOOLEAN;
        rel        RECORD;
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                       WHERE table_schema = '{schema}' AND table_name = 'call'
                         AND column_name = 'start' AND data_type = 'timestamp without time zone') THEN
            RETURN;
        END IF;

        WITH RECURSIVE built_on AS (
            SELECT r.ev_class AS oid
            FROM pg_depend d
            JOIN pg_rewrite r ON r.oid = d.objid
            WHERE d.classid = 'pg_rewrite'::regclass
              AND d.refclassid = 'pg_class'::regclass
              AND d.refobjid = '{schema}.call'::regclass
              AND r.ev_class <> d.refobjid
            UNION
            SELECT r.ev_class
            FROM built_on b
            JOIN pg_depend d ON d.classid = 'pg_rewrite'::regclass
                            AND d.refclassid = 'pg_class'::regclass
                            AND d.refobjid = b.oid
            JOIN pg_rewrite r ON r.oid = d.objid
            WHERE r.ev_class <> b.oid
        )
        SELECT coalesce(array_agg(DISTINCT oid), ARRAY[]::OID[]) INTO dependents FROM built_on;

        SELECT coalesce(array_agg(
                   'CREATE ' || CASE c.relkind WHEN 'm' THEN 'MATERIALIZED VIEW ' ELSE 'VIEW ' END
                   || quote_ident(n.nspname) || '.' || quote_ident(c.relname)
                   || ' AS ' || pg_get_viewdef(c.oid)), ARRAY[]::TEXT[])
        INTO pending
        FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.oid = ANY (dependents) AND c.relkind IN ('v', 'm');

        FOR rel IN SELECT c.relkind, quote_ident(n.nspname) || '.' || quote_ident(c.relname) AS name
                   FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
                   WHERE c.oid = ANY (dependents) AND c.relkind IN ('v', 'm') LOOP
            EXECUTE 'DROP ' || CASE rel.relkind WHEN 'm' THEN 'MATERIALIZED VIEW' ELSE 'VIEW' END
                    || ' IF EXISTS ' || rel.name || ' CASCADE';
        END LOOP;

        ALTER TABLE {schema}.call
            ALTER COLUMN start TYPE TIMESTAMPTZ USING start AT TIME ZONE 'UTC',
            ALTER COLUMN "end" TYPE TIMESTAMPTZ USING "end" AT TIME ZONE 'UTC';

        -- Views may build on each other, so keep going until every one has what it needs.
        WHILE cardinality(pending) > 0 LOOP
            retry := ARRAY[]::TEXT[];
            progressed := false;
            FOREACH statement IN ARRAY pending LOOP
                BEGIN
                    EXECUTE statement;
                    progressed := true;
                EXCEPTION WHEN undefined_table THEN
                    retry := retry || statement;
                END;
            END LOOP;
            pending := retry;
            IF cardinality(pending) > 0 AND NOT progressed THEN
                RAISE EXCEPTION USING MESSAGE = 'Could not recreate views after changing call times: '
                    || array_to_string(pending, chr(10));
            END IF;
        END LOOP;
    END $$;
    """,
]
"""Statements that bring an older database up to the current entities.

`create_all` only creates tables that do not exist yet, so a column added to an entity never
reaches a database that already has the table. Every statement here runs on every startup and
must therefore be idempotent and lossless — `ADD COLUMN IF NOT EXISTS`, a guarded type change
that keeps every value, never a drop, a rename or anything that can lose data. Anything that
cannot be expressed that way does not belong here and has to be applied by hand against a
dump first.
"""

with engine.connect() as conn:
    for upgrade in _SCHEMA_UPGRADES:
        conn.execute(sqlalchemy.text(upgrade.format(schema=schema)))
    conn.commit()
log.info(f"Applied {len(_SCHEMA_UPGRADES)} schema upgrades")


def _function_names(sql: str) -> list[str]:
    """Names of every function functions.sql defines."""
    return sorted(set(re.findall(r"CREATE OR REPLACE FUNCTION\s+[\w.]+\.(\w+)", sql)))


def _drop_functions(conn, names: list[str]) -> None:
    """Drops the file's functions before redeploying them.

    `CREATE OR REPLACE FUNCTION` refuses to change a function's return type, so a function that
    gains or loses a result column can never be replaced in a database that already has the old
    one. Dropping first makes functions.sql the single source of truth: whatever it says is what
    the database ends up with. Only functions the file itself defines are touched.
    """
    signatures = conn.execute(sqlalchemy.text(
        "SELECT p.oid::regprocedure::text AS signature "
        "FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace "
        "WHERE n.nspname = :schema AND p.proname = ANY(:names)"
    ), {"schema": schema, "names": names}).all()
    for row in signatures:
        conn.execute(sqlalchemy.text(f"DROP FUNCTION {row.signature}"))


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
        _drop_functions(conn, _function_names(sql))
        for statement in statements:
            conn.execute(sqlalchemy.text(statement))
        conn.commit()
    log.info(f"Deployed {len(statements)} SQL functions")

def get_session():
    with Session(engine) as session:
        yield session
