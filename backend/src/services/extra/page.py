from typing import TypeVar, Generic

from pydantic import BaseModel

T = TypeVar("Type")

class Page(BaseModel, Generic[T]):
    page: int
    size: int
    pages: int
    entries: list[T]

    class Config:
        arbitrary_types_allowed = True
