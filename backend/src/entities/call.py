from typing import Optional

from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


class CallMember(SQLModel, table=True):
    call_id: Optional[int] = Field(default=None, foreign_key="call.id", primary_key=True)
    member_id: Optional[int] = Field(default=None, foreign_key="member.id", primary_key=True)

class CallSubject(SQLModel, table=True):
    call_id: int | None = Field(default=None, foreign_key="call.id", primary_key=True)
    subject_id: int | None = Field(default=None, foreign_key="subject.id", primary_key=True)

class Subject(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    group: str
    name: str
    calls : list["Call"] = Relationship(back_populates="subjects", link_model=CallSubject, cascade_delete=True)

class Call(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    subjects: list[Subject] = Relationship(back_populates="calls", link_model=CallSubject, cascade_delete=True)
    start: datetime = Field(default=None, index=True)
    end: datetime = Field(default=None, index=True)
    duration: int = Field(default_factory=lambda data: data["call_end"] - data["call_start"])
    abort_reason: Optional[str] = Field(default=None)
    note: Optional[str] = Field(default=None)
    members: list["Member"] = Relationship(back_populates="calls", link_model=CallMember, cascade_delete=True)
