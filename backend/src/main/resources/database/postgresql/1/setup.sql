CREATE TABLE IF NOT EXISTS crew (
    name TEXT NOT NULL
);

ALTER TABLE crew
    ADD CONSTRAINT crew_pk
        PRIMARY KEY (name);

CREATE TABLE IF NOT EXISTS calls (
    start_timestamp TIMESTAMP             NOT NULL,
    end_timestamp   TIMESTAMP             NOT NULL,
    duration        INTEGER GENERATED ALWAYS AS (( extract(EPOCH FROM ( end_timestamp - start_timestamp )) / ( 60 )::NUMERIC )) STORED,
    call_type       TEXT                  NOT NULL,
    abort_reason    TEXT,
    note            TEXT,
    at_station      BOOLEAN DEFAULT FALSE NOT NULL
);

ALTER TABLE calls
    ADD PRIMARY KEY (start_timestamp);

CREATE TABLE IF NOT EXISTS exercises (
    date    DATE    NOT NULL,
    hours   NUMERIC NOT NULL,
    minutes INTEGER GENERATED ALWAYS AS (( ( hours * ( 60 )::NUMERIC ) )::INTEGER) STORED,
    subject TEXT    NOT NULL
);

ALTER TABLE exercises
    ADD PRIMARY KEY (date);

CREATE TABLE IF NOT EXISTS exercise_crew (
    exercise DATE NOT NULL,
    name     TEXT NOT NULL
);

ALTER TABLE exercise_crew
    ADD CONSTRAINT exercise_crew_pk
        PRIMARY KEY (name, exercise);

ALTER TABLE exercise_crew
    ADD CONSTRAINT exercise_crew_exercises_date_fk
        FOREIGN KEY (exercise) REFERENCES exercises;

ALTER TABLE exercise_crew
    ADD CONSTRAINT exercise_crew_crew_name_fk
        FOREIGN KEY (name) REFERENCES crew;

CREATE TABLE IF NOT EXISTS call_crew (
    call       TIMESTAMP             NOT NULL,
    name       TEXT                  NOT NULL,
    additional BOOLEAN DEFAULT FALSE NOT NULL
);

ALTER TABLE call_crew
    ADD CONSTRAINT call_crew_pk
        PRIMARY KEY (name, call);

ALTER TABLE call_crew
    ADD CONSTRAINT call_crew_calls_start_timestamp_fk
        FOREIGN KEY (call) REFERENCES calls;

ALTER TABLE call_crew
    ADD CONSTRAINT call_crew_crew_name_fk
        FOREIGN KEY (name) REFERENCES crew;

CREATE TABLE IF NOT EXISTS qualifications (
    name          TEXT NOT NULL,
    qualification TEXT NOT NULL
);

ALTER TABLE qualifications
    ADD CONSTRAINT qualifications_pk
        PRIMARY KEY (name, qualification);

ALTER TABLE qualifications
    ADD CONSTRAINT qualifications_crew_name_fk
        FOREIGN KEY (name) REFERENCES crew;

CREATE OR REPLACE VIEW calls_clean
        (start_timestamp, end_timestamp, duration, call_type, abort_reason, note, at_station) AS
    SELECT
        calls.start_timestamp,
        calls.end_timestamp,
        calls.duration,
        calls.call_type,
        calls.abort_reason,
        calls.note,
        calls.at_station
    FROM
        calls
    WHERE calls.call_type
              = ANY ( ARRAY ['FR'::TEXT, 'TH'::TEXT, 'Wachbesetzung'::TEXT, 'TH + NOTF'::TEXT, 'BRAND'::TEXT] );

CREATE OR REPLACE VIEW calls_crew_raw
        (start_timestamp, end_timestamp, duration, call_type, abort_reason, note, name, additional) AS
    SELECT
        calls.start_timestamp,
        calls.end_timestamp,
        CASE
            WHEN calls.at_station THEN 0
                                  ELSE calls.duration
        END AS duration,
        calls.call_type,
        calls.abort_reason,
        calls.note,
        crew.name,
        crew.additional
    FROM
        calls_clean calls
            LEFT JOIN call_crew crew
            ON calls.start_timestamp = crew.call
    WHERE crew.name IS NOT NULL
    ORDER BY calls.start_timestamp;

