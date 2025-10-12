from fastapi import Depends, APIRouter
from sqlmodel import Session
from sqlmodel import select

from data import get_session
from entities.youth import YouthExercise
from services.extra.errors import NotFoundError
from services.member import get_by_id as get_member_by_id

router = APIRouter(prefix="/youth_exercise",
                   tags=["youth_exercises"])


@router.delete("/member/{exercise_id}")
def add_members(*, session: Session = Depends(get_session), exercise_id: int, member_ids: list[int]):
    exercise = get_by_id(session=session, id=exercise_id)
    for member_ids in member_ids:
        member = get_member_by_id(session=session, id=member_ids)
        exercise.members.append(member)
    session.add(exercise)
    session.commit()


@router.delete("/member/{exercise_id}")
def remove_members(*, session: Session = Depends(get_session), exercise_id: int, member_ids: list[int]):
    exercise = get_by_id(session=session, id=exercise_id)
    for member_ids in member_ids:
        member = get_member_by_id(session=session, id=member_ids)
        exercise.members.remove(member)
    session.add(exercise)
    session.commit()


@router.get("/{id}")
def get_by_id(*, session: Session = Depends(get_session), id: int) -> YouthExercise:
    stmt = select(YouthExercise).where(YouthExercise.id == id)
    exercise = session.exec(stmt).one_or_none()
    if not exercise:
        raise NotFoundError(YouthExercise)
    return exercise


@router.delete("/{id}")
def delete(*, session: Session = Depends(get_session), id: int):
    stmt = select(YouthExercise).where(YouthExercise.id == id)
    exercise = session.exec(stmt).one_or_none()
    if not exercise:
        raise NotFoundError(YouthExercise)
    session.delete(exercise)
    session.commit()
