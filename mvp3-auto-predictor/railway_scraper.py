#!/usr/bin/env python3
"""
Railway Auto-Scraper Service for VCT Predictor
Runs daily at 3am to fetch fresh VLR.gg data
"""

import os
import sys
import time
import logging
import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
from flask import Flask, jsonify, request

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.database import MatchDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app for manual triggering
app = Flask(__name__)

class RailwayVCTScraper:
    def __init__(self):
        """Initialize the Railway scraper"""
        self.database_url = os.environ.get('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        self.db = MatchDatabase(self.database_url)
        self.scraper = cloudscraper.create_scraper()
        self.base_url = "https://www.vlr.gg"
        
        logger.info("🚀 Railway VCT Scraper initialized")
    
    def clean_team_name(self, team_name):
        """Clean team name by removing country suffixes"""
        # Remove common country suffixes
        suffixes = [
            'United States', 'Brazil', 'Canada', 'Mexico', 'Argentina',
            'Chile', 'Colombia', 'Peru', 'Uruguay', 'Paraguay',
            'Venezuela', 'Ecuador', 'Bolivia', 'Guyana', 'Suriname'
        ]
        
        for suffix in suffixes:
            if suffix in team_name:
                team_name = team_name.replace(suffix, '').strip()
                break
        
        return team_name
    
    def scrape_vct_standings(self):
        """Scrape VCT Americas standings from vlr.gg"""
        try:
            logger.info("🌐 Starting VCT standings scrape...")
            
            # VCT Americas Stage 2 standings URL
            url = f"{self.base_url}/event/standings/2025-americas-stage-2"
            
            # Fetch the page
            response = self.scraper.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the standings table
            standings_table = soup.find('table', class_='wf-table')
            if not standings_table:
                logger.error("❌ Could not find standings table")
                return False
            
            teams_data = []
            rows = standings_table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                try:
                    cells = row.find_all('td')
                    if len(cells) < 6:
                        continue
                    
                    # Extract team data
                    team_element = cells[1].find('div', class_='team-name')
                    if not team_element:
                        continue
                    
                    team_name = team_element.get_text(strip=True)
                    team_name = self.clean_team_name(team_name)
                    
                    # Extract record (W-L format)
                    record_cell = cells[2].get_text(strip=True)
                    if '-' in record_cell:
                        record = record_cell
                    else:
                        continue
                    
                    # Extract map differential
                    map_diff_cell = cells[3].get_text(strip=True)
                    if '/' in map_diff_cell:
                        map_diff = map_diff_cell
                    else:
                        continue
                    
                    # Extract round differential
                    round_diff_cell = cells[4].get_text(strip=True)
                    if '/' in round_diff_cell:
                        round_diff = round_diff_cell
                    else:
                        continue
                    
                    # Extract delta (round differential converted to number)
                    try:
                        if '/' in round_diff_cell:
                            wins, losses = map(int, round_diff_cell.split('/'))
                            delta = wins - losses
                        else:
                            delta = 0.0
                    except:
                        delta = 0.0
                    
                    # Determine group (Alpha or Omega)
                    # This is a simplified approach - you might need to adjust based on actual VCT structure
                    group_name = 'Alpha' if len(teams_data) < 6 else 'Omega'
                    
                    teams_data.append({
                        'group_name': group_name,
                        'team': team_name,
                        'record': record,
                        'map_diff': map_diff,
                        'round_diff': round_diff,
                        'delta': delta
                    })
                    
                    logger.info(f"✅ Scraped: {team_name} ({group_name}) - {record}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to parse team row: {e}")
                    continue
            
            if not teams_data:
                logger.error("❌ No team data extracted")
                return False
            
            logger.info(f"📊 Successfully scraped {len(teams_data)} teams")
            return teams_data
            
        except Exception as e:
            logger.error(f"❌ Scraping failed: {e}")
            return False
    
    def update_database(self, teams_data):
        """Update database with scraped team data"""
        try:
            logger.info("💾 Updating database...")
            
            # Clear existing data
            # Note: In production, you might want to keep historical data
            # For now, we'll replace the data
            
            # Insert new team data
            for team_data in teams_data:
                self.db.insert_match_data(
                    group=team_data['group_name'],
                    team=team_data['team'],
                    record=team_data['record'],
                    map_diff=team_data['map_diff'],
                    round_diff=team_data['round_diff'],
                    delta=team_data['delta']
                )
            
            # Update scraper health
            self.db.update_scraper_health(
                status='success',
                success_count=1,
                total_runs=1
            )
            
            logger.info("✅ Database updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database update failed: {e}")
            
            # Update scraper health with error
            self.db.update_scraper_health(
                status='error',
                success_count=0,
                total_runs=1,
                error_message=str(e)
            )
            return False
    
    def run_scrape(self):
        """Main scraping method"""
        start_time = time.time()
        logger.info("🚀 Starting VCT data scrape...")
        
        try:
            # Scrape VLR.gg
            teams_data = self.scrape_vct_standings()
            if not teams_data:
                logger.error("❌ Scraping failed, aborting database update")
                return False
            
            # Update database
            success = self.update_database(teams_data)
            
            elapsed_time = time.time() - start_time
            if success:
                logger.info(f"🎉 Scrape completed successfully in {elapsed_time:.2f}s")
            else:
                logger.error(f"❌ Scrape failed after {elapsed_time:.2f}s")
            
            return success
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"❌ Scrape crashed after {elapsed_time:.2f}s: {e}")
            
            # Update scraper health with error
            try:
                self.db.update_scraper_health(
                    status='error',
                    success_count=0,
                    total_runs=1,
                    error_message=str(e)
                )
            except:
                pass
            
            return False

# Global scraper instance
scraper = None

@app.route('/')
def home():
    """Home page showing scraper status"""
    try:
        if scraper:
            health = scraper.db.get_scraper_health()
            teams = scraper.db.get_all_teams_with_stats()
            return jsonify({
                'status': 'running',
                'scraper_health': health,
                'teams_count': len(teams),
                'message': 'VCT Scraper is running. Use /run-scrape to trigger manual scrape.'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Scraper not initialized'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/run-scrape')
def run_scrape():
    """Manually trigger the scraper"""
    try:
        if not scraper:
            return jsonify({
                'status': 'error',
                'message': 'Scraper not initialized'
            }), 500
        
        success = scraper.run_scrape()
        
        if success:
            teams = scraper.db.get_all_teams_with_stats()
            return jsonify({
                'status': 'success',
                'message': f'Scrape completed successfully. {len(teams)} teams in database.',
                'teams_count': len(teams)
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Scrape failed. Check logs for details.'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        if scraper:
            health_data = scraper.db.get_scraper_health()
            return jsonify(health_data)
        else:
            return jsonify({
                'status': 'error',
                'message': 'Scraper not initialized'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def main():
    """Main entry point for Railway scraper"""
    global scraper
    
    try:
        scraper = RailwayVCTScraper()
        logger.info("✅ Scraper initialized successfully")
        
        # Run initial scrape
        logger.info("🚀 Running initial scrape...")
        success = scraper.run_scrape()
        
        if success:
            logger.info("✅ Initial scrape completed successfully")
        else:
            logger.warning("⚠️ Initial scrape failed, but service is running")
        
        # Start Flask app for manual triggering
        logger.info("🌐 Starting Flask web interface...")
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
        
    except Exception as e:
        logger.error(f"❌ Scraper initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
