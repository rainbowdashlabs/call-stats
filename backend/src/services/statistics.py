import os

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session
from sqlalchemy import text

from data import get_session

router = APIRouter(prefix="/statistics", tags=["statistics"])

_schema = os.getenv("DB_SCHEMA", "public")


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
