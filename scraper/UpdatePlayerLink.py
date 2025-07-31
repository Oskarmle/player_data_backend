import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import time
import re
import psycopg2
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

BASE_URL = "https://www.bordtennisportalen.dk"

RANKING_URLS = [
    "https://www.bordtennisportalen.dk/DBTU/Ranglister/#59,42025,07/18/2025,0,,,4255,1,,,,,,,,0,,,,,,",
    "https://www.bordtennisportalen.dk/DBTU/Ranglister/#59,42025,07/18/2025,0,,,4260,1,,,,,,,,0,,,,,,",
]

def fetch_all_players():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("SELECT player_id FROM players")
    players = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return players

def scrape_current_data():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    data = {}

    for url in RANKING_URLS:
        print(f"🔹 Scraping: {url}")
        driver.get(url)
        time.sleep(7)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        table = soup.find("table", class_="RankingListGrid")
        if not table:
            continue

        rows = table.find("tbody").find_all("tr")
        for row in rows[1:]:
            cells = row.find_all("td")
            if len(cells) < 4:
                continue

            playerid = cells[2].get_text(strip=True)

            # ✅ Extract rank digits
            rank_raw = cells[1].get_text(strip=True)
            rank_digits = re.sub(r"\D", "", rank_raw)
            rank = int(rank_digits) if rank_digits else 9999
            print(f"   → {playerid} rank scraped: {rank_raw} → {rank}")

            # ✅ Player link
            a_tag = cells[3].find('a')
            player_link = BASE_URL + a_tag['href'] if a_tag else ''

            data[playerid] = {"link": player_link, "rank": rank}

    driver.quit()
    return data

def update_player_links_and_ranks():
    current_data = scrape_current_data()
    existing_players = fetch_all_players()

    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    for pid in existing_players:
        if pid in current_data:
            new_link = current_data[pid]["link"]
            new_rank = current_data[pid]["rank"]

            cur.execute(
                "UPDATE players SET player_link = %s, rank = %s WHERE player_id = %s",
                (new_link, new_rank, pid)
            )
            print(f"✅ Updated player_id={pid} → rank={new_rank}, link='{new_link}'")

        else:
            # Player disappeared → rank=9999, link=''
            cur.execute(
                "UPDATE players SET player_link = '', rank = 9999 WHERE player_id = %s",
                (pid,)
            )
            print(f"⚠️ Player_id={pid} disappeared → rank=9999, link cleared")

    conn.commit()
    cur.close()
    conn.close()
    print("\n🎯 Update finished successfully!")

if __name__ == "__main__":
    update_player_links_and_ranks()
