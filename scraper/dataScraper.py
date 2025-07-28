import os
import time
import uuid
import psycopg2
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables (NEON DB credentials)
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

# Connect to Neon PostgreSQL
conn = psycopg2.connect(DB_URL)
cursor = conn.cursor()

players = [
    {"id": "PE", "url": "https://www.bordtennisportalen.dk/DBTU/Spiller/VisSpiller/#305214,59,7467481,42024"},
    {"id": "BH", "url": "https://www.bordtennisportalen.dk/DBTU/Spiller/VisSpiller/#343985,59,7467244,42024"},
    {"id": "CN", "url": "https://www.bordtennisportalen.dk/DBTU/Spiller/VisSpiller/#316342,59,7482751,42024"},
    {"id": "DS", "url": "https://www.bordtennisportalen.dk/DBTU/Spiller/VisSpiller/#142898,59,7452335,42024"},
    {"id": "FB", "url": "https://www.bordtennisportalen.dk/DBTU/Spiller/VisSpiller/#328783,59,7465770,42024"},
    {"id": "HP", "url": "https://www.bordtennisportalen.dk/DBTU/Spiller/VisSpiller/#343754,59,7478937,42024"},
    {"id": "HW", "url": "https://www.bordtennisportalen.dk/DBTU/Spiller/VisSpiller/#141533,59,7449840,42024"},
    {"id": "JOJ", "url": "https://www.bordtennisportalen.dk/DBTU/Spiller/VisSpiller/#340787,59,7478179,42024"},
    {"id": "JR", "url": "https://www.bordtennisportalen.dk/DBTU/Spiller/VisSpiller/#342680,59,7466419,42024"},
    {"id": "JK", "url": "https://www.bordtennisportalen.dk/DBTU/Spiller/VisSpiller/#137062,59,7446704,42024"},
    {"id": "KS", "url": "https://www.bordtennisportalen.dk/DBTU/Spiller/VisSpiller/#343104,59,7477982,42024"},
    {"id": "MB", "url": "https://www.bordtennisportalen.dk/DBTU/Spiller/VisSpiller/#151637,59,7470091,42024"},
    {"id": "MR", "url": "https://www.bordtennisportalen.dk/DBTU/Spiller/VisSpiller/#319070,59,7457754,42024"},
    {"id": "NK", "url": "https://www.bordtennisportalen.dk/DBTU/Spiller/VisSpiller/#317843,59,7481672,42024"},
    # {"id": "NZ", "url": "https://www.bordtennisportalen.dk/DBTU/Spiller/VisSpiller/#346720,59,7478163,42024"},
    {"id": "OE", "url": "https://www.bordtennisportalen.dk/DBTU/Spiller/VisSpiller/#319068,59,7457598,42024"},
    {"id": "SM", "url": "https://www.bordtennisportalen.dk/DBTU/Spiller/VisSpiller/#329787,59,7478266,42024"},
    {"id": "SN", "url": "https://www.bordtennisportalen.dk/DBTU/Spiller/VisSpiller/#326538,59,7470020,42024"},
    {"id": "TD", "url": "https://www.bordtennisportalen.dk/DBTU/Spiller/VisSpiller/#326539,59,7459788,42024"},
    {"id": "TJ", "url": "https://www.bordtennisportalen.dk/DBTU/Spiller/VisSpiller/#352646,59,7488554,42024"},
    {"id": "TL", "url": "https://www.bordtennisportalen.dk/DBTU/Spiller/VisSpiller/#145074,59,7452597,42024"},
    {"id": "NW", "url": "https://www.bordtennisportalen.dk/DBTU/Spiller/VisSpiller/#132936,59,7459242,42024"},
    {"id": "HS", "url": "https://www.bordtennisportalen.dk/DBTU/Spiller/VisSpiller/#347786,59,7484507,42024"},

    # Add other players here
]

def insert_games_into_postgres(data, player_id):
    """Insert only new games if there are more new than existing."""
    cursor.execute("SELECT COUNT(*) FROM games WHERE player_id = %s", (player_id,))
    existing_count = cursor.fetchone()[0]

    print(f"Existing records for player '{player_id}': {existing_count}")
    new_count = len(data)
    print(f"Scraped new entries for player '{player_id}': {new_count}")

    records_to_insert = new_count - existing_count
    if records_to_insert <= 0:
        print(f"No new records to insert for player '{player_id}'.")
        return

    entries_to_insert = data[-records_to_insert:]

    for entry in entries_to_insert:
        cursor.execute(
            """
            INSERT INTO games (game_id, game_date, opponent_name, opponent_link, opponent_rating, 
                               opponent_club, player_rating, gained_lost, tournament, player_id)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                str(uuid.uuid4()),
                entry["game_date"],
                entry["opponent_name"],
                entry["opponent_link"],
                entry["opponent_rating"],
                entry["opponent_club"],
                entry["player_rating"],
                entry["gained_lost"],
                entry["tournament"],
                entry["player_id"]
            )
        )
        print(f"Inserted new game for {player_id}: {entry['opponent_name']} on {entry['game_date']}")

    conn.commit()
    print(f"Inserted {records_to_insert} new records into Postgres for player '{player_id}'.")


def scrap_player(player):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(player["url"])
    time.sleep(7)  # wait for full load
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    table = soup.find('table', {'class': 'playerprofilerankingpointstable'})
    rows = table.find_all('tr')[2:]

    last_date = ""
    last_tournament = ""
    games = []

    for row in rows:
        cols = row.find_all('td')
        if not cols:
            continue

        current_date = cols[0].text.strip()
        if current_date:
            last_date = current_date

        current_tournament = cols[1].text.strip()
        if current_tournament:
            last_tournament = current_tournament

        # Extract opponent name and link
        td = cols[2]
        opponent_name = td.find('a').text.strip() if td.find('a') else ''
        opponent_link = td.find('a')['href'] if td.find('a') else ''

        # Extract opponent club safely even if it contains commas
        td_html = str(td)
        close_tag_index = td_html.find('</a>')
        if close_tag_index != -1:
            after_a = td_html[close_tag_index + len('</a>'):]
            after_a_soup = BeautifulSoup(after_a, 'html.parser')
            opponent_club = after_a_soup.get_text().strip()
            if opponent_club.startswith(','):
                opponent_club = opponent_club[1:].strip()
        else:
            opponent_club = 'default'

        points = [c.text.strip() for c in cols[3:6]]

        # ✅ Convert dd-mm-yyyy → yyyy-mm-dd
        try:
            parsed_date = datetime.strptime(last_date, "%d-%m-%Y").date()
        except ValueError:
            parsed_date = None

        # Convert points to integers, including negative gained_lost
        def to_int(value):
            try:
                return int(value)
            except ValueError:
                return None

        games.append({
            "game_date": parsed_date,
            "opponent_name": opponent_name,
            "opponent_link": opponent_link,
            "opponent_rating": to_int(points[1]),
            "player_rating": to_int(points[0]),
            "gained_lost": to_int(points[2]),
            "tournament": last_tournament,
            "player_id": player["id"],
            "opponent_club": opponent_club
        })

    insert_games_into_postgres(games, player["id"])


# Run scraping
for player in players:
    scrap_player(player)

cursor.close()
conn.close()
