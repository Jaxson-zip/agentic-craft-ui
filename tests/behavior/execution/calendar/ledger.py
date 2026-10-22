"""Existing UTC storage; the UI selects calendar dates in UTC+08:00."""
from datetime import datetime, timezone, timedelta

LOCAL = timezone(timedelta(hours=8))


def for_day(rows, selected_day):
    return [row for row in rows if row['at'][:10] == selected_day]
