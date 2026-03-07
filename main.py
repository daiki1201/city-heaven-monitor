"""
City Heaven シフト監視ツール

シティヘブンの女の子の出勤予定を監視し、
新しい出勤が追加されたらLINE通知を送るツール
"""
import time
import schedule
from config import get_telegram_token, get_telegram_chat_id, get_check_interval, get_targets
from scraper import scrape_schedules
from storage import find_new_schedules, update_schedules
from notifier import send_telegram, format_new_schedule_message


def check_single_target(target: dict, bot_token: str, chat_id: str, is_first_run: bool = False) -> bool:
    """
    単一の監視対象をチェック

    Args:
        target: 監視対象の情報 {"name": ..., "url": ...}
        bot_token: Telegram Botトークン
        chat_id: Telegram Chat ID
        is_first_run: 初回実行フラグ（Trueの場合は通知しない）

    Returns:
        新しい出勤があった場合True
    """
    name = target.get("name", "不明")
    url = target.get("url", "")

    if not url:
        print(f"[{name}] URLが設定されていません")
        return False

    print(f"[{name}] チェック中...")

    # 出勤情報を取得
    current_schedules = scrape_schedules(url)

    if not current_schedules:
        print(f"[{name}] 出勤情報を取得できませんでした")
        return False

    # 新しい出勤を検出
    new_schedules = find_new_schedules(url, current_schedules)

    # 出勤情報を更新
    update_schedules(url, current_schedules)

    if new_schedules:
        print(f"[{name}] 新しい出勤: {len(new_schedules)}件")

        # 初回実行時は通知しない（既存データの初期化のみ）
        if not is_first_run:
            message = format_new_schedule_message(name, new_schedules)
            send_telegram(bot_token, chat_id, message)
        else:
            print(f"[{name}] 初回実行のため通知をスキップ")

        return True
    else:
        print(f"[{name}] 新しい出勤なし")
        return False


def check_all_targets(is_first_run: bool = False):
    """全ての監視対象をチェック"""
    print("=" * 50)
    print("チェック開始")
    print("=" * 50)

    bot_token = get_telegram_token()
    chat_id = get_telegram_chat_id()
    if not bot_token or not chat_id:
        print("エラー: Telegramの設定を確認してください")
        return

    targets = get_targets()
    if not targets:
        print("エラー: 監視対象が設定されていません")
        return

    for target in targets:
        try:
            check_single_target(target, bot_token, chat_id, is_first_run)
        except Exception as e:
            print(f"エラー: {target.get('name', '不明')} - {e}")

        # 連続アクセスを避けるため待機
        time.sleep(5)

    print("=" * 50)
    print("チェック完了")
    print("=" * 50)


def run_scheduler():
    """定期実行スケジューラーを起動"""
    interval = get_check_interval()
    print(f"定期実行モード: {interval}分ごとにチェック")

    # 初回実行（通知なし）
    check_all_targets(is_first_run=True)

    # スケジュール設定
    schedule.every(interval).minutes.do(check_all_targets)

    while True:
        schedule.run_pending()
        time.sleep(60)


def run_once():
    """1回だけ実行"""
    print("単発実行モード")
    check_all_targets(is_first_run=False)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # 単発実行
        run_once()
    else:
        # 定期実行
        run_scheduler()