CREATE OR REPLACE VIEW calls_crew_month(month, name, minutes, hours, calls) AS
    SELECT
        date_trunc('month'::TEXT, calls_crew_raw.start_timestamp)::DATE AS month,
        calls_crew_raw.name,
        sum(calls_crew_raw.duration)                                    AS minutes,
        round(sum(calls_crew_raw.duration)::NUMERIC / 60.0, 2)          AS hours,
        count(1)                                                        AS calls
    FROM
        calls_crew_raw
    WHERE calls_crew_raw.name IS NOT NULL
    GROUP BY ( date_trunc('month'::TEXT, calls_crew_raw.start_timestamp)::DATE ), calls_crew_raw.name
    ORDER BY ( date_trunc('month'::TEXT, calls_crew_raw.start_timestamp)::DATE ), calls_crew_raw.name;

CREATE OR REPLACE VIEW exercise_crew_raw(date, subject, name, minutes, hours) AS
    SELECT
        e.date,
        e.subject,
        c.name,
        e.minutes,
        e.hours
    FROM
        exercises e
            LEFT JOIN exercise_crew c
            ON e.date = c.exercise
    WHERE e.subject ~~* '%übung%'::TEXT
       OR e.subject ~~* '%sicherung%'::TEXT;

CREATE OR REPLACE VIEW exercise_count(date, count) AS
    SELECT
        exercise_crew_raw.date,
        count(1) AS count
    FROM
        exercise_crew_raw
    GROUP BY exercise_crew_raw.date
    ORDER BY exercise_crew_raw.date;

CREATE OR REPLACE VIEW exercise_crew_month(month, minutes, hours, name, count) AS
    SELECT
        date_trunc('month'::TEXT, e.date::TIMESTAMP WITH TIME ZONE)::DATE AS month,
        sum(e.minutes)                                                    AS minutes,
        sum(e.hours)                                                      AS hours,
        e.name,
        count(1)                                                          AS count
    FROM
        exercise_crew_raw e
    GROUP BY ( date_trunc('month'::TEXT, e.date::TIMESTAMP WITH TIME ZONE)::DATE ), e.name
    ORDER BY ( date_trunc('month'::TEXT, e.date::TIMESTAMP WITH TIME ZONE)::DATE ), e.name;

CREATE OR REPLACE VIEW calls_month(month, call_type, count, minutes, hours) AS
    SELECT
        date_trunc('MONTH'::TEXT, calls_clean.start_timestamp)::DATE AS month,
        calls_clean.call_type,
        count(1)                                                     AS count,
        sum(calls_clean.duration)                                    AS minutes,
        round(sum(calls_clean.duration)::NUMERIC / 60.0, 2)          AS hours
    FROM
        calls_clean
    GROUP BY ( date_trunc('MONTH'::TEXT, calls_clean.start_timestamp)::DATE ), calls_clean.call_type
    ORDER BY ( date_trunc('MONTH'::TEXT, calls_clean.start_timestamp)::DATE ), calls_clean.call_type;

CREATE OR REPLACE VIEW calls_crew_month_perc
        (month, name, minutes_perc, hours_perc, calls_perc, minutes, hours, calls, minutes_max, hours_max,
         calls_max)
AS
    WITH
        m_calls AS (
            SELECT
                calls_month.month,
                sum(calls_month.hours)   AS hours,
                sum(calls_month.minutes) AS minutes,
                sum(calls_month.count)   AS count
            FROM
                calls_month
            GROUP BY calls_month.month
        )
    SELECT
        ccm.month,
        ccm.name,
        round(ccm.minutes::NUMERIC / cm.minutes, 2) AS minutes_perc,
        round(ccm.hours / cm.hours, 2)              AS hours_perc,
        round(ccm.calls::NUMERIC / cm.count, 2)     AS calls_perc,
        ccm.minutes,
        ccm.hours,
        ccm.calls,
        cm.minutes                                  AS minutes_max,
        cm.hours                                    AS hours_max,
        cm.count                                    AS calls_max
    FROM
        calls_crew_month ccm
            LEFT JOIN m_calls cm
            ON ccm.month = cm.month;

