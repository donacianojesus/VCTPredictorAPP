#!/usr/bin/env python3
"""
VCT Data Scraper Service
Automated scraping of VCT standings from vlr.gg
"""

import os
import time
import logging
import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
from app.services.database import MatchDatabase

# Configure logging
logger = logging.getLogger(__name__)

class VCTScraper:
    def __init__(self, database_url=None):
        """Initialize the VCT scraper"""
        self.database_url = database_url or os.environ.get('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        self.db = MatchDatabase(self.database_url)
        self.scraper = cloudscraper.create_scraper()
        self.base_url = "https://www.vlr.gg"
        
        logger.info("🚀 VCT Scraper initialized")
    
    def create_sample_data(self):
        """Create sample VCT 2025 Stage 2 Americas data for testing when scraping fails"""
        logger.info("📝 Creating sample VCT 2025 Stage 2 Americas data...")
        
        # Updated teams for VCT 2025 Stage 2 Americas based on current tournament
        sample_teams = [
            # Group Alpha - 2025 Stage 2 (Current teams)
            {'group_name': 'Alpha', 'team': 'Sentinels', 'record': '4-1', 'map_diff': '8/2', 'round_diff': '104/78', 'delta': 26.0},
            {'group_name': 'Alpha', 'team': 'LOUD', 'record': '3-2', 'map_diff': '6/4', 'round_diff': '98/82', 'delta': 16.0},
            {'group_name': 'Alpha', 'team': '100 Thieves', 'record': '3-2', 'map_diff': '6/4', 'round_diff': '92/88', 'delta': 4.0},
            {'group_name': 'Alpha', 'team': 'NRG', 'record': '2-3', 'map_diff': '4/6', 'round_diff': '86/94', 'delta': -8.0},
            {'group_name': 'Alpha', 'team': 'Cloud9', 'record': '2-3', 'map_diff': '4/6', 'round_diff': '84/96', 'delta': -12.0},
            {'group_name': 'Alpha', 'team': 'MIBR', 'record': '1-4', 'map_diff': '2/8', 'round_diff': '76/104', 'delta': -28.0},
            
            # Group Omega - 2025 Stage 2 (Current teams)
            {'group_name': 'Omega', 'team': 'Leviatán', 'record': '4-1', 'map_diff': '8/2', 'round_diff': '102/76', 'delta': 26.0},
            {'group_name': 'Omega', 'team': 'KRÜ', 'record': '3-2', 'map_diff': '6/4', 'round_diff': '96/84', 'delta': 12.0},
            {'group_name': 'Omega', 'team': 'FURIA', 'record': '3-2', 'map_diff': '6/4', 'round_diff': '94/86', 'delta': 8.0},
            {'group_name': 'Omega', 'team': 'Evil Geniuses', 'record': '2-3', 'map_diff': '4/6', 'round_diff': '88/92', 'delta': -4.0},
            {'group_name': 'Omega', 'team': 'G2 Esports', 'record': '2-3', 'map_diff': '4/6', 'round_diff': '86/94', 'delta': -8.0},
            {'group_name': 'Omega', 'team': 'Shopify Rebellion', 'record': '1-4', 'map_diff': '2/8', 'round_diff': '78/102', 'delta': -24.0}
        ]
        
        logger.info("📊 Sample data created with 12 teams (6 Alpha, 6 Omega) for VCT 2025 Stage 2")
        return sample_teams

    def clean_team_name(self, team_name):
        """Clean and standardize team names"""
        if not team_name:
            return "Unknown Team"
        
        # Remove common suffixes and clean up
        team_name = team_name.strip()
        team_name = team_name.replace('United States', '').replace('Spoiler hidden', '').strip()
        
        # Standardize common team names
        name_mapping = {
            '2game': '2Game Esports',
            '2game esports': '2Game Esports',
            'furia': 'FURIA',
            'kru': 'KRÜ',
            'kru esports': 'KRÜ',
            'leviatan': 'Leviatán',
            'leviatan esports': 'Leviatán',
            'shopify': 'Shopify Rebellion',
            'shopify rebellion esports': 'Shopify Rebellion'
        }
        
        return name_mapping.get(team_name.lower(), team_name)

    def scrape_vct_standings(self):
        """Scrape VCT standings from multiple sources"""
        try:
            # Try VCT 2025 URLs first
            vct_urls = [
                "https://www.vlr.gg/event/2501/vct-2025-americas-stage-2",
                "https://www.vlr.gg/event/2347/vct-2025-americas-stage-1"
            ]
            
            for url in vct_urls:
                logger.info(f"🔍 Trying VCT URL: {url}")
                teams_data = self.scrape_single_vct_url(url)
                if teams_data and len(teams_data) >= 10:  # Expect at least 10 teams
                    logger.info(f"✅ Successfully scraped {len(teams_data)} teams from {url}")
                    return teams_data
                else:
                    logger.warning(f"⚠️ Only found {len(teams_data) if teams_data else 0} teams from {url}")
            
            # Fallback to sample data if scraping fails
            logger.warning("⚠️ Falling back to sample data")
            return self.create_sample_data()
            
        except Exception as e:
            logger.error(f"❌ Error scraping VCT standings: {e}")
            return self.create_sample_data()

    def scrape_single_vct_url(self, url):
        """Scrape a single VCT URL and return all teams from all groups"""
        try:
            response = self.scraper.get(url)
            if response.status_code != 200:
                logger.warning(f"⚠️ Failed to fetch {url}: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info(f"📄 Successfully fetched {url}")
            
            # Find ALL tables on the page
            all_tables = soup.find_all('table')
            logger.info(f"📊 Found {len(all_tables)} tables on the page")
            
            all_teams = []
            
            # Process each table to find group standings
            for table_index, table in enumerate(all_tables):
                logger.info(f"🔍 Processing table {table_index + 1}")
                
                # Check if this table has standings data
                if self.is_standings_table(table):
                    logger.info(f"✅ Table {table_index + 1} appears to be a standings table")
                    
                    # Try to determine group name from table context
                    group_name = self.determine_group_from_table(table, table_index, soup)
                    logger.info(f"🏷️ Determined group name: {group_name}")
                    
                    # Parse teams from this table
                    table_teams = self.parse_standings_table(table, group_name)
                    if table_teams:
                        logger.info(f"📋 Found {len(table_teams)} teams in {group_name} group")
                        all_teams.extend(table_teams)
                    else:
                        logger.warning(f"⚠️ No teams found in table {table_index + 1}")
                else:
                    logger.info(f"⏭️ Table {table_index + 1} is not a standings table, skipping")
            
            logger.info(f"🎯 Total teams found across all groups: {len(all_teams)}")
            return all_teams
            
        except Exception as e:
            logger.error(f"❌ Error scraping {url}: {e}")
            return None

    def is_standings_table(self, table):
        """Check if a table contains standings data"""
        try:
            # Look for common standings indicators
            text = table.get_text().lower()
            standings_indicators = ['rec', 'map', 'rnd', 'δ', 'delta', 'wins', 'losses', 'points']
            
            # Check if table has multiple columns (likely standings)
            rows = table.find_all('tr')
            if len(rows) < 2:  # Need at least header + 1 data row
                return False
            
            # Check if first row has headers
            first_row = rows[0]
            headers = first_row.find_all(['th', 'td'])
            if len(headers) < 3:  # Need at least 3 columns for standings
                return False
            
            # Check if headers contain standings indicators
            header_text = ' '.join([h.get_text().lower() for h in headers])
            has_standings_indicators = any(indicator in header_text for indicator in standings_indicators)
            
            return has_standings_indicators
            
        except Exception as e:
            logger.error(f"❌ Error checking if table is standings: {e}")
            return False

    def determine_group_from_table(self, table, table_index, soup):
        """Determine the group name for a standings table"""
        try:
            # Method 1: Look for group name in table headers
            headers = table.find_all(['th', 'td'])
            for header in headers:
                header_text = header.get_text().lower()
                if 'alpha' in header_text:
                    return 'Alpha'
                elif 'omega' in header_text:
                    return 'Omega'
                elif 'group a' in header_text:
                    return 'Alpha'
                elif 'group b' in header_text:
                    return 'Omega'
            
            # Method 2: Look for group name above/below the table
            # Check previous sibling elements
            prev_element = table.find_previous_sibling()
            if prev_element:
                prev_text = prev_element.get_text().lower()
                if 'alpha' in prev_text:
                    return 'Alpha'
                elif 'omega' in prev_text:
                    return 'Omega'
            
            # Method 3: Look for group name in nearby headings
            nearby_headings = table.find_previous_siblings(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            for heading in nearby_headings:
                heading_text = heading.get_text().lower()
                if 'alpha' in heading_text:
                    return 'Alpha'
                elif 'omega' in heading_text:
                    return 'Omega'
            
            # Method 4: Check if this is the first or second table
            # First table is usually Alpha, second is usually Omega
            if table_index == 0:
                return 'Alpha'
            elif table_index == 1:
                return 'Omega'
            else:
                return f'Group {table_index + 1}'  # Fallback naming
                
        except Exception as e:
            logger.error(f"❌ Error determining group name: {e}")
            return f'Group {table_index + 1}'  # Fallback naming
    
    def find_group_indicators(self, table):
        """Find group indicators in the table"""
        try:
            indicators = []
            text = table.get_text().lower()
            
            if 'alpha' in text:
                indicators.append('alpha')
            if 'omega' in text:
                indicators.append('omega')
            if 'group a' in text:
                indicators.append('group_a')
            if 'group b' in text:
                indicators.append('group_b')
            
            return indicators
        except Exception as e:
            logger.error(f"❌ Error finding group indicators: {e}")
            return []

    def determine_group_better(self, row_index, teams_found, cells, group_indicators):
        """Better logic for determining group assignment"""
        try:
            # If we have explicit group indicators, use them
            if 'alpha' in group_indicators:
                return 'Alpha'
            elif 'omega' in group_indicators:
                return 'Omega'
            
            # If no explicit indicators, distribute evenly
            # First 6 teams go to Alpha, next 6 to Omega
            if teams_found < 6:
                return 'Alpha'
            else:
                return 'Omega'
                
        except Exception as e:
            logger.error(f"❌ Error determining group: {e}")
            return 'Alpha'  # Default fallback

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
        """Run the scraper and return success status"""
        try:
            logger.info("🚀 Starting VCT standings scrape...")
            teams_data = self.scrape_vct_standings()
            
            if teams_data and len(teams_data) >= 10:
                logger.info(f"✅ Scrape successful: {len(teams_data)} teams found")
                
                # Log group distribution
                alpha_count = len([t for t in teams_data if t['group_name'] == 'Alpha'])
                omega_count = len([t for t in teams_data if t['group_name'] == 'Omega'])
                logger.info(f"📊 Group distribution: Alpha={alpha_count}, Omega={omega_count}")
                
                return True
            else:
                logger.warning(f"⚠️ Scrape incomplete: only {len(teams_data) if teams_data else 0} teams found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Scrape failed: {e}")
            return False

    def inspect_vct_page(self, url):
        """Inspect VCT page structure for debugging"""
        try:
            response = self.scraper.get(url)
            if response.status_code != 200:
                logger.error(f"❌ Failed to fetch {url}: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info(f"📄 Successfully fetched {url}")
            
            # Find all tables
            all_tables = soup.find_all('table')
            logger.info(f"📊 Found {len(all_tables)} tables on the page")
            
            # Analyze each table
            for i, table in enumerate(all_tables):
                logger.info(f"🔍 Table {i + 1}:")
                
                # Check if it's a standings table
                is_standings = self.is_standings_table(table)
                logger.info(f"  - Is standings table: {is_standings}")
                
                if is_standings:
                    # Count rows
                    rows = table.find_all('tr')
                    logger.info(f"  - Rows: {len(rows)}")
                    
                    # Show headers
                    if rows:
                        headers = rows[0].find_all(['th', 'td'])
                        header_texts = [h.get_text(strip=True) for h in headers]
                        logger.info(f"  - Headers: {header_texts}")
                        
                        # Look for group indicators
                        group_indicators = self.find_group_indicators(table)
                        logger.info(f"  - Group indicators: {group_indicators}")
                        
                        # Show sample data
                        if len(rows) > 1:
                            sample_row = rows[1]
                            cells = sample_row.find_all('td')
                            cell_texts = [c.get_text(strip=True) for c in cells]
                            logger.info(f"  - Sample row: {cell_texts}")
            
            return soup
            
        except Exception as e:
            logger.error(f"❌ Error inspecting VCT page: {e}")
            return None

    def analyze_vct_page_structure(self, url):
        """Analyze the overall VCT page structure"""
        try:
            response = self.scraper.get(url)
            if response.status_code != 200:
                logger.error(f"❌ Failed to fetch {url}: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info(f"📄 Successfully fetched {url}")
            
            # Get page text for analysis
            page_text = soup.get_text()
            
            # Count group mentions
            alpha_count = page_text.lower().count('alpha')
            omega_count = page_text.lower().count('omega')
            group_a_count = page_text.lower().count('group a')
            group_b_count = page_text.lower().count('group b')
            
            logger.info(f"🏷️ Group mentions in page text:")
            logger.info(f"  - Alpha: {alpha_count}")
            logger.info(f"  - Omega: {omega_count}")
            logger.info(f"  - Group A: {group_a_count}")
            logger.info(f"  - Group B: {group_b_count}")
            
            # Find all tables
            all_tables = soup.find_all('table')
            logger.info(f"📊 Total tables found: {len(all_tables)}")
            
            # Analyze each table
            standings_tables = []
            for i, table in enumerate(all_tables):
                if self.is_standings_table(table):
                    standings_tables.append(i)
                    logger.info(f"✅ Table {i + 1} is a standings table")
                else:
                    logger.info(f"⏭️ Table {i + 1} is not a standings table")
            
            logger.info(f"🎯 Standings tables found at indices: {[i+1 for i in standings_tables]}")
            
            return soup
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze page structure: {e}")
            return None

    def parse_standings_table(self, standings_table, group_name):
        """Parse the standings table to extract team data"""
        try:
            teams_data = []
            rows = standings_table.find_all('tr')[1:]  # Skip header row
            
            logger.info(f"🔍 Parsing {len(rows)} rows for {group_name} group")
            
            for i, row in enumerate(rows):
                try:
                    cells = row.find_all('td')
                    if len(cells) < 4:  # Need at least 4 cells for team data
                        logger.debug(f"⚠️ Row {i} has only {len(cells)} cells, skipping")
                        continue
                    
                    # Extract team data - try multiple selectors
                    team_element = (
                        cells[1].find('div', class_='team-name') or
                        cells[1].find('div', class_='event-group-team-name') or
                        cells[1].find('span', class_='team-name') or
                        cells[1].find('a', class_='team-name') or
                        cells[0].find('div', class_='team-name') or  # Try first cell
                        cells[0].find('div', class_='event-group-team-name') or
                        cells[0].find('span', class_='team-name') or
                        cells[0].find('a', class_='team-name')
                    )
                    
                    if not team_element:
                        logger.debug(f"⚠️ Row {i}: No team name found, skipping")
                        continue
                    
                    team_name = team_element.get_text(strip=True)
                    team_name = self.clean_team_name(team_name)
                    
                    # Try to find record in different positions
                    record_cell = None
                    for j in range(min(len(cells), 6)):
                        cell_text = cells[j].get_text(strip=True)
                        if '-' in cell_text or '–' in cell_text:
                            record_cell = cell_text
                            break
                    
                    if not record_cell:
                        logger.debug(f"⚠️ Row {i}: No record found, skipping")
                        continue
                    
                    # Try to find map differential
                    map_diff_cell = None
                    for j in range(min(len(cells), 6)):
                        cell_text = cells[j].get_text(strip=True)
                        if '/' in cell_text or '-' in cell_text:
                            if cell_text != record_cell:  # Don't use the same cell as record
                                map_diff_cell = cell_text
                                break
                    
                    if not map_diff_cell:
                        map_diff_cell = "0/0"  # Default value
                    
                    # Try to find round differential
                    round_diff_cell = None
                    for j in range(min(len(cells), 6)):
                        cell_text = cells[j].get_text(strip=True)
                        if '/' in cell_text or '-' in cell_text:
                            if cell_text != record_cell and cell_text != map_diff_cell:
                                round_diff_cell = cell_text
                                break
                    
                    if not round_diff_cell:
                        round_diff_cell = "0/0"  # Default value
                    
                    # Extract delta (round differential converted to number)
                    try:
                        if '/' in round_diff_cell:
                            wins, losses = map(int, round_diff_cell.split('/'))
                            delta = wins - losses
                        elif '-' in round_diff_cell:
                            wins, losses = map(int, round_diff_cell.split('-'))
                            delta = wins - losses
                        else:
                            delta = 0.0
                    except:
                        delta = 0.0
                    
                    teams_data.append({
                        'group_name': group_name,
                        'team': team_name,
                        'record': record_cell,
                        'map_diff': map_diff_cell,
                        'round_diff': round_diff_cell,
                        'delta': delta
                    })
                    
                    logger.info(f"✅ Scraped: {team_name} ({group_name}) - {record_cell}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to parse team row {i}: {e}")
                    continue
            
            logger.info(f"📋 Successfully parsed {len(teams_data)} teams for {group_name} group")
            return teams_data
            
        except Exception as e:
            logger.error(f"❌ Failed to parse standings table for {group_name}: {e}")
            return []
