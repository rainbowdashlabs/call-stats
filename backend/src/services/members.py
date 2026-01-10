from datetime import datetime

from fastapi import Depends, APIRouter
from sqlmodel import Session, select, or_

from data import get_session
from entities.member import Member
from services.extra.errors import ExistsError, NotFoundError

router = APIRouter(prefix="/members",
                   tags=["members"])


@router.post("")
def create(*, session: Session = Depends(get_session), member: Member) -> Member:
    statement = select(Member).where(Member.name == member.name)
    result = session.exec(statement).one_or_none()
    if result:
        raise ExistsError(result)
    session.add(member)
    session.commit()
    session.refresh(member)
    return member


@router.get("")
def get_all(*, session: Session = Depends(get_session), filter_active: bool = False, active_after: datetime = None) -> list[Member]:
    if active_after and filter_active:
        stmt = select(Member).where(or_(Member.retired == None, Member.retired > active_after))
    elif filter_active:
        stmt = select(Member).where(Member.retired == None)
    else:
        stmt = select(Member)
    result = session.exec(stmt).all()
    return sorted(list(result), key=lambda x: x.name)


@router.get("/search")
def search(*, session: Session = Depends(get_session), name: str) -> Member:
    stmt = select(Member).where(Member.name == name)
    result = session.exec(stmt).one_or_none()
    if not result:
        raise NotFoundError(Member)
    return result
