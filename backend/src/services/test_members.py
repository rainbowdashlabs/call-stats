from unittest import TestCase
from uuid import uuid4

from sqlmodel import Session

# noinspection PyUnusedImports
import main
from data import engine
from entities.member import Member
from services.extra.errors import NotFoundError
from services.member import delete, get_by_id, update
from services.members import create, search


class MembersTest(TestCase):
    """Runs against a shared database, so every fixture carries a unique suffix and is
    removed again afterwards."""

    def setUp(self):
        suffix = uuid4().hex[:8]
        self.created = f"Jane Doe {suffix}"
        self.renamed = f"Jane {suffix}"

    def test_create_member(self):
        with Session(engine) as session:
            member = create(session=session, member=Member(name=self.created))
            self.assertEqual(self.created, member.name)

    def test_update_member(self):
        with Session(engine) as session:
            member = create(session=session, member=Member(name=self.created))
            member.name = self.renamed
            update(session=session, new=member)
            self.assertEqual(self.renamed, get_by_id(session=session, id=member.id).name)

    def tearDown(self):
        with Session(engine) as session:
            for name in [self.created, self.renamed]:
                try:
                    member = search(session=session, name=name)
                except NotFoundError:
                    continue
                delete(session=session, id=member.id)
