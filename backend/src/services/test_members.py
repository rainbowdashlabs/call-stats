from unittest import TestCase

from entities.member import Member
from services.extra.errors import NotFoundError
from services.member import search, delete, update, get_by_id
from services.members import create


class MembersTest(TestCase):

    def setUp(self):
        print("Setting up")
        pass

    def test_create_member(self):
        member = create(Member(name="Jane Doe"))
        self.assertEqual(member.name, "Jane Doe")

    def test_update_member(self):
        member = create(Member(name="Jane Doe"))
        member.name = "Jane"
        update(member)
        member = get_by_id(member.id)
        self.assertEqual("Jane", member.name)

    def tearDown(self):
        print("Tearing down")
        for name in ["Jane Doe", "Jane"]:
            try:
                member = search(name=name)
            except NotFoundError:
                return
            if member:
                delete(member.id)
