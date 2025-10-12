import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class MemberExercise(SQLModel, table=True):
    exercise_id: Optional[int] = Field(default=None, foreign_key="exercise.id", primary_key=True)
    member_id: Optional[int] = Field(default=None, foreign_key="member.id", primary_key=True)


class Exercise(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    subject: str = Field(default=None)
    date: datetime.date = Field()
    duration: int = Field(default=None)
    members: list["Member"] = Relationship(back_populates="exercises",
                                           link_model=MemberExercise)
