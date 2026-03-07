"""シティヘブンのスクレイピング処理"""
import re
import time
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


def create_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def fetch_page(url: str, driver: Optional[webdriver.Chrome] = None) -> Optional[str]:
    close_driver = False
    if driver is None:
        driver = create_driver()
        close_driver = True

    try:
        driver.get(url)
        time.sleep(3)
        return driver.page_source
    except Exception as e:
        print(f"ページ取得エラー: {url} - {e}")
        return None
    finally:
        if close_driver:
            driver.quit()


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

    # 全テーブルからgirl_idのリンクを含むものを探す
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

    # row[0]: 日付ヘッダー、row[1]: 時間データ
    date_cells = rows[0].find_all("th", class_="week")
    dates = [cell.get_text(strip=True) for cell in date_cells]

    time_cells = rows[1].find_all("td")[1:]  # 最初のtd（写真）をスキップ

    for date, cell in zip(dates, time_cells):
        # 出勤なし
        if cell.find(class_="holiday"):
            continue

        # 時間テキストを抽出（受付終了divを除く）
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
    driver = create_driver()
    all_schedules = []

    try:
        for attend_url in attend_urls:
            html = fetch_page(attend_url, driver)
            if html:
                week_schedules = parse_attend_table(html, girl_id)
                all_schedules.extend(week_schedules)
            time.sleep(2)
    finally:
        driver.quit()

    print(f"取得した出勤情報: {len(all_schedules)}件")
    return all_schedules
