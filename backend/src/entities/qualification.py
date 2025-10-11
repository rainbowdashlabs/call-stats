from sqlmodel import SQLModel, Field, Relationship


class Qualification(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(default=None)
    members: list["MemberQualification"] = Relationship(back_populates="qualification", cascade_delete=True)
