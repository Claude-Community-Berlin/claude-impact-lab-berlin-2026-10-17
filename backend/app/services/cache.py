"""Tiny in-memory cache for the week board. Fine for a single-process demo."""

from app.schemas import WeekResponse

_week: dict[tuple[str, str], WeekResponse] = {}


def get_week(lang: str, day: str) -> WeekResponse | None:
    return _week.get((lang, day))


def set_week(lang: str, day: str, value: WeekResponse) -> None:
    _week[(lang, day)] = value


def clear() -> None:
    _week.clear()