CREATE OR REPLACE VIEW calls_year(year, call_type, count, minutes, hours) AS
    SELECT
        date_trunc('YEAR'::TEXT, calls_clean.start_timestamp)::DATE AS year,
        calls_clean.call_type,
        count(1)                                                    AS count,
        sum(calls_clean.duration)                                   AS minutes,
        round(sum(calls_clean.duration)::NUMERIC / 60.0, 2)         AS hours
    FROM
        calls_clean
    GROUP BY ( date_trunc('YEAR'::TEXT, calls_clean.start_timestamp)::DATE ), calls_clean.call_type;

CREATE OR REPLACE VIEW calls_crew_year(year, name, minutes, hours, calls) AS
    SELECT
        date_trunc('YEAR'::TEXT, calls_crew_month.month::TIMESTAMP WITH TIME ZONE)::DATE AS year,
        calls_crew_month.name,
        sum(calls_crew_month.minutes)                                                    AS minutes,
        round(sum(calls_crew_month.minutes) / 60.0, 2)                                   AS hours,
        sum(calls_crew_month.calls)                                                      AS calls
    FROM
        calls_crew_month
    GROUP BY ( date_trunc('YEAR'::TEXT, calls_crew_month.month::TIMESTAMP WITH TIME ZONE)::DATE ),
             calls_crew_month.name;

CREATE OR REPLACE VIEW calls_crew_year_perc
        (year, name, minutes_perc, hours_perc, calls_perc, minutes, hours, calls, minutes_max, hours_max,
         calls_max)
AS
    WITH
        m_calls AS (
            SELECT
                calls_year.year,
                sum(calls_year.hours)   AS hours,
                sum(calls_year.minutes) AS minutes,
                sum(calls_year.count)   AS count
            FROM
                calls_year
            GROUP BY calls_year.year
        )
    SELECT
        ccm.year,
        ccm.name,
        round(ccm.minutes / cm.minutes, 2) AS minutes_perc,
        round(ccm.hours / cm.hours, 2)     AS hours_perc,
        round(ccm.calls / cm.count, 2)     AS calls_perc,
        ccm.minutes,
        ccm.hours,
        ccm.calls,
        cm.minutes                         AS minutes_max,
        cm.hours                           AS hours_max,
        cm.count                           AS calls_max
    FROM
        calls_crew_year ccm
            LEFT JOIN m_calls cm
            ON ccm.year = cm.year;

CREATE OR REPLACE VIEW exercise_crew_year(year, minutes, hours, name, count) AS
    SELECT
        date_trunc('YEAR'::TEXT, e.date::TIMESTAMP WITH TIME ZONE)::DATE AS year,
        sum(e.minutes)                                                   AS minutes,
        sum(e.hours)                                                     AS hours,
        e.name,
        count(1)                                                         AS count
    FROM
        exercise_crew_raw e
    GROUP BY ( date_trunc('YEAR'::TEXT, e.date::TIMESTAMP WITH TIME ZONE)::DATE ), e.name
    ORDER BY ( date_trunc('YEAR'::TEXT, e.date::TIMESTAMP WITH TIME ZONE)::DATE ), e.name;

CREATE OR REPLACE VIEW crew_time_total_month(month, name, minutes, hours) AS
    SELECT
        a.month,
        a.name,
        sum(a.minutes)                  AS minutes,
        round(sum(a.minutes) / 60.0, 2) AS hours
    FROM
        (
            SELECT
                date_trunc('month'::TEXT, exercise_crew_raw.date::TIMESTAMP WITH TIME ZONE)::DATE AS month,
                sum(exercise_crew_raw.minutes)                                                    AS minutes,
                exercise_crew_raw.name
            FROM
                exercise_crew_raw
            GROUP BY ( date_trunc('month'::TEXT, exercise_crew_raw.date::TIMESTAMP WITH TIME ZONE)::DATE ),
                     exercise_crew_raw.name
            UNION
            SELECT
                date_trunc('month'::TEXT, calls_crew_raw.start_timestamp)::DATE AS month,
                sum(calls_crew_raw.duration)                                    AS minutes,
                calls_crew_raw.name
            FROM
                calls_crew_raw
            GROUP BY ( date_trunc('month'::TEXT, calls_crew_raw.start_timestamp)::DATE ), calls_crew_raw.name
        ) a
    GROUP BY a.month, a.name
    ORDER BY a.month, a.name;

