# 🏗️ VCT Predictor Project Structure

## 📁 Directory Organization

```
vct-predictor/
├── 📁 app/                          # Core Flask application
│   ├── __init__.py                  # Flask app factory & initialization
│   ├── routes.py                    # Web routes & API endpoints
│   └── 📁 services/                 # Business logic services
│       ├── __init__.py              # Services package init
│       ├── database.py              # Database operations
│       ├── scraper.py               # Web scraping service
│       └── predictor.py             # Match prediction service
│
├── 📁 config/                       # Configuration management
│   ├── __init__.py                  # Config package init
│   ├── base.py                      # Base configuration class
│   ├── development.py               # Development settings
│   └── production.py                # Production settings
│
├── 📁 static/                       # Static assets (CSS, JS, images)
│   ├── styles.css                   # Main stylesheet
│   ├── script.js                    # Frontend JavaScript
│   └── VCT_2023_Americas.png       # VCT logo
│
├── 📁 templates/                    # HTML templates
│   └── index.html                   # Main page template
│
├── 📁 scripts/                      # Utility scripts
│   ├── monitor.py                   # System monitoring tool
│   └── init_db.py                   # Database initialization
│
├── 📁 deployment/                   # Deployment configurations
│   ├── com.vctpredictor.autoscrape.plist      # macOS launchd config
│   ├── com.vctpredictor.autoscrape.prod.plist # Production launchd
│   ├── deploy.sh                    # Local deployment script
│   └── deploy_heroku.sh            # Heroku deployment script
│
├── 📁 docs/                         # Documentation
│   ├── PRODUCTION.md                # Production setup guide
│   └── DEPLOYMENT_OPTIONS.md        # Deployment options
│
├── 📁 tests/                        # Test files (to be created)
├── 📁 logs/                         # Application logs (auto-created)
│
├── 📄 run.py                        # Development entry point
├── 📄 wsgi.py                       # Production WSGI entry point
├── 📄 requirements.txt              # Python dependencies
├── 📄 requirements-prod.txt         # Production dependencies
├── 📄 Procfile                      # Heroku deployment
├── 📄 app.json                      # Heroku app configuration
├── 📄 .gitignore                    # Git ignore patterns
├── 📄 README.md                     # Project documentation
└── 📄 PROJECT_STRUCTURE.md          # This file
```

## 🔄 File Migration Summary

### Moved Files
- `app.py` → `app/__init__.py` (Flask app initialization)
- `db.py` → `app/services/database.py` (Database operations)
- `scraper.py` → `app/services/scraper.py` (Web scraping)
- `predictor.py` → `app/services/predictor.py` (Match predictions)
- `monitor.py` → `scripts/monitor.py` (Monitoring tool)
- `init_db.py` → `scripts/init_db.py` (Database setup)
- `config.py` → `config/base.py` (Base configuration)

### New Files Created
- `app/routes.py` (Web routes & API endpoints)
- `config/development.py` (Development configuration)
- `config/production.py` (Production configuration)
- `run.py` (Development entry point)
- `PROJECT_STRUCTURE.md` (This documentation)

### Configuration Files
- `config/base.py` - Base configuration with common settings
- `config/development.py` - Development-specific overrides
- `config/production.py` - Production-specific overrides

## 🚀 How to Run

### Development Mode
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python3 run.py
```

### Production Mode
```bash
# Set production environment
export FLASK_ENV=production

# Run with WSGI
python3 wsgi.py

# Or with Gunicorn
gunicorn wsgi:app
```

## 📊 Benefits of New Structure

### ✅ **Clean Separation of Concerns**
- **App Logic**: All in `app/` directory
- **Configuration**: Environment-specific configs in `config/`
- **Services**: Business logic separated in `app/services/`
- **Scripts**: Utility scripts in `scripts/`

### ✅ **Easy Deployment**
- **Development**: Use `run.py` for local development
- **Production**: Use `wsgi.py` for production servers
- **Heroku**: Ready with `Procfile` and `app.json`

### ✅ **Maintainable Code**
- **Modular**: Each service has its own file
- **Configurable**: Environment-based settings
- **Testable**: Clear structure for unit tests
- **Scalable**: Easy to add new features

### ✅ **Professional Standards**
- **Factory Pattern**: Flask app factory for flexibility
- **Blueprint**: Organized route management
- **Configuration**: Environment-based config management
- **Documentation**: Clear project structure

## 🔧 Next Steps

1. **Test the new structure**:
   ```bash
   python3 run.py
   ```

2. **Verify all imports work**:
   ```bash
   python3 -c "from app import app; print('✅ App imports successfully')"
   ```

3. **Run the scraper**:
   ```bash
   python3 scripts/init_db.py
   python3 app/services/scraper.py
   ```

4. **Deploy to production**:
   ```bash
   ./deployment/deploy.sh
   ```

## 📝 Notes

- **Database**: Still uses SQLite for development, can be PostgreSQL for production
- **Logs**: Will be created in `logs/` directory automatically
- **Virtual Environment**: Keep `venv/` in project root for development
- **Git**: Use `.gitignore` to exclude unnecessary files from version control

---

**Your VCT Predictor is now professionally organized and ready for production! 🚀**
