# Changelog

All notable changes to DoorDash 50-Point Alert will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

_No unreleased changes._

---

## [1.7.0] - 2026-01-25

### Added
- `src/list_contacts.py` - Dedicated script for listing contacts
- "The Deal" section on landing page with full promo details:
  - DashPass members only requirement
  - 50% off up to $10
  - NBA50 promo code
  - 9 AM - 11:59 PM PT validity window
  - Subtotal-only disclaimer

### Changed
- Landing page "How It Works" now shows correct promo window (9 AM - 11:59 PM PT)

### Removed
- Feedback feature entirely (worker + landing page popup)
- `add_contacts.py` - contacts already imported, file contained exposed emails

### Fixed
- `admin_tasks.yml` - Replaced fragile inline Python with dedicated script

### Security
- **Git history scrubbed** - Removed 86 subscriber emails from all commits
- **No emails exposed** - Only placeholder emails remain in codebase
- Removed XSS-vulnerable feedback handler
- Worker simplified to signup + unsubscribe only (2 env vars: RESEND_API_KEY, RESEND_AUDIENCE_ID)

---

## [1.5.1] - 2026-01-24

### Fixed
- Unsubscribe link now points to custom unsubscribe page instead of Resend default

---

## [1.5.0] - 2026-01-23

### Added
- **Broadcasts API** - Uses Resend Broadcasts for production emails (automatic unsubscribe handling)
- **Admin workflow** (`admin_tasks.yml`) - Manual workflow for contact management tasks
- **List contacts task** - View all subscribers and their status

### Changed
- Production emails now use Broadcasts API instead of individual sends

---

## [1.4.1] - 2026-01-22

### Fixed
- Email template rendering issues

---

## [1.4.0] - 2026-01-22

### Changed
- Complete email redesign with clean DoorDash style
- Professional HTML email with DoorDash red (#FF3008)
- Added player stats cards
- Added share button

---

## [1.3.0] - 2026-01-21

### Added
- Landing page images

### Changed
- Clean professional redesign with DoorDash brand colors

---

## [1.2.0] - 2026-01-20

### Added
- **Cloudflare Worker** for signup/unsubscribe handling
- Signup endpoint: `POST /`
- Unsubscribe endpoint: `GET/POST /unsubscribe`

---

## [1.1.0] - 2026-01-19

### Added
- **NBA V3 Box Score API** - Updated from deprecated V2 endpoint
- Unicode name handling (e.g., Doncic)
- Safe print for Windows console

---

## [1.0.0] - 2026-01-18

### Added
- Initial release
- **Score Checker** (`check_fifty.py`) - Daily NBA 50+ point game detection
- **Email Sender** (`send_email.py`) - Alert emails via Resend API
- **GitHub Actions Workflows**:
  - `check_scores.yml` - Runs at 1:30 AM PT daily
  - `send_alert.yml` - Runs at 9:00 AM PT daily
- **Landing Page** (`index.html`) - Signup page for subscribers
- Test mode with Luka's 73-point game (2024-01-26)
- Preview mode for email testing

---

# Project Status Summary

**Last Updated:** 2026-01-25

## Architecture

```
NBA API → check_fifty.py (1:30 AM PT) → alert_state.json → send_email.py (9:00 AM PT) → Resend Broadcasts → Subscribers
```

## Current Stats

| Metric | Value |
|--------|-------|
| **Subscribers** | 86 contacts (in Resend) |
| **Daily Schedule** | Check: 1:30 AM PT, Send: 9:00 AM PT |
| **Email Service** | Resend (Broadcasts API) |
| **Points Threshold** | 50+ points |
| **Promo Code** | NBA50 |
| **Promo Window** | 9 AM - 11:59 PM PT (DashPass members only) |
| **Max Discount** | 50% off, up to $10 |

## Files Overview

| File | Purpose |
|------|---------|
| `src/check_fifty.py` | NBA API score checker |
| `src/send_email.py` | Email sender (Broadcasts) |
| `src/list_contacts.py` | List all subscribers |
| `src/config.py` | Configuration settings |
| `data/alert_state.json` | Inter-workflow state |
| `.github/workflows/check_scores.yml` | Score check workflow (1:30 AM PT) |
| `.github/workflows/send_alert.yml` | Email send workflow (9:00 AM PT) |
| `.github/workflows/admin_tasks.yml` | Admin tasks (list_contacts) |
| `worker/index.js` | Cloudflare Worker (signup + unsubscribe) |
| `index.html` | Landing page |

## Required Secrets

### GitHub Actions
```
RESEND_API_KEY       - Resend API key
RESEND_AUDIENCE_ID   - Resend Audience UUID
EMAIL_FROM           - Sender email address
```

### Cloudflare Worker
```
RESEND_API_KEY       - Resend API key
RESEND_AUDIENCE_ID   - Resend Audience UUID
```

## Key URLs

| URL | Purpose |
|-----|---------|
| https://urielgre.github.io/doordash-fifty-alert/ | Landing page |
| https://fifty-point-signup.urielgre.workers.dev/ | Signup API (POST) |
| https://fifty-point-signup.urielgre.workers.dev/unsubscribe | Unsubscribe page |

## Testing

```bash
# Test score checker (Luka's 73-point game)
python src/check_fifty.py --test

# Preview email without sending
python src/send_email.py --preview

# Send test email
python src/send_email.py --test your@email.com

# List all contacts (requires env vars)
python src/list_contacts.py
```

## Workflow Status

Both workflows running successfully as of 2026-01-25:
- **check_scores.yml** - Runs daily at 1:30 AM PT
- **send_alert.yml** - Runs daily at 9:00 AM PT (only sends if alert_needed=true)

## Security Notes

- No real emails in codebase (git history scrubbed)
- All secrets via environment variables
- Worker only needs 2 env vars (no admin emails)
- XSS vulnerability removed (feedback feature deleted)
