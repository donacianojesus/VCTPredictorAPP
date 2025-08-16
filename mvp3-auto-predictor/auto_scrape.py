#!/usr/bin/env python3
from scraper import scrape_group_standings, save_to_db
import logging
import os
from datetime import datetime
import sys
import traceback

# Absolute path configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "auto_scraper.log")
DB_FILE = os.path.join(BASE_DIR, "val_standings.db")

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def run_scraper():
    try:
        logger.info("=" * 50)
        logger.info(f"Starting scheduled scrape at {datetime.now()}")
        
        # Backup database before scraping
        if os.path.exists(DB_FILE):
            backup_file = f"{DB_FILE}.backup"
            os.system(f"cp {DB_FILE} {backup_file}")
            logger.info(f"Created database backup: {backup_file}")
        
        # Run scraper
        standings = scrape_group_standings()
        
        if standings:
            saved_count = save_to_db(standings)
            logger.info(f"Successfully saved {saved_count} records to database")
            
            if saved_count == 0:
                logger.warning("No new records were saved")
        else:
            logger.error("No standings data was scraped")
            
    except Exception as e:
        logger.error(f"Scheduled scraper failed: {str(e)}")
        logger.error(traceback.format_exc())
        
    finally:
        logger.info(f"Scrape completed at {datetime.now()}")
        logger.info("=" * 50)

if __name__ == "__main__":
    run_scraper()