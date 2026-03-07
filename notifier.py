"""Telegram通知処理"""
import requests

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


def send_telegram(token: str, chat_id: str, message: str) -> bool:
    url = TELEGRAM_API.format(token=token)
    data = {
        "chat_id": chat_id,
        "text": message
    }

    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Telegram通知送信成功")
            return True
        else:
            print(f"Telegram通知送信失敗: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Telegram通知送信エラー: {e}")
        return False


def format_new_schedule_message(name: str, new_schedules: list) -> str:
    message = f"【{name}】新しい出勤予定\n"
    for schedule in new_schedules:
        message += f"・{schedule}\n"
    return message
