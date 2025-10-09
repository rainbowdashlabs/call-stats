from sqlmodel import SQLModel, Field, Relationship


class MemberYouthTraining(SQLModel, table=True):
    youth_training_id: int | None = Field(default=None, foreign_key="youthtraining.id", primary_key=True)
    member_id: int | None = Field(default=None, foreign_key="member.id", primary_key=True)


class YouthTraining(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    topic: str = Field(default=None)
    participants: int = Field(default=None)
    duration: int = Field(default=None)
    instructors: list["Member"] = Relationship(back_populates="youth_trainings", link_model=MemberYouthTraining)
