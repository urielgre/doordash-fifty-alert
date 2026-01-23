# DoorDash 50-Point Alert 🏀

Get notified when DoorDash's 50% off promo is live after an NBA player scores 50+ points.

## How It Works

1. **Check Scores** (1:30 AM PT daily): Script checks yesterday's NBA games for 50+ point performances
2. **Send Alert** (9:00 AM PT): If found, emails all subscribers about the promo
3. **Promo Window**: 9 AM - 11 AM PT the day after a 50+ point game

## Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/YOUR_USERNAME/doordash-fifty-alert.git
cd doordash-fifty-alert
pip install -r requirements.txt
```

### 2. Test NBA API

```bash
# Test with Luka's 73-point game (Jan 25, 2024)
python src/check_fifty.py --test

# Check yesterday's games
python src/check_fifty.py

# Check a specific date
python src/check_fifty.py --date 2024-01-25
```

### 3. Set Up Resend

1. Create account at [resend.com](https://resend.com)
2. Create an Audience (subscriber list)
3. Copy your API key and Audience ID

```bash
# Create .env file
cp .env.example .env
# Edit .env with your credentials
```

### 4. Test Email

```bash
# Preview email without sending
python src/send_email.py --preview

# Send test email to yourself
python src/send_email.py --test your@email.com
```

### 5. Deploy to GitHub

1. Create new GitHub repository
2. Push this code
3. Add secrets in Settings > Secrets:
   - `RESEND_API_KEY`
   - `RESEND_AUDIENCE_ID`
   - `EMAIL_FROM` (e.g., `DoorDash Alerts <alerts@yourdomain.com>`)

### 6. Deploy Landing Page

**Option A: GitHub Pages**
- Enable in Settings > Pages
- Set source to main branch

**Option B: Vercel**
- Connect repo to Vercel
- Auto-deploys on push

## File Structure

```
doordash-fifty-alert/
├── .github/workflows/
│   ├── check_scores.yml    # Daily score check (1:30 AM PT)
│   └── send_alert.yml      # Daily alert send (9:00 AM PT)
├── src/
│   ├── check_fifty.py      # NBA API score checker
│   ├── send_email.py       # Resend email sender
│   └── config.py           # Configuration
├── data/
│   └── alert_state.json    # Tracks if alert needed
├── index.html              # Signup landing page
├── requirements.txt
└── README.md
```

## GitHub Secrets Required

| Secret | Description | Example |
|--------|-------------|---------|
| `RESEND_API_KEY` | Your Resend API key | `re_xxxxxxxxx` |
| `RESEND_AUDIENCE_ID` | Your Resend Audience ID | `xxxxxxxx-xxxx-...` |
| `EMAIL_FROM` | Sender email address | `Alerts <alerts@domain.com>` |

## Manual Workflow Triggers

You can manually trigger workflows from GitHub Actions:

- **Check Scores**: Test with specific date or Luka's 73-pt game
- **Send Alert**: Send test email to any address

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your Resend credentials

# Test score checking
python src/check_fifty.py --test

# Preview email
python src/send_email.py --preview

# Send test email
python src/send_email.py --test your@email.com
```

## Cost

| Service | Free Tier | Usage |
|---------|-----------|-------|
| GitHub Actions | 2,000 min/month | ~60 min/month |
| Resend | 3,000 emails/month | Depends on subs |
| GitHub Pages | Unlimited | 1 page |
| **Total** | **$0/month** | ✅ |

## License

MIT
