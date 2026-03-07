"""出勤情報の保存・比較処理"""
import json
import os
from typing import Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SCHEDULES_FILE = os.path.join(DATA_DIR, "schedules.json")


def ensure_data_dir():
    """dataディレクトリが存在しない場合は作成"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def load_schedules() -> dict:
    """
    保存済みの出勤情報を読み込む

    Returns:
        {url: [schedule1, schedule2, ...], ...} 形式の辞書
    """
    ensure_data_dir()
    if not os.path.exists(SCHEDULES_FILE):
        return {}

    try:
        with open(SCHEDULES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_schedules(schedules: dict):
    """
    出勤情報を保存

    Args:
        schedules: {url: [schedule1, schedule2, ...], ...} 形式の辞書
    """
    ensure_data_dir()
    with open(SCHEDULES_FILE, "w", encoding="utf-8") as f:
        json.dump(schedules, f, ensure_ascii=False, indent=2)


def find_new_schedules(url: str, current_schedules: list) -> list:
    """
    新しく追加された出勤情報を検出

    Args:
        url: 対象のURL（キーとして使用）
        current_schedules: 現在の出勤情報リスト

    Returns:
        新しく追加された出勤情報のリスト
    """
    saved = load_schedules()
    previous_schedules = saved.get(url, [])

    # 前回にはなかった出勤情報を抽出
    new_schedules = [s for s in current_schedules if s not in previous_schedules]

    return new_schedules


def update_schedules(url: str, schedules: list):
    """
    指定URLの出勤情報を更新して保存

    Args:
        url: 対象のURL
        schedules: 出勤情報のリスト
    """
    all_schedules = load_schedules()
    all_schedules[url] = schedules
    save_schedules(all_schedules)
