from fastapi import Depends, APIRouter
from sqlmodel import Session, select

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
def get_all(*, session: Session = Depends(get_session), filter_active: bool = False) -> list[Member]:
    if filter_active:
        stmt = select(Member).where(Member.active == True)
    else:
        stmt = select(Member)
    result = session.exec(stmt).all()
    return list(result)


@router.get("/search")
def search(*, session: Session = Depends(get_session), name: str) -> Member:
    stmt = select(Member).where(Member.name == name)
    result = session.exec(stmt).one_or_none()
    if not result:
        raise NotFoundError(Member)
    return result
