# Render Deployment Checklist

Use this checklist to deploy your certificate generator to Render.

## Before You Start

- [ ] Code is working locally
- [ ] All changes are committed
- [ ] You have a GitHub account
- [ ] You have a Render account (free at render.com)
- [ ] You have a Supabase account (free at supabase.com)

## Step 1: Set Up Supabase Database

- [ ] Create Supabase project at supabase.com
- [ ] Wait for project to initialize (2-3 minutes)
- [ ] Go to Settings > Database > Connection string
- [ ] Copy the "URI" connection string
- [ ] Go to SQL Editor
- [ ] Run the SQL from `backend/SUPABASE_SETUP.md` to create templates table
- [ ] Verify table created: `SELECT * FROM templates;`

**Connection String Example:**
```
postgresql://postgres.abc123:password@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

Save this! You'll need it for Render.

## Step 2: Push Code to GitHub

- [ ] Create new repository on GitHub
- [ ] Initialize git: `git init`
- [ ] Add files: `git add .`
- [ ] Commit: `git commit -m "Initial deployment"`
- [ ] Add remote: `git remote add origin https://github.com/USERNAME/REPO.git`
- [ ] Push: `git push -u origin main`

## Step 3: Deploy Backend to Render

- [ ] Go to render.com/dashboard
- [ ] Click "New +" → "Web Service"
- [ ] Connect GitHub repository
- [ ] Configure service:
  - Name: `certificate-api`
  - Root Directory: `backend`
  - Runtime: `Python 3`
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
  - Instance Type: `Free`

- [ ] Add Environment Variables:
  - `DATABASE_TYPE` = `postgresql`
  - `DATABASE_URL` = (paste your Supabase connection string)
  - `PYTHON_VERSION` = `3.11.0`

- [ ] Click "Create Web Service"
- [ ] Wait for deployment (2-3 minutes)
- [ ] Note your backend URL (e.g., `https://certificate-api.onrender.com`)

## Step 4: Test Backend

- [ ] Visit: `https://certificate-api.onrender.com/`
- [ ] Verify response shows:
  ```json
  {
    "database": "postgresql",
    "urdu_support": true,
    ...
  }
  ```

## Step 5: Update Frontend for Production

- [ ] Edit `frontend/.env.production`:
  ```bash
  VITE_API_URL=https://your-actual-backend-url.onrender.com
  ```
- [ ] Commit changes:
  ```bash
  git add frontend/.env.production
  git commit -m "Update production API URL"
  git push
  ```

## Step 6: Deploy Frontend to Render

- [ ] Go to render.com/dashboard
- [ ] Click "New +" → "Static Site"
- [ ] Connect GitHub repository
- [ ] Configure site:
  - Name: `certificate-generator`
  - Root Directory: `frontend`
  - Build Command: `npm install && npm run build`
  - Publish Directory: `dist`

- [ ] Add Environment Variable:
  - `VITE_API_URL` = `https://your-backend-url.onrender.com`

- [ ] Click "Create Static Site"
- [ ] Wait for build (2-3 minutes)
- [ ] Note your frontend URL (e.g., `https://certificate-generator.onrender.com`)

## Step 7: Update CORS

- [ ] Edit `backend/main.py`:
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=[
          "http://localhost:5173",
          "https://certificate-generator.onrender.com",  # Add your frontend URL
      ],
      ...
  )
  ```

- [ ] Commit and push:
  ```bash
  git add backend/main.py
  git commit -m "Update CORS for production"
  git push
  ```

- [ ] Render will automatically redeploy backend

## Step 8: Final Testing

- [ ] Visit your frontend URL
- [ ] Upload a certificate template image
- [ ] Configure text position and settings
- [ ] Test English text: "John Doe"
- [ ] Test Urdu text: "احمد علی"
- [ ] Save template to database
- [ ] Generate certificate via API
- [ ] Verify Urdu text displays correctly (connected characters, RTL)

## Step 9: Test API Directly

- [ ] Test API endpoint:
  ```
  https://certificate-api.onrender.com/api/certificate/1?name=احمد%20علی
  ```
- [ ] Verify PNG image is returned with proper Urdu text

## Troubleshooting

### Backend Build Failed
- [ ] Check logs in Render dashboard
- [ ] Verify `requirements.txt` is correct
- [ ] Ensure Root Directory is set to `backend`

### Frontend Build Failed
- [ ] Check build logs
- [ ] Verify `package.json` exists in frontend directory
- [ ] Ensure VITE_API_URL is set

### Database Connection Error
- [ ] Double-check DATABASE_URL (no spaces, correct format)
- [ ] Verify Supabase project is active (not paused)
- [ ] Confirm templates table exists in Supabase

### CORS Error
- [ ] Verify frontend URL is in CORS allow_origins
- [ ] Check backend redeployed after CORS change
- [ ] Try adding `"*"` temporarily for testing

### Certificate Not Generating
- [ ] Create a template first through the UI
- [ ] Verify template language is 'ur' for Urdu
- [ ] Check backend logs for errors

## Post-Deployment

- [ ] Test from different devices/browsers
- [ ] Monitor logs for errors
- [ ] Consider upgrading to paid tier ($7/month) for always-on service
- [ ] Set up custom domain (optional)
- [ ] Add monitoring/alerting

## Costs

**Free Tier:**
- Backend: Free (sleeps after 15 min inactivity)
- Frontend: Free
- Database: Free (500MB)
- **Total: $0/month**

**Paid Tier (Recommended for Production):**
- Backend: $7/month (always on, faster)
- Frontend: Free
- Database: Free or $25/month for Supabase Pro
- **Total: $7-32/month**

## Important URLs

**Documentation:**
- Render Deployment Guide: `RENDER_DEPLOYMENT.md`
- Supabase Setup: `backend/SUPABASE_SETUP.md`
- Main README: `README.md`

**Your Live Services:**
```
Frontend: https://_____________________.onrender.com
Backend:  https://_____________________.onrender.com
Supabase: https://app.supabase.com/project/_____
```

**API Docs (Swagger):**
```
https://your-backend.onrender.com/docs
```

## Success Criteria

✅ All checkboxes above are complete
✅ Backend returns 200 OK at root endpoint
✅ Frontend loads without errors
✅ Can create templates through UI
✅ Can generate certificates with English names
✅ Can generate certificates with Urdu names (احمد علی)
✅ Urdu text displays correctly (connected, RTL)
✅ No CORS errors in browser console

---

**Congratulations!** 🎉 Your application is live!

Share your certificate generator:
- Frontend: https://your-site.onrender.com
- API: https://your-api.onrender.com/docs
