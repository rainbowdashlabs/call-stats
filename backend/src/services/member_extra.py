from fastapi import Depends, APIRouter
from sqlmodel import Session

from data import get_session
from entities.member import MemberQualification
from services.call import add_members as add_call_members, remove_members as remove_call_members
from services.exercise import add_members as add_exercise_members, remove_members as remove_exercise_members
from services.member import get_by_id
from services.youth_exercise import add_members as add_youth_exercise_members, \
    remove_members as remove_youth_exercise_members

router = APIRouter(prefix="/member",
                   tags=["members"])


@router.post("/{member_id}/qualification")
def add_qualification(*, session: Session = Depends(get_session), member_id: int, qualification: MemberQualification):
    member = get_by_id(session=session, id=member_id)
    member.qualifications.append(qualification)
    session.add(member)


@router.get("/{member_id}/qualifications")
def get_qualifications(*, session: Session = Depends(get_session), member_id: int):
    return get_by_id(session=session, id=member_id).qualifications


@router.delete("/{member_id}/qualification/{qualification_id}")
def remove_qualification(*, session: Session = Depends(get_session), member_id: int,
                         qualification: MemberQualification):
    member = get_by_id(session=session, id=member_id)
    member.qualifications.remove(qualification)
    session.add(member)
    session.commit()


@router.post("/{member_id}/call/{call_id}")
def add_call(*, session: Session = Depends(get_session), member_id: int, call_id: int):
    add_call_members(session=session, call_id=call_id, member_ids=[member_id])


@router.delete("/{member_id}/call/{call_id}")
def remove_call(*, session: Session = Depends(get_session), member_id: int, call_id: int):
    remove_call_members(session=session, call_id=call_id, member_ids=[member_id])


@router.post("/{member_id}/exercise/{call_id}")
def add_exercise(*, session: Session = Depends(get_session), member_id: int, call_id: int):
    add_exercise_members(session=session, call_id=call_id, member_ids=[member_id])


@router.delete("/{member_id}/exercise/{call_id}")
def remove_exercise(*, session: Session = Depends(get_session), member_id: int, call_id: int):
    remove_exercise_members(session=session, call_id=call_id, member_ids=[member_id])


@router.post("/{member_id}/youth_exercise/{call_id}")
def add_youth_exercise(*, session: Session = Depends(get_session), member_id: int, call_id: int):
    add_youth_exercise_members(session=session, call_id=call_id, member_ids=[member_id])


@router.delete("/{member_id}/youth_exercise/{call_id}")
def remove_youth_exercise(*, session: Session = Depends(get_session), member_id: int, call_id: int):
    remove_youth_exercise_members(session=session, call_id=call_id, member_ids=[member_id])
