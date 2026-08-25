-- 1. Daily call count rolling (no dependencies)
CREATE OR REPLACE FUNCTION {{schema}}.get_daily_call_count_rolling(
    _year INTEGER,
    _n_days INTEGER
    )
    RETURNS TABLE (
        DAY        DATE,
        CALL_COUNT BIGINT,
        CALL_HOURS BIGINT
    )
    LANGUAGE sql
    STABLE
AS
$$
WITH
    all_days AS (
        SELECT
            generate_series(
                make_date(_year, 1, 1),
                make_date(_year, 12, 31),
                '1 day'::INTERVAL
            )::DATE AS day
                ),
    call_dates AS (
        SELECT
            start::DATE                              AS call_date,
            extract(EPOCH FROM "end" - start) / 3600 AS hours
        FROM
            {{schema}}.call
        WHERE start >= make_date(_year - 1, 1, 1) - ( _n_days || ' days' )::INTERVAL
          AND start < make_date(_year + 1, 1, 1)
                )
SELECT
    d.day,
    count(c.call_date)          AS call_count,
    round(sum(c.hours))::BIGINT AS hours
FROM
    all_days d
        LEFT JOIN call_dates c
        ON c.call_date > d.day - _n_days
            AND c.call_date <= d.day
GROUP BY d.day
ORDER BY d.day;
$$;

