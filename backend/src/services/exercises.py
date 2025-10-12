from fastapi import Depends, APIRouter
from sqlmodel import Session, select

from data import get_session
from entities.exercise import Exercise

router = APIRouter(prefix="/exercises",
                   tags=["exercises"])


@router.post("")
def create(*, session: Session = Depends(get_session), exercise: Exercise) -> Exercise:
    session.add(exercise)
    session.commit()
    session.refresh(exercise)
    return exercise


@router.get("")
def get_all(*, session: Session = Depends(get_session), page: int = 1, per_page: int = 100) -> list[Exercise]:
    stmt = select(Exercise).order_by(Exercise.date.desc()).limit(per_page).offset((page - 1) * per_page)
    return list(session.exec(stmt).all())
