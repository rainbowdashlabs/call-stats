import os

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session
from sqlalchemy import text

from data import get_session

router = APIRouter(prefix="/statistics", tags=["statistics"])

_schema = os.getenv("DB_SCHEMA", "public")

DEFAULT_YEARS_BACK = 5


def _call(session: Session, function: str, **params):
    """Run one of the statistics SQL functions and return its rows."""
    arguments = ", ".join(f":{name}" for name in params)
    return session.exec(text(f"SELECT * FROM {_schema}.{function}({arguments})"), params=params)


class DailyCallCount(BaseModel):
    day: str
    call_count: int
    call_hours: int | None


class MemberDailyStats(BaseModel):
    day: str
    id: int
    name: str
    call_count: int
    call_count_total: int
    call_count_percentage: int
    call_hours: int
    call_hours_total: int
    call_hours_percentage: int


class CallGroupCount(BaseModel):
    group: str
    call_count: int


class CallGroupMonthCount(BaseModel):
    month: str
    group: str
    call_count: int


class YearSummary(BaseModel):
    call_count: int
    aborted: int
    count_call_hours: int
    count_crew_hours: int
    half_hours_members: float | None


class MemberYearStats(BaseModel):
    member_name: str
    call_count: int
    call_hours: int
    call_count_perc: int
    call_hours_perc: int


@router.get("/daily_calls")
def get_daily_calls(*, session: Session = Depends(get_session), year: int, n_days: int = 30) -> list[DailyCallCount]:
    result = session.exec(
        text(f"SELECT * FROM {_schema}.get_daily_call_count_rolling(CAST(:year AS INTEGER), CAST(:n_days AS INTEGER))"),
        params={"year": year, "n_days": n_days}
    )
    return [DailyCallCount(day=str(r.day), call_count=r.call_count, call_hours=r.call_hours) for r in result]


@router.get("/member_daily_calls")
def get_member_daily_calls(*, session: Session = Depends(get_session), year: int, n_days: int = 30, member: str | None = None) -> list[MemberDailyStats]:
    if member:
        result = session.exec(
            text(f"SELECT CAST(:year AS INTEGER) as unused, * FROM {_schema}.get_member_daily_call_count_rolling(CAST(:year AS INTEGER), CAST(:n_days AS INTEGER), :member)"),
            params={"year": year, "n_days": n_days, "member": member}
        )
        return [MemberDailyStats(
            day=str(r.day), id=0, name=member,
            call_count=r.call_count, call_count_total=r.call_count_total,
            call_count_percentage=r.call_count_percentage,
            call_hours=r.call_hours, call_hours_total=r.call_hours_total,
            call_hours_percentage=r.call_hours_percentage
        ) for r in result]
    else:
        result = session.exec(
            text(f"SELECT * FROM {_schema}.get_member_daily_call_count_rolling(CAST(:year AS INTEGER), CAST(:n_days AS INTEGER))"),
            params={"year": year, "n_days": n_days}
        )
        return [MemberDailyStats(
            day=str(r.day), id=r.id, name=r.name,
            call_count=r.call_count, call_count_total=r.call_count_total,
            call_count_percentage=r.call_count_percentage,
            call_hours=r.call_hours, call_hours_total=r.call_hours_total,
            call_hours_percentage=r.call_hours_percentage
        ) for r in result]


@router.get("/call_groups")
def get_call_groups(*, session: Session = Depends(get_session), year: int) -> list[CallGroupCount]:
    result = session.exec(
        text(f"SELECT * FROM {_schema}.get_call_group_count_by_year(CAST(:year AS INTEGER))"),
        params={"year": year}
    )
    return [CallGroupCount(group=r.group, call_count=r.call_count) for r in result]


@router.get("/call_groups_monthly")
def get_call_groups_monthly(*, session: Session = Depends(get_session), year: int) -> list[CallGroupMonthCount]:
    result = session.exec(
        text(f"SELECT * FROM {_schema}.get_call_group_count_by_month(CAST(:year AS INTEGER))"),
        params={"year": year}
    )
    return [CallGroupMonthCount(month=str(r.month), group=r.group, call_count=r.call_count) for r in result]


@router.get("/year_summary")
def get_year_summary(*, session: Session = Depends(get_session), year: int) -> YearSummary | None:
    result = session.exec(
        text(f"SELECT * FROM {_schema}.get_year_call_summary(CAST(:year AS INTEGER))"),
        params={"year": year}
    )
    row = result.first()
    if not row:
        return None
    return YearSummary(
        call_count=row.call_count or 0,
        aborted=row.aborted or 0,
        count_call_hours=row.count_call_hours or 0,
        count_crew_hours=row.count_crew_hours or 0,
        half_hours_members=row.half_hours_members
    )


