#!/usr/bin/env python3
"""
VCT Predictor Auto-Scraper Monitor
Provides real-time monitoring and insights for the 3am auto-scraper
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
import argparse
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HEALTH_CHECK_FILE = os.path.join(BASE_DIR, "scraper_health.json")
DB_FILE = os.path.join(BASE_DIR, "val_standings.db")
AUTO_SCRAPER_LOG = os.path.join(BASE_DIR, "auto_scraper.log")

def load_health_data():
    """Load scraper health data"""
    if not os.path.exists(HEALTH_CHECK_FILE):
        return None
    
    try:
        with open(HEALTH_CHECK_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading health data: {e}")
        return None

def check_database_health():
    """Check database status and recent data"""
    if not os.path.exists(DB_FILE):
        return "❌ Database file not found", None
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check table structure
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        if 'group_standings' not in tables:
            return "❌ Required table 'group_standings' not found", None
        
        # Check recent data
        cursor.execute("""
            SELECT COUNT(*) as team_count, 
                   MAX(last_updated) as last_update,
                   MIN(last_updated) as first_update
            FROM group_standings
        """)
        
        result = cursor.fetchone()
        team_count, last_update, first_update = result
        
        if team_count == 0:
            return "❌ No teams found in database", None
        
        # Check if data is recent (within 24 hours)
        if last_update:
            try:
                if isinstance(last_update, str):
                    last_update_dt = datetime.fromisoformat(last_update)
                else:
                    last_update_dt = last_update
                
                time_since_update = datetime.now() - last_update_dt
                if time_since_update > timedelta(hours=24):
                    status = f"⚠️  Data is {time_since_update.days} days old"
                else:
                    status = f"✅ Data is {time_since_update.seconds // 3600} hours old"
            except:
                status = "⚠️  Could not parse last update time"
        else:
            status = "⚠️  No last update timestamp found"
        
        conn.close()
        return status, {
            'team_count': team_count,
            'last_update': last_update,
            'first_update': first_update
        }
        
    except Exception as e:
        return f"❌ Database error: {e}", None

def check_log_files():
    """Check log file status and recent activity"""
    log_files = {
        'Auto Scraper': AUTO_SCRAPER_LOG,
        'Scraper': os.path.join(BASE_DIR, "scraper.log")
    }
    
    log_status = {}
    
    for log_name, log_path in log_files.items():
        if not os.path.exists(log_path):
            log_status[log_name] = "❌ Log file not found"
            continue
        
        try:
            # Check file size
            file_size = os.path.getsize(log_path)
            if file_size == 0:
                log_status[log_name] = "⚠️  Log file is empty"
                continue
            
            # Check last modification time
            mtime = os.path.getmtime(log_path)
            last_modified = datetime.fromtimestamp(mtime)
            time_since_mod = datetime.now() - last_modified
            
            if time_since_mod > timedelta(hours=24):
                log_status[log_name] = f"⚠️  Last modified {time_since_mod.days} days ago"
            else:
                log_status[log_name] = f"✅ Last modified {time_since_mod.seconds // 3600} hours ago"
                
        except Exception as e:
            log_status[log_name] = f"❌ Error checking log: {e}"
    
    return log_status

def get_recent_log_entries(log_file, lines=10):
    """Get recent entries from a log file"""
    if not os.path.exists(log_file):
        return []
    
    try:
        with open(log_file, 'r') as f:
            # Read last N lines
            lines_list = f.readlines()
            return lines_list[-lines:] if len(lines_list) > lines else lines_list
    except Exception:
        return []

def display_status():
    """Display comprehensive status information"""
    print("🔍 VCT Predictor Auto-Scraper Monitor")
    print("=" * 50)
    
    # Health Status
    print("\n📊 SCRAPER HEALTH STATUS")
    print("-" * 30)
    health_data = load_health_data()
    
    if health_data:
        print(f"Status: {health_data.get('status', 'Unknown')}")
        print(f"Last Run: {health_data.get('last_run', 'Unknown')}")
        print(f"Message: {health_data.get('message', 'No message')}")
        print(f"Success Rate: {health_data.get('success_count', 0)}/{health_data.get('total_runs', 0)}")
    else:
        print("❌ No health data available")
    
    # Database Health
    print("\n🗄️  DATABASE HEALTH")
    print("-" * 30)
    db_status, db_details = check_database_health()
    print(db_status)
    
    if db_details:
        print(f"Teams in database: {db_details['team_count']}")
        print(f"Last update: {db_details['last_update']}")
        print(f"First update: {db_details['first_update']}")
    
    # Log Files Status
    print("\n📝 LOG FILES STATUS")
    print("-" * 30)
    log_status = check_log_files()
    for log_name, status in log_status.items():
        print(f"{log_name}: {status}")
    
    # Recent Activity
    print("\n🔄 RECENT ACTIVITY")
    print("-" * 30)
    if os.path.exists(AUTO_SCRAPER_LOG):
        recent_logs = get_recent_log_entries(AUTO_SCRAPER_LOG, 5)
        if recent_logs:
            print("Recent auto-scraper activity:")
            for line in recent_logs:
                line = line.strip()
                if line and len(line) > 50:
                    # Truncate long lines
                    print(f"  {line[:50]}...")
                elif line:
                    print(f"  {line}")
        else:
            print("No recent activity found in auto-scraper log")
    else:
        print("Auto-scraper log not found")

def display_detailed_logs(log_file, lines=20):
    """Display detailed log information"""
    if not os.path.exists(log_file):
        print(f"❌ Log file {log_file} not found")
        return
    
    print(f"\n📋 DETAILED LOGS: {os.path.basename(log_file)}")
    print("-" * 50)
    
    recent_logs = get_recent_log_entries(log_file, lines)
    for line in recent_logs:
        print(line.rstrip())

def main():
    parser = argparse.ArgumentParser(description='VCT Predictor Auto-Scraper Monitor')
    parser.add_argument('--logs', action='store_true', help='Show detailed logs')
    parser.add_argument('--auto-scraper-logs', action='store_true', help='Show auto-scraper logs only')
    parser.add_argument('--scraper-logs', action='store_true', help='Show scraper logs only')
    parser.add_argument('--lines', type=int, default=20, help='Number of log lines to show (default: 20)')
    
    args = parser.parse_args()
    
    if args.logs:
        display_detailed_logs(AUTO_SCRAPER_LOG, args.lines)
        return
    
    if args.auto_scraper_logs:
        display_detailed_logs(AUTO_SCRAPER_LOG, args.lines)
        return
    
    if args.scraper_logs:
        scraper_log = os.path.join(BASE_DIR, "scraper.log")
        display_detailed_logs(scraper_log, args.lines)
        return
    
    # Default: show status
    display_status()

if __name__ == "__main__":
    main()
