#!/usr/bin/env python3
"""
VCT Predictor Flask Application
Main application initialization and configuration
"""

import os
import threading
import time
from datetime import datetime, timedelta
from flask import Flask
from config.base import get_config
from app.services.database import MatchDatabase
from app.services.predictor import DynamicPredictor

def create_app(config_class=None):
    """Application factory pattern"""
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    app = Flask(__name__,
                template_folder=os.path.join(project_root, 'templates'),
                static_folder=os.path.join(project_root, 'static'))
    
    # Load configuration
    if config_class is None:
        config_class = get_config()
    
    app.config.from_object(config_class)
    
    # Get database connection string
    database_url = os.environ.get('DATABASE_URL', config_class.DATABASE_PATH)
    
    # Initialize extensions with error handling
    try:
        db = MatchDatabase(database_url)
        predictor = DynamicPredictor(database_url)
        
        # Store instances in app context
        app.db = db
        app.predictor = predictor
        
        print(f"✅ Database and predictor initialized successfully")
        
        # Start background scraper if in production
        if os.environ.get('FLASK_ENV') == 'production':
            start_background_scraper(app)
        
    except Exception as e:
        print(f"⚠️ Warning: Could not initialize database/predictor: {e}")
        print("App will start but database features may not work")
        # Set to None so routes can handle gracefully
        app.db = None
        app.predictor = None
    
    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app

def start_background_scraper(app):
    """Start background scraper thread"""
    def scraper_worker():
        """Background worker for automatic scraping"""
        while True:
            try:
                # Wait until 3 AM
                now = datetime.now()
                next_run = now.replace(hour=3, minute=0, second=0, microsecond=0)
                
                if now.hour >= 3:
                    next_run += timedelta(days=1)
                
                sleep_seconds = (next_run - now).total_seconds()
                print(f"⏰ Next scraper run scheduled for {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"💤 Sleeping for {sleep_seconds/3600:.1f} hours...")
                
                time.sleep(sleep_seconds)
                
                # Run the scraper
                print("🚀 Running scheduled scraper...")
                try:
                    from app.services.scraper import VCTScraper
                    scraper = VCTScraper()
                    success = scraper.run_scrape()
                    
                    if success:
                        print("✅ Scheduled scraper completed successfully")
                    else:
                        print("❌ Scheduled scraper failed")
                        
                except Exception as e:
                    print(f"❌ Scheduled scraper error: {e}")
                
                # Wait a bit before next cycle
                time.sleep(300)  # 5 minutes
                
            except Exception as e:
                print(f"❌ Scraper worker error: {e}")
                time.sleep(3600)  # Wait 1 hour on error
    
    # Start scraper thread
    scraper_thread = threading.Thread(target=scraper_worker, daemon=True)
    scraper_thread.start()
    print("🔄 Background scraper started (runs daily at 3 AM)")

# Create app instance
app = create_app()

# Import routes after app creation to avoid circular imports
from app import routes
