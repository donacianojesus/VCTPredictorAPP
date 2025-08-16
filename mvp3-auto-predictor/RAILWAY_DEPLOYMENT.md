# 🚂 Railway Deployment Guide - VCT Predictor

## 🎯 **Goal: Deploy to Railway (FREE) and Cancel Heroku Charges**

## 📋 **Step-by-Step Deployment:**

### **Step 1: Create Railway Account**
1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Sign up with GitHub (recommended) or email
4. **Cost: FREE** ✅

### **Step 2: Create New Project**
1. Click "Deploy from GitHub repo"
2. Connect your GitHub account
3. Select your VCT Predictor repository
4. Click "Deploy Now"

### **Step 3: Add PostgreSQL Database**
1. In your Railway project dashboard
2. Click "New Service" → "Database" → "PostgreSQL"
3. **Cost: FREE** ✅ (included in free tier)

### **Step 4: Configure Environment Variables**
Railway will automatically detect your app, but you may need to set:
- `FLASK_ENV=production`
- `DATABASE_URL` (Railway will provide this automatically)

### **Step 5: Deploy**
1. Railway will automatically build and deploy your app
2. You'll get a URL like: `https://your-app-name.railway.app`
3. **Cost: FREE** ✅

## 💰 **Cost Comparison:**

| Platform | Hosting | Database | Total |
|----------|---------|----------|-------|
| **Heroku** | $7/month | $5/month | **$12/month** |
| **Railway** | FREE | FREE | **$0/month** |

**Savings: $12/month = $144/year!** 🎉

## 🚫 **Step 6: Cancel Heroku (Stop Charges)**

### **Option A: Delete Heroku App (Immediate)**
```bash
# This will stop all charges immediately
heroku apps:destroy vct-americas-predictor --confirm vct-americas-predictor
```

### **Option B: Remove Paid Add-ons (Keep App)**
```bash
# Remove the $5/month database
heroku addons:destroy postgresql-flat-82698 --app vct-americas-predictor

# This keeps your app but removes the database (and charges)
```

## 🔄 **Migration Process:**

### **Database Migration:**
1. **Export from Heroku** (if you want to keep data):
   ```bash
   heroku pg:backups:capture --app vct-americas-predictor
   heroku pg:backups:download --app vct-americas-predictor
   ```

2. **Import to Railway** (optional):
   - Railway will create a fresh database
   - Your app will initialize it automatically
   - All tables and sample data will be recreated

## ✅ **What You'll Have on Railway:**

- ✅ **Web App**: Same VCT Predictor interface
- ✅ **Database**: PostgreSQL for all your data
- ✅ **Auto-scraping**: Daily VCT data updates
- ✅ **Performance**: Often better than Heroku
- ✅ **Cost**: $0/month forever
- ✅ **Custom Domain**: Can add your own domain later

## 🎯 **Timeline:**

1. **Now**: Deploy to Railway (5 minutes)
2. **Test**: Make sure everything works
3. **Cancel Heroku**: Stop the $5/month charge
4. **Result**: Free, working VCT Predictor! 🎉

## 🆘 **Need Help?**

If you run into any issues:
1. Check Railway's logs in the dashboard
2. Verify environment variables are set
3. Check database connection
4. Test the web interface

---

**Ready to save $12/month and deploy for FREE? Let's do this! 🚀**
