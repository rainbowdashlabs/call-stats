from fastapi import Depends, APIRouter
from sqlmodel import Session, select

from data import get_session
from entities.member import Member
from services.extra.errors import NotFoundError, ExistsError

router = APIRouter(prefix="/member",
                   tags=["members"])


@router.put("/{id}")
def update(*, session: Session = Depends(get_session), new: Member) -> Member:
    old = get_by_id(session=session, id=new.id)
    if old.name != new.name:
        stmt = select(Member).where(Member.name == new.name)
        result = session.exec(stmt).one_or_none()
        if result:
            raise ExistsError(result)
    session.add(new)
    session.commit()
    session.refresh(new)
    return new


@router.get("/{id}")
def get_by_id(*, session: Session = Depends(get_session), id: int) -> Member:
    statement = select(Member).where(Member.id == id)
    result = session.exec(statement).first()
    if not result:
        raise NotFoundError(Member)
    return result


@router.delete("/{id}")
def delete(*, session: Session = Depends(get_session), id: int) -> None:
    member = get_by_id(session=session, id=id)
    session.delete(member)
    session.commit()
