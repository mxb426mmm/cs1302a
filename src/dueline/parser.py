from datetime import datetime, timedelta
import re


class ParseError(ValueError):
    pass


_WEEKDAYS = {
    "monday": 0, "mon": 0, "tuesday": 1, "tue": 1,
    "wednesday": 2, "wed": 2, "thursday": 3, "thu": 3,
    "friday": 4, "fri": 4, "saturday": 5, "sat": 5,
    "sunday": 6, "sun": 6,
}

_MONTHS = {
    "january": 1, "jan": 1, "february": 2, "feb": 2,
    "march": 3, "mar": 3, "april": 4, "apr": 4, "may": 5,
    "june": 6, "jun": 6, "july": 7, "jul": 7, "august": 8, "aug": 8,
    "september": 9, "sep": 9, "october": 10, "oct": 10,
    "november": 11, "nov": 11, "december": 12, "dec": 12,
}

_TIME_PATTERNS = [
    re.compile(r"(?P<hour>\d{1,2}):(?P<minute>\d{2})\s*(?P<ampm>am|pm)?", re.I),
    re.compile(r"(?P<hour>\d{1,2})(?::(?P<minute>\d{2}))?\s*(?P<ampm>am|pm)", re.I),
]


def _parse_time(text, base_hour=23, base_minute=59):
    for pat in _TIME_PATTERNS:
        m = pat.search(text)
        if m:
            hour = int(m.group("hour"))
            minute = int(m.group("minute") or 0)
            ampm = (m.group("ampm") or "").lower()
            if ampm == "am":
                hour = 0 if hour == 12 else hour
            elif ampm == "pm":
                hour = hour + 12 if hour < 12 else hour
            return hour, minute
    return base_hour, base_minute


def parse_due(text, now=None):
    now = now or datetime.now()
    lowered = text.strip().lower()

    if "tomorrow" in lowered:
        date = now.date() + timedelta(days=1)
        base = (9, 0)
    elif "today" in lowered:
        date = now.date()
        base = (23, 59)
    elif "next" in lowered:
        for name, iso in _WEEKDAYS.items():
            if name in lowered:
                days_ahead = (iso - now.weekday()) % 7 or 7
                date = now.date() + timedelta(days=days_ahead)
                base = (23, 59)
                break
        else:
            raise ParseError(f"no weekday in {text!r}")
    else:
        m = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", lowered)
        if m:
            date = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3))).date()
            base = (23, 59)
        else:
            m = re.search(r"(\d{1,2})\s*月\s*(\d{1,2})", lowered)
            if m:
                date = datetime(now.year, int(m.group(1)), int(m.group(2))).date()
                base = (23, 59)
            else:
                raise ParseError(f"could not parse date in {text!r}")

    hour, minute = _parse_time(lowered, *base)
    return datetime.combine(date, datetime.min.time()).replace(
        hour=hour, minute=minute, second=0, microsecond=0
    )
