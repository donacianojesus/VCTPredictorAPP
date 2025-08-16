# VCT Predictor - Valorant Champions Tour Match Prediction System

A sophisticated web application that predicts VCT match outcomes using **statistical analysis** and **real-time data scraping**.

## Architecture Overview

```
vct-predictor/
├── 📁 app/                    # Core Flask application
│   ├── __init__.py           # Flask app initialization
│   ├── routes.py             # Web routes and endpoints
│   └── 📁 services/          # Business logic services
│       ├── scraper.py        # Data scraping service
│       ├── predictor.py      # Statistical prediction service
│       └── database.py       # Database operations
├── 📁 static/                 # Static assets
│   ├── css/                  # Stylesheets
│   ├── js/                   # JavaScript files
│   └── images/               # Images and logos
├── 📁 templates/              # HTML templates
├── 📁 config/                 # Configuration files
├── 📁 scripts/                # Utility scripts
├── 📁 tests/                  # Test files
├── 📁 docs/                   # Documentation
├── 📁 deployment/             # Deployment configurations
├── requirements.txt           # Python dependencies
├── wsgi.py                   # Production WSGI entry point
├── Procfile                  # Heroku deployment
├── app.json                  # Heroku app configuration
└── README.md                 # This file
```

## Quick Start

### Prerequisites
- Python 3.8+
- pip
- Git

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/vct-predictor.git
cd vct-predictor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python3 scripts/init_db.py

# Run the application
python3 wsgi.py
```

### Development Mode
```bash
export FLASK_ENV=development
python3 app/__init__.py
```

## Features

- **Real-time VCT Data**: Automated scraping from vlr.gg
- **Statistical Predictions**: Win rate and performance-based match predictions
- **Team Analytics**: Comprehensive team performance metrics
- **Responsive Design**: Mobile and desktop optimized
- **Health Monitoring**: Real-time system status
- **Auto-scraping**: Daily data updates at 3am

## Configuration

### Environment Variables
```bash
export FLASK_ENV=production
export DATABASE_URL=your_database_url
export SECRET_KEY=your_secret_key
```

### Configuration Files
- `config/development.py` - Development settings
- `config/production.py` - Production settings
- `config/base.py` - Base configuration

## 📊 Data Sources & Prediction Method

### **Data Collection**
- **VLR.gg**: Official VCT standings and statistics
- **Real-time Updates**: Automated daily scraping
- **Data Validation**: Robust error handling and validation

### **Prediction Algorithm**
Our prediction system uses **statistical analysis**, not machine learning:

1. **Win Rate Calculation**: `wins / (wins + losses)` for each team
2. **Performance Metrics**: Map differences, round differences, delta scores
3. **Probability Distribution**: Normalized win rates to predict match outcomes
4. **Confidence Scoring**: Based on data quality and team performance history

**Example**: If Team A has 80% win rate vs Team B's 60% win rate:
- Team A predicted winner with 57% confidence
- Team B has 43% chance to win

## Deployment

### Heroku (Recommended)
```bash
# Deploy to Heroku
./deployment/deploy_heroku.sh
```

### Other Platforms
See `deployment/` directory for other deployment options.

## 🧪 Testing

```bash
# Run tests
python3 -m pytest tests/

# Run with coverage
python3 -m pytest --cov=app tests/
```

## Monitoring

### Web Interface
- Health status dashboard
- Real-time scraper monitoring
- Performance metrics

### Command Line
```bash
# System health check
python3 scripts/monitor.py

# View logs
tail -f logs/app.log
```
