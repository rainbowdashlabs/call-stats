from fastapi import Depends, APIRouter
from sqlmodel import Session, select

from sqlalchemy import func

from data import get_session
from entities.call import CallSubject, Subject
from services.extra.errors import InUseError, NotFoundError


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

    existing.name = subject.name
    existing.group = subject.group
    existing.archived = subject.archived

    session.add(existing)
    session.commit()
    session.refresh(existing)
    return existing


@router.delete("/{id}")
def delete(*, session: Session = Depends(get_session), id: int) -> None:
    """Removes a subject that was never used. One with call history has to be archived instead,
    so the calls it appears on keep their wording."""
    subject = get_by_id(session=session, id=id)
    used_by = session.exec(select(func.count()).select_from(CallSubject)
                           .where(CallSubject.subject_id == id)).one()
    if used_by:
        raise InUseError(Subject, f"{used_by} Einsätze")
    session.delete(subject)
    session.commit()
