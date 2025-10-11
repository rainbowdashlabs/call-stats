from sqlmodel import Session, select

from data import engine
from entities.member import Member
from services.extra.errors import ExistsError, NotFoundError
from web.app import router


@router.post("/members")
def create(member: Member) -> Member:
    with Session(engine) as session:
        statement = select(Member).where(Member.name == member.name)
        result = session.exec(statement).one_or_none()
        if result:
            raise ExistsError(result)
        session.add(member)
        session.commit()
        session.refresh(member)
    return member


@router.get("/members")
def get_all(filter_active: bool = False) -> list[Member]:
    with Session(engine) as session:
        if filter_active:
            stmt = select(Member).where(Member.active == True)
        else:
            stmt = select(Member)
        result = session.exec(stmt).all()
    return list(result)

@router.get("/members/search")
def search(name: str) -> Member:
    with Session(engine) as session:
        stmt = select(Member).where(Member.name == name)
        result = session.exec(stmt).one_or_none()
        if not result:
            raise NotFoundError(Member)
    return result
