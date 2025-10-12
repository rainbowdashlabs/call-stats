from fastapi import Depends, APIRouter
from sqlmodel import Session, select

from data import get_session
from entities.qualification import Qualification
from services.extra.errors import NotFoundError

router = APIRouter(prefix="/qualifications",
                   tags=["qualifications"])


@router.post("")
def create(*, session: Session = Depends(get_session), name: str) -> Qualification:
    qualification = Qualification(name=name)
    session.add(qualification)
    session.commit()
    session.refresh(qualification)
    return qualification


@router.get("")
def get_all(*, session: Session = Depends(get_session), ) -> list[Qualification]:
    stmt = select(Qualification)
    return list(session.exec(stmt).all())


@router.get("/search")
def get_by_name(*, session: Session = Depends(get_session), name: str) -> Qualification:
    stmt = select(Qualification).where(Qualification.name == name)
    qualification = session.exec(stmt).one_or_none()
    if not qualification:
        raise NotFoundError(Qualification)
    return qualification
