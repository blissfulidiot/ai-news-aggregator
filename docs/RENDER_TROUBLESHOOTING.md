# Render Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: Missing Environment Variables

**Error:** `OpenAI API key is required. Set OPENAI_API_KEY environment variable.`

**Solution:**
1. Go to Render Dashboard → Cron Job (`daily-news-runner`) → Environment
2. Click "Add Environment Variable"
3. Add:
   - Key: `OPENAI_API_KEY`
   - Value: Your OpenAI API key (starts with `sk-`)
4. Click "Save Changes"
5. The cron job will automatically restart

**Required Environment Variables:**
- `OPENAI_API_KEY` - Your OpenAI API key
- `SMTP_USERNAME` - Your Gmail address
- `SMTP_PASSWORD` - Your Gmail app password (16 characters)
- `FROM_EMAIL` - Your Gmail address
- `DATABASE_URL` - Automatically provided (don't set manually)

### Issue 2: Database Tables Not Initialized

**Error:** `relation "user_settings" does not exist` or `relation "sources" does not exist`

**Solution:**
1. Go to Render Dashboard → Cron Job (`daily-news-runner`) → Shell
2. Run:
   ```bash
   python scripts/create_tables.py
   ```
3. You should see:
   ```
   ✓ Tables created successfully!
   Created tables:
     - sources
     - articles
     - videos
     - user_settings
     - digests
     - digests_sent
   ```

### Issue 3: No Logs Appearing

**Possible Causes:**
1. Cron hasn't run yet (scheduled for 8 AM UTC daily)
2. Build failed

**Solution:**
1. Check Builds tab for build errors
2. Manually trigger the cron job:
   - Go to Events tab
   - Click "Trigger" or "Run Now"
3. Check logs immediately after triggering

### Issue 4: SMTP Authentication Failed

**Error:** `Authentication failed` or `Invalid credentials`

**Solution:**
1. Verify you're using a Gmail app password, not your regular password
2. Make sure 2-factor authentication is enabled on your Gmail account
3. Generate a new app password if needed:
   - Go to https://myaccount.google.com/apppasswords
   - Create new app password for "Mail"
   - Copy the 16-character password (no spaces)
4. Update `SMTP_PASSWORD` in Render Environment

### Issue 5: Script Fails Silently

**Solution:**
The script now includes better logging. Check logs for:
- `[STARTUP]` messages - confirms script started
- `[ERROR]` messages - shows what's missing
- `[FATAL ERROR]` - shows exceptions with traceback

## Quick Setup Checklist

- [ ] Environment variables set in Render dashboard
- [ ] Database tables initialized (run `create_tables.py` in Shell)
- [ ] At least one user profile created (use `manage_profile.py` in Shell)
- [ ] Build succeeded (check Builds tab)
- [ ] Test run completed (manually trigger cron job)

## Testing the Setup

1. **Initialize Database:**
   ```bash
   python scripts/create_tables.py
   ```

2. **Create a Test User:**
   ```bash
   python scripts/manage_profile.py create test@example.com "Test User" "Software developer" "AI, technology, news"
   ```

3. **Manually Trigger Cron Job:**
   - Go to Events tab
   - Click "Trigger" or "Run Now"
   - Watch logs for errors

4. **Check Results:**
   - Logs should show successful scraping, digest generation, and email sending
   - Check your email inbox for the test email

## Getting Help

If issues persist:
1. Check the full error traceback in logs
2. Verify all environment variables are set correctly
3. Ensure database tables are initialized
4. Check Render Status page for service outages
5. Contact Render support if needed

