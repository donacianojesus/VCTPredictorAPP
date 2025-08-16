# 🎮 VCT Predictor - Valorant Champions Tour Match Prediction System

A sophisticated web application that predicts VCT match outcomes using real-time data scraping and machine learning algorithms.

## 🏗️ Architecture Overview

```
vct-predictor/
├── 📁 app/                    # Core application logic
│   ├── __init__.py           # Flask app initialization
│   ├── routes.py             # Web routes and endpoints
│   ├── models.py             # Database models
│   └── services/             # Business logic services
│       ├── scraper.py        # Data scraping service
│       ├── predictor.py      # Match prediction service
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

## 🚀 Quick Start

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

## 🌐 Features

- **Real-time VCT Data**: Automated scraping from vlr.gg
- **Match Predictions**: AI-powered outcome predictions
- **Team Analytics**: Comprehensive team performance metrics
- **Responsive Design**: Mobile and desktop optimized
- **Health Monitoring**: Real-time system status
- **Auto-scraping**: Daily data updates at 3am

## 🔧 Configuration

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

## 📊 Data Sources

- **VLR.gg**: Official VCT standings and statistics
- **Real-time Updates**: Automated daily scraping
- **Data Validation**: Robust error handling and validation

## 🚀 Deployment

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

## 📈 Monitoring

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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: GitHub Issues
- **Documentation**: See `docs/` directory
- **Wiki**: Project wiki for detailed guides

---

**Built with ❤️ for the Valorant community**

**Version**: 2.0.0  
**Status**: Production Ready 🚀
