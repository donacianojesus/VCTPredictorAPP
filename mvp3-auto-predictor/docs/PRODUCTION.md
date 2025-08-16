# 🚀 VCT Predictor Production Deployment Guide

This guide will help you deploy your VCT Predictor to production mode.

## 📋 Prerequisites

- ✅ VCT Predictor development version working correctly
- ✅ macOS system with launchd support
- ✅ Python 3.8+ installed
- ✅ Virtual environment set up

## 🎯 Production Features

- **Production WSGI server** (Gunicorn-ready)
- **Enhanced error handling** and logging
- **Production configuration** management
- **Automated deployment** scripts
- **Production monitoring** tools
- **Enhanced security** settings

## 🚀 Quick Deployment

### Option 1: Automated Deployment (Recommended)

```bash
# Make deployment script executable
chmod +x deploy.sh

# Run automated deployment
./deploy.sh
```

This will:
- Install production dependencies
- Test production configuration
- Switch to production service
- Create startup scripts
- Verify everything works

### Option 2: Manual Deployment

```bash
# 1. Install production dependencies
source venv/bin/activate
pip install -r requirements-prod.txt

# 2. Create logs directory
mkdir -p logs

# 3. Test production configuration
python3 wsgi.py

# 4. Switch to production service
launchctl unload com.vctpredictor.autoscrape.plist
launchctl load com.vctpredictor.autoscrape.prod.plist
```

## 🌐 Running in Production

### Start Production App

```bash
./start_production.sh
```

**Available at**: `http://localhost:5000`

### Monitor Production

```bash
./monitor_production.sh
```

### Check Logs

```bash
# Auto-scraper logs
tail -f logs/daemon.log

# Error logs
tail -f logs/daemon.error.log

# Application logs
tail -f auto_scraper.log
```

## 🔧 Production Configuration

### Environment Variables

```bash
export FLASK_ENV=production
export PYTHONPATH=/path/to/your/project
```

### Configuration File

The `config.py` file automatically detects the environment and applies appropriate settings:

- **Development**: Debug mode, port 5001, verbose logging
- **Production**: Production mode, port 5000, minimal logging

## 📊 Monitoring & Health Checks

### Web Interface Health

- **URL**: `http://localhost:5000/api/health`
- **Auto-refresh**: Every 30 seconds
- **Shows**: Last run time, success rate, total runs

### Command Line Monitoring

```bash
# Overall status
python3 monitor.py

# Detailed logs
python3 monitor.py --logs --lines 50

# Auto-scraper specific
python3 monitor.py --auto-scraper-logs
```

## 🔒 Security Features

- **Production logging** (no sensitive debug info)
- **Error handling** (no stack traces in production)
- **Rate limiting** (built into launchd)
- **Process isolation** (background daemon)

## 🚨 Troubleshooting

### Common Issues

#### Service Not Starting
```bash
# Check service status
launchctl list | grep vctpredictor

# Check logs
tail -f logs/daemon.error.log

# Reload service
launchctl unload com.vctpredictor.autoscrape.prod.plist
launchctl load com.vctpredictor.autoscrape.prod.plist
```

#### App Not Accessible
```bash
# Check if app is running
ps aux | grep python3 | grep wsgi

# Check port usage
lsof -i :5000

# Restart app
./start_production.sh
```

#### Scraper Not Working
```bash
# Test scraper manually
python3 auto_scrape.py

# Check database
python3 monitor.py

# Verify launchd service
launchctl print system/com.vctpredictor.autoscrape.prod
```

## 📈 Performance Optimization

### Production Settings

- **Logging**: WARNING level only
- **Debug**: Disabled
- **Retries**: 5 attempts with 2-minute delays
- **Timeouts**: 60 seconds for network operations

### Monitoring

- **Health checks**: Every 30 seconds
- **Data freshness**: 24-hour threshold
- **Backup management**: Last 5 backups kept
- **Error tracking**: Comprehensive error logging

## 🔄 Maintenance

### Daily

- Check web interface health status
- Monitor auto-scraper success rate

### Weekly

- Review logs for errors
- Check database size and performance
- Verify backup integrity

### Monthly

- Update dependencies
- Review and rotate logs
- Performance analysis

## 📞 Support

If you encounter issues:

1. **Check logs** first
2. **Use monitoring tools**
3. **Test components individually**
4. **Verify service status**

## 🎉 Success Indicators

Your production deployment is successful when:

- ✅ Production app accessible at `http://localhost:5000`
- ✅ Auto-scraper runs daily at 3am
- ✅ Health monitoring shows success
- ✅ Logs show regular successful runs
- ✅ Database stays updated with fresh data

---

**Last Updated**: August 2025  
**Version**: Production 1.0  
**Status**: Ready for Deployment 🚀
