from __future__ import annotations

import re
import time

import cloudscraper
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}


def create_session() -> requests.Session:
    session = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "mobile": False}
    )
    session.headers.update(HEADERS)
    return session


def fetch_page(session: requests.Session, url: str, referer: str | None = None) -> str | None:
    headers = {}
    if referer:
        headers["Referer"] = referer

    try:
        response = session.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        return response.text
    except Exception as exc:
        status = ""
        body_preview = ""
        if "response" in locals():
            status = f" status={response.status_code}"
            body_preview = response.text[:160].replace("`n", " ")
        print(f"Page fetch error:{status} {url} - {exc} {body_preview}")
        return None


def extract_girl_info(url: str) -> tuple[str | None, str | None]:
    match = re.search(r"(https://www\.cityheaven\.net/.+?/)girlid-(\d+)/", url)
    if match:
        return match.group(1), match.group(2)
    return None, None


def build_attend_urls(shop_base: str, girl_id: str) -> list[str]:
    urls = [f"{shop_base}attend/?girl_id={girl_id}"]
    for week in range(2, 5):
        urls.append(f"{shop_base}attend/weekly/{week}/?girl_id={girl_id}")
    return urls


def parse_attend_table(html: str, girl_id: str) -> list[str]:
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
        time_text = time_text.replace("`n", "").replace(" ", "")
        if time_text:
            schedules.append(f"{date} {time_text}")

    return schedules


def scrape_schedules(url: str) -> list[str]:
    shop_base, girl_id = extract_girl_info(url)
    if not shop_base or not girl_id:
        print(f"Could not parse girl info from URL: {url}")
        return []

    session = create_session()

    # Warm up the session with the public profile page so later requests carry cookies.
    fetch_page(session, url, referer=shop_base)
    time.sleep(1)

    attend_urls = build_attend_urls(shop_base, girl_id)
    all_schedules: list[str] = []

    for attend_url in attend_urls:
        html = fetch_page(session, attend_url, referer=url)
        if html:
            week_schedules = parse_attend_table(html, girl_id)
            all_schedules.extend(week_schedules)
        time.sleep(1)

    unique_schedules = list(dict.fromkeys(all_schedules))
    print(f"Fetched schedules: {len(unique_schedules)}")
    return unique_schedules