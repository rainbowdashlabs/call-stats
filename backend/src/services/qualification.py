from sqlmodel import Session, select

from data import engine
from entities.qualification import Qualification
from services.extra.errors import NameExistsError, NotFoundError
from services.qualifications import get_by_name
from web.app import router


@router.get("/qualification/{id}")
def get_by_id(id: int) -> Qualification:
    with Session(engine) as session:
        stmt = select(Qualification).where(Qualification.id == id)
        qualification = session.exec(stmt).one_or_none()
        if not qualification:
            raise NotFoundError(Qualification)
        return qualification


@router.delete("/qualification/{id}")
def delete(id: int):
    qualification = get_by_id(id)
    with Session(engine) as session:
        session.delete(qualification)
        session.commit()


@router.patch("/qualification/{id}")
def update(new: Qualification) -> Qualification:
    with Session(engine) as session:
        old = get_by_id(new.id)
        if old.name != new.name:
            exists = get_by_name(new.name)
            if exists:
                raise NameExistsError(exists)
        session.add(new)
        session.commit()
        session.refresh(new)
        return new
