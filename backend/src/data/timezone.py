import os
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

# Call times are stored as UTC instants (TIMESTAMPTZ) and the browser shows them in its own
# zone, so neither the host's clock nor the viewer's location shifts anything. The only place
# a fixed zone is needed is the statistics, which group calls by day and hour of the brigade's
# local time; that zone is set on every database session.
APP_TIMEZONE_NAME = os.getenv("APP_TIMEZONE", "Europe/Berlin")
APP_TIMEZONE = ZoneInfo(APP_TIMEZONE_NAME)


def to_utc(value: datetime | None) -> datetime | None:
    """Makes a datetime an aware UTC instant; a naive value is taken to be UTC already."""
    if value is None:
        return value
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def to_local_date(timestamp: int | float) -> date:
    """The calendar day a unix timestamp falls on in the brigade's zone."""
    return datetime.fromtimestamp(timestamp, APP_TIMEZONE).date()
