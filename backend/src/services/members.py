from datetime import datetime, timedelta

from fastapi import Depends, APIRouter
from sqlalchemy import func
from sqlmodel import Session, select, or_

from data import get_session
from entities.call import Call, CallMember
from entities.member import Member, MemberUsage
from services.extra.errors import ExistsError, NotFoundError

router = APIRouter(prefix="/members",
                   tags=["members"])

USAGE_WINDOW_DAYS = 365


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


def _usage_by_member(session: Session) -> dict[int, int]:
    cutoff = datetime.now() - timedelta(days=USAGE_WINDOW_DAYS)
    stmt = (select(CallMember.member_id, func.count())
            .join(Call, Call.id == CallMember.call_id)
            .where(Call.start >= cutoff)
            .group_by(CallMember.member_id))
    return {member_id: count for member_id, count in session.exec(stmt)}


@router.get("")
def get_all(*, session: Session = Depends(get_session), filter_active: bool = False, active_after: datetime = None) -> list[MemberUsage]:
    if active_after and filter_active:
        stmt = select(Member).where(or_(Member.retired == None, Member.retired > active_after))
    elif filter_active:
        stmt = select(Member).where(Member.retired == None)
    else:
        stmt = select(Member)
    result = session.exec(stmt).all()
    usage = _usage_by_member(session)
    return sorted([MemberUsage(id=m.id, name=m.name, joined=m.joined, retired=m.retired,
                              usage=usage.get(m.id, 0))
                   for m in result], key=lambda x: x.name)


@router.get("/search")
def search(*, session: Session = Depends(get_session), name: str) -> Member:
    stmt = select(Member).where(Member.name == name)
    result = session.exec(stmt).one_or_none()
    if not result:
        raise NotFoundError(Member)
    return result
