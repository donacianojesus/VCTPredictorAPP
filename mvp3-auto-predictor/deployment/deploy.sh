#!/bin/bash
# Production Deployment Script for VCT Predictor

set -e  # Exit on any error

echo "🚀 Starting VCT Predictor Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/Users/jesusdonaciano/Desktop/projects/VCTPredictorAPP/mvp3-auto-predictor"
VENV_DIR="$PROJECT_DIR/venv"
LOGS_DIR="$PROJECT_DIR/logs"

echo -e "${YELLOW}📁 Project Directory: $PROJECT_DIR${NC}"

# Step 1: Create logs directory
echo -e "${YELLOW}📝 Creating logs directory...${NC}"
mkdir -p "$LOGS_DIR"
echo -e "${GREEN}✅ Logs directory created${NC}"

# Step 2: Activate virtual environment and install production dependencies
echo -e "${YELLOW}📦 Installing production dependencies...${NC}"
source "$VENV_DIR/bin/activate"
pip install -r requirements-prod.txt
echo -e "${GREEN}✅ Production dependencies installed${NC}"

# Step 3: Test production configuration
echo -e "${YELLOW}🧪 Testing production configuration...${NC}"
python3 wsgi.py &
WSGI_PID=$!
sleep 3

# Check if the app is running
if curl -s http://localhost:5000/api/health > /dev/null; then
    echo -e "${GREEN}✅ Production app test successful${NC}"
    kill $WSGI_PID
else
    echo -e "${RED}❌ Production app test failed${NC}"
    kill $WSGI_PID
    exit 1
fi

# Step 4: Stop development service
echo -e "${YELLOW}🛑 Stopping development service...${NC}"
launchctl unload com.vctpredictor.autoscrape.plist 2>/dev/null || true
echo -e "${GREEN}✅ Development service stopped${NC}"

# Step 5: Load production service
echo -e "${YELLOW}🔄 Loading production service...${NC}"
launchctl load com.vctpredictor.autoscrape.prod.plist
echo -e "${GREEN}✅ Production service loaded${NC}"

# Step 6: Verify production service
echo -e "${YELLOW}🔍 Verifying production service...${NC}"
if launchctl list | grep -q "com.vctpredictor.autoscrape.prod"; then
    echo -e "${GREEN}✅ Production service is running${NC}"
else
    echo -e "${RED}❌ Production service failed to start${NC}"
    exit 1
fi

# Step 7: Test scraper
echo -e "${YELLOW}🧪 Testing production scraper...${NC}"
python3 auto_scrape.py
echo -e "${GREEN}✅ Production scraper test successful${NC}"

# Step 8: Create production startup script
echo -e "${YELLOW}📝 Creating production startup script...${NC}"
cat > "$PROJECT_DIR/start_production.sh" << 'EOF'
#!/bin/bash
# Production startup script for VCT Predictor

cd "$(dirname "$0")"
source venv/bin/activate
export FLASK_ENV=production

echo "🚀 Starting VCT Predictor in production mode..."
python3 wsgi.py
EOF

chmod +x "$PROJECT_DIR/start_production.sh"
echo -e "${GREEN}✅ Production startup script created${NC}"

# Step 9: Create production monitoring script
echo -e "${YELLOW}📊 Creating production monitoring script...${NC}"
cat > "$PROJECT_DIR/monitor_production.sh" << 'EOF'
#!/bin/bash
# Production monitoring script for VCT Predictor

cd "$(dirname "$0")"
source venv/bin/activate
export FLASK_ENV=production

echo "🔍 VCT Predictor Production Monitor"
echo "=================================="
python3 monitor.py
EOF

chmod +x "$PROJECT_DIR/monitor_production.sh"
echo -e "${GREEN}✅ Production monitoring script created${NC}"

echo ""
echo -e "${GREEN}🎉 Production deployment completed successfully!${NC}"
echo ""
echo "📋 Next steps:"
echo "1. Start production app: ./start_production.sh"
echo "2. Monitor production: ./monitor_production.sh"
echo "3. Check logs: tail -f logs/daemon.log"
echo "4. Auto-scraper runs daily at 3am"
echo ""
echo "🌐 Production app will be available at: http://localhost:5000"
echo "🔒 Auto-scraper is now running in production mode"
