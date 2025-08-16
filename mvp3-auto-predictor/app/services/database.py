# MVP 3: Database Operations

import logging
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MatchDatabase:
    def __init__(self, db_path='val_standings.db'):
        self.db_path = db_path
        self.is_postgres = db_path.startswith('postgresql://')
        self.init_database()
        
    def get_connection(self):
        """Get database connection based on type"""
        if self.is_postgres:
            try:
                import psycopg2
                return psycopg2.connect(self.db_path)
            except ImportError:
                logger.error("psycopg2 not available for PostgreSQL")
                raise
        else:
            import sqlite3
            return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Create group standings table
            if self.is_postgres:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS group_standings (
                        id SERIAL PRIMARY KEY,
                        group_name VARCHAR(50) NOT NULL,
                        team VARCHAR(100) NOT NULL,
                        record VARCHAR(20) NOT NULL,
                        map_diff VARCHAR(20) NOT NULL,
                        round_diff VARCHAR(20) NOT NULL,
                        delta REAL NOT NULL,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(group_name, team)
                    )
                """)
                
                # Create scraper health tracking table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS scraper_health (
                        id SERIAL PRIMARY KEY,
                        last_run TIMESTAMP,
                        status VARCHAR(50) DEFAULT 'unknown',
                        success_count INTEGER DEFAULT 0,
                        total_runs INTEGER DEFAULT 0,
                        last_error TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create data updates tracking table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS data_updates (
                        id SERIAL PRIMARY KEY,
                        update_date DATE NOT NULL,
                        matches_added INTEGER NOT NULL,
                        status VARCHAR(50) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            else:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS group_standings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        group_name TEXT NOT NULL,
                        team TEXT NOT NULL,
                        record TEXT NOT NULL,
                        map_diff TEXT NOT NULL,
                        round_diff TEXT NOT NULL,
                        delta REAL NOT NULL,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(group_name, team)
                    )
                """)
                
                # Create scraper health tracking table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS scraper_health (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        last_run TIMESTAMP,
                        status TEXT DEFAULT 'unknown',
                        success_count INTEGER DEFAULT 0,
                        total_runs INTEGER DEFAULT 0,
                        last_error TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create data updates tracking table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS data_updates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        update_date DATE NOT NULL,
                        matches_added INTEGER NOT NULL,
                        status TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            
            conn.commit()
            logger.debug(f"Database initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise
            
        finally:
            conn.close()
    
    def insert_match(self, match_data):
        """
        Insert a single match, avoiding duplicates
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO matches 
                (match_id, date, team1, team2, team1_score, team2_score, 
                 map_name, tournament, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                match_data.get('match_id', ''),
                match_data['date'],
                match_data['team1'],
                match_data['team2'],
                match_data['team1_score'],
                match_data['team2_score'],
                match_data.get('map_name', ''),
                match_data.get('tournament', ''),
                datetime.now().isoformat()
            ))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
            
        except Exception as e:
            logger.error(f"Error inserting match: {e}")
            return False
        finally:
            conn.close()
    
    def insert_matches_batch(self, matches_list):
        """
        Insert multiple matches efficiently
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        inserted_count = 0
        
        try:
            for match_data in matches_list:
                cursor.execute('''
                    INSERT OR IGNORE INTO matches 
                    (match_id, date, team1, team2, team1_score, team2_score, 
                     map_name, tournament, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    match_data.get('match_id', ''),
                    match_data['date'],
                    match_data['team1'],
                    match_data['team2'],
                    match_data['team1_score'],
                    match_data['team2_score'],
                    match_data.get('map_name', ''),
                    match_data.get('tournament', ''),
                    datetime.now().isoformat()
                ))
                
                if cursor.rowcount > 0:
                    inserted_count += 1
            
            conn.commit()
            
            # Record the update
            self.record_data_update(inserted_count, "success")
            
            return inserted_count
            
        except Exception as e:
            logger.error(f"Error in batch insert: {e}")
            self.record_data_update(0, f"error: {e}")
            return 0
        finally:
            conn.close()
    
    def record_data_update(self, matches_added, status):
        """Track when we last updated data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO data_updates (update_date, matches_added, status, created_at)
                VALUES (?, ?, ?, ?)
            ''', (
                datetime.now().date().isoformat(),
                matches_added,
                status,
                datetime.now().isoformat()
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error recording update: {e}")
        finally:
            conn.close()
    
    def get_team_recent_matches(self, team_name, days_back=30, limit=20):
        """
        Get recent matches for a team
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days_back)).date().isoformat()
        
        cursor.execute('''
            SELECT * FROM matches 
            WHERE (LOWER(team1) = LOWER(?) OR LOWER(team2) = LOWER(?))
            AND date >= ?
            ORDER BY date DESC 
            LIMIT ?
        ''', (team_name, team_name, cutoff_date, limit))
        
        matches = []
        for row in cursor.fetchall():
            match = {
                'id': row[0],
                'match_id': row[1],
                'date': row[2],
                'team1': row[3],
                'team2': row[4],
                'team1_score': row[5],
                'team2_score': row[6],
                'map_name': row[7],
                'tournament': row[8],
                'created_at': row[9]
            }
            matches.append(match)
        
        conn.close()
        return matches
    
    def calculate_team_stats(self, team_name, days_back=30):
        """
        Calculate win rate and other stats for a team
        My reasoning: This is the dynamic version of the hard-coded stats
        """
        matches = self.get_team_recent_matches(team_name, days_back)
        
        if not matches:
            return {
                'team_name': team_name,
                'matches_found': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0.5,  # Default to 50% if no data
                'avg_score': 0,
                'last_updated': 'No data'
            }
        
        wins = 0
        losses = 0
        total_score = 0
        
        for match in matches:
            # Determine if this team won
            if match['team1'].lower() == team_name.lower():
                team_score = match['team1_score']
                opponent_score = match['team2_score']
            else:
                team_score = match['team2_score']
                opponent_score = match['team1_score']
            
            if team_score > opponent_score:
                wins += 1
            else:
                losses += 1
            
            total_score += team_score
        
        total_matches = wins + losses
        win_rate = wins / total_matches if total_matches > 0 else 0.5
        avg_score = total_score / total_matches if total_matches > 0 else 0
        
        return {
            'team_name': team_name,
            'matches_found': total_matches,
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'avg_score': avg_score,
            'last_updated': matches[0]['date'] if matches else 'No data'
        }
    
    def get_head_to_head(self, team1, team2, limit=10):
        """Get recent head-to-head matches between two teams"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM matches 
            WHERE (
                (LOWER(team1) = LOWER(?) AND LOWER(team2) = LOWER(?))
                OR 
                (LOWER(team1) = LOWER(?) AND LOWER(team2) = LOWER(?))
            )
            ORDER BY date DESC 
            LIMIT ?
        ''', (team1, team2, team2, team1, limit))
        
        matches = []
        team1_wins = 0
        
        for row in cursor.fetchall():
            match = {
                'date': row[2],
                'team1': row[3],
                'team2': row[4],
                'team1_score': row[5],
                'team2_score': row[6],
                'map_name': row[7],
                'tournament': row[8]
            }
            matches.append(match)
            
            # Count wins for team1 (regardless of which side they were on in the match)
            if ((match['team1'].lower() == team1.lower() and match['team1_score'] > match['team2_score']) or
                (match['team2'].lower() == team1.lower() and match['team2_score'] > match['team1_score'])):
                team1_wins += 1
        
        conn.close()
        
        total_matches = len(matches)
        team1_win_rate = team1_wins / total_matches if total_matches > 0 else 0.5
        
        return {
            'total_matches': total_matches,
            'team1_wins': team1_wins,
            'team2_wins': total_matches - team1_wins,
            'team1_win_rate': team1_win_rate,
            'recent_matches': matches
        }
    
    def get_database_stats(self):
        """Get overall database statistics for monitoring"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total matches
        cursor.execute('SELECT COUNT(*) FROM matches')
        total_matches = cursor.fetchone()[0]
        
        # Unique teams
        cursor.execute('SELECT COUNT(DISTINCT team1) + COUNT(DISTINCT team2) FROM matches')
        unique_teams = cursor.fetchone()[0]
        
        # Date range
        cursor.execute('SELECT MIN(date), MAX(date) FROM matches')
        date_range = cursor.fetchone()
        
        # Latest update
        cursor.execute('SELECT * FROM data_updates ORDER BY created_at DESC LIMIT 1')
        latest_update = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_matches': total_matches,
            'unique_teams': unique_teams,
            'earliest_match': date_range[0],
            'latest_match': date_range[1],
            'last_update': latest_update[4] if latest_update else 'Never',
            'last_update_status': latest_update[3] if latest_update else 'Never'
        }
    
    def get_available_teams(self):
        """Get list of teams that have recent match data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get teams with matches in last 60 days
        cutoff_date = (datetime.now() - timedelta(days=60)).date().isoformat()
        
        cursor.execute('''
            SELECT DISTINCT team1 as team FROM matches WHERE date >= ?
            UNION
            SELECT DISTINCT team2 as team FROM matches WHERE date >= ?
            ORDER BY team
        ''', (cutoff_date, cutoff_date))
        
        teams = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return teams
    
    def get_all_teams_with_stats(self, days_back=30):
        """
        Returns a list of all teams with their stats and group info from the group_standings table.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get all teams from group_standings table
            cursor.execute('''
                SELECT group_name, team, record, map_diff, round_diff, delta, last_updated
                FROM group_standings
                ORDER BY group_name, delta DESC
            ''')
            
            rows = cursor.fetchall()
            team_list = []
            
            for row in rows:
                group_name, team, record, map_diff, round_diff, delta, last_updated = row
                
                # Parse the record to get wins and losses
                # Record format is like "4-0" or "3–1" (wins-losses)
                try:
                    # Handle different types of dashes (regular hyphen, en dash, em dash)
                    if '–' in record:  # en dash
                        wins_part, losses_part = record.split('–')
                    elif '—' in record:  # em dash
                        wins_part, losses_part = record.split('—')
                    elif '-' in record:  # regular hyphen
                        wins_part, losses_part = record.split('-')
                    else:
                        raise ValueError(f"Invalid record format: {record}")
                    
                    wins = int(wins_part.strip())
                    losses = int(losses_part.strip())
                    total_matches = wins + losses
                    win_rate = wins / total_matches if total_matches > 0 else 0.0
                except (ValueError, IndexError) as e:
                    logger.warning(f"Failed to parse record '{record}' for team {team}: {e}")
                    wins = 0
                    losses = 0
                    win_rate = 0.0
                
                # Create team entry with all required info
                team_entry = {
                    'team': team,
                    'group_name': group_name,
                    'record': record,
                    'map_diff': map_diff,
                    'round_diff': round_diff,
                    'delta': delta,
                    'wins': wins,
                    'losses': losses,
                    'win_rate': win_rate,
                    'last_updated': last_updated
                }
                
                team_list.append(team_entry)
            
            return team_list
            
        except Exception as e:
            logger.error(f"Error getting teams with stats: {e}")
            return []
        finally:
            conn.close()
    
    def insert_match_data(self, group, team, record, map_diff, round_diff, delta):
        """
        Insert or update a team's group standing record into the group_standings table.
        
        Args:
            group (str): Group name (e.g. 'Alpha' or 'Omega')
            team (str): Team name
            record (str): Win-loss record (e.g. "3-1")
            map_diff (str): Map differential (e.g. "6-2")
            round_diff (str): Round differential (e.g. "92-60")
            delta (float): Delta value
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create table if it doesn't exist with correct schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS group_standings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT NOT NULL,
                team TEXT NOT NULL,
                record TEXT NOT NULL,
                map_diff TEXT NOT NULL,
                round_diff TEXT NOT NULL,
                delta REAL DEFAULT 0.0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(group_name, team)
            )
        """)

        cursor.execute("""
            INSERT OR REPLACE INTO group_standings 
            (group_name, team, record, map_diff, round_diff, delta, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (group, team, record, map_diff, round_diff, delta, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def update_scraper_health(self, status, success_count=None, total_runs=None, error_message=None):
        """Update scraper health status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if self.is_postgres:
                cursor.execute("""
                    INSERT INTO scraper_health (last_run, status, success_count, total_runs, last_error, updated_at)
                    VALUES (CURRENT_TIMESTAMP, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (id) DO UPDATE SET
                        last_run = CURRENT_TIMESTAMP,
                        status = EXCLUDED.status,
                        success_count = EXCLUDED.success_count,
                        total_runs = EXCLUDED.total_runs,
                        last_error = EXCLUDED.last_error,
                        updated_at = CURRENT_TIMESTAMP
                """, (status, success_count, total_runs, error_message))
            else:
                cursor.execute("""
                    INSERT OR REPLACE INTO scraper_health 
                    (id, last_run, status, success_count, total_runs, last_error, updated_at)
                    VALUES (1, CURRENT_TIMESTAMP, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (status, success_count, total_runs, error_message))
            
            conn.commit()
            logger.debug(f"Scraper health updated: {status}")
            
        except Exception as e:
            logger.error(f"Failed to update scraper health: {e}")
            raise
        finally:
            conn.close()
    
    def get_scraper_health(self):
        """Get current scraper health status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if self.is_postgres:
                cursor.execute("""
                    SELECT last_run, status, success_count, total_runs, last_error
                    FROM scraper_health 
                    ORDER BY updated_at DESC 
                    LIMIT 1
                """)
            else:
                cursor.execute("""
                    SELECT last_run, status, success_count, total_runs, last_error
                    FROM scraper_health 
                    ORDER BY updated_at DESC 
                    LIMIT 1
                """)
            
            result = cursor.fetchone()
            if result:
                return {
                    'last_run': result[0],
                    'status': result[1],
                    'success_count': result[2] or 0,
                    'total_runs': result[3] or 0,
                    'last_error': result[4]
                }
            else:
                return {
                    'last_run': None,
                    'status': 'unknown',
                    'success_count': 0,
                    'total_runs': 0,
                    'last_error': None
                }
                
        except Exception as e:
            logger.error(f"Failed to get scraper health: {e}")
            return {
                'last_run': None,
                'status': 'error',
                'success_count': 0,
                'total_runs': 0,
                'last_error': str(e)
            }
        finally:
            conn.close()

# Usage example and testing
if __name__ == "__main__":
    # Initialize database
    db = MatchDatabase()
    
    # Test with some sample data
    sample_matches = [
        {
            'match_id': 'test1',
            'date': '2024-01-15',
            'team1': 'Sentinels',
            'team2': '100 Thieves',
            'team1_score': 13,
            'team2_score': 8,
            'map_name': 'Ascent',
            'tournament': 'VCT Americas'
        },
        {
            'match_id': 'test2',
            'date': '2024-01-14',
            'team1': 'LOUD',
            'team2': 'Sentinels',
            'team1_score': 13,
            'team2_score': 11,
            'map_name': 'Bind',
            'tournament': 'VCT Americas'
        }
    ]
    
    print("Testing database operations...")
    
    # Insert sample data
    inserted = db.insert_matches_batch(sample_matches)
    print(f"Inserted {inserted} matches")
    
    # Test team stats calculation
    stats = db.calculate_team_stats('Sentinels')
    print(f"Sentinels stats: {stats}")
    
    # Test head-to-head
    h2h = db.get_head_to_head('Sentinels', '100 Thieves')
    print(f"Head-to-head: {h2h}")
    
    # Database overview
    db_stats = db.get_database_stats()
    print(f"Database stats: {db_stats}")
    
    # Test get_all_teams_with_stats
    print("\nTesting get_all_teams_with_stats...")
    all_teams = db.get_all_teams_with_stats()
    print(f"Found {len(all_teams)} teams with stats:")
    for team in all_teams:
        print(f"- {team['name']} (Group {team['group']}): {team['win_rate']:.2%} WR")