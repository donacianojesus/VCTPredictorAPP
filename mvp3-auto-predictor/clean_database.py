#!/usr/bin/env python3
"""
Database cleanup script to remove old sample data and prepare for fresh VCT data
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def clean_database():
    """Clean up the database and remove old data"""
    try:
        from app.services.database import MatchDatabase
        
        print("🧹 Starting database cleanup...")
        
        # Initialize database (use your Railway PostgreSQL URL)
        # For local testing, you can use SQLite
        database_url = os.environ.get('DATABASE_URL', 'sqlite:///clean_test.db')
        db = MatchDatabase(database_url)
        
        print(f"📊 Connected to database: {database_url}")
        
        # Get current teams
        current_teams = db.get_all_teams_with_stats()
        print(f"📋 Found {len(current_teams) if current_teams else 0} teams in database")
        
        if current_teams:
            print("\n🏆 Current teams in database:")
            for team in current_teams:
                print(f"  - {team['team']} ({team['group_name']}) - {team['record']}")
            
            # Check for problematic team names
            bad_names = [t for t in current_teams if any(suffix in t['team'] for suffix in ['Brazil', 'Argentina', 'United States'])]
            if bad_names:
                print(f"\n⚠️ Found {len(bad_names)} teams with bad names:")
                for team in bad_names:
                    print(f"  - {team['team']}")
            
            # Ask for confirmation
            response = input("\n❓ Do you want to clear all current data? (yes/no): ")
            if response.lower() == 'yes':
                print("🗑️ Clearing all team data...")
                
                # Clear all teams
                try:
                    db.clear_all_teams()
                    print("✅ Database cleared successfully!")
                except Exception as e:
                    print(f"❌ Error clearing database: {e}")
                    return False
            else:
                print("⏭️ Skipping database cleanup")
                return True
        else:
            print("✅ Database is already empty")
            return True
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = clean_database()
    if success:
        print("\n🎉 Database cleanup completed!")
        print("Next step: Run the scraper to get fresh VCT data")
    else:
        print("\n❌ Database cleanup failed!") 