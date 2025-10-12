from fastapi import Depends, APIRouter
from sqlmodel import Session, select

from data import get_session
from entities.call import Subject
from services.extra.errors import NotFoundError


router = APIRouter(prefix="/subject",
                   tags=["subjects"])


@router.get("/{id}")
def get_by_id(*, session: Session = Depends(get_session), id: int) -> Subject:
    stmt = select(Subject).where(Subject.id == id)
    subject = session.exec(stmt).one_or_none()
    if subject is None:
        raise NotFoundError(Subject)
    return subject


@router.patch("/{id}")
def update(*, session: Session = Depends(get_session), id: int, subject: Subject) -> Subject:
    # Fetch existing subject by id
    stmt = select(Subject).where(Subject.id == id)
    existing = session.exec(stmt).one_or_none()
    if existing is None:
        raise NotFoundError(Subject)

    # Update fields
    existing.name = subject.name
    existing.group = subject.group

    session.add(existing)
    session.commit()
    session.refresh(existing)
    return existing


@router.delete("/{id}")
def delete(*, session: Session = Depends(get_session), id: int) -> None:
    subject = get_by_id(session=session, id=id)
    session.delete(subject)
    session.commit()
