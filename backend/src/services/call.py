from sqlmodel import Session

from data import engine
from entities.call import Call
from services.extra.errors import NotFoundError
from services.member import get_by_id as get_member_by_id
from web.app import router
from sqlmodel import select


@router.patch("/call/member/{call_id}")
def add_members(call_id: int, member_id: list[int]):
    with Session(engine) as session:
        call = get_by_id(call_id)
        for member_id in member_id:
            member = get_member_by_id(member_id)
            call.members.append(member)
        session.add(call)
        session.commit()


@router.patch("/call/member/{call_id}")
def remove_members(call_id: int, member_id: list[int]):
    with Session(engine) as session:
        call = get_by_id(call_id)
        for member_id in member_id:
            member = get_member_by_id(member_id)
            call.members.remove(member)
        session.add(call)
        session.commit()

@router.get("/call/{id}")
def get_by_id(id: int):
    with Session(engine) as session:
        statement = select(Call).where(Call.id == id)
        result = session.exec(statement).first()
        if not result:
            raise NotFoundError(Call)
    return result


@router.patch("/call")
def update(new: Call):
    with Session(engine) as session:
        old = get_by_id(new.id)
        if old.start != new.start:
            raise ValueError("Start date cannot be changed")
        session.add(new)
        session.commit()
        session.refresh(new)


@router.delete("/call/{id}")
def delete(id: int):
    with Session(engine) as session:
        call = get_by_id(id)
        session.delete(call)
        session.commit()
