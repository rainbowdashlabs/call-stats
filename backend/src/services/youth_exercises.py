from fastapi import Depends, APIRouter
from sqlmodel import Session, select

from data import get_session
from entities.youth import YouthExercise

router = APIRouter(prefix="/youth_exercises",
                   tags=["youth_exercises"])


@router.post("")
def create(*, session: Session = Depends(get_session), exercise: YouthExercise) -> YouthExercise:
    session.add(exercise)
    session.commit()
    session.refresh(exercise)
    return exercise


@router.get("")
def get_all(*, session: Session = Depends(get_session), page: int = 1, per_page: int = 100) -> list[YouthExercise]:
    stmt = select(YouthExercise).order_by(YouthExercise.date.desc()).limit(per_page).offset((page - 1) * per_page)
    return list(session.exec(stmt).all())
