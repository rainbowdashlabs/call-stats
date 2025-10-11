from sqlmodel import Session
from sqlmodel import select

from data import engine
from entities.exercise import Exercise
from services.extra.errors import NotFoundError
from services.member import get_by_id as get_member_by_id
from web.app import router


@router.delete("/exercise/member/{exercise_id}")
def add_members(exercise_id: int, member_id: list[int]):
    with Session(engine) as session:
        exercise = get_by_id(exercise_id)
        for member_id in member_id:
            member = get_member_by_id(member_id)
            exercise.members.append(member)
        session.add(exercise)
        session.commit()


@router.delete("/exercise/member/{exercise_id}")
def remove_members(exercise_id: int, member_id: list[int]):
    with Session(engine) as session:
        exercise = get_by_id(exercise_id)
        for member_id in member_id:
            member = get_member_by_id(member_id)
            exercise.members.remove(member)
        session.add(exercise)
        session.commit()


@router.get("/exercise/{id}")
def get_by_id(id: int) -> Exercise:
    with Session(engine) as session:
        stmt = select(Exercise).where(Exercise.id == id)
        exercise = session.exec(stmt).one_or_none()
        if not exercise:
            raise NotFoundError(Exercise)
        return exercise


@router.delete("/exercise/{id}")
def delete(id: int):
    with Session(engine) as session:
        stmt = select(Exercise).where(Exercise.id == id)
        exercise = session.exec(stmt).one_or_none()
        if not exercise:
            raise NotFoundError(Exercise)
        session.delete(exercise)
        session.commit()
