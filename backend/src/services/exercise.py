from fastapi import Depends, APIRouter
from sqlmodel import Session
from sqlmodel import select

from data import get_session
from entities.exercise import Exercise
from services.extra.errors import NotFoundError
from services.member import get_by_id as get_member_by_id

router = APIRouter(prefix="/exercise",
                   tags=["exercises"])


@router.put("/{exercise_id}/member")
def add_members(*, session: Session = Depends(get_session), exercise_id: int, member_ids: list[int]):
    exercise = get_by_id(session=session, id=exercise_id)
    for member_ids in member_ids:
        member = get_member_by_id(session=session, id=member_ids)
        exercise.members.append(member)
    session.add(exercise)
    session.commit()


@router.delete("/{exercise_id}/member")
def remove_members(*, session: Session = Depends(get_session), exercise_id: int, member_ids: list[int]):
    exercise = get_by_id(session=session, id=exercise_id)
    for member_ids in member_ids:
        member = get_member_by_id(session=session, id=member_ids)
        exercise.members.remove(member)
    session.add(exercise)
    session.commit()


@router.get("/{id}")
def get_by_id(*, session: Session = Depends(get_session), id: int) -> Exercise:
    stmt = select(Exercise).where(Exercise.id == id)
    exercise = session.exec(stmt).one_or_none()
    if not exercise:
        raise NotFoundError(Exercise)
    return exercise


@router.delete("/{id}")
def delete(*, session: Session = Depends(get_session), id: int):
    stmt = select(Exercise).where(Exercise.id == id)
    exercise = session.exec(stmt).one_or_none()
    if not exercise:
        raise NotFoundError(Exercise)
    session.delete(exercise)
    session.commit()
