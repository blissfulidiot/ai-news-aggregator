# Render Deployment Guide

Complete guide for deploying the AI News Aggregator to Render.

## Quick Start (Recommended)

The fastest way to deploy is using the `render.yaml` file:

1. **Push to GitHub**
   ```bash
   git push origin main
   ```

2. **Connect to Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Blueprint"
   - Select your GitHub repository
   - Render will automatically detect `render.yaml`

3. **Set Environment Variables**
   - Go to the Cron Job service → Environment tab
   - Add: `OPENAI_API_KEY`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `FROM_EMAIL`
   - `DATABASE_URL` is automatically provided

4. **Initialize Database**
   - Use Render Shell: `python scripts/create_tables.py`

That's it! The cron job runs daily at 8 AM UTC.

## What Gets Deployed

### Services Created

1. **PostgreSQL Database** (`news-aggregator-db`)
   - Managed PostgreSQL service
   - Automatically provides `DATABASE_URL` to other services
   - Free tier available for testing

2. **Cron Job** (`daily-news-runner`)
   - Runs `scripts/daily_runner.py` on schedule
   - Default: Daily at 8 AM UTC
   - Has access to PostgreSQL via `DATABASE_URL`

## Environment Variables

### Required (Set Manually)

Add these in Render dashboard → Cron Job → Environment:

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | `sk-...` |
| `SMTP_USERNAME` | Gmail address | `your.email@gmail.com` |
| `SMTP_PASSWORD` | Gmail app password | `16-char-app-password` |
| `FROM_EMAIL` | Sender email | `your.email@gmail.com` |

### Optional (Defaults Provided)

| Variable | Default | Description |
|----------|---------|-------------|
| `SMTP_HOST` | `smtp.gmail.com` | SMTP server |
| `SMTP_PORT` | `587` | SMTP port |

### Automatic (No Setup Needed)

| Variable | Source |
|----------|--------|
| `DATABASE_URL` | Automatically provided by PostgreSQL service |

## Customizing the Schedule

Edit `render.yaml` and modify the `schedule` field:

```yaml
schedule: "0 8 * * *"  # Daily at 8 AM UTC
```

Common schedules:
- `"0 8 * * *"` - Daily at 8 AM UTC
- `"0 */6 * * *"` - Every 6 hours
- `"0 0 * * *"` - Daily at midnight UTC
- `"*/30 * * * *"` - Every 30 minutes (for testing)

Cron format: `minute hour day month weekday`

## Database Initialization

After deployment, initialize the database tables:

### Option 1: Render Shell (Easiest)

1. Go to Cron Job service → Shell tab
2. Run:
   ```bash
   python scripts/create_tables.py
   ```

### Option 2: Local Connection

1. Get `DATABASE_URL` from Render dashboard → PostgreSQL service
2. Set locally:
   ```bash
   export DATABASE_URL="postgresql://user:pass@host:port/dbname"
   python scripts/create_tables.py
   ```

### Option 3: Render Shell (One-liner)

```bash
cd /opt/render/project/src && python scripts/create_tables.py
```

## Manual Setup (Without render.yaml)

If you prefer manual setup:

### 1. Create PostgreSQL Database

1. Go to Render Dashboard → New → PostgreSQL
2. Name: `news-aggregator-db`
3. Database: `news_aggregator`
4. User: `postgres`
5. Plan: Free (or paid for production)
6. Copy the `DATABASE_URL` (you'll need it)

### 2. Create Cron Job

1. Go to Render Dashboard → New → Cron Job
2. Name: `daily-news-runner`
3. Command: `python scripts/daily_runner.py`
4. Schedule: `0 8 * * *` (daily at 8 AM UTC)
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `python scripts/daily_runner.py`

### 3. Connect to GitHub

1. In Cron Job settings → Connect to GitHub
2. Select your repository
3. Branch: `main` (or your default branch)

### 4. Set Environment Variables

In Cron Job → Environment tab, add:
- `DATABASE_URL` - From PostgreSQL service (auto-linked if same account)
- `OPENAI_API_KEY` - Your OpenAI API key
- `SMTP_USERNAME` - Gmail address
- `SMTP_PASSWORD` - Gmail app password
- `FROM_EMAIL` - Gmail address

### 5. Initialize Database

Use Render Shell (see above).

## Troubleshooting

### Cron Job Not Running

1. Check logs: Cron Job → Logs tab
2. Verify schedule format in `render.yaml`
3. Check environment variables are set
4. Verify database connection

### Database Connection Errors

1. Verify `DATABASE_URL` is set (auto-provided)
2. Check PostgreSQL service is running
3. Ensure database is initialized: `python scripts/create_tables.py`

### Import Errors

1. Check `requirements.txt` includes all dependencies
2. Verify Python version (3.13+)
3. Check build logs for missing packages

### Email Not Sending

1. Verify SMTP credentials in environment variables
2. Check Gmail app password is correct (not regular password)
3. Check logs for SMTP errors
4. Test locally: `python scripts/test_smtp.py recipient@example.com`

### No Content Found

1. Check scraping logs
2. Verify RSS feed URLs are accessible
3. Increase time window: Edit `daily_runner.py` or use `--hours 168`
4. Check YouTube channel usernames are correct

## Monitoring

### View Logs

- **Cron Job Logs**: Cron Job service → Logs tab
- **Database Logs**: PostgreSQL service → Logs tab

### Check Status

- **Cron Job**: Shows last run time and status
- **Database**: Shows connection count and size

### Manual Trigger

To manually trigger the pipeline:
1. Go to Cron Job service → Manual Deploy
2. Or use Render Shell: `python scripts/daily_runner.py`

## Cost Considerations

### Free Tier

- PostgreSQL: 90 days free, then $7/month
- Cron Job: Free (runs on schedule)

### Paid Plans

- PostgreSQL Starter: $7/month (persistent)
- PostgreSQL Standard: $20/month (better performance)

### Tips to Reduce Costs

- Use free tier for testing
- Upgrade only when needed
- Monitor database size
- Optimize cron schedule (run less frequently if needed)

## Updating Deployment

### After Code Changes

1. Push to GitHub:
   ```bash
   git push origin main
   ```

2. Render automatically redeploys (if auto-deploy enabled)

3. Or manually trigger: Service → Manual Deploy

### After Environment Variable Changes

1. Update in Render dashboard → Environment tab
2. Service automatically restarts

### After render.yaml Changes

1. Push changes to GitHub
2. Render detects changes and redeploys services

## Security Best Practices

1. **Never commit secrets** - Use environment variables
2. **Use app passwords** - Not regular Gmail passwords
3. **Rotate credentials** - Regularly update API keys
4. **Monitor access** - Check Render logs regularly
5. **Use paid plans** - For production (better security)

## Support

- Render Docs: https://render.com/docs
- Render Support: https://render.com/support
- Project Issues: GitHub Issues

