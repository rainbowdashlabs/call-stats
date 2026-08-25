from datetime import datetime, timedelta

from fastapi import Depends, APIRouter
from sqlalchemy import func
from sqlmodel import Session, select

from data import get_session
from entities.call import Call, CallSubject, Subject, SubjectUsage
from services.base import MultiSelectGroup, MultiSelectItem
from services.extra.errors import ExistsError

router = APIRouter(prefix="/subjects",
                   tags=["subjects"])

USAGE_WINDOW_DAYS = 730


@router.post("")
def create(*, session: Session = Depends(get_session), subject: Subject) -> Subject:
    stmt = select(Subject).where(Subject.name == subject.name).where(Subject.group != subject.group)
    exists = session.exec(stmt).one_or_none()
    if exists:
        raise ExistsError(exists)
    session.add(subject)
    session.commit()
    session.refresh(subject)
    return subject


def _usage_by_subject(session: Session) -> dict[int, int]:
    cutoff = datetime.now() - timedelta(days=USAGE_WINDOW_DAYS)
    stmt = (select(CallSubject.subject_id, func.count())
            .join(Call, Call.id == CallSubject.call_id)
            .where(Call.start >= cutoff)
            .group_by(CallSubject.subject_id))
    return {subject_id: count for subject_id, count in session.exec(stmt)}


@router.get("")
def get_all(*, session: Session = Depends(get_session), grouped: bool = False) -> list[SubjectUsage] | list[MultiSelectGroup]:
    stmt = select(Subject)
    subjects: list[Subject] = list(session.exec(stmt))
    if grouped:
        groups: dict[str, list[MultiSelectItem]] = {}
        for subject in subjects:
            if not subject.group in groups:
                groups[subject.group] = []
            groups[subject.group].append(MultiSelectItem(label=subject.name, value=subject.id))
        result = [MultiSelectGroup(items=sorted(v, key=lambda x: x.label), label=k) for k, v in groups.items()]
        return sorted(result, key=lambda x: x.label)
    usage = _usage_by_subject(session)
    return sorted([SubjectUsage(id=s.id, name=s.name, group=s.group, usage=usage.get(s.id, 0))
                   for s in subjects], key=lambda x: x.name)
