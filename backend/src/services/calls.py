from datetime import datetime

from sqlmodel import Session, select

from data import engine
from entities.call import Call
from web.app import router


@router.post("/calls")
def create(call: Call):
    with Session(engine) as session:
        session.add(call)
        session.commit()


@router.get("/calls")
def get_all(page: int = 1, per_page: int = 100) -> list[Call]:
    with Session(engine) as session:
        stmt = select(Call).order_by(Call.start.desc()).limit(per_page).offset((page - 1) * per_page)
        return list(session.exec(stmt))


@router.get("/calls/search")
def get_all(start: datetime = None, end: datetime = None, page: int = 1, per_page: int = 100) -> list[Call]:
    with Session(engine) as session:
        stmt = select(Call)
        if start:
            stmt = stmt.where(Call.start >= start)
        if end:
            stmt = stmt.where(Call.end >= end)
        stmt = stmt.order_by(Call.start.desc()).limit(per_page).offset((page - 1) * per_page)
        return list(session.exec(stmt))
