from typing import Union

from pydantic import BaseModel, RootModel
from sqlmodel import Session, select

from data import engine
from services.extra.errors import NotFoundError

class MultiSelectItem(BaseModel):
    label: str
    value: Union[int, str]

class MultiSelectGroup(BaseModel):
    label: str
    items: list[MultiSelectItem]


def get_by_id(id: int, cls: type):
    with Session(engine) as session:
        statement = select(cls).where(cls.id == id)
        result = session.exec(statement).first()
        if not result:
            raise NotFoundError(cls)
    return result