@router.get("/member_year_stats")
def get_member_year_stats(*, session: Session = Depends(get_session), year: int) -> list[MemberYearStats]:
    result = session.exec(
        text(f"SELECT * FROM {_schema}.get_member_call_year_stats(CAST(:year AS INTEGER))"),
        params={"year": year}
    )
    return [MemberYearStats(
        member_name=r.member_name, call_count=r.call_count,
        call_hours=r.call_hours, call_count_perc=r.call_count_perc,
        call_hours_perc=r.call_hours_perc
    ) for r in result]


class MemberCallEntry(BaseModel):
    call_id: int
    start: str
    end: str
    subjects: str


@router.get("/member_calls/{member_id}")
def get_member_calls(*, session: Session = Depends(get_session), member_id: int, year: int | None = None) -> list[MemberCallEntry]:
    query = """
        SELECT c.id as call_id, c.start, c.end,
               string_agg(s.name, ' + ' ORDER BY cs.subject_order) as subjects
        FROM call c
        JOIN callmember cm ON cm.call_id = c.id
        LEFT JOIN callsubject cs ON cs.call_id = c.id
        LEFT JOIN subject s ON s.id = cs.subject_id
        WHERE cm.member_id = :member_id
    """
    params = {"member_id": member_id}
    if year:
        query += " AND extract(YEAR FROM c.start) = CAST(:year AS INTEGER)"
        params["year"] = year
    query += " GROUP BY c.id, c.start, c.end ORDER BY c.start DESC LIMIT 100"
    result = session.exec(text(query), params=params)
    return [MemberCallEntry(
        call_id=r.call_id, start=str(r.start), end=str(r.end), subjects=r.subjects or ''
    ) for r in result]


class YearRange(BaseModel):
    min_year: int
    max_year: int


class YearlySeriesEntry(BaseModel):
    year: int
    call_count: int
    call_hours: int
    crew_hours: int
    aborted: int
    avg_crew: float
    exercise_count: int
    exercise_hours: int
    exercise_attendance: int
    youth_count: int
    youth_hours: int
    youth_participants: int
    roster_members: int
    participating_members: int


class CallTimeProfileEntry(BaseModel):
    weekday: int
    hour: int
    call_count: int


class CallSubjectCount(BaseModel):
    name: str
    group: str
    call_count: int


class AbortReasonCount(BaseModel):
    reason: str
    call_count: int


class DurationBucket(BaseModel):
    bucket: str
    call_count: int


class LongestCall(BaseModel):
    call_id: int
    start: str
    minutes: int
    crew: int
    subjects: str


class QualificationCoverage(BaseModel):
    call_count: int
    with_leader: int
    with_driver: int
    with_both: int


class TurnoutBucket(BaseModel):
    bucket: str
    member_count: int


class ExerciseSummary(BaseModel):
    exercise_count: int
    exercise_hours: int
    attendance: int
    avg_attendance: float
    crew_hours: int


class ExerciseSession(BaseModel):
    exercise_id: int
    exercise_date: str
    subject: str
    minutes: int
    attendance: int


class ExerciseMemberStats(BaseModel):
    member_id: int
    member_name: str
    attended: int
    exercise_hours: int
    attended_perc: int


class YouthSummary(BaseModel):
    session_count: int
    session_hours: int
    participants: int
    avg_participants: float
    instructor_count: int
    instructor_hours: int


class YouthSession(BaseModel):
    exercise_id: int
    exercise_date: str
    subject: str
    minutes: int
    participants: int
    instructors: int


class CombinedMemberStats(BaseModel):
    member_id: int
    member_name: str
    call_count: int
    call_hours: int
    exercise_count: int
    exercise_hours: int
    youth_count: int
    youth_hours: int
    total_hours: int


class MembershipEntry(BaseModel):
    year: int
    roster_members: int
    retired_in_year: int
    participating_members: int


class MemberYearTrendEntry(BaseModel):
    year: int
    call_count: int
    call_hours: int
    call_count_perc: int
    exercise_count: int
    youth_count: int


@router.get("/year_range")
def get_year_range(*, session: Session = Depends(get_session)) -> YearRange:
    row = _call(session, "get_data_year_range").first()
    return YearRange(min_year=row.min_year, max_year=row.max_year)


