from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import selectinload
from sqlmodel import Session
from sqlmodel import select

from data import get_session
from entities.call import Call, FullCall, CallSubject, UpdateCall
from entities.member import SimpleMember
from services.extra.errors import NotFoundError
from services.member import get_by_id as get_member_by_id
from services.subject import get_by_id as get_subject_by_id

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


@router.delete("/member/{call_id}")
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
def update(*, session: Session = Depends(get_session), call: UpdateCall) -> FullCall:
    existing = _get_call_by_id(session=session, id=call.id)
    existing.start = call.start
    existing.end = call.end
    existing.additional = call.additional
    existing.abort_reason = call.abort_reason
    existing.note = call.note

    subject_ids = list(dict.fromkeys(call.subjects))
    for subject_id in subject_ids:
        get_subject_by_id(session=session, id=subject_id)
    links = {link.subject_id: link for link in existing.subjects}
    for subject_id, link in links.items():
        if subject_id not in subject_ids:
            session.delete(link)
    for order, subject_id in enumerate(subject_ids):
        link = links.get(subject_id)
        if link:
            link.subject_order = order
        else:
            session.add(CallSubject(call_id=existing.id, subject_id=subject_id, subject_order=order))

    member_ids = list(dict.fromkeys(call.members))
    existing.members = [get_member_by_id(session=session, id=member_id) for member_id in member_ids]

    session.add(existing)
    session.commit()
    session.expire_all()
    return FullCall.convert(_get_call_by_id(session=session, id=call.id))


@router.delete("/{id}")
def delete(*, session: Session = Depends(get_session), id: int):
    call = _get_call_by_id(session=session, id=id)
    session.delete(call)
    session.commit()
