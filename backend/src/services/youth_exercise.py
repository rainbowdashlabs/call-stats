from fastapi import Depends, APIRouter
from sqlalchemy.orm import selectinload
from sqlmodel import Session
from sqlmodel import select

from data import get_session
from entities.youth import YouthExercise, FullYouthExercise
from entities.member import SimpleMember
from services.extra.errors import NotFoundError
from services.member import get_by_id as get_member_by_id

router = APIRouter(prefix="/youth_exercise",
                   tags=["youth_exercises"])

FullYouthExercise.model_rebuild(_types_namespace={"SimpleMember": SimpleMember})


@router.patch("/member/{exercise_id}")
def add_members(*, session: Session = Depends(get_session), exercise_id: int, member_ids: list[int]):
    exercise = _get_youth_exercise_by_id(session=session, id=exercise_id)
    for member_ids in member_ids:
        member = get_member_by_id(session=session, id=member_ids)
        exercise.instructors.append(member)
    session.add(exercise)
    session.commit()


@router.delete("/member/{exercise_id}")
def remove_members(*, session: Session = Depends(get_session), exercise_id: int, member_ids: list[int]):
    exercise = _get_youth_exercise_by_id(session=session, id=exercise_id)
    for member_ids in member_ids:
        member = get_member_by_id(session=session, id=member_ids)
        exercise.instructors.remove(member)
    session.add(exercise)
    session.commit()


def _get_youth_exercise_by_id(session: Session, id: int) -> YouthExercise:
    stmt = (
        select(YouthExercise)
        .where(YouthExercise.id == id)
        .options(selectinload(YouthExercise.instructors))
    )
    exercise = session.exec(stmt).one_or_none()
    if not exercise:
        raise NotFoundError(YouthExercise)
    return exercise


@router.get("/{id}")
def get_by_id(*, session: Session = Depends(get_session), id: int) -> FullYouthExercise:
    return FullYouthExercise.convert(_get_youth_exercise_by_id(session, id))


@router.delete("/{id}")
def delete(*, session: Session = Depends(get_session), id: int):
    exercise = _get_youth_exercise_by_id(session, id)
    session.delete(exercise)
    session.commit()