@router.get("/yearly_series")
def get_yearly_series(*, session: Session = Depends(get_session), year: int,
                      years_back: int = DEFAULT_YEARS_BACK) -> list[YearlySeriesEntry]:
    rows = _call(session, "get_yearly_series", year_from=year - years_back + 1, year_to=year)
    return [YearlySeriesEntry(
        year=r.year, call_count=r.call_count, call_hours=r.call_hours, crew_hours=r.crew_hours,
        aborted=r.aborted, avg_crew=float(r.avg_crew), exercise_count=r.exercise_count,
        exercise_hours=r.exercise_hours, exercise_attendance=r.exercise_attendance,
        youth_count=r.youth_count, youth_hours=r.youth_hours, youth_participants=r.youth_participants,
        roster_members=r.roster_members, participating_members=r.participating_members
    ) for r in rows]


@router.get("/call_time_profile")
def get_call_time_profile(*, session: Session = Depends(get_session), year: int) -> list[CallTimeProfileEntry]:
    rows = _call(session, "get_call_time_profile", year=year)
    return [CallTimeProfileEntry(weekday=r.weekday, hour=r.hour, call_count=r.call_count) for r in rows]


@router.get("/call_subjects")
def get_call_subjects(*, session: Session = Depends(get_session), year: int, limit: int = 10) -> list[CallSubjectCount]:
    rows = _call(session, "get_call_subjects", year=year, limit=limit)
    return [CallSubjectCount(name=r.name, group=r.group, call_count=r.call_count) for r in rows]


@router.get("/abort_reasons")
def get_abort_reasons(*, session: Session = Depends(get_session), year: int) -> list[AbortReasonCount]:
    rows = _call(session, "get_abort_reasons", year=year)
    return [AbortReasonCount(reason=r.reason, call_count=r.call_count) for r in rows]


@router.get("/call_durations")
def get_call_durations(*, session: Session = Depends(get_session), year: int) -> list[DurationBucket]:
    rows = _call(session, "get_call_durations", year=year)
    return [DurationBucket(bucket=r.bucket, call_count=r.call_count) for r in rows]


@router.get("/longest_calls")
def get_longest_calls(*, session: Session = Depends(get_session), year: int, limit: int = 5) -> list[LongestCall]:
    rows = _call(session, "get_longest_calls", year=year, limit=limit)
    return [LongestCall(call_id=r.call_id, start=str(r.start), minutes=r.minutes,
                        crew=r.crew, subjects=r.subjects) for r in rows]


@router.get("/qualification_coverage")
def get_qualification_coverage(*, session: Session = Depends(get_session), year: int) -> QualificationCoverage:
    row = _call(session, "get_qualification_coverage", year=year).first()
    return QualificationCoverage(call_count=row.call_count, with_leader=row.with_leader,
                                 with_driver=row.with_driver, with_both=row.with_both)


@router.get("/turnout_distribution")
def get_turnout_distribution(*, session: Session = Depends(get_session), year: int) -> list[TurnoutBucket]:
    rows = _call(session, "get_turnout_distribution", year=year)
    return [TurnoutBucket(bucket=r.bucket, member_count=r.member_count) for r in rows]


@router.get("/exercise_summary")
def get_exercise_summary(*, session: Session = Depends(get_session), year: int) -> ExerciseSummary:
    row = _call(session, "get_exercise_summary", year=year).first()
    return ExerciseSummary(exercise_count=row.exercise_count, exercise_hours=row.exercise_hours,
                           attendance=row.attendance, avg_attendance=float(row.avg_attendance),
                           crew_hours=row.crew_hours)


@router.get("/exercise_sessions")
def get_exercise_sessions(*, session: Session = Depends(get_session), year: int) -> list[ExerciseSession]:
    rows = _call(session, "get_exercise_sessions", year=year)
    return [ExerciseSession(exercise_id=r.exercise_id, exercise_date=str(r.exercise_date),
                            subject=r.subject, minutes=r.minutes, attendance=r.attendance) for r in rows]


@router.get("/exercise_member_stats")
def get_exercise_member_stats(*, session: Session = Depends(get_session), year: int) -> list[ExerciseMemberStats]:
    rows = _call(session, "get_exercise_member_stats", year=year)
    return [ExerciseMemberStats(member_id=r.member_id, member_name=r.member_name, attended=r.attended,
                                exercise_hours=r.exercise_hours, attended_perc=r.attended_perc) for r in rows]


@router.get("/youth_summary")
def get_youth_summary(*, session: Session = Depends(get_session), year: int) -> YouthSummary:
    row = _call(session, "get_youth_summary", year=year).first()
    return YouthSummary(session_count=row.session_count, session_hours=row.session_hours,
                        participants=row.participants, avg_participants=float(row.avg_participants),
                        instructor_count=row.instructor_count, instructor_hours=row.instructor_hours)


