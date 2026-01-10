from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import selectinload
from sqlmodel import Session
from sqlmodel import select

from data import get_session
from entities.call import Call, FullCall, CallSubject
from entities.member import SimpleMember
from services.extra.errors import NotFoundError
from services.member import get_by_id as get_member_by_id

router = APIRouter(prefix="/call",
                   tags=["calls"])

FullCall.model_rebuild(_types_namespace={"SimpleMember": SimpleMember})

@router.patch("/member/{call_id}")
def add_members(*, session: Session = Depends(get_session), call_id: int, member_ids: list[int]):
    call = _get_call_by_id(session=session, id=call_id)
    for member_ids in member_ids:
        member = get_member_by_id(session=session, id=member_ids)
        call.members.append(member)
    session.add(call)
    session.commit()


@router.patch("/member/{call_id}")
def remove_members(*, session: Session = Depends(get_session), call_id: int, member_ids: list[int]):
    call = _get_call_by_id(session=session, id=call_id)
    for member_ids in member_ids:
        member = get_member_by_id(session=session, id=member_ids)
        call.members.remove(member)
    session.add(call)
    session.commit()


def _get_call_by_id(*, session: Session, id: int) -> Call:
    statement = (
        select(Call)
        .where(Call.id == id)
        .options(
            selectinload(Call.subjects).selectinload(CallSubject.subject),
            selectinload(Call.members)
        )
    )
    result = session.exec(statement).first()
    if not result:
        raise NotFoundError(Call)
    return result


@router.get("/{id}")
def get_by_id(*, session: Session = Depends(get_session), id: int) -> FullCall:
    return FullCall.convert(_get_call_by_id(session=session, id=id))


@router.patch("")
def update(*, session: Session = Depends(get_session), new: Call):
    old = _get_call_by_id(session=session, id=new.id)
    if old.start != new.start:
        raise ValueError("Start date cannot be changed")
    session.add(new)
    session.commit()
    session.refresh(new)


@router.delete("/{id}")
def delete(*, session: Session = Depends(get_session), id: int):
    call = _get_call_by_id(session=session, id=id)
    session.delete(call)
    session.commit()
