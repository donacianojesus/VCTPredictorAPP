#!/usr/bin/env python3
"""
WSGI entry point for Railway deployment
"""

import os
from app import create_app
from config.production import ProductionConfig

# Set production environment
os.environ['FLASK_ENV'] = 'production'

# Create production app
app = create_app(ProductionConfig)

if __name__ == "__main__":
    config = ProductionConfig()
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
