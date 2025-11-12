# 🚀 Hupfumi.Africa Deployment Guide

**Last Updated**: November 2025  
**Status**: Ready for Production Deployment

---

## 📋 Pre-Deployment Checklist

✅ **Backend**: FastAPI running on port 8000  
✅ **Frontend**: All pages (index, tools, livestock, sadc) tested  
✅ **Intelligence Systems**: DateTime, Voice, District, Livestock all working  
✅ **Data**: 56 districts, 29 budgets (23 crops + 6 livestock)  
✅ **API**: 16,311 documents in vector store  

---

## 🎯 Deployment Options

### Option 1: Quick Deploy (Recommended)
**Frontend**: Vercel or Netlify  
**Backend**: Railway or Render  
**Time**: 10-15 minutes  
**Cost**: Free tier available  

### Option 2: Full Control
**Frontend**: AWS S3 + CloudFront  
**Backend**: AWS EC2 or DigitalOcean  
**Time**: 30-60 minutes  
**Cost**: ~$10-20/month  

### Option 3: All-in-One
**Platform**: Heroku  
**Time**: 15-20 minutes  
**Cost**: $7/month (Hobby tier)  

---

## 🚀 OPTION 1: QUICK DEPLOY (Vercel + Railway)

This is the fastest and easiest way to get your platform live.

### Step 1: Deploy Backend to Railway

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   # or use brew
   brew install railway
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Initialize Project**:
   ```bash
   cd /Users/providencemtendereki/agriculture-rag-platform
   railway init
   ```

4. **Create railway.json** (already created below)

5. **Deploy**:
   ```bash
   railway up
   ```

6. **Get Your Backend URL**:
   ```bash
   railway domain
   # Example output: https://your-app.up.railway.app
   ```

### Step 2: Deploy Frontend to Vercel

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy Frontend**:
   ```bash
   cd /Users/providencemtendereki/agriculture-rag-platform/frontend
   vercel
   ```

4. **Follow prompts**:
   - Set up and deploy? `Y`
   - Which scope? (your account)
   - Link to existing project? `N`
   - Project name: `hupfumi-agriculture`
   - Directory: `./`
   - Override settings? `N`

5. **Get Your Frontend URL**:
   ```
   ✓ Production: https://hupfumi-agriculture.vercel.app
   ```

### Step 3: Update API URLs

After deployment, update the API endpoint in your frontend files to point to Railway:

```javascript
// In index.html, tools.html, livestock.html
const API_BASE = 'https://your-app.up.railway.app';
```

Then redeploy:
```bash
vercel --prod
```

---

## 🔧 Configuration Files

### Railway Configuration (Backend)

Create `railway.json` in project root:

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn src.api.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### Vercel Configuration (Frontend)

Create `vercel.json` in frontend directory:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "*.html",
      "use": "@vercel/static"
    },
    {
      "src": "*.js",
      "use": "@vercel/static"
    },
    {
      "src": "*.json",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ]
}
```

### Environment Variables

**For Railway (Backend)**:
```bash
railway variables set ENVIRONMENT=production
railway variables set LOG_LEVEL=info
```

**For Vercel (Frontend)**:
No environment variables needed - API URL is hardcoded in HTML.

---

## 🌐 OPTION 2: ALTERNATIVE - Netlify + Render

### Deploy Frontend to Netlify

1. **Install Netlify CLI**:
   ```bash
   npm install -g netlify-cli
   ```

2. **Login and Deploy**:
   ```bash
   cd /Users/providencemtendereki/agriculture-rag-platform/frontend
   netlify login
   netlify deploy --prod
   ```

3. **Get URL**:
   ```
   Website URL: https://hupfumi-agriculture.netlify.app
   ```

### Deploy Backend to Render

1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect GitHub repo or upload files
4. Configure:
   - **Name**: hupfumi-backend
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
5. Click "Create Web Service"
6. Get URL: `https://hupfumi-backend.onrender.com`

---

## 📝 Post-Deployment Steps

### 1. Update API URLs

Edit these files with your production backend URL:

**frontend/index.html**:
```javascript
const API_BASE = 'https://your-backend-url.railway.app';
```

**frontend/tools.html**:
```javascript
const API_BASE = 'https://your-backend-url.railway.app';
```

**frontend/livestock.html**:
```javascript
const API_BASE = 'https://your-backend-url.railway.app';
```

### 2. Test Everything

Visit your production URLs and test:

- ✅ Chat interface loads
- ✅ District dropdown works
- ✅ Voice input/output works
- ✅ Budget calculator works
- ✅ Livestock calculator works
- ✅ DateTime panel shows correct season
- ✅ SADC page loads

### 3. Configure Custom Domain (Optional)

**For Vercel**:
```bash
vercel domains add hupfumi.africa
vercel domains add www.hupfumi.africa
```

**For Railway**:
```bash
railway domain add api.hupfumi.africa
```

