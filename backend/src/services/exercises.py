from sqlmodel import Session, select

from data import engine
from entities.exercise import Exercise
from web.app import router


@router.post("/exercises")
def create(exercise: Exercise) -> Exercise:
    with Session(engine) as session:
        session.add(exercise)
        session.commit()
        session.refresh(exercise)
        return exercise


@router.get("/exercises")
def get_all(page: int = 1, per_page: int = 100) -> list[Exercise]:
    with Session(engine) as session:
        stmt = select(Exercise).order_by(Exercise.date.desc()).limit(per_page).offset((page - 1) * per_page)
        return list(session.exec(stmt).all())