-- 2. Member daily call count rolling (single member, depends on #1)
CREATE OR REPLACE FUNCTION {{schema}}.get_member_daily_call_count_rolling(
    _year INTEGER,
    _n_days INTEGER,
    _member_name VARCHAR
    )
    RETURNS TABLE (
        DAY                   DATE,
        CALL_COUNT            BIGINT,
        CALL_COUNT_TOTAL      BIGINT,
        CALL_COUNT_PERCENTAGE INTEGER,
        CALL_HOURS            BIGINT,
        CALL_HOURS_TOTAL      BIGINT,
        CALL_HOURS_PERCENTAGE INTEGER
    )
    LANGUAGE sql
    STABLE
AS
$$
WITH
    all_days AS (
        SELECT
            generate_series(
                make_date(_year, 1, 1),
                make_date(_year, 12, 31),
                '1 day'::INTERVAL
            )::DATE AS day
                ),
    member_call_dates AS (
        SELECT
            c.start::DATE                            AS call_date,
            extract(EPOCH FROM "end" - start) / 3600 AS hours
        FROM
            {{schema}}.call c
                JOIN {{schema}}.callmember cm
                ON cm.call_id = c.id
                JOIN {{schema}}.member m
                ON m.id = cm.member_id
        WHERE m.name = _member_name
          AND c.start >= make_date(_year - 1, 1, 1) - ( _n_days || ' days' )::INTERVAL
          AND c.start < make_date(_year + 1, 1, 1)
                ),
    rolling_counts AS (
        SELECT
            d.day,
            count(mcd.call_date)                       AS call_count,
            coalesce(round(sum(mcd.hours)), 0)::BIGINT AS call_hours
        FROM
            all_days d
                LEFT JOIN member_call_dates mcd
                ON mcd.call_date > d.day - _n_days
                    AND mcd.call_date <= d.day
        GROUP BY d.day
        ORDER BY d.day
                )
SELECT
    day,
    c.call_count,
    total.call_count AS call_count_total,
    CASE WHEN total.call_count = 0 THEN 0
                                   ELSE round(c.call_count / total.call_count::NUMERIC, 2) * 100
    END              AS call_count_percentage,
    c.call_hours,
    total.call_hours AS call_hours_total,
    CASE WHEN total.call_hours = 0 THEN 0
                                   ELSE round(c.call_hours / total.call_hours::NUMERIC, 2) * 100
    END              AS call_hours_percentage
FROM
    rolling_counts c
        LEFT JOIN {{schema}}.get_daily_call_count_rolling(_year, _n_days) total
        USING (day)
$$;

-- 3. Member daily call count rolling (all members, depends on #2)
CREATE OR REPLACE FUNCTION {{schema}}.get_member_daily_call_count_rolling(
    _year INTEGER,
    _n_days INTEGER
    )
    RETURNS TABLE (
        DAY                   DATE,
        ID                    INTEGER,
        NAME                  TEXT,
        CALL_COUNT            BIGINT,
        CALL_COUNT_TOTAL      BIGINT,
        CALL_COUNT_PERCENTAGE INTEGER,
        CALL_HOURS            BIGINT,
        CALL_HOURS_TOTAL      BIGINT,
        CALL_HOURS_PERCENTAGE INTEGER
    )
    LANGUAGE sql
    STABLE
AS
$$
WITH
    members AS (
        SELECT
            id,
            name
        FROM
            {{schema}}.member
        WHERE retired IS NULL
           OR extract(YEAR FROM retired) >= _year
               ),
    stats AS (
        SELECT
            day,
            m.id,
            m.name,
            call_count,
            call_count_total,
            call_count_percentage,
            call_hours,
            call_hours_total,
            call_hours_percentage
        FROM
            members m, LATERAL {{schema}}.get_member_daily_call_count_rolling(_year, _n_days, m.name)
        ORDER BY day, m.name
               ),
    remove as (
        select id, sum(stats.call_count) as total FROM stats GROUP BY id
              )
    select * from stats WHERE id not in (select id from remove WHERE total = 0);
$$;

-- 4. Call group count by year (no dependencies)
CREATE OR REPLACE FUNCTION {{schema}}.get_call_group_count_by_year(
    _year INTEGER
)
    RETURNS TABLE (
        "group"    TEXT,
        CALL_COUNT BIGINT
    )
    LANGUAGE sql
    STABLE
AS
$$
SELECT
    s.group,
    count(1) AS call_count
FROM
    {{schema}}.callsubject cs
        LEFT JOIN {{schema}}.call c
        ON c.id = cs.call_id
        LEFT JOIN {{schema}}.subject s
        ON s.id = cs.subject_id
WHERE subject_order = 0
  AND extract(YEAR FROM start) = _year
GROUP BY s.group;
$$;

-- 5. Call group count by month (no dependencies)
CREATE OR REPLACE FUNCTION {{schema}}.get_call_group_count_by_month(
    _year INTEGER
)
    RETURNS TABLE (
        MONTH      DATE,
        "group"    TEXT,
        CALL_COUNT BIGINT
    )
    LANGUAGE sql
    STABLE
AS
$$
SELECT
    date_trunc('month', start)::DATE,
    s.group,
    count(1) AS call_count
FROM
    {{schema}}.callsubject cs
        LEFT JOIN {{schema}}.call c
        ON c.id = cs.call_id
        LEFT JOIN {{schema}}.subject s
        ON s.id = cs.subject_id
WHERE subject_order = 0
  AND extract(YEAR FROM start) = _year
GROUP BY date_trunc('month', start)::DATE, s.group;
$$;

-- 6. Call stats per call (no dependencies)
CREATE OR REPLACE FUNCTION {{schema}}.get_call_stats(_id INTEGER
)
    RETURNS TABLE (
        STRENGTH INT,
        LEADER   INT,
        DRIVER   INT
    )
    LANGUAGE sql
    STABLE
AS
$$
WITH
    member AS (
        SELECT
            cm.member_id,
            array_agg(q.name) AS qualifications
        FROM
            {{schema}}.callmember cm
                LEFT JOIN {{schema}}.memberqualification mq
                ON cm.member_id = mq.member_id
                LEFT JOIN {{schema}}.qualification q
                ON mq.qualification_id = q.id
        WHERE call_id = _id
        GROUP BY cm.member_id
        ORDER BY cm.member_id
              ),
    driver AS (
        SELECT
            member_id
        FROM
            member
        WHERE 'MA' = ANY ( qualifications )
        ORDER BY array_length(qualifications, 1)
        LIMIT 1
              ),
    leader AS (
        SELECT
            member_id
        FROM
            member
        WHERE 'SF' = ANY ( qualifications )
          AND member_id NOT IN (
            SELECT
                member_id
            FROM
                driver
                               )
        LIMIT 1
              )
SELECT
    (SELECT count(1) FROM member),
    (SELECT count(1) FROM leader),
    (SELECT count(1) FROM driver);
$$;

-- 7. Call stats by year (depends on #6)
CREATE OR REPLACE FUNCTION {{schema}}.get_call_stats_by_year(_year INTEGER
)
    RETURNS TABLE (
        CALL_ID  INTEGER,
        START    TIMESTAMPTZ,
        "end"    TIMESTAMPTZ,
        STRENGTH INT,
        LEADER   INT,
        DRIVER   INT
    )
    LANGUAGE sql
    STABLE
AS
$$
WITH
    calls AS (
        SELECT *
        FROM
            {{schema}}.call
        WHERE extract(YEAR FROM start) = _year
    )
SELECT
    id,
    start,
    "end",
    strength,
    leader,
    driver
FROM
    calls, LATERAL {{schema}}.get_call_stats(calls.id);
$$;

-- 8. Member call year stats (single member, no function dependencies)
CREATE OR REPLACE FUNCTION {{schema}}.get_member_call_year_stats(_year INTEGER, _member TEXT
                                                                 )
    RETURNS TABLE (
        CALL_COUNT      BIGINT,
        CALL_HOURS      BIGINT,
        CALL_COUNT_PERC INTEGER,
        CALL_HOURS_PERC INTEGER
    )
    LANGUAGE sql
    STABLE
AS
$$
WITH
    members AS (
        SELECT
            id
        FROM
            {{schema}}.member
        WHERE name = _member
               ),
    stats AS (
        SELECT
            count(1)                                                                      AS call_count,
            coalesce(round(( sum(extract(EPOCH FROM "end" - start) / 3600) )), 0)::BIGINT AS call_hours
        FROM
            members m
                LEFT JOIN {{schema}}.callmember cm
                ON m.id = cm.member_id
                LEFT JOIN {{schema}}.call c
                ON cm.call_id = c.id
        WHERE extract(YEAR FROM start) = _year
               ),
    summary AS (
        SELECT
            count(1) AS call_count,
            coalesce(sum(extract(EPOCH FROM "end" - start) / 3600), 0)::BIGINT AS count_call_hours
        FROM {{schema}}.call
        WHERE extract(YEAR FROM start) = _year
    )
SELECT
    ms.call_count,
    ms.call_hours,
    CASE s.call_count WHEN 0 THEN 0 ELSE round(( ms.call_count / s.call_count::NUMERIC ) * 100) END AS call_count_perc,
    CASE s.count_call_hours WHEN 0 THEN 0
                                   ELSE round(( ms.call_hours / s.count_call_hours::NUMERIC ) * 100)
    END                                                                                             AS call_hours_perc
FROM
    stats ms, summary s;
$$;

-- 9. Member call year stats (all members, depends on #8)
CREATE OR REPLACE FUNCTION {{schema}}.get_member_call_year_stats(_year INTEGER
)
    RETURNS TABLE (
        MEMBER_NAME     TEXT,
        CALL_COUNT      BIGINT,
        CALL_HOURS      BIGINT,
        CALL_COUNT_PERC INTEGER,
        CALL_HOURS_PERC INTEGER
    )
    LANGUAGE sql
    STABLE
AS
$$
WITH
    members AS (
        SELECT
            id,
            name
        FROM
            {{schema}}.member
        WHERE retired IS NULL
           OR extract(YEAR FROM retired) >= _year
    )
SELECT
    m.name,
    call_count,
    call_hours,
    call_count_perc,
    call_hours_perc
FROM
    members m,
    LATERAL {{schema}}.get_member_call_year_stats(_year, m.name) ms
WHERE call_count != 0
ORDER BY m.name;
$$;

-- 10. Min people for half hours (depends on #9)
CREATE OR REPLACE FUNCTION {{schema}}.get_min_people_for_half_hours(_year INTEGER
)
    RETURNS NUMERIC
    LANGUAGE sql
    STABLE
AS
$$
WITH
    member_stats AS (
        SELECT
            call_hours,
            sum(call_hours) OVER ()                      AS total_year_hours,
            row_number() OVER (ORDER BY call_hours DESC) AS rank_id
        FROM
            {{schema}}.get_member_call_year_stats(_year)
                    ),
    running_stats AS (
        SELECT
            call_hours,
            total_year_hours,
            sum(call_hours) OVER (ORDER BY call_hours DESC, rank_id) AS running_total,
            count(*) OVER ()                                         AS total_people_count
        FROM
            member_stats
                    )
SELECT
    round(count(*) / max(total_people_count)::NUMERIC * 100) AS people_count
FROM
    running_stats
WHERE
    running_total - call_hours < total_year_hours / 2.0;
$$;

-- 11. Year call summary (depends on #10)
CREATE OR REPLACE FUNCTION {{schema}}.get_year_call_summary(
    _year INTEGER
)
    RETURNS TABLE (
        CALL_COUNT         BIGINT,
        ABORTED            BIGINT,
        COUNT_CALL_HOURS   BIGINT,
        COUNT_CREW_HOURS   BIGINT,
        HALF_HOURS_MEMBERS NUMERIC
    )
    LANGUAGE sql
    STABLE
AS
$$
WITH
    calls AS (
        SELECT
            id,
            extract(EPOCH FROM "end" - start) / 3600 AS duration,
            abort_reason IS NOT NULL                 AS aborted
        FROM
            {{schema}}.call
        WHERE extract(YEAR FROM start) = _year
             ),
    member_count AS (
        SELECT
            call_id,
            count(1) AS member_count
        FROM
            {{schema}}.callmember
        WHERE call_id IN (
            SELECT
                id
            FROM
                calls
                         )
        GROUP BY call_id
             )
SELECT
    count(1)                                AS call_count,
    count(1) FILTER ( WHERE aborted )       AS aborted,
    sum(duration)::INT                      AS count_call_hours,
    sum(duration * c.member_count)::INTEGER AS count_crew_hours,
    {{schema}}.get_min_people_for_half_hours(_year)
FROM
    calls
        LEFT JOIN member_count c
        ON calls.id = c.call_id;
$$;

-- 12. Range of years that hold any data at all
CREATE OR REPLACE FUNCTION {{schema}}.get_data_year_range()
    RETURNS TABLE (
        MIN_YEAR INTEGER,
        MAX_YEAR INTEGER
    )
    LANGUAGE sql
    STABLE
AS
$$
WITH
    years AS (
        SELECT extract(YEAR FROM start)::INTEGER AS year FROM {{schema}}.call
        UNION ALL
        SELECT extract(YEAR FROM exercise_date)::INTEGER FROM {{schema}}.exercise
        UNION ALL
        SELECT extract(YEAR FROM exercise_date)::INTEGER FROM {{schema}}.youthexercise
            )
SELECT
    coalesce(min(year), extract(YEAR FROM now())::INTEGER),
    coalesce(max(year), extract(YEAR FROM now())::INTEGER)
FROM
    years;
$$;

-- 13. One row per year across every activity type, the backbone of all comparisons
CREATE OR REPLACE FUNCTION {{schema}}.get_yearly_series(
    _year_from INTEGER,
    _year_to INTEGER
)
    RETURNS TABLE (
        YEAR                 INTEGER,
        CALL_COUNT           BIGINT,
        CALL_HOURS           BIGINT,
        CREW_HOURS           BIGINT,
        ABORTED              BIGINT,
        AVG_CREW             NUMERIC,
        EXERCISE_COUNT       BIGINT,
        EXERCISE_HOURS       BIGINT,
        EXERCISE_ATTENDANCE  BIGINT,
        YOUTH_COUNT          BIGINT,
        YOUTH_HOURS          BIGINT,
        YOUTH_PARTICIPANTS   BIGINT,
        ROSTER_MEMBERS       BIGINT,
        PARTICIPATING_MEMBERS BIGINT
    )
    LANGUAGE sql
    STABLE
AS
$$
WITH
    years AS (
        SELECT generate_series(_year_from, _year_to) AS year
          ),
    calls AS (
        SELECT
            extract(YEAR FROM c.start)::INTEGER                AS year,
            c.id,
            extract(EPOCH FROM c."end" - c.start) / 3600       AS hours,
            c.abort_reason IS NOT NULL                         AS aborted,
            (SELECT count(1) FROM {{schema}}.callmember cm WHERE cm.call_id = c.id) AS crew
        FROM
            {{schema}}.call c
          ),
    call_stats AS (
        SELECT
            year,
            count(1)                          AS call_count,
            round(sum(hours))::BIGINT         AS call_hours,
            round(sum(hours * crew))::BIGINT  AS crew_hours,
            count(1) FILTER ( WHERE aborted ) AS aborted,
            round(avg(crew), 1)               AS avg_crew
        FROM
            calls
        GROUP BY year
          ),
    exercises AS (
        SELECT
            extract(YEAR FROM e.exercise_date)::INTEGER AS year,
            count(1)                                    AS exercise_count,
            round(sum(e.duration) / 60.0)::BIGINT       AS exercise_hours,
            sum((SELECT count(1) FROM {{schema}}.memberexercise me WHERE me.exercise_id = e.id)) AS attendance
        FROM
            {{schema}}.exercise e
        GROUP BY 1
          ),
    youth AS (
        SELECT
            extract(YEAR FROM y.exercise_date)::INTEGER AS year,
            count(1)                                    AS youth_count,
            round(sum(y.duration) / 60.0)::BIGINT       AS youth_hours,
            sum(coalesce(y.participants, 0))::BIGINT    AS youth_participants
        FROM
            {{schema}}.youthexercise y
        GROUP BY 1
          ),
    roster AS (
        SELECT
            y.year,
            count(1) AS roster_members
        FROM
            years y
                JOIN {{schema}}.member m
                ON ( m.joined IS NULL OR extract(YEAR FROM m.joined) <= y.year )
                    AND ( m.retired IS NULL OR extract(YEAR FROM m.retired) >= y.year )
        GROUP BY y.year
          ),
    participating AS (
        SELECT
            year,
            count(DISTINCT member_id) AS participating_members
        FROM
            (
                SELECT extract(YEAR FROM c.start)::INTEGER AS year, cm.member_id
                FROM {{schema}}.callmember cm JOIN {{schema}}.call c ON c.id = cm.call_id
                UNION
                SELECT extract(YEAR FROM e.exercise_date)::INTEGER, me.member_id
                FROM {{schema}}.memberexercise me JOIN {{schema}}.exercise e ON e.id = me.exercise_id
                UNION
                SELECT extract(YEAR FROM y.exercise_date)::INTEGER, my.member_id
                FROM {{schema}}.memberyouthexercise my JOIN {{schema}}.youthexercise y ON y.id = my.youth_training_id
            ) activity
        GROUP BY year
          )
SELECT
    y.year,
    coalesce(c.call_count, 0),
    coalesce(c.call_hours, 0),
    coalesce(c.crew_hours, 0),
    coalesce(c.aborted, 0),
    coalesce(c.avg_crew, 0),
    coalesce(e.exercise_count, 0),
    coalesce(e.exercise_hours, 0),
    coalesce(e.attendance, 0),
    coalesce(yo.youth_count, 0),
    coalesce(yo.youth_hours, 0),
    coalesce(yo.youth_participants, 0),
    coalesce(r.roster_members, 0),
    coalesce(p.participating_members, 0)
FROM
    years y
        LEFT JOIN call_stats c ON c.year = y.year
        LEFT JOIN exercises e ON e.year = y.year
        LEFT JOIN youth yo ON yo.year = y.year
        LEFT JOIN roster r ON r.year = y.year
        LEFT JOIN participating p ON p.year = y.year
ORDER BY y.year;
$$;

-- 14. When calls happen: weekday (1 = Monday) by hour of day
CREATE OR REPLACE FUNCTION {{schema}}.get_call_time_profile(_year INTEGER)
    RETURNS TABLE (
        WEEKDAY    INTEGER,
        HOUR       INTEGER,
        CALL_COUNT BIGINT
    )
    LANGUAGE sql
    STABLE
AS
$$
SELECT
    extract(ISODOW FROM start)::INTEGER,
    extract(HOUR FROM start)::INTEGER,
    count(1)
FROM
    {{schema}}.call
WHERE extract(YEAR FROM start) = _year
GROUP BY 1, 2
ORDER BY 1, 2;
$$;

-- 15. Most frequent subjects of a year, not just their groups
CREATE OR REPLACE FUNCTION {{schema}}.get_call_subjects(_year INTEGER, _limit INTEGER)
    RETURNS TABLE (
        NAME       TEXT,
        "group"    TEXT,
        CALL_COUNT BIGINT
    )
    LANGUAGE sql
    STABLE
AS
$$
SELECT
    s.name::TEXT,
    s."group"::TEXT,
    count(1)
FROM
    {{schema}}.callsubject cs
        JOIN {{schema}}.call c ON c.id = cs.call_id
        JOIN {{schema}}.subject s ON s.id = cs.subject_id
WHERE extract(YEAR FROM c.start) = _year
GROUP BY s.name, s."group"
ORDER BY count(1) DESC, s.name
LIMIT _limit;
$$;

-- 16. Why calls were aborted
CREATE OR REPLACE FUNCTION {{schema}}.get_abort_reasons(_year INTEGER)
    RETURNS TABLE (
        REASON     TEXT,
        CALL_COUNT BIGINT
    )
    LANGUAGE sql
    STABLE
AS
$$
SELECT
    abort_reason::TEXT,
    count(1)
FROM
    {{schema}}.call
WHERE extract(YEAR FROM start) = _year
  AND abort_reason IS NOT NULL
GROUP BY abort_reason
ORDER BY count(1) DESC;
$$;

-- 17. How long calls take, bucketed, plus the follow-up effort booked on them
CREATE OR REPLACE FUNCTION {{schema}}.get_call_durations(_year INTEGER)
    RETURNS TABLE (
        BUCKET     TEXT,
        SORT_ORDER INTEGER,
        CALL_COUNT BIGINT
    )
    LANGUAGE sql
    STABLE
AS
$$
WITH
    buckets AS (
        SELECT
            CASE
                WHEN minutes < 30 THEN 1
                WHEN minutes < 60 THEN 2
                WHEN minutes < 120 THEN 3
                WHEN minutes < 240 THEN 4
                ELSE 5
            END AS sort_order
        FROM
            (
                SELECT extract(EPOCH FROM "end" - start) / 60 AS minutes
                FROM {{schema}}.call
                WHERE extract(YEAR FROM start) = _year
            ) durations
               ),
    labels AS (
        SELECT * FROM ( VALUES (1, '< 30 min'), (2, '30–60 min'), (3, '1–2 h'), (4, '2–4 h'), (5, '> 4 h') )
            AS l (sort_order, label)
              )
SELECT
    l.label::TEXT,
    l.sort_order,
    count(b.sort_order)
FROM
    labels l
        LEFT JOIN buckets b ON b.sort_order = l.sort_order
GROUP BY l.label, l.sort_order
ORDER BY l.sort_order;
$$;

-- 18. The longest calls of a year
CREATE OR REPLACE FUNCTION {{schema}}.get_longest_calls(_year INTEGER, _limit INTEGER)
    RETURNS TABLE (
        CALL_ID  INTEGER,
        START    TIMESTAMPTZ,
        MINUTES  INTEGER,
        CREW     BIGINT,
        SUBJECTS TEXT
    )
    LANGUAGE sql
    STABLE
AS
$$
SELECT
    c.id,
    c.start,
    round(extract(EPOCH FROM c."end" - c.start) / 60)::INTEGER,
    (SELECT count(1) FROM {{schema}}.callmember cm WHERE cm.call_id = c.id),
    coalesce((SELECT string_agg(s.name, ' + ' ORDER BY cs.subject_order)
              FROM {{schema}}.callsubject cs
                       JOIN {{schema}}.subject s ON s.id = cs.subject_id
              WHERE cs.call_id = c.id), '')::TEXT
FROM
    {{schema}}.call c
WHERE extract(YEAR FROM c.start) = _year
ORDER BY c."end" - c.start DESC
LIMIT _limit;
$$;

-- 19. How many calls had a unit leader and a driver on board
CREATE OR REPLACE FUNCTION {{schema}}.get_qualification_coverage(_year INTEGER)
    RETURNS TABLE (
        CALL_COUNT  BIGINT,
        WITH_LEADER BIGINT,
        WITH_DRIVER BIGINT,
        WITH_BOTH   BIGINT
    )
    LANGUAGE sql
    STABLE
AS
$$
SELECT
    count(1),
    count(1) FILTER ( WHERE leader > 0 ),
    count(1) FILTER ( WHERE driver > 0 ),
    count(1) FILTER ( WHERE leader > 0 AND driver > 0 )
FROM
    {{schema}}.get_call_stats_by_year(_year);
$$;

-- 20. How the roster spreads across the year: members bucketed by calls attended
CREATE OR REPLACE FUNCTION {{schema}}.get_turnout_distribution(_year INTEGER)
    RETURNS TABLE (
        BUCKET       TEXT,
        SORT_ORDER   INTEGER,
        MEMBER_COUNT BIGINT
    )
    LANGUAGE sql
    STABLE
AS
$$
WITH
    per_member AS (
        SELECT
            m.id,
            (SELECT count(1)
             FROM {{schema}}.callmember cm
                      JOIN {{schema}}.call c ON c.id = cm.call_id
             WHERE cm.member_id = m.id
               AND extract(YEAR FROM c.start) = _year) AS calls
        FROM
            {{schema}}.member m
        WHERE ( m.joined IS NULL OR extract(YEAR FROM m.joined) <= _year )
  AND ( m.retired IS NULL OR extract(YEAR FROM m.retired) >= _year )
                  ),
    bucketed AS (
        SELECT
            CASE
                WHEN calls = 0 THEN 1
                WHEN calls <= 5 THEN 2
                WHEN calls <= 20 THEN 3
                WHEN calls <= 50 THEN 4
                ELSE 5
            END AS sort_order
        FROM
            per_member
                ),
    labels AS (
        SELECT * FROM ( VALUES (1, '0'), (2, '1–5'), (3, '6–20'), (4, '21–50'), (5, '> 50') )
            AS l (sort_order, label)
              )
SELECT
    l.label::TEXT,
    l.sort_order,
    count(b.sort_order)
FROM
    labels l
        LEFT JOIN bucketed b ON b.sort_order = l.sort_order
GROUP BY l.label, l.sort_order
ORDER BY l.sort_order;
$$;

-- 21. Exercises of a year in numbers
CREATE OR REPLACE FUNCTION {{schema}}.get_exercise_summary(_year INTEGER)
    RETURNS TABLE (
        EXERCISE_COUNT  BIGINT,
        EXERCISE_HOURS  BIGINT,
        ATTENDANCE      BIGINT,
        AVG_ATTENDANCE  NUMERIC,
        CREW_HOURS      BIGINT
    )
    LANGUAGE sql
    STABLE
AS
$$
WITH
    exercises AS (
        SELECT
            e.id,
            e.duration,
            (SELECT count(1) FROM {{schema}}.memberexercise me WHERE me.exercise_id = e.id) AS attendance
        FROM
            {{schema}}.exercise e
        WHERE extract(YEAR FROM e.exercise_date) = _year
                 )
SELECT
    count(1),
    round(coalesce(sum(duration), 0) / 60.0)::BIGINT,
    coalesce(sum(attendance), 0)::BIGINT,
    coalesce(round(avg(attendance), 1), 0),
    round(coalesce(sum(duration * attendance), 0) / 60.0)::BIGINT
FROM
    exercises;
$$;

-- 22. Every exercise of a year with the number of people who attended
CREATE OR REPLACE FUNCTION {{schema}}.get_exercise_sessions(_year INTEGER)
    RETURNS TABLE (
        EXERCISE_ID   INTEGER,
        EXERCISE_DATE DATE,
        SUBJECT       TEXT,
        MINUTES       INTEGER,
        ATTENDANCE    BIGINT
    )
    LANGUAGE sql
    STABLE
AS
$$
SELECT
    e.id,
    e.exercise_date,
    e.subject::TEXT,
    e.duration,
    (SELECT count(1) FROM {{schema}}.memberexercise me WHERE me.exercise_id = e.id)
FROM
    {{schema}}.exercise e
WHERE extract(YEAR FROM e.exercise_date) = _year
ORDER BY e.exercise_date;
$$;

-- 23. Exercise attendance per member, with the share of the year's exercises attended
CREATE OR REPLACE FUNCTION {{schema}}.get_exercise_member_stats(_year INTEGER)
    RETURNS TABLE (
        MEMBER_ID       INTEGER,
        MEMBER_NAME     TEXT,
        ATTENDED        BIGINT,
        EXERCISE_HOURS  BIGINT,
        ATTENDED_PERC   INTEGER
    )
    LANGUAGE sql
    STABLE
AS
$$
WITH
    exercises AS (
        SELECT id, duration
        FROM {{schema}}.exercise
        WHERE extract(YEAR FROM exercise_date) = _year
                 ),
    total AS (
        SELECT count(1) AS count FROM exercises
             )
SELECT
    m.id,
    m.name::TEXT,
    count(e.id),
    round(coalesce(sum(e.duration), 0) / 60.0)::BIGINT,
    CASE
        WHEN (SELECT count FROM total) = 0 THEN 0
        ELSE round(count(e.id) * 100.0 / (SELECT count FROM total))::INTEGER
    END
FROM
    {{schema}}.member m
        LEFT JOIN {{schema}}.memberexercise me ON me.member_id = m.id
        LEFT JOIN exercises e ON e.id = me.exercise_id
WHERE ( m.joined IS NULL OR extract(YEAR FROM m.joined) <= _year )
  AND ( m.retired IS NULL OR extract(YEAR FROM m.retired) >= _year )
GROUP BY m.id, m.name
ORDER BY count(e.id) DESC, m.name;
$$;

-- 24. Youth work of a year in numbers
CREATE OR REPLACE FUNCTION {{schema}}.get_youth_summary(_year INTEGER)
    RETURNS TABLE (
        SESSION_COUNT     BIGINT,
        SESSION_HOURS     BIGINT,
        PARTICIPANTS      BIGINT,
        AVG_PARTICIPANTS  NUMERIC,
        INSTRUCTOR_COUNT  BIGINT,
        INSTRUCTOR_HOURS  BIGINT
    )
    LANGUAGE sql
    STABLE
AS
$$
WITH
    sessions AS (
        SELECT
            y.id,
            y.duration,
            coalesce(y.participants, 0) AS participants,
            (SELECT count(1) FROM {{schema}}.memberyouthexercise my WHERE my.youth_training_id = y.id) AS instructors
        FROM
            {{schema}}.youthexercise y
        WHERE extract(YEAR FROM y.exercise_date) = _year
                )
SELECT
    count(1),
    round(coalesce(sum(duration), 0) / 60.0)::BIGINT,
    coalesce(sum(participants), 0)::BIGINT,
    coalesce(round(avg(participants), 1), 0),
    (SELECT count(DISTINCT my.member_id)
     FROM {{schema}}.memberyouthexercise my
     WHERE my.youth_training_id IN (SELECT id FROM sessions)),
    round(coalesce(sum(duration * instructors), 0) / 60.0)::BIGINT
FROM
    sessions;
$$;

-- 25. Every youth session of a year with participants and instructors
CREATE OR REPLACE FUNCTION {{schema}}.get_youth_sessions(_year INTEGER)
    RETURNS TABLE (
        EXERCISE_ID   INTEGER,
        EXERCISE_DATE DATE,
        SUBJECT       TEXT,
        MINUTES       INTEGER,
        PARTICIPANTS  INTEGER,
        INSTRUCTORS   BIGINT
    )
    LANGUAGE sql
    STABLE
AS
$$
SELECT
    y.id,
    y.exercise_date,
    y.subject::TEXT,
    y.duration,
    coalesce(y.participants, 0),
    (SELECT count(1) FROM {{schema}}.memberyouthexercise my WHERE my.youth_training_id = y.id)
FROM
    {{schema}}.youthexercise y
WHERE extract(YEAR FROM y.exercise_date) = _year
ORDER BY y.exercise_date;
$$;

-- 26. Calls, exercises and youth work of a year rolled into one figure per member
CREATE OR REPLACE FUNCTION {{schema}}.get_combined_member_stats(_year INTEGER)
    RETURNS TABLE (
        MEMBER_ID      INTEGER,
        MEMBER_NAME    TEXT,
        CALL_COUNT     BIGINT,
        CALL_HOURS     BIGINT,
        EXERCISE_COUNT BIGINT,
        EXERCISE_HOURS BIGINT,
        YOUTH_COUNT    BIGINT,
        YOUTH_HOURS    BIGINT,
        TOTAL_HOURS    BIGINT
    )
    LANGUAGE sql
    STABLE
AS
$$
WITH
    calls AS (
        SELECT
            cm.member_id,
            count(1)                                                  AS call_count,
            sum(extract(EPOCH FROM c."end" - c.start) / 3600)          AS call_hours
        FROM
            {{schema}}.callmember cm
                JOIN {{schema}}.call c ON c.id = cm.call_id
        WHERE extract(YEAR FROM c.start) = _year
        GROUP BY cm.member_id
          ),
    exercises AS (
        SELECT
            me.member_id,
            count(1)                    AS exercise_count,
            sum(e.duration) / 60.0      AS exercise_hours
        FROM
            {{schema}}.memberexercise me
                JOIN {{schema}}.exercise e ON e.id = me.exercise_id
        WHERE extract(YEAR FROM e.exercise_date) = _year
        GROUP BY me.member_id
              ),
    youth AS (
        SELECT
            my.member_id,
            count(1)                    AS youth_count,
            sum(y.duration) / 60.0      AS youth_hours
        FROM
            {{schema}}.memberyouthexercise my
                JOIN {{schema}}.youthexercise y ON y.id = my.youth_training_id
        WHERE extract(YEAR FROM y.exercise_date) = _year
        GROUP BY my.member_id
          )
SELECT
    m.id,
    m.name::TEXT,
    coalesce(c.call_count, 0),
    round(coalesce(c.call_hours, 0))::BIGINT,
    coalesce(e.exercise_count, 0),
    round(coalesce(e.exercise_hours, 0))::BIGINT,
    coalesce(y.youth_count, 0),
    round(coalesce(y.youth_hours, 0))::BIGINT,
    round(coalesce(c.call_hours, 0) + coalesce(e.exercise_hours, 0) + coalesce(y.youth_hours, 0))::BIGINT
FROM
    {{schema}}.member m
        LEFT JOIN calls c ON c.member_id = m.id
        LEFT JOIN exercises e ON e.member_id = m.id
        LEFT JOIN youth y ON y.member_id = m.id
WHERE ( m.joined IS NULL OR extract(YEAR FROM m.joined) <= _year )
  AND ( m.retired IS NULL OR extract(YEAR FROM m.retired) >= _year )
ORDER BY 9 DESC, m.name;
$$;

-- 27. One member's activity across several years
CREATE OR REPLACE FUNCTION {{schema}}.get_member_year_trend(
    _member_id INTEGER,
    _year_from INTEGER,
    _year_to INTEGER
)
    RETURNS TABLE (
        YEAR            INTEGER,
        CALL_COUNT      BIGINT,
        CALL_HOURS      BIGINT,
        CALL_COUNT_PERC INTEGER,
        EXERCISE_COUNT  BIGINT,
        YOUTH_COUNT     BIGINT
    )
    LANGUAGE sql
    STABLE
AS
$$
WITH
    years AS (
        SELECT generate_series(_year_from, _year_to) AS year
          ),
    calls AS (
        SELECT
            extract(YEAR FROM c.start)::INTEGER              AS year,
            count(1)                                         AS call_count,
            round(sum(extract(EPOCH FROM c."end" - c.start) / 3600))::BIGINT AS call_hours
        FROM
            {{schema}}.callmember cm
                JOIN {{schema}}.call c ON c.id = cm.call_id
        WHERE cm.member_id = _member_id
        GROUP BY 1
          ),
    totals AS (
        SELECT
            extract(YEAR FROM start)::INTEGER AS year,
            count(1)                          AS call_count
        FROM
            {{schema}}.call
        GROUP BY 1
           ),
    exercises AS (
        SELECT
            extract(YEAR FROM e.exercise_date)::INTEGER AS year,
            count(1)                                    AS exercise_count
        FROM
            {{schema}}.memberexercise me
                JOIN {{schema}}.exercise e ON e.id = me.exercise_id
        WHERE me.member_id = _member_id
        GROUP BY 1
              ),
    youth AS (
        SELECT
            extract(YEAR FROM y.exercise_date)::INTEGER AS year,
            count(1)                                    AS youth_count
        FROM
            {{schema}}.memberyouthexercise my
                JOIN {{schema}}.youthexercise y ON y.id = my.youth_training_id
        WHERE my.member_id = _member_id
        GROUP BY 1
          )
SELECT
    y.year,
    coalesce(c.call_count, 0),
    coalesce(c.call_hours, 0),
    CASE
        WHEN coalesce(t.call_count, 0) = 0 THEN 0
        ELSE round(coalesce(c.call_count, 0) * 100.0 / t.call_count)::INTEGER
    END,
    coalesce(e.exercise_count, 0),
    coalesce(yo.youth_count, 0)
FROM
    years y
        LEFT JOIN calls c ON c.year = y.year
        LEFT JOIN totals t ON t.year = y.year
        LEFT JOIN exercises e ON e.year = y.year
        LEFT JOIN youth yo ON yo.year = y.year
ORDER BY y.year;
$$;

-- 28. Roster development: who is on the books and who retired, per year
CREATE OR REPLACE FUNCTION {{schema}}.get_membership(
    _year_from INTEGER,
    _year_to INTEGER
)
    RETURNS TABLE (
        YEAR                  INTEGER,
        ROSTER_MEMBERS        BIGINT,
        JOINED_IN_YEAR        BIGINT,
        RETIRED_IN_YEAR       BIGINT,
        PARTICIPATING_MEMBERS BIGINT
    )
    LANGUAGE sql
    STABLE
AS
$$
SELECT
    s.year,
    s.roster_members,
    (SELECT count(1)
     FROM {{schema}}.member m
     WHERE extract(YEAR FROM m.joined) = s.year),
    (SELECT count(1)
     FROM {{schema}}.member m
     WHERE extract(YEAR FROM m.retired) = s.year),
    s.participating_members
FROM
    {{schema}}.get_yearly_series(_year_from, _year_to) s
ORDER BY s.year;
$$;
