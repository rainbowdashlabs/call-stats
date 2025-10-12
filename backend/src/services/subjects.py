from fastapi import Depends, APIRouter
from sqlmodel import Session, select

from data import get_session
from entities.call import Subject
from services.base import MultiSelectGroup, MultiSelectItem
from services.extra.errors import ExistsError

router = APIRouter(prefix="/subjects",
                   tags=["subjects"])

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


@router.get("")
def get_all(*, session: Session = Depends(get_session), grouped: bool = False) -> list[Subject] | list[MultiSelectGroup]:
    stmt = select(Subject)
    subjects : list[Subject] = list(session.exec(stmt))
    if grouped:
        groups: dict[str, list[MultiSelectItem]] = {}
        for subject in subjects:
            if not subject.group in groups:
                groups[subject.group] = []
            groups[subject.group].append(MultiSelectItem(label=subject.name, value=subject.id))
        result = [MultiSelectGroup(items=sorted(v, key=lambda x: x.label), label=k) for k,v in groups.items()]
        return sorted(result, key=lambda x: x.label)
    return sorted(subjects, key=lambda x: x.name)
