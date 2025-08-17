# VCT Predictor - Valorant Champions Tour Match Prediction System

A sophisticated web application that predicts VCT match outcomes using **statistical analysis** and **real-time data scraping**.

## 🚀 Live Demo

**Deployed on Railway**: [Your Railway URL here]

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
│   ├── styles.css            # Main stylesheet
│   ├── script.js             # JavaScript functionality
│   └── VCT_2023_Americas.png # VCT branding
├── 📁 templates/              # HTML templates
│   └── index.html            # Main application interface
├── 📁 config/                 # Configuration files
│   ├── base.py               # Base configuration
│   ├── development.py        # Development settings
│   └── production.py         # Production settings
├── 📁 scripts/                # Utility scripts
│   └── init_railway_db.py    # Railway database initialization
├── 📁 docs/                   # Documentation
│   ├── RAILWAY_DEPLOYMENT.md # Railway deployment guide
│   └── RAILWAY_SCRAPER_SETUP.md # Scraper service setup
├── requirements.txt           # Python dependencies
├── wsgi.py                   # Production WSGI entry point
├── Procfile                  # Railway deployment process
├── railway.json              # Railway deployment configuration
├── railway_scraper.py        # Railway scraper service
├── railway_scraper.json      # Scraper service configuration
└── README.md                 # This file
```

## Quick Start

### Prerequisites
- Python 3.8+
- pip
- Git

### Local Development
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
python3 scripts/init_railway_db.py

# Run the application
python3 run.py
```

### Production Mode
```bash
# Set production environment
export FLASK_ENV=production
export DATABASE_URL=your_database_url
export SECRET_KEY=your_secret_key

# Run with production WSGI
python3 wsgi.py
```

## Features

- **Real-time VCT Data**: Automated scraping from vlr.gg
- **Statistical Predictions**: Win rate and performance-based match predictions
- **Team Analytics**: Comprehensive team performance metrics
- **Responsive Design**: Mobile and desktop optimized
- **Health Monitoring**: Real-time system status
- **Auto-scraping**: Daily data updates at 3am
- **Railway Integration**: Seamless deployment and scaling

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

## 🚀 Deployment

### Railway (Recommended)
```bash
# Deploy to Railway
git push railway main
```

**Railway Configuration:**
- `railway.json` - Deployment settings
- `Procfile` - Process definition
- `wsgi.py` - Production entry point
- `requirements.txt` - Dependencies

### Railway Scraper Service
The application includes a separate Railway scraper service for automated data updates:
- `railway_scraper.py` - Scraper service implementation
- `railway_scraper.json` - Scraper service configuration

See `docs/RAILWAY_SCRAPER_SETUP.md` for detailed setup instructions.

## 🧪 Testing

```bash
# Run tests
python3 -m pytest tests/

# Run with coverage
python3 -m pytest --cov=app tests/
```

## Monitoring

### Web Interface
- Health status dashboard at `/api/health`
- Real-time scraper monitoring
- Performance metrics

### API Endpoints
- `GET /` - Main application interface
- `GET /api/health` - System health status
- `POST /api/init-db` - Initialize database with sample data

## 📚 Documentation

- `RAILWAY_DEPLOYMENT.md` - Complete Railway deployment guide
- `RAILWAY_SCRAPER_SETUP.md` - Scraper service configuration
- `PROJECT_STRUCTURE.md` - Detailed project architecture

## 🔧 Troubleshooting

### Common Issues
1. **Database Connection**: Ensure `DATABASE_URL` is set correctly
2. **App Startup**: Check Railway logs for startup errors
3. **Dependencies**: Verify all packages in `requirements.txt` are installed

### Railway Logs
```bash
# View Railway deployment logs
railway logs
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ for the Valorant community**
