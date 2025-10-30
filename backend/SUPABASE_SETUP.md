# Supabase PostgreSQL Setup Guide

This guide will help you set up Supabase as your production database for the certificate generator.

## Step 1: Create a Supabase Account

1. Go to [https://supabase.com](https://supabase.com)
2. Click "Start your project"
3. Sign up with GitHub, Google, or email

## Step 2: Create a New Project

1. Click "New Project" in your dashboard
2. Fill in the project details:
   - **Project Name**: `certificate-generator` (or your preferred name)
   - **Database Password**: Choose a strong password (save this!)
   - **Region**: Select the closest region to your users
   - **Pricing Plan**: Free tier is fine for testing

3. Click "Create new project"
4. Wait 2-3 minutes for Supabase to provision your database

## Step 3: Get Your Database Credentials

1. In your Supabase project dashboard, click "Settings" (gear icon) in the sidebar
2. Click "Database" under Settings
3. Scroll down to "Connection string" section
4. You'll find several connection modes. We'll use **"URI"** mode.

### Connection String Format:
```
postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

**Example:**
```
postgresql://postgres.abcdefghijklmnop:YourPassword123@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

### Important Notes:
- Replace `[password]` with your database password
- The connection string uses **port 6543** (Supabase pooler for better performance)
- Keep this connection string secret - never commit it to git!

## Step 4: Create the Templates Table

1. In Supabase dashboard, click "SQL Editor" in the sidebar
2. Click "New query"
3. Copy and paste this SQL:

```sql
-- Create templates table
CREATE TABLE IF NOT EXISTS templates (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    image_base64 TEXT NOT NULL,
    text_x REAL NOT NULL,
    text_y REAL NOT NULL,
    font TEXT NOT NULL,
    font_size INTEGER NOT NULL,
    alignment TEXT NOT NULL,
    color TEXT NOT NULL,
    language TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster queries
CREATE INDEX idx_templates_language ON templates(language);
CREATE INDEX idx_templates_created_at ON templates(created_at DESC);

-- Enable Row Level Security (optional, for added security)
ALTER TABLE templates ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (you can customize this later)
CREATE POLICY "Allow all operations on templates" ON templates
    FOR ALL
    USING (true)
    WITH CHECK (true);
```

4. Click "Run" or press `Ctrl+Enter`
5. You should see "Success. No rows returned"

## Step 5: Configure Your Application

Create a `.env` file in the `backend` directory:

```bash
# Database Configuration
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
DATABASE_TYPE=postgresql

# Optional: Fallback to SQLite for local development
# DATABASE_TYPE=sqlite
# DATABASE_PATH=certificates.db
```

**Replace the placeholders:**
- `[project-ref]`: Your project reference (e.g., `abcdefghijklmnop`)
- `[password]`: Your database password
- `[region]`: Your region (e.g., `us-east-1`)

## Step 6: Install Dependencies

In your backend directory, run:

```bash
pip install -r requirements.txt
```

This will install `psycopg2-binary` (PostgreSQL driver) and other dependencies.

## Step 7: Test the Connection

Run your application:

```bash
python main.py
```

Visit: `http://localhost:8000/`

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

If you see `"database": "postgresql"`, congratulations! You're connected to Supabase.

## Troubleshooting

### Error: "could not connect to server"
- Check your internet connection
- Verify the connection string is correct
- Make sure you replaced `[password]` with actual password (no brackets)

### Error: "relation 'templates' does not exist"
- Go back to Step 4 and run the SQL to create the table

### Error: "password authentication failed"
- Double-check your database password in the connection string
- You can reset the password in Supabase Settings > Database

### Want to switch back to SQLite?
Change in `.env`:
```bash
DATABASE_TYPE=sqlite
DATABASE_PATH=certificates.db
```

## Security Best Practices

1. **Never commit `.env` file to git**
   - Add `.env` to your `.gitignore` file

2. **Use environment variables in production**
   - On deployment platforms (Render, Railway, Vercel, etc.)
   - Set `DATABASE_URL` as an environment variable

3. **Rotate your database password regularly**
   - Change it in Supabase Settings > Database
   - Update your `.env` file

## Next Steps

- Deploy your backend to a cloud platform (Render, Railway, Fly.io)
- Set up Supabase Storage for better image handling (optional)
- Configure Row Level Security policies for multi-user support
- Enable Supabase Realtime for live updates (optional)

## Support

- Supabase Docs: [https://supabase.com/docs](https://supabase.com/docs)
- Supabase Discord: [https://discord.supabase.com](https://discord.supabase.com)
