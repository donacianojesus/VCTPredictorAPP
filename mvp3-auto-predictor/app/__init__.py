#!/usr/bin/env python3
"""
VCT Predictor Flask Application
Main application initialization and configuration
"""

import os
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
    
    # Initialize extensions
    db = MatchDatabase(database_url)
    predictor = DynamicPredictor(database_url)
    
    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    # Store instances in app context
    app.db = db
    app.predictor = predictor
    
    return app

# Create app instance
app = create_app()

# Import routes after app creation to avoid circular imports
from app import routes