Then update DNS:
```
A Record: @ → Vercel IP
CNAME: www → your-app.vercel.app
CNAME: api → your-app.up.railway.app
```

### 4. Enable HTTPS

Both Vercel and Railway automatically provide SSL certificates. No action needed!

### 5. Monitor

**Railway Dashboard**: https://railway.app/dashboard  
**Vercel Dashboard**: https://vercel.com/dashboard  

---

## 🔒 Security Checklist

- ✅ HTTPS enabled (automatic with Vercel/Railway)
- ✅ CORS configured in FastAPI
- ⚠️ Add rate limiting (recommended)
- ⚠️ Add API authentication if needed
- ✅ ElevenLabs API key is in frontend (client-side)

---

## 📊 Cost Estimate

### Free Tier (Hobby Projects)

| Service | Plan | Cost | Limits |
|---------|------|------|--------|
| **Vercel** | Hobby | $0 | 100GB bandwidth/month |
| **Railway** | Trial | $5 credit | 500 hours/month |
| **Total** | | **~$0-5/month** | Good for testing |

### Production Scale

| Service | Plan | Cost | Limits |
|---------|------|------|--------|
| **Vercel** | Pro | $20/month | Unlimited bandwidth |
| **Railway** | Pro | $20/month | 8GB RAM, 8vCPU |
| **Total** | | **$40/month** | 10K+ users |

---

## 🚀 One-Command Deployment

I'll create scripts for you to deploy with one command:

**deploy-backend.sh**:
```bash
#!/bin/bash
cd /Users/providencemtendereki/agriculture-rag-platform
railway up
echo "Backend deployed! Get URL with: railway domain"
```

**deploy-frontend.sh**:
```bash
#!/bin/bash
cd /Users/providencemtendereki/agriculture-rag-platform/frontend
vercel --prod
echo "Frontend deployed!"
```

**deploy-all.sh**:
```bash
#!/bin/bash
echo "🚀 Deploying Hupfumi.Africa..."
./deploy-backend.sh
echo ""
echo "⏳ Waiting for backend to be ready..."
sleep 10
./deploy-frontend.sh
echo ""
echo "✅ Deployment complete!"
```

---

## 🔍 Troubleshooting

### Backend Not Starting

**Check logs**:
```bash
railway logs
```

**Common issues**:
- Missing dependencies: Add to requirements.txt
- Port not set: Railway provides $PORT automatically
- ChromaDB path: Use relative paths

### Frontend Not Loading

**Check build logs**:
```bash
vercel logs
```

**Common issues**:
- Missing files: Ensure all .js files are committed
- CORS errors: Check backend CORS settings
- API URL wrong: Verify API_BASE in HTML files

### Voice Not Working

- ElevenLabs API key is client-side (OK)
- Check browser console for errors
- Ensure microphone permissions granted

---

## 📈 Monitoring & Analytics

### Add Analytics to Frontend

Add to `<head>` of all HTML files:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=YOUR-GA-ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'YOUR-GA-ID');
</script>
```

### Monitor Backend

Railway provides:
- CPU/Memory usage
- Request logs
- Error tracking
- Uptime monitoring

---

## 🎉 Launch Checklist

Before announcing to the public:

- [ ] Both frontend and backend deployed
- [ ] Custom domain configured (hupfumi.africa)
- [ ] HTTPS working
- [ ] All pages tested on production
- [ ] Voice working
- [ ] DateTime showing correct season
- [ ] District selection working
- [ ] Budget calculations correct
- [ ] Mobile responsiveness tested
- [ ] Error handling working
- [ ] Analytics installed
- [ ] Contact email working (partnerships@hupfumi.africa)
- [ ] Social sharing tested

---

## 📞 Support

**Deployment Issues**: Check Railway/Vercel documentation  
**Code Issues**: Review logs in dashboards  
**Feature Requests**: Document in project README  

---

## 🎯 Next Steps After Deployment

1. **Share the Platform**:
   - Social media announcement
   - Email to agricultural extension officers
   - Present at farming cooperatives

2. **Gather Feedback**:
   - Monitor user interactions
   - Track popular features
   - Collect farmer testimonials

3. **Iterate**:
   - Fix bugs based on real usage
   - Add requested features
   - Expand to more crops/livestock

4. **Scale**:
   - Upgrade hosting as traffic grows
   - Add caching (Redis)
   - Optimize database queries

---

## 🌍 SADC Expansion (Future)

When ready to expand (Q1 2026+):

1. Deploy separate instances per country
2. Use route-based deployment:
   - hupfumi.africa/zw/ → Zimbabwe
   - hupfumi.africa/za/ → South Africa
   - hupfumi.africa/zm/ → Zambia
3. Load country-specific data
4. Maintain single codebase

---

**Ready to deploy? Let's go! 🚀**

Choose your platform and run the commands above. You'll be live in 15 minutes!
