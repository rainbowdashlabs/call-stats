from sqlmodel import Session, select

from data import engine
from entities.youth import YouthExercise
from web.app import router


@router.post("/youth_exercises")
def create(exercise: YouthExercise) -> YouthExercise:
    with Session(engine) as session:
        session.add(exercise)
        session.commit()
        session.refresh(exercise)
        return exercise


@router.get("/youth_exercises")
def get_all(page: int = 1, per_page: int = 100) -> list[YouthExercise]:
    with Session(engine) as session:
        stmt = select(YouthExercise).order_by(YouthExercise.date.desc()).limit(per_page).offset((page - 1) * per_page)
        return list(session.exec(stmt).all())
