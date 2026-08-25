from datetime import datetime, timedelta
from unittest import TestCase
from uuid import uuid4

from sqlmodel import Session

# noinspection PyUnusedImports
import main
from data import engine
from entities.call import CreateCall, Subject
from entities.member import Member
from services.call import add_members as add_call_members, delete as delete_call, get_by_id as get_call
from services.calls import create as create_call
from services.member import delete as delete_member
from services.members import create as create_member
from services.subject import delete as delete_subject
from services.subjects import create as create_subject


class CallCreation(TestCase):
    """Runs against a shared database, so every fixture carries a unique suffix and is
    removed again afterwards."""

    def setUp(self):
        self.suffix = uuid4().hex[:8]
        self.call_id = None
        self.subject_ids = []
        self.member_ids = []

    def test_create_call(self):
        with Session(engine) as session:
            first = create_subject(session=session, subject=Subject(name=f"Fire 1 {self.suffix}", group="Fire"))
            second = create_subject(session=session, subject=Subject(name=f"Fire 2 {self.suffix}", group="Fire"))
            self.subject_ids = [first.id, second.id]

            attending = create_member(session=session, member=Member(name=f"Jane Doe {self.suffix}"))
            joining = create_member(session=session, member=Member(name=f"John Doe {self.suffix}"))
            self.member_ids = [attending.id, joining.id]

            call = create_call(session=session, call=CreateCall(
                subjects=[first.id, second.id],
                start=datetime.now() - timedelta(minutes=35),
                end=datetime.now(),
                additional=2,
                members=[attending.id]))
            self.call_id = call.id

            add_call_members(session=session, call_id=call.id, member_ids=[joining.id])

            created = get_call(session=session, id=call.id)
            self.assertEqual([first.name, second.name], [s.name for s in created.subjects])
            self.assertEqual({attending.name, joining.name}, {m.name for m in created.members})
            self.assertEqual(2, created.additional)

    def tearDown(self):
        with Session(engine) as session:
            if self.call_id:
                delete_call(session=session, id=self.call_id)
            for member_id in self.member_ids:
                delete_member(session=session, id=member_id)
            for subject_id in self.subject_ids:
                delete_subject(session=session, id=subject_id)
