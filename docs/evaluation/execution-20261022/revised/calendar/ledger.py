"""Existing UTC storage; the UI selects calendar dates in UTC+08:00."""
from datetime import datetime, timezone, timedelta

LOCAL = timezone(timedelta(hours=8))


def for_day(rows, selected_day):
    start = datetime.fromisoformat(selected_day).replace(tzinfo=LOCAL)
    end = start + timedelta(days=1)
    return [row for row in rows
            if start <= datetime.fromisoformat(row['at'].replace('Z', '+00:00')) < end]
