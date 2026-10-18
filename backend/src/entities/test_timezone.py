from datetime import date, datetime, timezone
from unittest import TestCase
from zoneinfo import ZoneInfo

from data.timezone import to_local_date, to_utc
from entities.call import CreateCall, UpdateCall


class UtcInstants(TestCase):
    """The API receives unix timestamps and keeps them as UTC instants, whatever the host's clock."""

    def test_timestamp_becomes_utc_instant(self):
        call = CreateCall(subjects=[1], start=1768073400, end=1768077000, members=[1])  # 2026-01-10 19:30 UTC
        self.assertEqual(datetime(2026, 1, 10, 19, 30, tzinfo=timezone.utc), call.start)
        self.assertEqual(timezone.utc, call.start.tzinfo)
        self.assertEqual(datetime(2026, 1, 10, 20, 30), call.start.astimezone(ZoneInfo("Europe/Berlin")).replace(tzinfo=None))

    def test_offset_input_is_normalised_to_utc(self):
        berlin = datetime(2025, 7, 13, 20, 30, tzinfo=ZoneInfo("Europe/Berlin"))
        call = UpdateCall(id=1, subjects=[1], start=berlin, end=berlin, members=[1])
        self.assertEqual(datetime(2025, 7, 13, 18, 30, tzinfo=timezone.utc), call.start)
        self.assertEqual(timezone.utc, call.start.tzinfo)

    def test_naive_datetime_is_taken_as_utc(self):
        call = CreateCall(subjects=[1], start=datetime(2024, 3, 1, 10, 0), end=datetime(2024, 3, 1, 11, 0), members=[1])
        self.assertEqual(datetime(2024, 3, 1, 10, 0, tzinfo=timezone.utc), call.start)

    def test_helpers(self):
        self.assertIsNone(to_utc(None))
        self.assertEqual(datetime(2026, 1, 10, 19, 30, tzinfo=timezone.utc),
                         to_utc(datetime(2026, 1, 10, 20, 30, tzinfo=ZoneInfo("Europe/Berlin"))))
        self.assertEqual(date(2026, 1, 11), to_local_date(1768086000))  # 2026-01-10 23:00 UTC is already the 11th in Berlin
