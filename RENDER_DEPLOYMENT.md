# Deploying to Render

This guide will walk you through deploying your certificate generator to Render with Supabase PostgreSQL.

## Prerequisites

1. **GitHub Account** - Your code needs to be on GitHub
2. **Render Account** - Sign up at [render.com](https://render.com) (free tier available)
3. **Supabase Account** - For PostgreSQL database (follow SUPABASE_SETUP.md)

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend    │────▶│  Supabase   │
│  (Static)   │     │  (Web Service)│     │ (PostgreSQL)│
│   Render    │     │    Render     │     │   Cloud     │
└─────────────┘     └──────────────┘     └─────────────┘
```

## Step 1: Prepare Your Repository

### 1.1 Push Code to GitHub

```bash
cd "C:\Users\DELL\certificate urdu\certificate-generator2"

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Prepare for Render deployment"

# Create GitHub repo and push
# (Follow GitHub's instructions to create a new repository)
git remote add origin https://github.com/YOUR_USERNAME/certificate-generator.git
git branch -M main
git push -u origin main
```

### 1.2 Create Backend Build Script

Create `backend/build.sh`:

```bash
#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt
```

### 1.3 Create Backend Start Script

This is already in your code, but verify `backend/main.py` has:

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Step 2: Deploy Backend to Render

### 2.1 Create Web Service

1. Go to [render.com/dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select your repository: `certificate-generator`

### 2.2 Configure Web Service

Fill in the following settings:

| Field | Value |
|-------|-------|
| **Name** | `certificate-api` (or your choice) |
| **Region** | Choose closest to your users |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | `Free` (for testing) |

### 2.3 Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add these variables:

```bash
DATABASE_TYPE=postgresql
DATABASE_URL=your-supabase-connection-string-here
PYTHON_VERSION=3.11.0
```

**Important**: Get your DATABASE_URL from Supabase:
- Go to Supabase Dashboard → Settings → Database
- Copy "URI" connection string
- Example: `postgresql://postgres.xxx:password@xxx.supabase.co:6543/postgres`

### 2.4 Deploy

1. Click **"Create Web Service"**
2. Wait 2-3 minutes for deployment
3. Your API will be available at: `https://certificate-api.onrender.com`

### 2.5 Test Backend

Visit: `https://certificate-api.onrender.com/`

You should see:
```json
{
  "message": "Certificate API",
  "urdu_support": true,
  "libraqm_available": false,
  "urdu_font": "Tahoma",
  "templates_count": 0,
  "database": "postgresql"
}
```

**Important**: Note your backend URL! You'll need it for the frontend.

## Step 3: Deploy Frontend to Render

### 3.1 Update Frontend API URL

Edit `frontend/.env.production`:

```bash
VITE_API_URL=https://certificate-api.onrender.com
```

If the file doesn't exist, create it.

### 3.2 Update vite.config.js

Ensure `frontend/vite.config.js` has:

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
  preview: {
    port: 5173,
  }
})
```

### 3.3 Create Static Site

1. Go to Render Dashboard
2. Click **"New +"** → **"Static Site"**
3. Connect your GitHub repository
4. Select your repository: `certificate-generator`

### 3.4 Configure Static Site

| Field | Value |
|-------|-------|
| **Name** | `certificate-generator` |
| **Branch** | `main` |
| **Root Directory** | `frontend` |
| **Build Command** | `npm install && npm run build` |
| **Publish Directory** | `dist` |

### 3.5 Add Environment Variable

Click **"Advanced"** → **"Add Environment Variable"**:

```bash
VITE_API_URL=https://certificate-api.onrender.com
```

**Important**: Replace with YOUR actual backend URL from Step 2.4

### 3.6 Deploy

1. Click **"Create Static Site"**
2. Wait 2-3 minutes for build and deployment
3. Your frontend will be available at: `https://certificate-generator.onrender.com`

## Step 4: Configure CORS

Update `backend/main.py` to allow your frontend domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://certificate-generator.onrender.com",  # Add your frontend URL
        "*"  # Remove this in production for better security
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Commit and push:
```bash
git add backend/main.py
git commit -m "Update CORS for production"
git push
```

Render will automatically redeploy your backend.

## Step 5: Test Everything

### 5.1 Test Backend API
```bash
curl https://certificate-api.onrender.com/
```

