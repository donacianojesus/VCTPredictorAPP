#!/usr/bin/env python3
"""
Development configuration for VCT Predictor
"""

from config.base import Config

class DevelopmentConfig(Config):
    """Development-specific overrides"""
    
    # Development server settings
    HOST = "127.0.0.1"
    PORT = 5001
    
    # Development-specific logging
    LOG_LEVEL = 'DEBUG'
    
    # Development database
    DATABASE_PATH = "val_standings.db"  # Relative path for development
