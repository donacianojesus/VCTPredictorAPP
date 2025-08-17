#!/usr/bin/env python3
"""
Production configuration for VCT Predictor
"""

import os
from config.base import Config

class ProductionConfig(Config):
    """Production-specific overrides"""
    
    # Production server settings
    HOST = "0.0.0.0"
    PORT = int(os.environ.get('PORT', 5000))
    
    # Production security
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Production database
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Production logging
    LOG_LEVEL = 'WARNING'
