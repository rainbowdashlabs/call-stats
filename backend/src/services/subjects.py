from sqlmodel import Session, select

from data import engine
from entities.call import Subject
from web.app import router


@router.post("/subjects")
def create(subject: Subject) -> Subject:
    with Session(engine) as session:
        session.add(subject)
        session.commit()
        session.refresh(subject)
        return subject


@router.get("/subjects")
def get_all() -> list[Subject]:
    with Session(engine) as session:
        stmt = select(Subject)
        return list(session.exec(stmt))
