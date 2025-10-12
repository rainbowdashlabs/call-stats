import datetime

from sqlmodel import SQLModel, Field, Relationship


class MemberYouthExercise(SQLModel, table=True):
    youth_training_id: int | None = Field(default=None, foreign_key="youthexercise.id", primary_key=True)
    member_id: int | None = Field(default=None, foreign_key="member.id", primary_key=True)


class YouthExercise(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    subject: str
    date: datetime.date = Field(default=None)
    duration: int = Field(default=None)
    participants: int = Field(default=None)
    instructors: list["Member"] = Relationship(back_populates="youth_exercise", link_model=MemberYouthExercise)
