"""
Send email alert if 50+ point game occurred.
Runs daily at 9:00 AM PT via GitHub Actions.

Usage:
    python send_email.py              # Send alert if needed (reads state file)
    python send_email.py --test       # Send test email to yourself
    python send_email.py --preview    # Preview email HTML without sending
"""

import json
import argparse
import os
import unicodedata
from datetime import datetime
from pathlib import Path

# Local config
import sys
sys.path.insert(0, str(Path(__file__).parent))
from config import (
    ALERT_STATE_FILE,
    RESEND_API_KEY,
    RESEND_AUDIENCE_ID,
    EMAIL_FROM,
)


def safe_print(text: str):
    """Print text safely, handling Unicode characters on Windows."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Normalize Unicode and replace problematic characters
        normalized = unicodedata.normalize('NFKD', text)
        ascii_text = normalized.encode('ascii', 'replace').decode('ascii')
        print(ascii_text)


def load_alert_state() -> dict:
    """Load alert state from JSON file."""
    if not ALERT_STATE_FILE.exists():
        return {"alert_needed": False, "performances": []}

    with open(ALERT_STATE_FILE) as f:
        return json.load(f)


def get_subscribers() -> list:
    """Get all subscribers from Resend Audience."""
    import resend
    resend.api_key = RESEND_API_KEY

    try:
        response = resend.Contacts.list(audience_id=RESEND_AUDIENCE_ID)
        subscribers = [contact["email"] for contact in response["data"]]
        print(f"Found {len(subscribers)} subscribers")
        return subscribers
    except Exception as e:
        print(f"Error fetching subscribers: {e}")
        return []


def build_email_html(performances: list) -> str:
    """Build the alert email HTML with 90s NBA vibes."""

    # Build player list
    if len(performances) == 1:
        perf = performances[0]
        player_text = f"<span style='color: #FFD700; font-weight: bold;'>{perf['player']}</span> dropped <span style='color: #FF1493; font-weight: bold;'>{perf['points']} POINTS</span> last night!"
    else:
        players = " // ".join([
            f"<span style='color: #FFD700;'>{p['player']}</span> ({p['points']})"
            for p in performances
        ])
        player_text = f"Multiple ballers went off: {players}"

    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap" rel="stylesheet">
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #2D1B4E;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(180deg, #1a0a2e 0%, #2D1B4E 100%); border: 4px solid #00CED1; position: relative;">

            <!-- Yellow Corner Triangle (top-left) -->
            <div style="width: 0; height: 0; border-left: 40px solid #FFD700; border-bottom: 40px solid transparent; position: absolute; top: -4px; left: -4px;"></div>

            <!-- Header -->
            <div style="background: linear-gradient(135deg, #6B2D9B 0%, #2D1B4E 100%); padding: 30px; text-align: center; border-bottom: 3px solid #FF6B35;">
                <div style="font-size: 60px; margin-bottom: 10px;">🏀</div>
                <h1 style="font-family: 'Bebas Neue', Arial, sans-serif; color: #FFD700; margin: 0; font-size: 42px; letter-spacing: 4px; text-shadow: 3px 3px 0 #FF6B35;">50% OFF IS LIVE!</h1>
                <p style="color: #00CED1; font-size: 12px; letter-spacing: 3px; margin-top: 8px;">★ ★ ★ BALLIN' SINCE '95 ★ ★ ★</p>
            </div>

            <!-- Content -->
            <div style="padding: 30px;">
                <p style="font-size: 18px; color: #c9b8e0; line-height: 1.7; margin-top: 0;">
                    {player_text}
                </p>

                <!-- Promo Box -->
                <div style="background: linear-gradient(90deg, #FF6B35 0%, #FF1493 100%); color: white; padding: 25px; text-align: center; margin: 25px 0; border-left: 5px solid #FFD700;">
                    <div style="font-family: 'Bebas Neue', Arial, sans-serif; font-size: 48px; font-weight: bold; letter-spacing: 3px; text-shadow: 3px 3px 0 #6B2D9B;">50% OFF</div>
                    <div style="font-size: 14px; letter-spacing: 2px; margin-top: 5px;">VALID UNTIL 11:00 AM PT TODAY</div>
                </div>

                <!-- How to use -->
                <h3 style="font-family: 'Bebas Neue', Arial, sans-serif; color: #00CED1; margin-bottom: 15px; font-size: 20px; letter-spacing: 3px;">THE GAME PLAN:</h3>
                <ol style="color: #c9b8e0; line-height: 2; padding-left: 20px; margin: 0;">
                    <li>Open the <strong style="color: #FFD700;">DoorDash app</strong></li>
                    <li>Look for the <strong style="color: #FFD700;">50% off banner</strong></li>
                    <li>Order before <strong style="color: #FF1493;">11 AM PT</strong>!</li>
                </ol>

                <!-- Stats Box -->
                <div style="background: rgba(0, 206, 209, 0.1); padding: 20px; margin-top: 25px; border-left: 4px solid #00CED1;">
                    <h4 style="margin: 0 0 15px 0; color: #FF1493; font-size: 14px; text-transform: uppercase; letter-spacing: 2px; font-family: 'Bebas Neue', Arial, sans-serif;">LAST NIGHT'S BIG PERFORMANCE</h4>
                    {"".join([f'''
                    <div style="display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid rgba(107, 45, 155, 0.3);">
                        <span style="color: #c9b8e0; font-weight: bold;">{p['player']} ({p['team']})</span>
                        <span style="font-family: 'Bebas Neue', Arial, sans-serif; font-size: 22px; color: #FFD700; text-shadow: 2px 2px 0 #FF6B35;">{p['points']} PTS</span>
                    </div>
                    ''' for p in performances])}
                </div>
            </div>

            <!-- Footer -->
            <div style="background: rgba(0, 0, 0, 0.3); padding: 20px; text-align: center; border-top: 2px dashed #6B2D9B;">
                <p style="color: #6a5a7a; font-size: 11px; margin: 0; letter-spacing: 1px;">
                    FREE FOREVER // UNSUBSCRIBE ANYTIME // NO SPAM
                    <br><br>
                    <a href="{{{{RESEND_UNSUBSCRIBE_URL}}}}" style="color: #00CED1;">Unsubscribe</a>
                </p>
            </div>

            <!-- Pink Corner Triangle (bottom-right) -->
            <div style="width: 0; height: 0; border-right: 40px solid #FF1493; border-top: 40px solid transparent; position: absolute; bottom: -4px; right: -4px;"></div>

        </div>
    </div>
</body>
</html>
    """


