from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship

mapper = lambda data: data["end"] - data["start"]


class CallMember(SQLModel, table=True):
    call_id: Optional[int] = Field(default=None, foreign_key="call.id", primary_key=True)
    member_id: Optional[int] = Field(default=None, foreign_key="member.id", primary_key=True)


class CallSubject(SQLModel, table=True):
    call_id: int | None = Field(default=None, foreign_key="call.id", primary_key=True)
    subject_id: int | None = Field(default=None, foreign_key="subject.id", primary_key=True)
    order: int = Field(default=None)

    call: "Call" = Relationship(back_populates="subjects")
    subject: "Subject" = Relationship(back_populates="calls")


class Subject(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    group: str
    name: str
    calls: list[CallSubject] = Relationship(back_populates="subject")


class Call(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    subjects: list[CallSubject] = Relationship(back_populates="call")
    start: datetime = Field(default=None, index=True)
    end: datetime = Field(default=None, index=True)
    abort_reason: Optional[str] = Field(default=None)
    note: Optional[str] = Field(default=None)
    members: list["Member"] = Relationship(back_populates="calls", link_model=CallMember)


class CreateCall(BaseModel):
    subjects: list[int]
    start: datetime
    end: datetime
    abort_reason: Optional[str]
    note: Optional[str]
    members: list[int]
