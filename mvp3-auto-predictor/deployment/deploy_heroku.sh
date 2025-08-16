#!/bin/bash
# Heroku Deployment Script for VCT Predictor

set -e  # Exit on any error

echo "🚀 Starting VCT Predictor Heroku Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo -e "${RED}❌ Heroku CLI not found!${NC}"
    echo -e "${YELLOW}📥 Please install Heroku CLI first:${NC}"
    echo "   https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Check if user is logged into Heroku
if ! heroku auth:whoami &> /dev/null; then
    echo -e "${RED}❌ Not logged into Heroku!${NC}"
    echo -e "${YELLOW}🔐 Please login first:${NC}"
    echo "   heroku login"
    exit 1
fi

# Get app name from user
echo -e "${BLUE}📝 Enter your Heroku app name (or press Enter to generate one):${NC}"
read -r APP_NAME

if [ -z "$APP_NAME" ]; then
    APP_NAME="vct-predictor-$(date +%s)"
    echo -e "${YELLOW}📝 Generated app name: $APP_NAME${NC}"
fi

echo -e "${YELLOW}🚀 Deploying to Heroku app: $APP_NAME${NC}"

# Step 1: Create Heroku app
echo -e "${YELLOW}📱 Creating Heroku app...${NC}"
if heroku apps:info "$APP_NAME" &> /dev/null; then
    echo -e "${GREEN}✅ App $APP_NAME already exists${NC}"
else
    heroku create "$APP_NAME"
    echo -e "${GREEN}✅ Heroku app created: $APP_NAME${NC}"
fi

# Step 2: Set environment variables
echo -e "${YELLOW}🔧 Setting environment variables...${NC}"
heroku config:set FLASK_ENV=production --app "$APP_NAME"
heroku config:set PYTHONPATH=/app --app "$APP_NAME"
echo -e "${GREEN}✅ Environment variables set${NC}"

# Step 3: Add PostgreSQL addon
echo -e "${YELLOW}🗄️  Adding PostgreSQL database...${NC}"
heroku addons:create heroku-postgresql:mini --app "$APP_NAME"
echo -e "${GREEN}✅ PostgreSQL database added${NC}"

# Step 4: Deploy the app
echo -e "${YELLOW}📤 Deploying to Heroku...${NC}"
git add .
git commit -m "Deploy to Heroku" || git commit -m "Initial commit"
git push heroku main || git push heroku master

# Step 5: Open the app
echo -e "${YELLOW}🌐 Opening your deployed app...${NC}"
heroku open --app "$APP_NAME"

# Step 6: Show app info
echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}📱 Your VCT Predictor is now live at:${NC}"
echo -e "${GREEN}   https://$APP_NAME.herokuapp.com${NC}"
echo ""
echo -e "${BLUE}🔧 Useful Heroku commands:${NC}"
echo -e "${YELLOW}   View logs:${NC} heroku logs --tail --app $APP_NAME"
echo -e "${YELLOW}   Open app:${NC} heroku open --app $APP_NAME"
echo -e "${YELLOW}   Run console:${NC} heroku run python3 --app $APP_NAME"
echo -e "${YELLOW}   Check status:${NC} heroku ps --app $APP_NAME"
echo ""
echo -e "${BLUE}⚠️  Important Notes:${NC}"
echo -e "${YELLOW}   • Auto-scraping will need to be set up differently on Heroku${NC}"
echo -e "${YELLOW}   • Consider using Heroku Scheduler addon for periodic tasks${NC}"
echo -e "${YELLOW}   • Database will be PostgreSQL instead of SQLite${NC}"
echo ""
echo -e "${GREEN}🚀 Your VCT Predictor is now accessible worldwide!${NC}"
