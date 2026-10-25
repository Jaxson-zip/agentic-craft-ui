"""Existing UTC storage; the UI selects calendar dates in UTC+08:00."""
from datetime import datetime, timezone, timedelta

LOCAL = timezone(timedelta(hours=8))


def for_day(rows, selected_day):
    """Select the local calendar day, preserving row identity and input order."""
    start = datetime.fromisoformat(selected_day).replace(tzinfo=LOCAL)
    end = start + timedelta(days=1)
    result = []
    for row in rows:
        at = datetime.fromisoformat(row['at'].replace('Z', '+00:00'))
        # Storage is UTC, including timestamps without an explicit offset.
        if at.tzinfo is None:
            at = at.replace(tzinfo=timezone.utc)
        if start <= at < end:
            result.append(row)
    return result
