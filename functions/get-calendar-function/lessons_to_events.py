from datetime import datetime, timedelta
from hashlib import md5
from uuid import UUID

from dateutil.parser import isoparse
from ics import Event

LESSON_TYPE_TO_TAG = {
    "Лекции": "Лек",
    "Практические занятия": "Прак",
    "Лабораторные занятия": "Лаб",
    "Занятия спортом": "Спорт",
}

LESSON_KEY_NAMES = {
    "group": "Группа",
    "teacher_name": "Преподаватель",
    "teacher_fio": "Преподаватель",
    "zoom_url": "Ссылка на Zoom",
    "zoom_password": "Пароль Zoom",
    "zoom_info": "Доп. информация для Zoom",
    "note": "Примечание",
}


def lesson_type_to_tag(lesson_type: str) -> str:
    return LESSON_TYPE_TO_TAG.get(lesson_type, lesson_type)


def raw_lesson_to_description(raw_lesson: dict) -> str:
    lines = []
    for key, name in LESSON_KEY_NAMES.items():
        if raw_lesson.get(key):
            lines.append(f"{name}: {raw_lesson[key]}")

    _msk_formatted_datetime = (datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M")
    lines.append(f"Обновлено: {_msk_formatted_datetime} MSK")
    return "\n".join(lines)


def raw_lesson_to_location(raw_lesson: dict):
    elements = []
    for key in "room", "building":
        if raw_lesson.get(key):
            elements.append(raw_lesson[key])
    result = ", ".join(elements)

    if raw_lesson.get("zoom_url"):
        result = f"Zoom / {result}" if result else "Zoom"

    return result or None


def raw_lesson_to_uuid(raw_lesson: dict):
    unique_str = f"{raw_lesson['date']},{raw_lesson['time_start']},{raw_lesson['subject']}"
    md5_of_lesson = md5(unique_str.encode("utf-8")).hexdigest()
    return str(UUID(hex=md5_of_lesson))


def raw_lesson_to_event(raw_lesson: dict) -> Event:
    begin = isoparse(f"{raw_lesson['date']}T{raw_lesson['time_start']}:00+03:00")
    end = isoparse(f"{raw_lesson['date']}T{raw_lesson['time_end']}:00+03:00")

    # If there is a mistake in event
    if begin > end:
        begin, end = end, begin

    event = Event(
        name=f"[{lesson_type_to_tag(raw_lesson['type'])}] {raw_lesson['subject']}",
        begin=begin,
        end=end,
        description=raw_lesson_to_description(raw_lesson),
        location=raw_lesson_to_location(raw_lesson),
        uid=raw_lesson_to_uuid(raw_lesson),
    )

    if raw_lesson["zoom_url"]:
        event.url = raw_lesson["zoom_url"]

    return event
