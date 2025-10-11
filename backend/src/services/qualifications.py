from sqlmodel import Session, select

from data import engine
from entities.qualification import Qualification
from services.extra.errors import NotFoundError
from web.app import router


@router.post("/qualifications")
def create(name: str) -> Qualification:
    qualification = Qualification(name=name)
    with Session(engine) as session:
        session.add(qualification)
        session.commit()
        session.refresh(qualification)
        return qualification


@router.get("/qualifications")
def get_all() -> list[Qualification]:
    with Session(engine) as session:
        stmt = select(Qualification)
        return list(session.exec(stmt).all())


@router.get("/qualifications/search")
def get_by_name(name: str) -> Qualification:
    with Session(engine) as session:
        stmt = select(Qualification).where(Qualification.name == name)
        qualification = session.exec(stmt).one_or_none()
        if not qualification:
            raise NotFoundError(Qualification)
        return qualification
