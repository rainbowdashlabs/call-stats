from typing import TypeVar, Generic

from pydantic import BaseModel

Type = TypeVar("Type")

class Page(BaseModel, Generic[Type]):
    page: int
    size: int
    pages: int
    entries: list[Type]

    class Config:
        arbitrary_types_allowed = True
