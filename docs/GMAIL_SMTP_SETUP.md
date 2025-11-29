# Gmail SMTP Setup Guide

This guide explains how to set up Gmail SMTP with an app password to send emails from the news aggregator.

## Why Use App Password Instead of Gmail API?

- **Simpler setup**: No OAuth flow or credentials.json file needed
- **Easier to use**: Just configure SMTP credentials in `.env`
- **Same reliability**: Uses Gmail's SMTP server directly
- **Better for automation**: No token refresh needed

## Step-by-Step Setup

### Step 1: Enable 2-Factor Authentication

1. Go to your [Google Account Security](https://myaccount.google.com/security)
2. Under "Signing in to Google", click **2-Step Verification**
3. Follow the prompts to enable 2-factor authentication
4. This is required to generate app passwords

### Step 2: Generate App Password

1. Go to [App Passwords](https://myaccount.google.com/apppasswords)
   - You may need to sign in again
2. Select **Mail** from the "Select app" dropdown
3. Select **Other (Custom name)** from the "Select device" dropdown
4. Enter a name like "News Aggregator" or "AI News Aggregator"
5. Click **Generate**
6. **Copy the 16-character password** (it will look like: `abcd efgh ijkl mnop`)
   - **Important**: You can only see this password once!

### Step 3: Configure Environment Variables

Add the following to your `.env` file:

```bash
# Gmail SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
FROM_EMAIL=your_email@gmail.com
```

**Important Notes:**
- `SMTP_USERNAME`: Your Gmail address (e.g., `yourname@gmail.com`)
- `SMTP_PASSWORD`: The 16-character app password (remove spaces if any)
- `FROM_EMAIL`: Usually the same as `SMTP_USERNAME`
- `SMTP_HOST`: `smtp.gmail.com` (default)
- `SMTP_PORT`: `587` for TLS (default)

### Step 4: Test the Configuration

Run the test script to verify everything works:

```bash
python scripts/test_smtp.py
```

Or send a test email digest:

```bash
python scripts/send_email_digest.py your_email@example.com 24 html
```

## Troubleshooting

### "SMTP credentials not configured"
- Make sure all SMTP variables are set in your `.env` file
- Check that the file is in the project root
- Restart your application/script after adding variables

### "Authentication failed" or "Invalid credentials"
- Verify your app password is correct (16 characters, no spaces)
- Make sure 2-factor authentication is enabled
- Try generating a new app password

### "Connection refused" or "Connection timeout"
- Check your firewall/network settings
- Verify SMTP_PORT is 587 (not 465)
- Try using port 465 with SSL instead (requires code change)

### "Email not received"
- Check spam/junk folder
- Verify recipient email address is correct
- Check Gmail account for any security alerts
- Make sure you're not hitting Gmail's sending limits (500 emails/day for free accounts)

## Gmail Sending Limits

- **Free Gmail accounts**: 500 emails per day
- **Google Workspace**: 2000 emails per day
- **Maximum email size**: 25MB

If you need to send more emails, consider:
- Using a dedicated email service (SendGrid, Mailgun, etc.)
- Upgrading to Google Workspace
- Using multiple Gmail accounts with rotation

## Security Best Practices

1. **Never commit `.env` file** - It's already in `.gitignore`
2. **Use app passwords** - Don't use your main Gmail password
3. **Rotate app passwords** - Generate new ones periodically
4. **Limit access** - Only give app passwords to trusted applications
5. **Monitor usage** - Check your Google Account for unusual activity

## Alternative: Using Gmail API

If you prefer using Gmail API with OAuth 2.0 instead of SMTP, see:
- `docs/GMAIL_API_SETUP.md` (if exists)
- [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python)

## References

- [Gmail SMTP Settings](https://support.google.com/mail/answer/7126229)
- [App Passwords Help](https://support.google.com/accounts/answer/185833)
- [Mailtrap Gmail API Guide](https://mailtrap.io/blog/send-emails-with-gmail-api/)

