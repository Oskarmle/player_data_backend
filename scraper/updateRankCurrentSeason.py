import os
import sys
import io
import time
import re
import psycopg2
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

BASE_URL = "https://www.bordtennisportalen.dk"

# Add your club ranking URLs here
RANKING_URLS = [
    # Gladsaxe
    "https://www.bordtennisportalen.dk/DBTU/Ranglister/#59,42025,08/29/2025,0,,,4260,1,,,,,,,,0,,,,,,",
    # Fredensborg
    "https://www.bordtennisportalen.dk/DBTU/Ranglister/#59,42025,08/29/2025,0,,,4255,1,,,,,,,,0,,,,,,",
]

# Connect to PostgreSQL
conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

def extract_season_from_url(url: str) -> str:
    """Extract the season (yyyy/yyyy) from the update date in the URL."""
    match = re.search(r"(\d{2}/\d{2}/\d{4})", url)
    if not match:
        return "unknown"

    date_str = match.group(1)
    date_obj = datetime.strptime(date_str, "%m/%d/%Y")

    year = date_obj.year
    month = date_obj.month

    if month >= 7:  # July → December
        season = f"{year}/{year+1}"
    else:  # January → June
        season = f"{year-1}/{year}"

    return season

def scrape_players(driver, url):
    """Scrape players from a ranking URL using the existing driver session."""
    print(f"\n🔹 Scraping ranking list: {url}")
    season = extract_season_from_url(url)
    print(f"📅 Season detected: {season}")

    driver.get(url)
    time.sleep(7)  # wait for table to load
    soup = BeautifulSoup(driver.page_source, "html.parser")

    table = soup.find("table", class_="RankingListGrid")
    if not table:
        print(f"❌ No table found on {url}")
        return [], season

    tbody = table.find("tbody")
    rows = tbody.find_all("tr") if tbody else []
    players = []

    for row in rows[1:]:  # skip header
        cells = row.find_all("td")
        if len(cells) < 5:
            continue

        # Rank
        rank_raw = cells[1].get_text(strip=True)
        rank_digits = re.sub(r"\D", "", rank_raw)
        rank = int(rank_digits) if rank_digits else None

        # Player name and link
        name_td = cells[3]
        a_tag = name_td.find("a")
        name = a_tag.text.strip() if a_tag else ""
        player_link = BASE_URL + a_tag['href'] if a_tag else ""

        # Points
        points = cells[4].get_text(strip=True)
        current_points = int(points) if points.isdigit() else None

        players.append({
            "name": name,
            "rank": rank,
            "player_link": player_link,
            "current_points": current_points
        })

    print(f"✅ Found {len(players)} players in ranking list")
    return players, season

def update_players(players_data, season):
    updated_count = 0
    skipped_count = 0

    for p in players_data:
        cur.execute("SELECT user_id FROM users WHERE name = %s", (p["name"],))
        user_row = cur.fetchone()
        if not user_row:
            print(f"⚠ User not found for {p['name']}, skipping...")
            skipped_count += 1
            continue
        user_id = user_row[0]

        # Update player record for the current season (rank, points, link only)
        cur.execute("""
            UPDATE players
            SET rank = %s,
                player_link = %s,
                current_points = %s
            WHERE user_id = %s AND season = %s
        """, (
            p["rank"],
            p["player_link"],
            p["current_points"],
            user_id,
            season
        ))

        if cur.rowcount > 0:
            print(f"🔄 Updated {p['name']} ({season}) → Rank {p['rank']}")
            updated_count += 1
        else:
            print(f"⚠ No existing record for {p['name']} in season {season}, skipped")
            skipped_count += 1

    conn.commit()
    print(f"\n✅ Update complete for {season}: {updated_count} players updated, {skipped_count} skipped.\n")

# --- Run ---
# Start a single Chrome session for all URLs
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

for url in RANKING_URLS:
    scraped_players, season = scrape_players(driver, url)
    update_players(scraped_players, season)

driver.quit()
cur.close()
conn.close()
print("✅ Finished updating ranks for all URLs, connection closed.")
