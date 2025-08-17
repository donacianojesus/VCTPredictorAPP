#!/usr/bin/env python3
"""
Test script to check current database state and update with fresh VCT data
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_current_data():
    """Test the current database state"""
    try:
        from app.services.database import MatchDatabase
        from app.services.scraper import VCTScraper
        
        print("🔍 Testing current database state...")
        
        # Initialize database
        db = MatchDatabase('sqlite:///test_current.db')
        
        # Check current teams
        teams = db.get_all_teams_with_stats()
        print(f"📊 Current teams in database: {len(teams) if teams else 0}")
        
        if teams:
            print("\n🏆 Current teams:")
            for team in teams[:5]:  # Show first 5
                print(f"  - {team['team']} ({team['group_name']}) - {team['record']}")
            if len(teams) > 5:
                print(f"  ... and {len(teams) - 5} more teams")
        else:
            print("❌ No teams found in database")
        
        # Test scraper
        print("\n🚀 Testing VCT scraper...")
        scraper = VCTScraper()
        scraper.db = db  # Connect to database
        
        # Run scraper
        success = scraper.run_scrape()
        
        if success:
            print("✅ Scraper completed successfully!")
            
            # Check updated teams
            updated_teams = db.get_all_teams_with_stats()
            print(f"📊 Updated teams in database: {len(updated_teams) if updated_teams else 0}")
            
            if updated_teams:
                print("\n🏆 Updated teams:")
                alpha_teams = [t for t in updated_teams if t['group_name'] == 'Alpha']
                omega_teams = [t for t in updated_teams if t['group_name'] == 'Omega']
                
                print(f"  Group Alpha: {len(alpha_teams)} teams")
                for team in alpha_teams:
                    print(f"    - {team['team']} ({team['record']}) - {team['delta']}")
                
                print(f"  Group Omega: {len(omega_teams)} teams")
                for team in omega_teams:
                    print(f"    - {team['team']} ({team['record']}) - {team['delta']}")
        else:
            print("❌ Scraper failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_current_data() 