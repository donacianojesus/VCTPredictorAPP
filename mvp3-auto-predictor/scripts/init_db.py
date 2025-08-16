#!/usr/bin/env python3
"""
Initialize the VCT Predictor database with proper schema
"""

import sqlite3
import os
from datetime import datetime

def init_database():
    """Initialize the database with proper schema"""
    db_path = "val_standings.db"
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        print(f"Removing existing database: {db_path}")
        os.remove(db_path)
    
    print(f"Creating new database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create group_standings table with correct schema
        cursor.execute("""
            CREATE TABLE group_standings (
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
        
        # Create data_updates tracking table
        cursor.execute("""
            CREATE TABLE data_updates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                update_date DATE NOT NULL,
                matches_added INTEGER NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create matches table for historical data (if needed)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT UNIQUE,
                date TEXT NOT NULL,
                team1 TEXT NOT NULL,
                team2 TEXT NOT NULL,
                team1_score INTEGER NOT NULL,
                team2_score INTEGER NOT NULL,
                map_name TEXT,
                tournament TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print("✅ Database schema created successfully")
        
        # Insert some sample data for testing
        sample_data = [
            ('Alpha', 'SEN', '4-0', '8/1', '120/63', 48.0),
            ('Alpha', 'G2', '3-1', '7/3', '122/74', 48.0),
            ('Alpha', 'C9', '3-1', '6/2', '92/60', 32.0),
            ('Alpha', 'EG', '1-3', '3/7', '83/122', -39.0),
            ('Alpha', '2G', '1-3', '3/7', '92/104', -12.0),
            ('Alpha', 'FUR', '0-4', '1/8', '39/116', -77.0),
            ('Omega', 'NRG', '4-1', '8/4', '138/119', 19.0),
            ('Omega', 'LEV', '3-2', '8/6', '160/137', 23.0),
            ('Omega', '100T', '3-2', '7/5', '128/118', 10.0),
            ('Omega', 'KRÜ', '2-3', '6/8', '131/137', -6.0),
            ('Omega', 'LOUD', '1-3', '4/7', '105/124', -19.0),
            ('Omega', 'MIBR', '1-3', '3/6', '84/111', -27.0)
        ]
        
        cursor.executemany("""
            INSERT INTO group_standings (group_name, team, record, map_diff, round_diff, delta, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [(group, team, record, map_diff, round_diff, delta, datetime.now().isoformat()) 
               for group, team, record, map_diff, round_diff, delta in sample_data])
        
        conn.commit()
        print(f"✅ Inserted {len(sample_data)} sample team records")
        
        # Verify the data
        cursor.execute("SELECT COUNT(*) FROM group_standings")
        count = cursor.fetchone()[0]
        print(f"✅ Database now contains {count} team records")
        
        # Show sample data
        cursor.execute("SELECT group_name, team, record, map_diff, round_diff, delta FROM group_standings LIMIT 5")
        sample_rows = cursor.fetchall()
        print("\n📊 Sample data:")
        for row in sample_rows:
            print(f"  {row[1]} ({row[0]}): {row[2]} | Maps: {row[3]} | Rounds: {row[4]} | Δ: {row[5]}")
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Initializing VCT Predictor Database...")
    init_database()
    print("✅ Database initialization complete!")
