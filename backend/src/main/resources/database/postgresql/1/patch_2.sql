CREATE UNIQUE INDEX exercise_crew_exercise_id_crew_id_uindex ON exercise_crew (exercise_id, crew_id);
ALTER TABLE exercise_crew
    ADD PRIMARY KEY USING INDEX exercise_crew_exercise_id_crew_id_uindex;

CREATE UNIQUE INDEX call_crew_call_id_crew_id_uindex ON call_crew (call_id, crew_id);
ALTER TABLE call_crew
    ADD PRIMARY KEY USING INDEX call_crew_call_id_crew_id_uindex;

ALTER TABLE qualifications
    ADD COLUMN since DATE DEFAULT now()::DATE;
UPDATE qualifications
SET
    since = '2020-01-01'::DATE
WHERE TRUE;

CREATE OR REPLACE VIEW call_meta
        (call_id, call, duration, call_type, abort_reason, note, strength, strength_slim, additional_crew, leader,
         driver,
         crew, crew_names)
AS
    WITH
        crew_meta AS (
            SELECT
                cc.call_id,
                ca.start_timestamp                                                                           AS call,
                count(1) FILTER (WHERE NOT cc.additional)                                                    AS strength,
                count(1) FILTER (WHERE cc.additional)                                                        AS additional_crew,
                coalesce(bool_or('Staffelführer' = q.qualification AND q.since < ca.start_timestamp), FALSE) AS leader,
                coalesce(bool_or('Maschinist' = q.qualification AND q.since < ca.start_timestamp), FALSE)    AS driver,
                array_agg(DISTINCT cr.name)                                                                  AS crew_names
            FROM
                call_crew cc
                    LEFT JOIN crew cr
                    ON cc.crew_id = cr.id
                    LEFT JOIN qualifications q
                    ON cr.id = q.crew_id
                    LEFT JOIN calls ca
                    ON cc.call_id = ca.id
            GROUP BY cc.call_id, ca.start_timestamp
            ORDER BY cc.call_id
                     ),
        call_meta AS (
            SELECT
                id,
                c.start_timestamp                      AS call,
                c.duration,
                c.call_type,
                c.abort_reason,
                c.note,
                coalesce(m.strength, 0::BIGINT)        AS strength,
                coalesce(m.additional_crew, 0::BIGINT) AS additional_crew,
                coalesce(m.leader, FALSE)              AS leader,
                coalesce(m.driver, FALSE)              AS driver,
                coalesce(m.strength > 3, FALSE)        AS crew,
                m.crew_names
            FROM
                calls_clean c
                    LEFT JOIN crew_meta m
                    ON c.start_timestamp = m.call
                     )
    SELECT
        call_meta.id,
        call_meta.call,
        call_meta.duration,
        call_meta.call_type,
        call_meta.abort_reason,
        call_meta.note,
        call_meta.strength,
        call_meta.strength -
            CASE
                WHEN call_meta.leader THEN 1
                                      ELSE 0
            END -
            CASE
                WHEN call_meta.driver THEN 1
                                      ELSE 0
            END AS strength_slim,
        call_meta.additional_crew,
        call_meta.leader,
        call_meta.driver,
        call_meta.crew,
        call_meta.crew_names
    FROM
        call_meta
    ORDER BY call_meta.call;

CREATE TABLE users (
    id       SERIAL PRIMARY KEY,
    name     TEXT NOT NULL,
    password TEXT NOT NULL,
    enabled  BOOLEAN DEFAULT FALSE
);

CREATE UNIQUE INDEX users_name_uindex ON users (lower(name));

CREATE TABLE user_roles (
    user_id INTEGER,
    role    TEXT
);

CREATE TABLE user_session (
    user_id     INTEGER,
    token       TEXT,
    valid_until TIMESTAMP
);
