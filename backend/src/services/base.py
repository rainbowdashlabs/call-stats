from sqlmodel import Session, select

from data import engine
from services.extra.errors import NotFoundError


def get_by_id(id: int, cls: type):
    with Session(engine) as session:
        statement = select(cls).where(cls.id == id)
        result = session.exec(statement).first()
        if not result:
            raise NotFoundError(cls)
    return result
