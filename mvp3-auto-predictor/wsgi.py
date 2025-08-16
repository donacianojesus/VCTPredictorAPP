#!/usr/bin/env python3
"""
WSGI entry point for production deployment
"""

import os
import sys
from app import create_app
from config.production import ProductionConfig

# Set production environment
os.environ['FLASK_ENV'] = 'production'

# Create production app
app = create_app(ProductionConfig)

# Verify database connection
with app.app_context():
    try:
        teams = app.db.get_all_teams_with_stats()
        print(f"✅ Database connected: {len(teams)} teams found")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    config = ProductionConfig()
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
