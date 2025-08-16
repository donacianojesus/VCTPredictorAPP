from db import MatchDatabase
import cloudscraper
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

EVENT_URL = "https://www.vlr.gg/event/2501/vct-2025-americas-stage-2"

def scrape_group_standings():
    logger.debug(f"Starting scrape from {EVENT_URL}")
    
    scraper = cloudscraper.create_scraper()
    response = scraper.get(EVENT_URL, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    standings_data = []

    # Debug HTML structure
    with open('debug.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())

    # Updated selectors based on actual HTML structure
    group_cards = soup.select(".event-group")
    logger.debug(f"Found {len(group_cards)} group cards")

    for card in group_cards:
        try:
            # Get group name
            header = card.select_one("th.mod-title")
            if not header:
                continue
                
            group_name = header.get_text(strip=True).replace("Group ", "")
            logger.debug(f"Processing group: {group_name}")

            # Get team rows
            rows = card.select("tbody tr")
            logger.debug(f"Found {len(rows)} team rows in group {group_name}")

            for row in rows:
                try:
                    # Get team name (more precise selector)
                    team_name_elem = row.select_one(".event-group-team-name")
                    if not team_name_elem:
                        continue
                    team_name = team_name_elem.get_text(strip=True)

                    # Get stats cells
                    cells = row.select("td.mod-stat")
                    if len(cells) < 4:
                        continue

                    # Extract data
                    record = cells[0].get_text(strip=True)
                    map_diff = cells[1].get_text(strip=True)
                    round_diff = cells[2].get_text(strip=True)
                    delta = cells[3].select_one(".diff").get_text(strip=True)

                    logger.debug(f"""
                    Found team data:
                    - Team: {team_name}
                    - Record: {record}
                    - Map Diff: {map_diff}
                    - Round Diff: {round_diff}
                    - Delta: {delta}
                    """)

                    standings_data.append((
                        group_name,
                        team_name,
                        record,
                        map_diff,
                        round_diff,
                        delta
                    ))

                except Exception as e:
                    logger.error(f"Error processing row: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Error processing group card: {str(e)}")
            continue

    logger.debug(f"Scraped {len(standings_data)} total standings entries")
    return standings_data

def save_to_db(standings_data):
    """Save scraped standings data to database"""
    logger.debug(f"Saving {len(standings_data)} records to database")
    
    db = MatchDatabase('val_standings.db')
    saved_count = 0
    
    for group_name, team, record, map_diff, round_diff, delta in standings_data:
        try:
            # Clean the data
            team = team.replace('United States', '').replace('Brazil', '').replace('Argentina', '').strip()
            map_diff = map_diff.strip()
            round_diff = round_diff.strip() 
            delta = delta.replace('+', '').strip()
            
            logger.debug(f"""
            Saving team data:
            - Group: {group_name}
            - Team: {team}
            - Record: {record}
            - Map Diff: {map_diff}
            - Round Diff: {round_diff}
            - Delta: {delta}
            """)
            
            db.insert_match_data(
                group=group_name,
                team=team,
                record=record,
                map_diff=map_diff,
                round_diff=round_diff,
                delta=delta
            )
            saved_count += 1
            
        except Exception as e:
            logger.error(f"Error saving {team}: {str(e)}")
            continue
    
    return saved_count

if __name__ == "__main__":
    try:
        standings = scrape_group_standings()
        if standings:
            print(f"✅ Scraped {len(standings)} standings entries")
            for entry in standings:
                print(f"- {entry[1]}: {entry[2]} ({entry[0]})")
                
            # Save to database
            saved_count = save_to_db(standings)
            print(f"✅ Saved {saved_count} records to database")
        else:
            print("❌ No standings data was scraped!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
