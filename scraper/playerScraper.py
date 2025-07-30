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

# Load environment variables (NEON DB credentials)
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

BASE_URL = "https://www.bordtennisportalen.dk"

# ✅ Add all ranking URLs here
RANKING_URLS = [
    # Fredensborg rating list
    "https://www.bordtennisportalen.dk/DBTU/Ranglister/#59,42024,06/29/2025,0,,,4255,1,,,,,,,,0,,,,,,",
    # Gladsaxe rating list season 2024/2025
    "https://www.bordtennisportalen.dk/DBTU/Ranglister/#59,42024,06/29/2025,0,,,4260,1,,,,,,,,0,,,,,,",
]

def insert_into_database(players):
    """Insert scraped players into the PostgreSQL database."""
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    insert_query = """
    INSERT INTO players (player_id, rank, name, player_link, player_club, current_points)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (player_id) DO UPDATE
    SET rank = EXCLUDED.rank,
        name = EXCLUDED.name,
        player_link = EXCLUDED.player_link,
        player_club = EXCLUDED.player_club,
        current_points = EXCLUDED.current_points;
    """

    for p in players:
        cur.execute(insert_query, (
            p["player_id"],
            p["rank"],
            p["name"],
            p["player_link"],
            p["player_club"],
            int(p["current_points"]) if str(p["current_points"]).isdigit() else None
        ))

    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Inserted {len(players)} players into database.")

def scrape_rankings_from_url(url):
    """Scrape one ranking page."""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)
    time.sleep(7)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    table = soup.find("table", class_="RankingListGrid")
    if not table:
        print(f"⚠️ No table found on {url}")
        return []

    tbody = table.find("tbody")
    if not tbody:
        print(f"⚠️ No tbody on {url}")
        return []

    rows = tbody.find_all("tr")
    players = []

    for row in rows[1:]:
        cells = row.find_all("td")
        if len(cells) < 5:
            continue

        # ✅ Extract and clean rank
        rank_raw = cells[1].get_text(strip=True)
        rank_digits = re.sub(r"\D", "", rank_raw)  # keep only digits
        if not rank_digits:
            print(f"⏭️ Skipping player with invalid rank: {rank_raw}")
            continue
        rank = int(rank_digits)

        playerid = cells[2].get_text(strip=True)

        name_td = cells[3]
        a_tag = name_td.find('a')
        name = a_tag.text.strip() if a_tag else ''
        player_link = BASE_URL + a_tag['href'] if a_tag else ''

        full_text = name_td.get_text(separator=' ', strip=True)
        club_text = ''
        if name and full_text.startswith(name):
            club_text = full_text[len(name):].strip()
            if club_text.startswith(','):
                club_text = club_text[1:].strip()

        points = cells[4].get_text(strip=True)

        players.append({
            "player_id": playerid,
            "rank": rank,  # already an integer
            "name": name,
            "player_link": player_link,
            "player_club": club_text,
            "current_points": points
        })

    return players

def scrape_all_rankings():
    all_players = []
    for url in RANKING_URLS:
        print(f"\n🔹 Scraping: {url}")
        players = scrape_rankings_from_url(url)
        print(f"✅ Found {len(players)} players")
        all_players.extend(players)
    return all_players

if __name__ == "__main__":
    data = scrape_all_rankings()
    if data:
        insert_into_database(data)
    print("\n🎯 Done!")
