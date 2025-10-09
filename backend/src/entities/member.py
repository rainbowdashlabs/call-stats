from typing import Optional

from sqlmodel import SQLModel, Field, Relationship

from entities.call import CallMember
from entities.training import MemberTraining
from entities.youth import MemberYouthTraining


class MemberQualification(SQLModel, table=True):
    member_id: Optional[int] = Field(default=None, foreign_key="member.id", primary_key=True)
    qualification_id: Optional[int] = Field(default=None, foreign_key="qualification.id", primary_key=True)


class Qualification(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(default=None)
    since: int = Field(default=None, index=True, unique=True)
    members: list["Member"] = Relationship(back_populates="qualifications", link_model=MemberQualification)


class Member(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(default=None)
    qualifications: list[Qualification] = Relationship(back_populates="members", link_model=MemberQualification)
    calls: list["Call"] = Relationship(back_populates="members", link_model=CallMember)
    youth_trainings: list["YouthTraining"] = Relationship(back_populates="members", link_model=MemberYouthTraining)
    trainings: list["Training"] = Relationship(back_populates="members", link_model=MemberTraining)
