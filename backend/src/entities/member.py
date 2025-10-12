from datetime import date
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship

from entities.call import CallMember
from entities.exercise import MemberExercise
from entities.youth import MemberYouthExercise


class MemberQualification(SQLModel, table=True):
    member_id: Optional[int] = Field(default=None, primary_key=True, foreign_key="member.id")
    member: "Member" = Relationship(back_populates="qualifications")
    qualification_id: int = Field(default=None, primary_key=True, foreign_key="qualification.id")
    qualification: "Qualification" = Relationship(back_populates="members", )
    since: date = Field(default=None)


class Member(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(default=None)
    active: bool = Field(default=True)
    qualifications: list[MemberQualification] = Relationship(back_populates="member",
                                                             cascade_delete=True)
    calls: list["Call"] = Relationship(back_populates="members",
                                       link_model=CallMember)
    youth_exercise: list["YouthExercise"] = Relationship(back_populates="instructors",
                                                         link_model=MemberYouthExercise)
    exercises: list["Exercise"] = Relationship(back_populates="members",
                                               link_model=MemberExercise)