def build_email_text(performances: list) -> str:
    """Build plain text version of email with 90s vibes."""

    if len(performances) == 1:
        perf = performances[0]
        player_text = f"{perf['player']} DROPPED {perf['points']} POINTS last night!"
    else:
        players = " // ".join([f"{p['player']} ({p['points']})" for p in performances])
        player_text = f"Multiple ballers went off: {players}"

    stats = "\n".join([
        f"  * {p['player']} ({p['team']}): {p['points']} PTS"
        for p in performances
    ])

    return f"""
==================================
  50-POINT ALERTS
  * * * Ballin' Since '95 * * *
==================================

{player_text}

+--------------------------------+
|                                |
|          50% OFF               |
|                                |
|   Valid until 11:00 AM PT      |
|                                |
+--------------------------------+

THE GAME PLAN:
1. Open the DoorDash app
2. Look for the 50% off banner
3. Order before 11 AM PT!

Last Night's Performance:
{stats}

---
You're receiving this because you signed up for 50-Point Alerts.
Unsubscribe: {{{{RESEND_UNSUBSCRIBE_URL}}}}
    """


def send_alert(state: dict, test_email: str = None):
    """
    Send alert email to all subscribers (or test email).

    Args:
        state: Alert state dict with performances
        test_email: If provided, only send to this email
    """
    import resend
    resend.api_key = RESEND_API_KEY

    performances = state.get("performances", [])

    if test_email:
        recipients = [test_email]
        print(f"[TEST MODE] Sending to: {test_email}")
    else:
        recipients = get_subscribers()
        if not recipients:
            print("No subscribers to notify")
            return

    html_content = build_email_html(performances)
    text_content = build_email_text(performances)

    try:
        # Send email
        response = resend.Emails.send({
            "from": EMAIL_FROM,
            "to": recipients,
            "subject": "🏀 50% OFF DoorDash - LIVE NOW until 11 AM PT!",
            "html": html_content,
            "text": text_content,
        })

        print(f"\n✅ Email sent successfully!")
        print(f"   Recipients: {len(recipients)}")
        print(f"   Email ID: {response.get('id', 'N/A')}")

    except Exception as e:
        print(f"\n❌ Error sending email: {e}")
        raise


def clear_alert_state():
    """Clear the alert state after sending."""
    state = {
        "alert_needed": False,
        "performances": [],
        "cleared_at": datetime.now().isoformat()
    }
    with open(ALERT_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    print("Alert state cleared")


def preview_email():
    """Preview the email HTML in terminal."""
    state = load_alert_state()

    if not state.get("performances"):
        # Use mock data for preview
        state["performances"] = [{
            "player": "Luka Doncic",
            "team": "DAL",
            "points": 73,
            "rebounds": 10,
            "assists": 7
        }]

    html = build_email_html(state["performances"])
    text = build_email_text(state["performances"])

    print("\n" + "=" * 60)
    print("  EMAIL PREVIEW (Plain Text)")
    print("=" * 60)
    safe_print(text)

    # Save HTML preview
    preview_path = Path(__file__).parent.parent / "data" / "email_preview.html"
    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\nHTML preview saved to: {preview_path}")
    print("Open this file in a browser to see the full email design.")


def main():
    parser = argparse.ArgumentParser(description="Send DoorDash 50-point alert emails")
    parser.add_argument("--test", type=str, metavar="EMAIL", help="Send test email to specified address")
    parser.add_argument("--preview", action="store_true", help="Preview email without sending")
    args = parser.parse_args()

    print("=" * 60)
    print("  DoorDash 50-Point Alert - Email Sender")
    print("=" * 60)

    # Preview mode
    if args.preview:
        preview_email()
        return

    # Check for API key
    if not RESEND_API_KEY:
        print("\n❌ RESEND_API_KEY not set!")
        print("   Set it as an environment variable:")
        print("   export RESEND_API_KEY=re_xxxxx")
        print("\n   Or create a .env file with:")
        print("   RESEND_API_KEY=re_xxxxx")
        return

    # Load state
    state = load_alert_state()
    print(f"\nAlert state file: {ALERT_STATE_FILE}")

    # Test mode
    if args.test:
        print(f"\n[TEST MODE]")
        # Use mock data if no real performances
        if not state.get("performances"):
            state["performances"] = [{
                "player": "Luka Doncic",
                "team": "DAL",
                "points": 73,
                "rebounds": 10,
                "assists": 7
            }]
        send_alert(state, test_email=args.test)
        return

    # Production mode
    if not state.get("alert_needed"):
        print("\nNo alert needed today")
        return

    print(f"\n🚨 Alert needed! {len(state.get('performances', []))} performances found")

    send_alert(state)
    clear_alert_state()

    print("\n✅ Done!")


if __name__ == "__main__":
    main()