@router.get("/youth_sessions")
def get_youth_sessions(*, session: Session = Depends(get_session), year: int) -> list[YouthSession]:
    rows = _call(session, "get_youth_sessions", year=year)
    return [YouthSession(exercise_id=r.exercise_id, exercise_date=str(r.exercise_date), subject=r.subject,
                         minutes=r.minutes, participants=r.participants, instructors=r.instructors) for r in rows]


@router.get("/combined_member_stats")
def get_combined_member_stats(*, session: Session = Depends(get_session), year: int) -> list[CombinedMemberStats]:
    rows = _call(session, "get_combined_member_stats", year=year)
    return [CombinedMemberStats(
        member_id=r.member_id, member_name=r.member_name, call_count=r.call_count, call_hours=r.call_hours,
        exercise_count=r.exercise_count, exercise_hours=r.exercise_hours, youth_count=r.youth_count,
        youth_hours=r.youth_hours, total_hours=r.total_hours) for r in rows]


@router.get("/membership")
def get_membership(*, session: Session = Depends(get_session), year: int,
                   years_back: int = DEFAULT_YEARS_BACK) -> list[MembershipEntry]:
    rows = _call(session, "get_membership", year_from=year - years_back + 1, year_to=year)
    return [MembershipEntry(year=r.year, roster_members=r.roster_members,
                            retired_in_year=r.retired_in_year,
                            participating_members=r.participating_members) for r in rows]


@router.get("/member_year_trend/{member_id}")
def get_member_year_trend(*, session: Session = Depends(get_session), member_id: int, year: int,
                          years_back: int = DEFAULT_YEARS_BACK) -> list[MemberYearTrendEntry]:
    rows = _call(session, "get_member_year_trend", member_id=member_id,
                 year_from=year - years_back + 1, year_to=year)
    return [MemberYearTrendEntry(year=r.year, call_count=r.call_count, call_hours=r.call_hours,
                                 call_count_perc=r.call_count_perc, exercise_count=r.exercise_count,
                                 youth_count=r.youth_count) for r in rows]


class MemberYearSummary(MemberYearStats):
    rank: int
    member_count: int


@router.get("/member_year_summary")
def get_member_year_summary(*, session: Session = Depends(get_session), year: int,
                            member: str) -> MemberYearSummary | None:
    ranked = sorted(get_member_year_stats(session=session, year=year),
                    key=lambda e: (-e.call_count, e.member_name))
    for position, entry in enumerate(ranked, start=1):
        if entry.member_name == member:
            return MemberYearSummary(**entry.model_dump(), rank=position, member_count=len(ranked))
    return None


class PresentationData(BaseModel):
    """Everything the presentation deck needs, in one payload, so no slide waits on a request."""
    year: int
    call_summary: YearSummary | None
    call_groups: list[CallGroupCount]
    call_groups_monthly: list[CallGroupMonthCount]
    call_subjects: list[CallSubjectCount]
    call_time_profile: list[CallTimeProfileEntry]
    call_durations: list[DurationBucket]
    qualification_coverage: QualificationCoverage
    exercise_summary: ExerciseSummary
    exercise_sessions: list[ExerciseSession]
    exercise_member_stats: list[ExerciseMemberStats]
    youth_summary: YouthSummary
    youth_sessions: list[YouthSession]
    combined_member_stats: list[CombinedMemberStats]
    turnout_distribution: list[TurnoutBucket]
    membership: list[MembershipEntry]
    yearly_series: list[YearlySeriesEntry]


@router.get("/presentation")
def get_presentation(*, session: Session = Depends(get_session), year: int,
                     years_back: int = DEFAULT_YEARS_BACK) -> PresentationData:
    return PresentationData(
        year=year,
        call_summary=get_year_summary(session=session, year=year),
        call_groups=get_call_groups(session=session, year=year),
        call_groups_monthly=get_call_groups_monthly(session=session, year=year),
        call_subjects=get_call_subjects(session=session, year=year, limit=10),
        call_time_profile=get_call_time_profile(session=session, year=year),
        call_durations=get_call_durations(session=session, year=year),
        qualification_coverage=get_qualification_coverage(session=session, year=year),
        exercise_summary=get_exercise_summary(session=session, year=year),
        exercise_sessions=get_exercise_sessions(session=session, year=year),
        exercise_member_stats=get_exercise_member_stats(session=session, year=year),
        youth_summary=get_youth_summary(session=session, year=year),
        youth_sessions=get_youth_sessions(session=session, year=year),
        combined_member_stats=get_combined_member_stats(session=session, year=year),
        turnout_distribution=get_turnout_distribution(session=session, year=year),
        membership=get_membership(session=session, year=year, years_back=years_back),
        yearly_series=get_yearly_series(session=session, year=year, years_back=years_back),
    )
