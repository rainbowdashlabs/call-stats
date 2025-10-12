from datetime import datetime, timedelta
from unittest import TestCase

from sqlmodel import Session

# noinspection PyUnusedImports
import main
from data import engine
from entities.call import Subject, CreateCall
from entities.member import Member
from services.call import add_members as add_call_members
from services.calls import create as create_call
from services.members import create as create_member
from services.subjects import create as create_subject


class CallCreation(TestCase):

    def setUp(self):
        print("Setting up")

    def test_create_call(self):
        with Session(engine) as session:
            first = create_subject(session=session, subject=Subject(name="Fire 1", group="Fire"))
            second = create_subject(session=session, subject=Subject(name="Fire 2", group="Fire"))

            member = create_member(session=session, member=Member(name="Jane Doe2"))
            call = CreateCall(subjects=[first, second],
                              start=datetime.now() - timedelta(minutes=35),
                              end=datetime.now(),
                              members=[member.id])
            call = create_call(session=session, call=call)
            add_call_members(session=session, call_id=call.id, member_ids=[member.id])
