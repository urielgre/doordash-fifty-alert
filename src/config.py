"""
Configuration for DoorDash 50-Point Alert system.
"""

import os
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ALERT_STATE_FILE = DATA_DIR / "alert_state.json"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# Resend configuration (set via environment variables)
RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
RESEND_AUDIENCE_ID = os.environ.get("RESEND_AUDIENCE_ID")

# Email configuration
EMAIL_FROM = os.environ.get("EMAIL_FROM", "DoorDash Alerts <alerts@yourdomain.com>")

# NBA API settings
NBA_API_DELAY = 0.6  # Seconds between API calls to avoid rate limiting
POINTS_THRESHOLD = 50  # Minimum points for alert

# Promo window (Pacific Time)
PROMO_START = "9:00 AM PT"
PROMO_END = "11:59 PM PT"
