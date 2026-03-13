from __future__ import annotations

import sys
import time

from config import (
    get_check_interval,
    get_targets,
    get_telegram_chat_id,
    get_telegram_token,
)
from notifier import format_new_schedule_message, send_telegram
from scraper import scrape_schedules
from storage import find_new_schedules, has_saved_schedules, update_schedules


def check_single_target(
    target: dict,
    bot_token: str,
    chat_id: str,
    is_first_run: bool = False,
) -> bool:
    name = target.get("name", "unknown")
    url = target.get("url", "")

    if not url:
        print(f"[{name}] Missing URL; skipping.")
        return False

    print(f"[{name}] Checking schedules...")
    current_schedules = scrape_schedules(url)

    if not current_schedules:
        print(f"[{name}] No schedules found.")
        return False

    new_schedules = find_new_schedules(url, current_schedules)
    update_schedules(url, current_schedules)

    if not new_schedules:
        print(f"[{name}] No new schedules.")
        return False

    print(f"[{name}] Found {len(new_schedules)} new schedule(s).")

    if is_first_run:
        print(f"[{name}] Initial run; skipping notification.")
        return True

    message = format_new_schedule_message(name, new_schedules)
    sent = send_telegram(bot_token, chat_id, message)
    if not sent:
        print(f"[{name}] Failed to send Telegram notification.")
    return sent


def check_all_targets(is_first_run: bool = False) -> None:
    print("=" * 50)
    print("Starting schedule check")
    print("=" * 50)

    bot_token = get_telegram_token()
    chat_id = get_telegram_chat_id()
    if not bot_token or not chat_id:
        print("Error: Telegram settings are missing.")
        return

    targets = get_targets()
    if not targets:
        print("Error: No targets configured.")
        return

    for target in targets:
        try:
            check_single_target(target, bot_token, chat_id, is_first_run)
        except Exception as exc:
            print(f"Error while checking {target.get('name', 'unknown')}: {exc}")

        time.sleep(5)

    print("=" * 50)
    print("Finished schedule check")
    print("=" * 50)


def run_scheduler() -> None:
    interval = get_check_interval()
    print(f"Running continuous checks every {interval} minute(s).")

    first_run = not has_saved_schedules()
    if first_run:
        print("No saved schedules found yet; the first run will only bootstrap local state.")

    check_all_targets(is_first_run=first_run)
    next_run = time.time() + (interval * 60)

    while True:
        now = time.time()
        if now >= next_run:
            check_all_targets()
            next_run = now + (interval * 60)

        time.sleep(10)


def run_once(bootstrap: bool | None = None) -> None:
    if bootstrap is None:
        bootstrap = not has_saved_schedules()

    if bootstrap:
        print("No saved schedules found yet; this run will only bootstrap local state.")

    print("Running single check.")
    check_all_targets(is_first_run=bootstrap)


if __name__ == "__main__":
    args = set(sys.argv[1:])
    bootstrap = "--bootstrap" in args

    if "--once" in args:
        run_once(bootstrap=bootstrap if bootstrap else None)
    else:
        run_scheduler()