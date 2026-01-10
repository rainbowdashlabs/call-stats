from datetime import date
from typing import Optional

from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship

from data.types import EpochDate


class MemberExercise(SQLModel, table=True):
    exercise_id: Optional[int] = Field(default=None, foreign_key="exercise.id", primary_key=True)
    member_id: Optional[int] = Field(default=None, foreign_key="member.id", primary_key=True)


class Exercise(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    subject: str = Field(default=None)
    exercise_date: date = Field(default=None, sa_type=EpochDate)
    duration: int = Field(default=None)
    members: list["Member"] = Relationship(back_populates="exercises",
                                           link_model=MemberExercise)


class FullExercise(BaseModel):
    id: int
    subject: str
    exercise_date: date
    duration: int
    members: list["SimpleMember"]

    @staticmethod
    def convert(exercise: Exercise):
        from entities.member import SimpleMember
        return FullExercise(id=exercise.id,
                            subject=exercise.subject,
                            exercise_date=exercise.exercise_date,
                            duration=exercise.duration,
                            members=[SimpleMember.convert(e) for e in exercise.members])
