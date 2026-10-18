from datetime import datetime, date

from sqlalchemy import TypeDecorator, Date as SQLDate

from data.timezone import to_local_date

class EpochDate(TypeDecorator):
    impl = SQLDate
    cache_ok = True

    def process_bind_param(self, value, dialect) -> date:
        if value is None:
            return value
        if isinstance(value, (int, float)):
            return to_local_date(value)
        if isinstance(value, str):
            # Handle ISO date strings like "2024-01-15"
            return datetime.fromisoformat(value).date()
        return value
