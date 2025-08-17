import os
import sys
import io
import time
import uuid
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

# Example ranking URLs
RANKING_URLS = [
    # 25/26
        # Gladsaxe
    "https://www.bordtennisportalen.dk/DBTU/Ranglister/#59,42025,08/15/2025,0,,,4260,1,,,,,,,,0,,,,,,",
        # Fredensborg
    "https://www.bordtennisportalen.dk/DBTU/Ranglister/#59,42025,08/15/2025,0,,,4255,1,,,,,,,,0,,,,,,",
    # 24/25
        # Gladsaxe
    # "https://www.bordtennisportalen.dk/DBTU/Ranglister/#59,42024,06/29/2025,0,,,4260,1,,,,,,,,0,,,,,,",
        # Fredensborg
    # "https://www.bordtennisportalen.dk/DBTU/Ranglister/#59,42024,06/29/2025,0,,,4255,1,,,,,,,,0,,,,,,",
    # 23/24
        # Gladsaxe
    # "https://www.bordtennisportalen.dk/DBTU/Ranglister/#59,42023,06/21/2024,0,,,4260,1,,,,,,,,0,,,,,,",
        # Fredensborg
    # "https://www.bordtennisportalen.dk/DBTU/Ranglister/#59,42023,06/21/2024,0,,,4255,1,,,,,,,,0,,,,,,",
    # 22/23
        # Gladsaxe
    # "https://www.bordtennisportalen.dk/DBTU/Ranglister/#59,42022,06/23/2023,0,,,4260,1,,,,,,,,0,,,,,,",
        # Fredensborg
    # "https://www.bordtennisportalen.dk/DBTU/Ranglister/#59,42022,06/23/2023,0,,,4255,1,,,,,,,,0,,,,,,",
    # 21/22
        # Gladsaxe
    # "https://www.bordtennisportalen.dk/DBTU/Ranglister/#59,42021,06/24/2022,0,,,4260,1,,,,,,,,0,,,,,,",
        # Fredensborg
    # "https://www.bordtennisportalen.dk/DBTU/Ranglister/#59,42021,06/24/2022,0,,,4255,1,,,,,,,,0,,,,,,",
    # 20/21
        # Gladsaxe
    # "https://www.bordtennisportalen.dk/DBTU/Ranglister/#59,42020,07/01/2021,0,,,4260,1,,,,,,,,0,,,,,,",
        # Fredensborg
    # "https://www.bordtennisportalen.dk/DBTU/Ranglister/#59,42020,07/01/2021,0,,,4255,1,,,,,,,,0,,,,,,",
    # 19/20
        # Gladsaxe
    # "https://www.bordtennisportalen.dk/DBTU/Ranglister/#59,42019,08/13/2020,0,,,4260,1,,,,,,,,0,,,,,,",
        # Fredensborg
    # "https://www.bordtennisportalen.dk/DBTU/Ranglister/#59,42019,08/13/2020,0,,,4255,1,,,,,,,,0,,,,,,",
]


# Connect to Neon PostgreSQL
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

def scrape_players(url):
    print(f"\n🔹 Scraping: {url}")
    season = extract_season_from_url(url)
    print(f"📅 Season detected: {season}")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)
    time.sleep(7)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

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

        # Club
        full_text = name_td.get_text(separator=' ', strip=True)
        club_text = ""
        if name and full_text.startswith(name):
            club_text = full_text[len(name):].strip()
            if club_text.startswith(","):
                club_text = club_text[1:].strip()

        # Points
        points = cells[4].get_text(strip=True)
        current_points = int(points) if points.isdigit() else None

        players.append({
            "name": name,
            "rank": rank,
            "player_link": player_link,
            "player_club": club_text,
            "current_points": current_points
        })

    print(f"✅ Found {len(players)} players")
    return players, season

def insert_players(players_data, season):
    for p in players_data:
        # Get user_id from users table
        cur.execute("SELECT user_id FROM users WHERE name = %s", (p["name"],))
        user_row = cur.fetchone()
        if not user_row:
            print(f"⚠ User not found for {p['name']}, skipping...")
            continue
        user_id = user_row[0]

        # Check if this user already has a player entry for this season
        cur.execute("""
            SELECT 1 FROM players WHERE user_id = %s AND season = %s
        """, (user_id, season))
        existing = cur.fetchone()

        if existing:
            print(f"⏩ Player {p['name']} already exists for season {season}, skipping...")
            continue

        # Insert new season entry
        cur.execute("""
            INSERT INTO players (player_id, rank, season, player_link, player_club, current_points, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            str(uuid.uuid4()),
            p["rank"],
            season,
            p["player_link"],
            p["player_club"],
            p["current_points"],
            user_id
        ))
        print(f"✅ Inserted player: {p['name']} ({season})")

    conn.commit()
    print("✅ All players processed.\n")

# Main loop
for url in RANKING_URLS:
    scraped_players, season = scrape_players(url)
    insert_players(scraped_players, season)

cur.close()
conn.close()
print("✅ Scraping finished, connection closed.")
