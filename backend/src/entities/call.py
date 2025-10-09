from typing import Optional

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import SQLModel, Field, Relationship


class CallMember(SQLModel, table=True):
    call_id: Optional[int] = Field(default=None, foreign_key="call.id", primary_key=True)
    member_id: Optional[int] = Field(default=None, foreign_key="member.id", primary_key=True)

class CallSubject(SQLModel, table=True):
    call_id: int | None = Field(default=None, foreign_key="call.id", primary_key=True)
    subject_id: int | None = Field(default=None, foreign_key="subject.id", primary_key=True)

class Subject(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    calls : list["Call"] = Relationship(back_populates="subjects", link_model=CallSubject)

class Call(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    subjects: list[Subject] = Relationship(back_populates="calls", link_model=CallSubject)
    call_start: int = Field(default=None, index=True, unique=True)
    call_end: int = Field(default=None, index=True, unique=True)
    duration: int = Field(default_factory=lambda data: data["call_end"] - data["call_start"])
    abort_reason: str = Field(default=None)
    members: list["Member"] = Relationship(back_populates="calls", link_model=CallMember)
