#!/usr/bin/env python3
"""
Development entry point for VCT Predictor
Run this for local development
"""

from app import app
from config.development import DevelopmentConfig

if __name__ == "__main__":
    config = DevelopmentConfig()
    print(f"🚀 Starting VCT Predictor in development mode...")
    print(f"📱 Web interface: http://{config.HOST}:{config.PORT}")
    print(f"🔧 Debug mode: {config.DEBUG}")
    print(f"📊 Database: {config.DATABASE_PATH}")
    print("Press Ctrl+C to stop the server")
    
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
