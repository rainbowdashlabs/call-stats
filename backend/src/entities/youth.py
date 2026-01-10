from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship
from datetime import date
from data.types import EpochDate


class MemberYouthExercise(SQLModel, table=True):
    youth_training_id: int | None = Field(default=None, foreign_key="youthexercise.id", primary_key=True)
    member_id: int | None = Field(default=None, foreign_key="member.id", primary_key=True)


class YouthExercise(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    subject: str
    exercise_date: date = Field(default=None, sa_type=EpochDate)
    duration: int = Field(default=None)
    participants: int = Field(default=None)
    instructors: list["Member"] = Relationship(back_populates="youth_exercise", link_model=MemberYouthExercise)


class FullYouthExercise(BaseModel):
    id: int
    subject: str
    exercise_date: date
    duration: int
    participants: int
    instructors: list["SimpleMember"]

    @staticmethod
    def convert(exercise: YouthExercise):
        from entities.member import SimpleMember
        return FullYouthExercise(id=exercise.id,
                                 subject=exercise.subject,
                                 exercise_date=exercise.exercise_date,
                                 duration=exercise.duration,
                                 participants=exercise.participants,
                                 instructors=[SimpleMember.convert(e) for e in exercise.instructors])
