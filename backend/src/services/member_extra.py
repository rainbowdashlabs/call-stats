from sqlmodel import Session

from data import engine
from entities.member import MemberQualification
from services.call import add_members as add_call_members, remove_members as remove_call_members
from services.exercise import add_members as add_exercise_members, remove_members as remove_exercise_members
from services.member import get_by_id
from services.youth_exercise import add_members as add_youth_exercise_members, \
    remove_members as remove_youth_exercise_members
from web.app import router


@router.post("/member/{member_id}/qualification")
def add_qualification(member_id: int, qualification: MemberQualification):
    with Session(engine) as session:
        member = get_by_id(member_id)
        member.qualifications.append(qualification)
        session.add(member)


@router.get("/member/{member_id}/qualifications")
def get_qualifications(member_id: int):
    return get_by_id(member_id).qualifications


@router.delete("/member/{member_id}/qualification/{qualification_id}")
def remove_qualification(member_id: int, qualification: MemberQualification):
    with Session(engine) as session:
        member = get_by_id(member_id)
        member.qualifications.remove(qualification)
        session.add(member)
        session.commit()


@router.post("/member/{member_id}/call/{call_id}")
def add_call(member_id: int, call_id: int):
    add_call_members(call_id, [member_id])


@router.delete("/member/{member_id}/call/{call_id}")
def remove_call(member_id: int, call_id: int):
    remove_call_members(call_id, [member_id])


@router.post("/member/{member_id}/exercise/{call_id}")
def add_exercise(member_id: int, call_id: int):
    add_exercise_members(call_id, [member_id])


@router.delete("/member/{member_id}/exercise/{call_id}")
def remove_exercise(member_id: int, call_id: int):
    remove_exercise_members(call_id, [member_id])


@router.post("/member/{member_id}/youth_exercise/{call_id}")
def add_youth_exercise(member_id: int, call_id: int):
    add_youth_exercise_members(call_id, [member_id])


@router.delete("/member/{member_id}/youth_exercise/{call_id}")
def remove_youth_exercise(member_id: int, call_id: int):
    remove_youth_exercise_members(call_id, [member_id])
