from __future__ import annotations

import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SCHEDULES_FILE = os.path.join(DATA_DIR, "schedules.json")


def ensure_data_dir() -> None:
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def load_schedules() -> dict:
    ensure_data_dir()
    if not os.path.exists(SCHEDULES_FILE):
        return {}

    try:
        with open(SCHEDULES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def has_saved_schedules() -> bool:
    return bool(load_schedules())


def save_schedules(schedules: dict) -> None:
    ensure_data_dir()
    with open(SCHEDULES_FILE, "w", encoding="utf-8") as f:
        json.dump(schedules, f, ensure_ascii=False, indent=2)


def find_new_schedules(url: str, current_schedules: list) -> list:
    saved = load_schedules()
    previous_schedules = saved.get(url, [])
    return [schedule for schedule in current_schedules if schedule not in previous_schedules]


def update_schedules(url: str, schedules: list) -> None:
    all_schedules = load_schedules()
    all_schedules[url] = schedules
    save_schedules(all_schedules)