### 5.2 Test Frontend
1. Visit: `https://certificate-generator.onrender.com`
2. Upload a certificate template
3. Add Urdu text: احمد علی
4. Generate certificate
5. Verify it appears correctly

### 5.3 Test Certificate Generation

Create a test template, then visit:
```
https://certificate-api.onrender.com/api/certificate/1?name=احمد%20علی
```

You should see a certificate PNG image with properly formatted Urdu text.

## Troubleshooting

### Backend Build Fails

**Error: "Could not find a version that satisfies the requirement"**
- Solution: Add `PYTHON_VERSION=3.11.0` environment variable

**Error: "No module named 'db'"**
- Solution: Make sure Root Directory is set to `backend`

### Frontend Build Fails

**Error: "VITE_API_URL is not defined"**
- Solution: Add `VITE_API_URL` environment variable in Render dashboard

**Error: "Failed to fetch"**
- Solution: Check CORS settings in backend
- Verify API URL is correct in frontend

### Database Connection Error

**Error: "could not connect to server"**
- Solution: Verify DATABASE_URL is correct
- Check Supabase project is not paused
- Ensure templates table exists (run SQL from SUPABASE_SETUP.md)

### Certificate Not Generating

**Error: "Template not found"**
- Solution: Create a template first through the frontend UI

**Urdu text not showing**
- Solution: Verify template language is set to 'ur'
- Check arabic-reshaper and python-bidi are installed (they should be in requirements.txt)

### Free Tier Limitations

**Backend goes to sleep after 15 minutes of inactivity**
- Solution: Upgrade to paid plan ($7/month) for always-on service
- Or: Accept 30-50 second cold start on first request

**Build takes too long**
- Solution: Optimize build process or upgrade to faster instance

## Cost Estimation

### Free Tier (Good for testing)
- Backend: Free Web Service (sleeps after 15 min inactivity)
- Frontend: Free Static Site
- Database: Supabase Free Tier (500MB)
- **Total: $0/month**

### Paid Tier (Production ready)
- Backend: Starter Web Service - $7/month
- Frontend: Still free!
- Database: Supabase Free Tier (500MB) or Pro ($25/month for more)
- **Total: $7-32/month**

## Custom Domain (Optional)

### Add Custom Domain to Frontend
1. Go to your Static Site settings
2. Click "Custom Domains"
3. Add your domain (e.g., `certificates.yourdomain.com`)
4. Follow DNS configuration instructions

### Add Custom Domain to Backend
1. Go to your Web Service settings
2. Click "Custom Domains"
3. Add your API subdomain (e.g., `api.yourdomain.com`)
4. Update frontend VITE_API_URL

## Continuous Deployment

Render automatically redeploys when you push to GitHub:

```bash
# Make changes to your code
git add .
git commit -m "Update feature"
git push

# Render will automatically:
# 1. Detect the push
# 2. Build your application
# 3. Deploy the new version
```

## Monitoring

### View Logs
1. Go to Render Dashboard
2. Click on your service
3. Click "Logs" tab
4. Monitor real-time logs

### Check Service Health
- Backend: `https://certificate-api.onrender.com/`
- Frontend: `https://certificate-generator.onrender.com/`

## Security Best Practices

1. **Environment Variables**: Never commit `.env` to git
2. **CORS**: Remove `"*"` from allowed origins in production
3. **Database**: Use strong password for Supabase
4. **API Keys**: Store in Render environment variables, not in code
5. **HTTPS**: Render provides free SSL certificates automatically

## Next Steps

- Set up monitoring with Render's built-in tools
- Configure custom domain for professional branding
- Upgrade to paid tier for always-on service
- Add authentication for admin features
- Set up automated backups for Supabase

## Support

- Render Docs: [render.com/docs](https://render.com/docs)
- Render Discord: [render.com/discord](https://render.com/discord)
- Supabase Docs: [supabase.com/docs](https://supabase.com/docs)

## Quick Reference

```bash
# Backend URL
https://certificate-api.onrender.com

# Frontend URL
https://certificate-generator.onrender.com

# API Docs
https://certificate-api.onrender.com/docs

# Test Certificate Generation
https://certificate-api.onrender.com/api/certificate/1?name=YourName
```

---

**Congratulations!** 🎉 Your certificate generator is now live and accessible from anywhere in the world!
