from datetime import datetime
from math import ceil

from fastapi import Depends, APIRouter
from sqlalchemy import func
from sqlmodel import Session, select

from data import get_session
from entities.call import Call, CallSubject, CreateCall, FullCall
from services.extra.page import Page
from services.member import get_by_id as get_member_by_id

router = APIRouter(prefix="/calls",
                   tags=["calls"])


@router.post("")
def create(*, session: Session = Depends(get_session), call: CreateCall) -> Call:
    created = Call(start=call.start, end=call.end, abort_reason=call.abort_reason, note=call.note)
    session.add(created)
    session.commit()
    session.refresh(created)
    for i, subject in enumerate(call.subjects):
        session.add(CallSubject(call_id=created.id, subject_id=subject, order=i))
    for member in call.members:
        created.members.append(get_member_by_id(session=session, id=member))
    session.commit()
    return created


@router.get("")
def get_all(*, session: Session = Depends(get_session), page: int = 1, per_page: int = 100) -> dict:
    stmt = select(Call).order_by(Call.start.desc()).limit(per_page).offset((page - 1) * per_page)
    res = session.exec(stmt)
    res = [FullCall.convert(e) for e in res]
    stmt = select(func.count(Call.id)).select_from(Call)
    count: int = (session.exec(stmt)).first()
    count = ceil(count / float(per_page))
    return Page(page=page, size=per_page, pages=count, entries=res).model_dump()


@router.get("/search")
def search(*, session: Session = Depends(get_session), start: datetime = None, end: datetime = None, page: int = 1,
           per_page: int = 100) -> list[Call]:
    stmt = select(Call)
    if start:
        stmt = stmt.where(Call.start >= start)
    if end:
        stmt = stmt.where(Call.end >= end)
    stmt = stmt.order_by(Call.start.desc()).limit(per_page).offset((page - 1) * per_page)
    return list(session.exec(stmt))
