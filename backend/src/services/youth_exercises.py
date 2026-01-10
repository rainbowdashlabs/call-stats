from math import ceil

from fastapi import Depends, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from data import get_session
from entities.youth import YouthExercise, FullYouthExercise
from entities.member import SimpleMember
from services.extra.page import Page

router = APIRouter(prefix="/youth_exercises",
                   tags=["youth_exercises"])

FullYouthExercise.model_rebuild(_types_namespace={"SimpleMember": SimpleMember})


@router.post("")
def create(*, session: Session = Depends(get_session), exercise: YouthExercise) -> YouthExercise:
    session.add(exercise)
    session.commit()
    session.refresh(exercise)
    return exercise


@router.get("")
def get_all(*, session: Session = Depends(get_session), page: int = 1, per_page: int = 100) -> Page[FullYouthExercise]:
    stmt = (
        select(YouthExercise)
        .options(selectinload(YouthExercise.instructors))
        .order_by(YouthExercise.exercise_date.desc())
        .limit(per_page)
        .offset((page - 1) * per_page)
    )
    res = [FullYouthExercise.convert(e) for e in session.exec(stmt).all()]
    stmt = select(func.count(YouthExercise.id)).select_from(YouthExercise)
    count: int = (session.exec(stmt)).first()
    count = ceil(count / float(per_page))
    return Page(page=page, size=per_page, pages=count, entries=res)
