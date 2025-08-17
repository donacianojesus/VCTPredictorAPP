# 🚂 Railway Auto-Scraper Setup Guide

## 🎯 **Goal: Deploy Auto-Scraper to Railway (FREE)**

Your VCT Predictor now has a **Railway-based auto-scraper** that runs daily at 3am UTC to fetch fresh VLR.gg data!

## 📋 **Step-by-Step Setup:**

### **Step 1: Create New Railway Project for Scraper**
1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Choose "Deploy from GitHub repo"
4. Select your VCTPredictorAPP repository
5. **Important:** Set the **Root Directory** to `mvp3-auto-predictor`

### **Step 2: Configure Scraper Service**
1. In your new Railway project
2. Railway will auto-detect it's a Python app
3. Set these environment variables:
   ```
   DATABASE_URL={{Postgres.DATABASE_URL}}
   ```
   (Use the same PostgreSQL database from your main app)

### **Step 3: Deploy Scraper**
1. Railway will automatically build and deploy
2. The scraper will run daily at **3am UTC**
3. **Cost: FREE** ✅

## ⏰ **How It Works:**

- **Daily at 3am UTC:** Scraper automatically runs
- **Fetches data:** From VLR.gg VCT Americas standings
- **Updates database:** Replaces old data with fresh standings
- **Health tracking:** Monitors success/failure rates
- **Logs everything:** Full visibility into scraping process

## 🔧 **Files Created:**

1. **`railway_scraper.py`** - Main scraper service
2. **`railway_scraper.json`** - Railway configuration
3. **`requirements-scraper.txt`** - Python dependencies
4. **`RAILWAY_SCRAPER_SETUP.md`** - This guide

## 📊 **What You'll Get:**

- ✅ **Real VLR.gg data** (not sample data)
- ✅ **Daily updates** at 3am
- ✅ **Automatic health monitoring**
- ✅ **Zero maintenance** (set it and forget it)
- ✅ **100% FREE** forever

## 🚀 **Deployment Steps:**

1. **Create new Railway project** for scraper
2. **Connect to same database** (DATABASE_URL)
3. **Deploy** (automatic)
4. **Test** by running scraper manually
5. **Monitor** daily automatic runs

## 🎉 **Result:**

Your VCT Predictor will have:
- **Live VCT standings** from VLR.gg
- **Daily automatic updates** at 3am
- **Real-time data** instead of sample data
- **Professional scraping service** running 24/7

## 🆘 **Need Help?**

If you run into issues:
1. Check Railway logs
2. Verify DATABASE_URL is set
3. Test scraper manually first
4. Check database connection

---

**Ready to deploy your auto-scraper? Let's make it happen! 🚀**

## 🎯 **Next Steps:**

1. **Create new Railway project** for scraper
2. **Set root directory** to `mvp3-auto-predictor`
3. **Configure DATABASE_URL** environment variable
4. **Deploy and test!**

**Your VCT Predictor will have real-time data in no time! 🎮**
