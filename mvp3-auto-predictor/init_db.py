#!/usr/bin/env python3
"""
Database Initialization Script
This script populates the database with sample data so the app can run.
"""

from db import MatchDatabase
from datetime import datetime

def init_sample_data():
    """Initialize the database with sample group standings and matches data"""
    print("Initializing database with sample data...")
    
    db = MatchDatabase('val_standings.db')
    
    # Sample group standings data (VCT Americas Stage 2) - CORRECT DATA
    sample_standings = [
        # Group Alpha
        ('Alpha', 'Sentinels', '4-0', '8/1', '111/63', 48),
        ('Alpha', 'G2 Esports', '3-1', '7/3', '122/74', 48),
        ('Alpha', 'Cloud9', '3-1', '6/2', '92/60', 32),
        ('Alpha', 'Evil Geniuses', '1-3', '3/7', '83/122', -39),
        ('Alpha', '2Game Esports', '1-3', '3/7', '92/104', -12),
        ('Alpha', 'FURIA', '0-4', '1/8', '39/116', -77),
        
        # Group Omega
        ('Omega', 'NRG', '4-1', '8/4', '138/119', 19),
        ('Omega', 'LEVIATÁN', '3-2', '8/6', '160/137', 23),
        ('Omega', '100 Thieves', '3-2', '7/5', '128/118', 10),
        ('Omega', 'VISA KRÜ', '2-3', '6/8', '131/137', -6),
        ('Omega', 'LOUD', '1-3', '4/7', '105/124', -19),
        ('Omega', 'MIBR', '1-3', '3/6', '84/111', -27),
    ]
    
    # Insert group standings
    print("Inserting group standings...")
    for group, team, record, map_diff, round_diff, delta in sample_standings:
        db.insert_match_data(group, team, record, map_diff, round_diff, delta)
        print(f"  Added {team} to Group {group}")
    
    # Sample matches data
    sample_matches = [
        {
            'match_id': 'VCT001',
            'date': '2024-01-15',
            'team1': 'Sentinels',
            'team2': '100 Thieves',
            'team1_score': 13,
            'team2_score': 8,
            'map_name': 'Ascent',
            'tournament': 'VCT Americas Stage 2'
        },
        {
            'match_id': 'VCT002',
            'date': '2024-01-14',
            'team1': 'LOUD',
            'team2': 'Sentinels',
            'team1_score': 13,
            'team2_score': 11,
            'map_name': 'Bind',
            'tournament': 'VCT Americas Stage 2'
        },
        {
            'match_id': 'VCT003',
            'date': '2024-01-13',
            'team1': 'Leviatán',
            'team2': 'KRÜ',
            'team1_score': 13,
            'team2_score': 9,
            'map_name': 'Haven',
            'tournament': 'VCT Americas Stage 2'
        },
        {
            'match_id': 'VCT004',
            'date': '2024-01-12',
            'team1': 'FURIA',
            'team2': 'Evil Geniuses',
            'team1_score': 13,
            'team2_score': 10,
            'map_name': 'Split',
            'tournament': 'VCT Americas Stage 2'
        },
        {
            'match_id': 'VCT005',
            'date': '2024-01-11',
            'team1': 'Cloud9',
            'team2': 'MIBR',
            'team1_score': 13,
            'team2_score': 7,
            'map_name': 'Icebox',
            'tournament': 'VCT Americas Stage 2'
        }
    ]
    
    # Insert sample matches
    print("\nInserting sample matches...")
    inserted_count = db.insert_matches_batch(sample_matches)
    print(f"  Inserted {inserted_count} matches")
    
    # Verify data
    print("\nVerifying database contents...")
    all_teams = db.get_all_teams_with_stats()
    print(f"  Found {len(all_teams)} teams with stats")
    
    db_stats = db.get_database_stats()
    print(f"  Database stats: {db_stats}")
    
    print("\nDatabase initialization complete!")
    print("You can now run the Flask app with: python app.py")

if __name__ == "__main__":
    init_sample_data()
