from sqlmodel import Session, select

from data import engine
from entities.member import Member, MemberQualification
from services.extra.errors import NotFoundError, ExistsError
from web.app import router


@router.put("/member/{id}")
def update(new: Member) -> Member:
    with Session(engine) as session:
        old = get_by_id(new.id)
        if old.name != new.name:
            try:
                exists = search(new.name)
            except NotFoundError:
                pass
            else:
                raise ExistsError(exists)
        session.add(new)
        session.commit()
        session.refresh(new)
        return new


@router.get("/member/{id}")
def get_by_id(id: int) -> Member:
    with Session(engine) as session:
        statement = select(Member).where(Member.id == id)
        result = session.exec(statement).first()
        if not result:
            raise NotFoundError(Member)
    return result


@router.delete("/member/{id}")
def delete(id: int) -> None:
    with Session(engine) as session:
        member = get_by_id(id)
        session.delete(member)
        session.commit()


