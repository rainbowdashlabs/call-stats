from fastapi import Depends, APIRouter
from sqlmodel import Session, select

from data import get_session
from entities.qualification import Qualification
from services.extra.errors import NameExistsError, NotFoundError, IdChangeError
from services.qualifications import get_by_name

router = APIRouter(prefix="/qualification",
                   tags=["qualifications"])


@router.get("/{id}")
def get_by_id(*, session: Session = Depends(get_session), id: int) -> Qualification:
    stmt = select(Qualification).where(Qualification.id == id)
    qualification = session.exec(stmt).one_or_none()
    if not qualification:
        raise NotFoundError(Qualification)
    return qualification


@router.delete("/{id}")
def delete(*, session: Session = Depends(get_session), id: int):
    qualification = get_by_id(session=session, id=id)
    session.delete(qualification)
    session.commit()


@router.patch("/{id}")
def update(*, session: Session = Depends(get_session), id: int, new: Qualification) -> Qualification:
    if id != new.id:
        raise IdChangeError(Qualification)
    old = get_by_id(session=session, id=id)
    if old.name != new.name:
        exists = get_by_name(session=session, name=new.name)
        if exists:
            raise NameExistsError(exists)
    session.add(new)
    session.commit()
    session.refresh(new)
    return new
