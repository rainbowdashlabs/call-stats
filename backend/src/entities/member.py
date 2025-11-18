from datetime import date
from typing import Optional

from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship

from data.types import EpochDate
from entities.call import CallMember
from entities.exercise import MemberExercise
from entities.youth import MemberYouthExercise


class MemberQualification(SQLModel, table=True):
    member_id: Optional[int] = Field(default=None, primary_key=True, foreign_key="member.id")
    member: "Member" = Relationship(back_populates="qualifications")
    qualification_id: int = Field(default=None, primary_key=True, foreign_key="qualification.id")
    qualification: "Qualification" = Relationship(back_populates="members", )
    since: Optional[date] = Field(default=None, sa_type=EpochDate)


class Member(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(default=None)
    retired: Optional[date] = Field(default=None, sa_type=EpochDate)
    qualifications: list[MemberQualification] = Relationship(back_populates="member",
                                                             cascade_delete=True)
    calls: list["Call"] = Relationship(back_populates="members",
                                       link_model=CallMember)
    youth_exercise: list["YouthExercise"] = Relationship(back_populates="instructors",
                                                         link_model=MemberYouthExercise)
    exercises: list["Exercise"] = Relationship(back_populates="members",
                                               link_model=MemberExercise)

    def update(self, member: "Member"):
        self.name = member.name
        self.retired = member.retired

class SimpleMember(BaseModel):
    id: int
    name: str

    @staticmethod
    def convert(member: Member) -> "SimpleMember":
        return SimpleMember(id=member.id,
                            name=member.name)
