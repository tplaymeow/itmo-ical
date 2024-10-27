from datetime import date
from typing import Iterable

import requests

_API_BASE_URL = "https://my.itmo.ru/api"

def get_academic_year_start() -> int:
    today = date.today()
    return today.year - 1 if today < today.replace(month=8, day=1) else today.year

def parse_lessons(data: dict) -> Iterable[dict]:
    return (
        {"date": day["date"], **lesson}
        for day in data["data"]
        for lesson in day["lessons"]
    )

def get_raw_lessons(auth_token: str) -> Iterable[dict]:
    term_start_year = get_academic_year_start()
    resp = requests.get(
        _API_BASE_URL + "/schedule/schedule/personal",
        headers={"Authorization": f"Bearer {auth_token}"},
        params={
            "date_start": f"{term_start_year}-08-01",
            "date_end": f"{term_start_year + 1}-07-31",
        }
    )
    resp.raise_for_status()
    return parse_lessons(resp.json())
