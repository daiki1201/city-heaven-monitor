"""シティヘブンのスクレイピング処理"""
import re
import time
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def fetch_page(url: str) -> str | None:
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"ページ取得エラー: {url} - {e}")
        return None


def extract_girl_info(url: str) -> tuple:
    """
    girlid URLからshop base URLとgirl IDを抽出

    例: https://www.cityheaven.net/tokyo/A1312/A131205/siroi-pocha/girlid-60704700/?lo=1
    → ("https://www.cityheaven.net/tokyo/A1312/A131205/siroi-pocha/", "60704700")
    """
    match = re.search(r'(https://www\.cityheaven\.net/.+?/)girlid-(\d+)/', url)
    if match:
        return match.group(1), match.group(2)
    return None, None


def build_attend_urls(shop_base: str, girl_id: str) -> list:
    """4週分のattend URLを生成"""
    urls = [f"{shop_base}attend/?girl_id={girl_id}"]
    for week in range(2, 5):
        urls.append(f"{shop_base}attend/weekly/{week}/?girl_id={girl_id}")
    return urls


def parse_attend_table(html: str, girl_id: str) -> list:
    """
    attend HTMLから指定girl_idのスケジュールをパース

    Returns:
        ["3/7(土) 11:00-15:00", ...] 形式のリスト（出勤日のみ）
    """
    soup = BeautifulSoup(html, "html.parser")
    schedules = []

    target_table = None
    for table in soup.find_all("table"):
        if table.find("a", href=lambda h: h and f"girlid-{girl_id}" in h):
            target_table = table
            break

    if not target_table:
        return schedules

    rows = target_table.find_all("tr")
    if len(rows) < 2:
        return schedules

    date_cells = rows[0].find_all("th", class_="week")
    dates = [cell.get_text(strip=True) for cell in date_cells]

    time_cells = rows[1].find_all("td")[1:]

    for date, cell in zip(dates, time_cells):
        if cell.find(class_="holiday"):
            continue

        for div in cell.find_all("div"):
            div.decompose()

        time_text = cell.get_text(separator="", strip=True)
        time_text = time_text.replace("\n", "").replace(" ", "")

        if time_text:
            schedules.append(f"{date} {time_text}")

    return schedules


def scrape_schedules(url: str) -> list:
    """
    指定URLから出勤情報をスクレイピング（4週分）

    Args:
        url: 女の子のgirlid URL

    Returns:
        出勤情報のリスト（例: ["3/7(土) 11:00-15:00", ...]）
    """
    shop_base, girl_id = extract_girl_info(url)
    if not shop_base or not girl_id:
        print(f"URLからgirl情報を取得できませんでした: {url}")
        return []

    attend_urls = build_attend_urls(shop_base, girl_id)
    all_schedules = []

    for attend_url in attend_urls:
        html = fetch_page(attend_url)
        if html:
            week_schedules = parse_attend_table(html, girl_id)
            all_schedules.extend(week_schedules)
        time.sleep(1)

    print(f"取得した出勤情報: {len(all_schedules)}件")
    return all_schedules