CREATE OR REPLACE VIEW crew_time_total_year
        (year, name, minutes, hours, call_minutes, call_hours, exercise_minutes, exercise_hours) AS
    WITH
        excercise_hours
            AS (
            SELECT
                date_trunc('year'::TEXT, exercise_crew_raw.date::TIMESTAMP WITH TIME ZONE)::DATE AS year,
                sum(exercise_crew_raw.minutes)                                                   AS minutes,
                exercise_crew_raw.name
            FROM
                exercise_crew_raw
            GROUP BY ( date_trunc('year'::TEXT, exercise_crew_raw.date::TIMESTAMP WITH TIME ZONE)::DATE ),
                     exercise_crew_raw.name
               ),
        call_hours AS (
            SELECT
                date_trunc('year'::TEXT, calls_crew_raw.start_timestamp)::DATE AS year,
                sum(calls_crew_raw.duration)                                   AS minutes,
                calls_crew_raw.name
            FROM
                calls_crew_raw
            GROUP BY ( date_trunc('year'::TEXT, calls_crew_raw.start_timestamp)::DATE ), calls_crew_raw.name
               ),
        total_hours AS (
            SELECT
                a.year,
                a.name,
                sum(a.minutes) AS minutes
            FROM
                (
                    SELECT
                        excercise_hours.year,
                        excercise_hours.minutes,
                        excercise_hours.name
                    FROM
                        excercise_hours
                    UNION ALL
                    SELECT
                        call_hours.year,
                        call_hours.minutes,
                        call_hours.name
                    FROM
                        call_hours
                ) a
            GROUP BY a.year, a.name
               )
    SELECT
        t.year,
        t.name,
        coalesce(t.minutes, 0::NUMERIC)                          AS minutes,
        round(t.minutes / 60.0, 2)                               AS hours,
        coalesce(c.minutes, 0::BIGINT)                           AS call_minutes,
        round(coalesce(c.minutes, 0::BIGINT)::NUMERIC / 60.0, 2) AS call_hours,
        coalesce(e.minutes, 0::BIGINT)                           AS exercise_minutes,
        round(coalesce(e.minutes, 0::BIGINT)::NUMERIC / 60.0, 2) AS exercise_hours
    FROM
        total_hours t
            LEFT JOIN call_hours c
            ON t.year = c.year AND t.name = c.name
            LEFT JOIN excercise_hours e
            ON t.year = e.year AND t.name = e.name
    ORDER BY t.year, t.name;

CREATE OR REPLACE VIEW crew_qualifications(name, qualifications) AS
    SELECT
        qualifications.name,
        array_agg(qualifications.qualification) AS qualifications
    FROM
        qualifications
    GROUP BY qualifications.name;

CREATE OR REPLACE VIEW call_meta
        (call, duration, call_type, abort_reason, note, strength, strength_slim, additional_crew, leader, driver,
         crew, crew_names)
