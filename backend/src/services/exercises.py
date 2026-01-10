from math import ceil

from fastapi import Depends, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from data import get_session
from entities.exercise import Exercise, FullExercise
from entities.member import SimpleMember
from services.extra.page import Page

router = APIRouter(prefix="/exercises",
                   tags=["exercises"])

FullExercise.model_rebuild(_types_namespace={"SimpleMember": SimpleMember})

@router.post("")
def create(*, session: Session = Depends(get_session), exercise: Exercise) -> Exercise:
    session.add(exercise)
    session.commit()
    session.refresh(exercise)
    return exercise


@router.get("")
def get_all(*, session: Session = Depends(get_session), page: int = 1, size: int = 100) -> Page[FullExercise]:
    stmt = (
        select(Exercise)
        .options(selectinload(Exercise.members))
        .order_by(Exercise.exercise_date.desc())
        .limit(size)
        .offset((page - 1) * size)
    )
    exercises = [FullExercise.convert(e) for e in list(session.exec(stmt).all())]
    stmt = select(func.count(Exercise.id)).select_from(Exercise)
    count: int = (session.exec(stmt)).first()
    count = ceil(count / float(size))
    return Page(page=page, size=size, entries=exercises, pages=count)
