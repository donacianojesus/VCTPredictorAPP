from app.services.database import MatchDatabase
import cloudscraper
from bs4 import BeautifulSoup
import logging
import os

# Set up logging configuration with file handler
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "scraper.log")
DB_PATH = os.path.join(BASE_DIR, "val_standings.db")

# Configure logging once at module level
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
# Create module-level logger
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

# Update save_to_db function
def save_to_db(standings_data, db_path=DB_PATH):
    """Save scraped standings data to database"""
    # Use module-level logger instead of creating new one
    global logger
    
    try:
        logger.debug(f"Saving {len(standings_data)} records to database at {db_path}")
        
        db = MatchDatabase(db_path)
        saved_count = 0
        
        for group_name, team, record, map_diff, round_diff, delta in standings_data:
            try:
                # Enhanced team name cleaning
                team_clean = clean_team_name(team)
                
                # Validate data before saving
                if not validate_team_data(team_clean, record, map_diff, round_diff, delta):
                    logger.warning(f"Skipping invalid data for {team_clean}: record={record}, map_diff={map_diff}, round_diff={round_diff}, delta={delta}")
                    continue
                
                # Extract numeric values from map_diff and round_diff
                try:
                    # Handle different formats for map_diff and round_diff
                    # They can come as "6/2" or "6-2" format, but we'll save as "6/2"
                    if '/' in map_diff:
                        map_wins, map_losses = map_diff.split('/')
                    elif '–' in map_diff:  # en dash
                        map_wins, map_losses = map_diff.split('–')
                    elif '—' in map_diff:  # em dash
                        map_wins, map_losses = map_diff.split('—')
                    elif '-' in map_diff:  # regular hyphen
                        map_wins, map_losses = map_diff.split('-')
                    else:
                        map_wins, map_losses = map_diff, '0'
                    
                    if '/' in round_diff:
                        round_wins, round_losses = round_diff.split('/')
                    elif '–' in round_diff:  # en dash
                        round_wins, round_losses = round_diff.split('–')
                    elif '—' in round_diff:  # em dash
                        round_wins, round_losses = round_diff.split('—')
                    elif '-' in round_diff:  # regular hyphen
                        round_wins, round_losses = round_diff.split('-')
                    else:
                        round_wins, round_losses = round_diff, '0'
                    
                    # Clean delta value
                    delta_clean = float(delta.replace('+', '').strip())
                    
                    db.insert_match_data(
                        group=group_name,
                        team=team_clean,
                        record=record,
                        map_diff=f"{map_wins}/{map_losses}",  # Use "/" format
                        round_diff=f"{round_wins}/{round_losses}",  # Use "/" format
                        delta=delta_clean
                    )
                    saved_count += 1
                    logger.debug(f"Saved {team_clean} data successfully")
                    
                except ValueError as e:
                    logger.error(f"Data parsing error for {team_clean}: {e}")
                    continue
                
            except Exception as e:
                logger.error(f"Error saving {team}: {str(e)}")
                continue
        
        logger.info(f"Successfully saved {saved_count} records")
        return saved_count
        
    except Exception as e:
        logger.error(f"Database save operation failed: {str(e)}")
        return 0

def clean_team_name(team_name):
    """Clean and standardize team names"""
    # Remove country suffixes that sometimes get appended
    country_suffixes = [
        'United States', 'Brazil', 'Argentina', 'Canada', 'Mexico',
        'Chile', 'Colombia', 'Peru', 'Uruguay', 'Paraguay'
    ]
    
    cleaned_name = team_name
    for suffix in country_suffixes:
        if suffix in cleaned_name:
            cleaned_name = cleaned_name.replace(suffix, '').strip()
    
    # Handle specific team name variations
    team_variations = {
        '2Game Esports': '2G',
        'VISA KRÜ': 'KRÜ',
        'LEVIATÁN': 'LEV',
        'Evil Geniuses': 'EG',
        '100 Thieves': '100T',
        'Cloud9': 'C9',
        'G2 Esports': 'G2',
        'Sentinels': 'SEN',
        'FURIA': 'FUR',
        'LOUD': 'LOUD',
        'MIBR': 'MIBR',
        'NRG': 'NRG'
    }
    
    # Try to find exact match first
    for full_name, short_name in team_variations.items():
        if cleaned_name == full_name:
            return short_name
    
    # If no exact match, return cleaned name
    return cleaned_name

def validate_team_data(team_name, record, map_diff, round_diff, delta):
    """Validate scraped data before saving"""
    try:
        # Check team name
        if not team_name or len(team_name.strip()) < 2:
            return False
        
        # Check record format (should be like "3-1" or "3–1")
        if not record:
            return False
        
        # Accept any dash type in record
        if not any(dash in record for dash in ['-', '–', '—']):
            return False
        
        # Check map_diff format (should be like "6/2" or "6-2")
        if not map_diff:
            return False
        
        # Accept both slash and dash formats
        if not any(separator in map_diff for separator in ['/', '-', '–', '—']):
            return False
        
        # Check round_diff format (should be like "92/60" or "92-60")
        if not round_diff:
            return False
        
        # Accept both slash and dash formats
        if not any(separator in round_diff for separator in ['/', '-', '–', '—']):
            return False
        
        # Check delta (should be a number, possibly with + or -)
        delta_str = str(delta).replace('+', '').replace('-', '')
        try:
            float(delta_str)
        except ValueError:
            return False
        
        return True
        
    except Exception:
        return False

if __name__ == "__main__":
    try:
        standings = scrape_group_standings()
        if standings:
            logger.info(f"✅ Scraped {len(standings)} standings entries")
            for entry in standings:
                logger.debug(f"- {entry[1]}: {entry[2]} ({entry[0]})")
                
            # Save to database
            saved_count = save_to_db(standings)
            logger.info(f"✅ Saved {saved_count} records to database")
        else:
            logger.error("❌ No standings data was scraped!")
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