AS
    WITH
        crew_meta AS (
            SELECT
                c.call,
                count(1) FILTER (WHERE NOT c.additional)                                   AS strength,
                count(1) FILTER (WHERE c.additional)                                       AS additional_crew,
                coalesce(bool_or('Staffelführer'::TEXT = ANY ( q.qualifications )), FALSE) AS leader,
                coalesce(bool_or('Maschinist'::TEXT = ANY ( q.qualifications )), FALSE)    AS driver,
                array_agg(c.name)                                                          AS crew_names
            FROM
                call_crew c
                    LEFT JOIN crew_qualifications q
                    ON c.name = q.name
            GROUP BY c.call
            ORDER BY c.call
                     ),
        call_meta AS (
            SELECT
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

CREATE OR REPLACE VIEW call_issues(call, abort_reason, abort_reason_original, crew_names) AS
    SELECT
        call_meta.call,
        CASE
            WHEN call_meta.abort_reason <> ''::TEXT THEN call_meta.abort_reason
            WHEN NOT call_meta.crew                 THEN 'Kein Personal'::TEXT
            WHEN NOT call_meta.driver               THEN 'Kein Maschinist'::TEXT
            WHEN NOT call_meta.crew                 THEN 'Kein Staffelführer'::TEXT
                                                    ELSE NULL::TEXT
        END                    AS abort_reason,
        call_meta.abort_reason AS abort_reason_original,
        call_meta.crew_names
    FROM
        call_meta;

CREATE OR REPLACE VIEW aborted_calls (call, abort_reason, abort_reason_original, crew_names, crew, driver, leader) AS
    SELECT
        call_meta.call,
        CASE
            WHEN call_meta.abort_reason <> ''::TEXT THEN call_meta.abort_reason
            WHEN NOT call_meta.crew                 THEN 'Kein Personal'::TEXT
            WHEN NOT call_meta.driver               THEN 'Kein Maschinist'::TEXT
            WHEN NOT call_meta.leader               THEN 'Kein Staffelführer'::TEXT
                                                    ELSE NULL::TEXT
        END                    AS abort_reason,
        call_meta.abort_reason AS abort_reason_original,
        call_meta.crew_names,
        call_meta.crew,
        call_meta.driver,
        call_meta.leader
    FROM
        call_meta;

CREATE OR REPLACE VIEW aborted_calls_count(year, abort_reason, count, count_orig) AS
    SELECT
        date_trunc('YEAR'::TEXT, aborted_calls.call)::DATE                                       AS year,
        aborted_calls.abort_reason,
        count(1)                                                                                 AS count,
        count(1) FILTER (WHERE aborted_calls.abort_reason = aborted_calls.abort_reason_original) AS count_orig
    FROM
        aborted_calls
    WHERE aborted_calls.abort_reason IS NOT NULL
    GROUP BY ( date_trunc('YEAR'::TEXT, aborted_calls.call)::DATE ), aborted_calls.abort_reason;

CREATE OR REPLACE VIEW crew_issues(year, no_leader, no_crew, no_driver) AS
    SELECT
        date_trunc('YEAR'::TEXT, aborted_calls.call)::DATE AS year,
        count(1) FILTER (WHERE NOT aborted_calls.leader)   AS no_leader,
        count(1) FILTER (WHERE NOT aborted_calls.crew)     AS no_crew,
        count(1) FILTER (WHERE NOT aborted_calls.driver)   AS no_driver
    FROM
        aborted_calls
    WHERE aborted_calls.abort_reason IS NOT NULL
    GROUP BY ( date_trunc('YEAR'::TEXT, aborted_calls.call)::DATE );

CREATE OR REPLACE VIEW exercises_clean(date, hours, minutes, subject) AS
    SELECT
        exercises.date,
        exercises.hours,
        exercises.minutes,
        exercises.subject
    FROM
        exercises
    WHERE exercises.subject ~~* '%übung%'::TEXT
       OR exercises.subject ~~* '%sicherung%'::TEXT;

CREATE OR REPLACE VIEW calls_crew_hour(year, hour, name, perc, perc_total, calls, total_count) AS
    WITH
        crew_hour AS (
            SELECT
                date_trunc('YEAR'::TEXT, calls_crew_raw.start_timestamp) AS year,
                extract(HOUR FROM calls_crew_raw.start_timestamp)        AS hour,
                calls_crew_raw.name,
                count(1)                                                 AS calls
            FROM
                calls_crew_raw
            GROUP BY ( date_trunc('YEAR'::TEXT, calls_crew_raw.start_timestamp) ),
                     calls_crew_raw.name,
                     ( extract(HOUR FROM calls_crew_raw.start_timestamp) )
            ORDER BY ( date_trunc('YEAR'::TEXT, calls_crew_raw.start_timestamp) ),
                     calls_crew_raw.name,
                     ( extract(HOUR FROM calls_crew_raw.start_timestamp) )
                     ),
        calls_hour AS (
            SELECT
                date_trunc('YEAR'::TEXT, calls_clean.start_timestamp) AS year,
                extract(HOUR FROM calls_clean.start_timestamp)        AS hour,
                count(1)                                              AS calls
            FROM
                calls_clean
            GROUP BY ( date_trunc('YEAR'::TEXT, calls_clean.start_timestamp) ),
                     ( extract(HOUR FROM calls_clean.start_timestamp) )
                     )
    SELECT
        c.year,
        c.hour,
        c.name,
        c.calls::NUMERIC / t.calls           AS perc,
        c.calls::NUMERIC / ch.calls::NUMERIC AS perc_total,
        c.calls,
        t.calls                              AS total_count
    FROM
        crew_hour c
            LEFT JOIN calls_crew_year t
            USING (year, name)
            LEFT JOIN calls_hour ch
            USING (year, hour)
    ORDER BY c.hour, c.name;

