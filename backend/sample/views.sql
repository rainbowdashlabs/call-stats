CREATE OR REPLACE FUNCTION call_stats.get_daily_call_count_rolling(
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
        -- Generate all days in the given year
        SELECT
            generate_series(
                make_date(_year, 1, 1),
                make_date(_year, 12, 31),
                '1 day'::INTERVAL
            )::DATE AS day
                ),
    call_dates AS (
        -- Get all calls from the given year and the end of the previous year
        -- (we need previous year data for the rolling window at year start)
        SELECT
            start::DATE                              AS call_date,
            extract(EPOCH FROM "end" - start) / 3600 AS hours
        FROM
            call_stats.call
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

CREATE OR REPLACE FUNCTION call_stats.get_member_daily_call_count_rolling(
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
            call_stats.call c
                JOIN call_stats.callmember cm
                ON cm.call_id = c.id
                JOIN call_stats.member m
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
        LEFT JOIN call_stats.get_daily_call_count_rolling(_year, _n_days) total
        USING (day)
$$;

CREATE OR REPLACE FUNCTION call_stats.get_member_daily_call_count_rolling(
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
            call_stats.member
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
            members m, LATERAL call_stats.get_member_daily_call_count_rolling(_year, _n_days, m.name)
        ORDER BY day, m.name
               ),
    remove as (
        select id, sum(stats.call_count) as total FROM stats GROUP BY id
              )
    select * from stats WHERE id not in (select id from remove WHERE total = 0);
$$;

CREATE OR REPLACE FUNCTION call_stats.get_call_group_count_by_year(
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
    call_stats.callsubject cs
        LEFT JOIN call_stats.call c
        ON c.id = cs.call_id
        LEFT JOIN call_stats.subject s
        ON s.id = cs.subject_id
WHERE subject_order = 0
  AND extract(YEAR FROM start) = _year
GROUP BY s.group;
$$;

SELECT *
FROM
    get_call_group_count_by_year(2025);

CREATE OR REPLACE FUNCTION call_stats.get_call_group_count_by_month(
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
    call_stats.callsubject cs
        LEFT JOIN call_stats.call c
        ON c.id = cs.call_id
        LEFT JOIN call_stats.subject s
        ON s.id = cs.subject_id
WHERE subject_order = 0
  AND extract(YEAR FROM start) = _year
GROUP BY date_trunc('month', start)::DATE, s.group;
$$;
CREATE OR REPLACE FUNCTION call_stats.get_year_call_summary(
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
            call_stats.call
        WHERE extract(YEAR FROM start) = _year
             ),
    member_count AS (
        SELECT
            call_id,
            count(1) AS member_count
        FROM
            call_stats.callmember
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
    call_stats.get_min_people_for_half_hours(_year)
FROM
    calls
        LEFT JOIN member_count c
        ON calls.id = c.call_id;
$$;

CREATE OR REPLACE FUNCTION call_stats.get_call_stats(_id INTEGER
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
            call_stats.callmember cm
                LEFT JOIN call_stats.memberqualification mq
                ON cm.member_id = mq.member_id
                LEFT JOIN call_stats.qualification q
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
    (
        SELECT
            count(1)
        FROM
            member
    ),
    (
        SELECT
            count(1)
        FROM
            leader
    ),
    (
        SELECT
            count(1)
        FROM
            driver
    );
$$;

CREATE OR REPLACE FUNCTION call_stats.get_call_stats_by_year(_year INTEGER
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
            call_stats.call
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
    calls, LATERAL call_stats.get_call_stats(calls.id);
$$;

CREATE OR REPLACE FUNCTION call_stats.get_member_call_year_stats(_year INTEGER, _member TEXT
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
            call_stats.member
        WHERE name = _member
               ),
    stats AS (
        SELECT
            count(1)                                                                      AS call_count,
            coalesce(round(( sum(extract(EPOCH FROM "end" - start) / 3600) )), 0)::BIGINT AS call_hours
        FROM
            members m
                LEFT JOIN call_stats.callmember cm
                ON m.id = cm.member_id
                LEFT JOIN call_stats.call c
                ON cm.call_id = c.id
        WHERE extract(YEAR FROM start) = _year
               )
SELECT
    ms.call_count,
    ms.call_hours,
    CASE s.call_count WHEN 0 THEN 0 ELSE round(( ms.call_count / s.call_count::NUMERIC ) * 100) END AS call_count_perc,
    CASE s.count_crew_hours WHEN 0 THEN 0
                                   ELSE round(( ms.call_hours / s.count_call_hours::NUMERIC ) * 100)
    END                                                                                             AS call_hours_perc
FROM
    stats ms
        LEFT JOIN call_stats.get_year_call_summary(_year) s
        ON TRUE;
$$;
CREATE OR REPLACE FUNCTION call_stats.get_member_call_year_stats(_year INTEGER
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
            call_stats.member
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
    LATERAL call_stats.get_member_call_year_stats(_year, m.name) ms
WHERE call_count != 0
ORDER BY m.name;
$$;

WITH
    member_stats AS (
        -- Get hours for every member who participated this year
        SELECT
            call_hours,
            sum(call_hours) OVER () AS total_year_hours
        FROM
            call_stats.get_member_call_year_stats(2025)
                    ),
    running_stats AS (
        -- Order by hours descending and calculate running total
        SELECT
            call_hours,
            total_year_hours,
            sum(call_hours)
            OVER (ORDER BY call_hours DESC, row_number() OVER (ORDER BY call_hours DESC)) AS running_total,
            count(*) OVER ()                                                              AS total_people_count
        FROM
            member_stats
                    )
SELECT
    count(*)                                                                  AS people_count,
    max(total_people_count)                                                   AS total_people,
    max(total_year_hours)                                                     AS total_hours,
    max(running_total) FILTER (WHERE running_total >= total_year_hours / 2.0) AS reached_hours
FROM
    running_stats
WHERE
    -- Keep only rows until we hit or exceed the 50% mark
    running_total - call_hours < total_year_hours / 2.0;

CREATE OR REPLACE FUNCTION call_stats.get_min_people_for_half_hours(_year INTEGER
)
    RETURNS NUMERIC
    LANGUAGE sql
    STABLE
AS
$$
WITH
    member_stats AS (
        -- Get hours and total sum
        SELECT
            call_hours,
            sum(call_hours) OVER ()                      AS total_year_hours,
            row_number() OVER (ORDER BY call_hours DESC) AS rank_id
        FROM
            call_stats.get_member_call_year_stats(_year)
                    ),
    running_stats AS (
        -- Calculate running total using the rank_id to avoid the nesting error
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
    -- Include everyone until the running total reaches/crosses the 50% mark
    running_total - call_hours < total_year_hours / 2.0;
$$;