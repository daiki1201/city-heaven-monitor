"""設定ファイルの読み込み"""
import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
TARGETS_PATH = os.path.join(os.path.dirname(__file__), "targets.json")


def load_config() -> dict:
    """config.jsonを読み込む（存在する場合のみ）"""
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_targets_config() -> dict:
    """targets.jsonを読み込む"""
    with open(TARGETS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_telegram_token() -> str:
    """Telegram Botトークンを取得（環境変数優先）"""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if token:
        return token
    config = load_config()
    return config.get("telegram_bot_token", "")


def get_telegram_chat_id() -> str:
    """Telegram Chat IDを取得（環境変数優先）"""
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if chat_id:
        return chat_id
    config = load_config()
    return config.get("telegram_chat_id", "")


def get_check_interval() -> int:
    """チェック間隔（分）を取得"""
    return load_targets_config().get("check_interval_minutes", 30)


def get_targets() -> list:
    """監視対象リストを取得"""
    return load_targets_config().get("targets", [])
