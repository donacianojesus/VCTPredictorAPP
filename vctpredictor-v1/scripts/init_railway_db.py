#!/usr/bin/env python3
"""
Initialize Railway PostgreSQL Database with Sample Data
Run this to populate the database with team data
"""

import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.database import MatchDatabase

def init_railway_database():
    """Initialize Railway database with sample data"""
    
    # Get database URL from environment (Railway will set this)
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        print("Make sure you're running this on Railway or have DATABASE_URL set")
        return False
    
    print(f"🚀 Initializing Railway database...")
    print(f"📊 Database URL: {database_url[:20]}...")
    
    try:
        # Initialize database (this will create tables)
        db = MatchDatabase(database_url)
        print("✅ Database connection successful")
        
        # Sample team data for VCT Americas
        sample_teams = [
            # Group Alpha
            {
                'group_name': 'Alpha',
                'team': 'Sentinels',
                'record': '4-1',
                'map_diff': '8/2',
                'round_diff': '104/78',
                'delta': 26.0
            },
            {
                'group_name': 'Alpha',
                'team': 'LOUD',
                'record': '3-2',
                'map_diff': '6/4',
                'round_diff': '98/82',
                'delta': 16.0
            },
            {
                'group_name': 'Alpha',
                'team': '100 Thieves',
                'record': '3-2',
                'map_diff': '6/4',
                'round_diff': '92/88',
                'delta': 4.0
            },
            {
                'group_name': 'Alpha',
                'team': 'NRG',
                'record': '2-3',
                'map_diff': '4/6',
                'round_diff': '86/94',
                'delta': -8.0
            },
            {
                'group_name': 'Alpha',
                'team': 'Cloud9',
                'record': '2-3',
                'map_diff': '4/6',
                'round_diff': '84/96',
                'delta': -12.0
            },
            {
                'group_name': 'Alpha',
                'team': 'MIBR',
                'record': '1-4',
                'map_diff': '2/8',
                'round_diff': '76/104',
                'delta': -28.0
            },
            
            # Group Omega
            {
                'group_name': 'Omega',
                'team': 'Leviatán',
                'record': '4-1',
                'map_diff': '8/2',
                'round_diff': '102/76',
                'delta': 26.0
            },
            {
                'group_name': 'Omega',
                'team': 'KRÜ',
                'record': '3-2',
                'map_diff': '6/4',
                'round_diff': '96/84',
                'delta': 12.0
            },
            {
                'group_name': 'Omega',
                'team': 'FURIA',
                'record': '3-2',
                'map_diff': '6/4',
                'round_diff': '94/86',
                'delta': 8.0
            },
            {
                'group_name': 'Omega',
                'team': 'Evil Geniuses',
                'record': '2-3',
                'map_diff': '4/6',
                'round_diff': '88/92',
                'delta': -4.0
            },
            {
                'group_name': 'Omega',
                'team': 'G2 Esports',
                'record': '2-3',
                'map_diff': '4/6',
                'round_diff': '86/94',
                'delta': -8.0
            },
            {
                'group_name': 'Omega',
                'team': 'Shopify Rebellion',
                'record': '1-4',
                'map_diff': '2/8',
                'round_diff': '78/102',
                'delta': -24.0
            }
        ]
        
        # Insert sample teams
        print(f"📝 Inserting {len(sample_teams)} sample teams...")
        for team_data in sample_teams:
            db.insert_match_data(
                group=team_data['group_name'],
                team=team_data['team'],
                record=team_data['record'],
                map_diff=team_data['map_diff'],
                round_diff=team_data['round_diff'],
                delta=team_data['delta']
            )
            print(f"  ✅ {team_data['team']} ({team_data['group_name']})")
        
        # Initialize scraper health
        print("🔄 Initializing scraper health tracking...")
        db.update_scraper_health(
            status='idle',
            success_count=0,
            total_runs=0
        )
        
        # Verify data
        print("🔍 Verifying database content...")
        teams = db.get_all_teams_with_stats()
        print(f"✅ Database now contains {len(teams)} teams")
        
        # Show sample teams
        print("\n📊 Sample teams in database:")
        for team in teams[:5]:  # Show first 5
            print(f"  - {team['team']} (Group {team['group_name']}): {team['record']}")
        
        print("\n🎉 Railway database initialization complete!")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_railway_database()
    sys.exit(0 if success else 1)
