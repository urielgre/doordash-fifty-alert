# Changelog

All notable changes to DoorDash 50-Point Alert will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- `src/list_contacts.py` - Dedicated script for listing contacts (replaces inline Python)

### Fixed
- `admin_tasks.yml` - Replaced fragile inline Python with dedicated script

### Security
- `worker/index.js` - Added HTML escaping to prevent XSS in feedback emails
- `worker/index.js` - Moved admin emails to environment variables
- Removed `add_contacts.py` containing hardcoded subscriber emails
- Scrubbed git history to remove all exposed email addresses

---

## [1.5.1] - 2026-01-24

### Fixed
- Unsubscribe link now points to custom unsubscribe page instead of Resend default

---

## [1.5.0] - 2026-01-23

### Added
- **Broadcasts API** - Uses Resend Broadcasts for production emails (automatic unsubscribe handling)
- **Admin workflow** (`admin_tasks.yml`) - Manual workflow for contact management tasks
- **Bulk contact import** - `add_contacts.py` with 0.6s rate limiting (86 contacts)
- **List contacts task** - View all subscribers and their status

### Changed
- Production emails now use Broadcasts API instead of individual sends
- Added rate limiting to contact imports (max 2 requests/sec)

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
- Feedback popup for user suggestions
- Landing page images

### Changed
- Clean professional redesign with DoorDash brand colors
- 90s NBA aesthetic elements

---

## [1.2.0] - 2026-01-20

### Added
- **Cloudflare Worker** for signup/unsubscribe handling
- Signup endpoint: `POST /`
- Unsubscribe endpoint: `GET/POST /unsubscribe`
- Feedback handler: `POST /feedback`

---

## [1.1.0] - 2026-01-19

### Added
- **NBA V3 Box Score API** - Updated from deprecated V2 endpoint
- Unicode name handling (e.g., Dončić → Doncic)
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

## Architecture

```
NBA API → check_fifty.py (1:30 AM PT) → alert_state.json → send_email.py (9:00 AM PT) → Resend Broadcasts → Subscribers
```

## Current Stats

| Metric | Value |
|--------|-------|
| **Subscribers** | 86 contacts |
| **Daily Schedule** | Check: 1:30 AM PT, Send: 9:00 AM PT |
| **Email Service** | Resend (Broadcasts API) |
| **Points Threshold** | 50+ points |
| **Promo Code** | NBA50 |
| **Promo Window** | 9 AM - 11 AM PT |

## Files Overview

| File | Purpose |
|------|---------|
| `src/check_fifty.py` | NBA API score checker |
| `src/send_email.py` | Email sender (Broadcasts) |
| `src/add_contacts.py` | Bulk contact import |
| `src/config.py` | Configuration settings |
| `data/alert_state.json` | Inter-workflow state |
| `.github/workflows/check_scores.yml` | Score check workflow |
| `.github/workflows/send_alert.yml` | Email send workflow |
| `.github/workflows/admin_tasks.yml` | Admin tasks workflow |
| `worker/index.js` | Cloudflare Worker |
| `index.html` | Landing page |

## Required Secrets (GitHub)

```
RESEND_API_KEY       - Resend API key
RESEND_AUDIENCE_ID   - Resend Audience UUID
EMAIL_FROM           - Sender email address
```

## Key URLs

- **Landing Page**: https://urielgre.github.io/doordash-fifty-alert/
- **Signup Worker**: https://fifty-point-signup.urielgre.workers.dev/
- **Unsubscribe**: https://fifty-point-signup.urielgre.workers.dev/unsubscribe

## Testing

```bash
# Test score checker (Luka's 73-point game)
python src/check_fifty.py --test

# Preview email without sending
python src/send_email.py --preview

# Send test email
python src/send_email.py --test your@email.com
```

## Known Issues

- `admin_tasks.yml` may have shell quoting issues with inline Python code (investigating)
