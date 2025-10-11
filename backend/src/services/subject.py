from sqlmodel import Session, select

from data import engine
from entities.call import Subject
from services.extra.errors import NotFoundError
from web.app import router


@router.get("/subject/{id}")
def get_by_id(id: int) -> Subject:
    with Session(engine) as session:
        stmt = select(Subject).where(Subject.id == id)
        subject = session.exec(stmt).one_or_none()
        if subject is None:
            raise NotFoundError(Subject)
        return subject


@router.delete("/subject/{id}")
def delete(id: int) -> None:
    with Session(engine) as session:
        subject = get_by_id(id)
        session.delete(subject)
        session.commit()
