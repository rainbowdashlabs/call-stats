from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class MemberTraining(SQLModel, table=True):
    training_id: Optional[int] = Field(default=None, foreign_key="training.id", primary_key=True)
    member_id: Optional[int] = Field(default=None, foreign_key="member.id", primary_key=True)


class Training(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    subject: str
    date: int = Field(default=None)
    duration: int = Field(default=None)
    members: list["Member"] = Relationship(back_populates="trainings", link_model=MemberTraining)
