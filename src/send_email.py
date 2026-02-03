"""
Send email alert if 50+ point game occurred.
Runs daily at 9:00 AM PT via GitHub Actions.

Usage:
    python send_email.py              # Send alert if needed (reads state file)
    python send_email.py --test EMAIL # Send test email to specified address
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
    """Build the alert email HTML - clean DoorDash style."""

    # Build player summary
    if len(performances) == 1:
        perf = performances[0]
        player_summary = f"{perf['player']} dropped {perf['points']} points last night!"
    else:
        player_summary = f"{len(performances)} players scored 50+ last night!"

    # Build player cards
    player_cards = ""
    for p in performances:
        player_cards += f"""
        <tr>
            <td style="padding: 12px 0; border-bottom: 1px solid #f0f0f0;">
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td>
                            <div style="font-weight: 600; color: #1F1F1F; font-size: 15px;">{p['player']}</div>
                            <div style="color: #999; font-size: 13px; margin-top: 2px;">{p['team']}</div>
                        </td>
                        <td align="right">
                            <span style="font-size: 22px; font-weight: 800; color: #FF3008;">{p['points']}</span>
                            <span style="color: #999; font-size: 12px;"> PTS</span>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        """

    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DoorDash $5 Off - Live Now!</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; background-color: #f7f7f7;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f7f7f7;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 500px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">

                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #FF3008 0%, #C41E00 100%); padding: 40px 30px; text-align: center;">
                            <div style="font-size: 48px; margin-bottom: 12px;">🏀</div>
                            <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: 800; letter-spacing: -0.5px;">$5 OFF IS LIVE!</h1>
                            <p style="margin: 12px 0 0 0; color: rgba(255,255,255,0.9); font-size: 15px;">{player_summary}</p>
                        </td>
                    </tr>

                    <!-- Promo Box -->
                    <tr>
                        <td style="padding: 30px;">
                            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #FFF5F3; border-radius: 8px; border: 2px solid #FF3008;">
                                <tr>
                                    <td style="padding: 24px; text-align: center;">
                                        <div style="font-size: 42px; font-weight: 800; color: #FF3008; letter-spacing: -1px;">$5 OFF</div>
                                        <div style="color: #666; font-size: 14px; margin-top: 8px;">On $15+ orders · DashPass members · Delivery only</div>
                                        <table cellpadding="0" cellspacing="0" style="margin: 16px auto 0 auto;">
                                            <tr>
                                                <td style="background: #1F1F1F; padding: 12px 24px; border-radius: 6px; text-align: center;">
                                                    <span style="color: #999; font-size: 12px;">USE CODE</span><br>
                                                    <span style="color: white; font-size: 20px; font-weight: 800; letter-spacing: 2px;">NBA50</span>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- How to Redeem -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px;">
                            <h3 style="margin: 0 0 16px 0; font-size: 14px; font-weight: 700; color: #1F1F1F; text-transform: uppercase; letter-spacing: 0.5px;">How to Redeem</h3>
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td style="padding: 10px 0;">
                                        <table cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td width="32" height="32" style="background-color: #FF3008; border-radius: 16px; text-align: center; vertical-align: middle;">
                                                    <span style="color: #ffffff; font-weight: 700; font-size: 14px; line-height: 32px;">1</span>
                                                </td>
                                                <td style="padding-left: 14px; color: #666; font-size: 15px;">Open the DoorDash app</td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 0;">
                                        <table cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td width="32" height="32" style="background-color: #FF3008; border-radius: 16px; text-align: center; vertical-align: middle;">
                                                    <span style="color: #ffffff; font-weight: 700; font-size: 14px; line-height: 32px;">2</span>
                                                </td>
                                                <td style="padding-left: 14px; color: #666; font-size: 15px;">Add items to your cart ($15+ subtotal, delivery only)</td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 0;">
                                        <table cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td width="32" height="32" style="background-color: #FF3008; border-radius: 16px; text-align: center; vertical-align: middle;">
                                                    <span style="color: #ffffff; font-weight: 700; font-size: 14px; line-height: 32px;">3</span>
                                                </td>
                                                <td style="padding-left: 14px; color: #666; font-size: 15px;">Apply code <strong style="color: #FF3008;">NBA50</strong> at checkout</td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Last Night's Games -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px;">
                            <h3 style="margin: 0 0 12px 0; font-size: 14px; font-weight: 700; color: #1F1F1F; text-transform: uppercase; letter-spacing: 0.5px;">Last Night's 50+ Games</h3>
                            <table width="100%" cellpadding="0" cellspacing="0">
                                {player_cards}
                            </table>
                        </td>
                    </tr>

                    <!-- Share Button -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px; text-align: center;">
                            <p style="margin: 0 0 12px 0; color: #666; font-size: 13px;">Know someone who loves DoorDash deals?</p>
                            <table cellpadding="0" cellspacing="0" style="margin: 0 auto;">
                                <tr>
                                    <td style="background: #FF3008; border-radius: 6px;">
                                        <a href="https://urielgre.github.io/doordash-fifty-alert/" style="display: inline-block; padding: 12px 24px; color: #ffffff; text-decoration: none; font-weight: 600; font-size: 14px;">Share with Friends</a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #1F1F1F; padding: 24px 30px; text-align: center;">
                            <p style="margin: 0 0 12px 0; color: rgba(255,255,255,0.6); font-size: 12px;">
                                You're receiving this because you signed up for 50-Point Alerts.
                            </p>
                            <p style="margin: 0; color: rgba(255,255,255,0.4); font-size: 11px;">
                                <a href="https://fifty-point-signup.urielgre.workers.dev/unsubscribe" style="color: rgba(255,255,255,0.6); text-decoration: underline;">Unsubscribe</a>
                                &nbsp;&nbsp;·&nbsp;&nbsp;
                                <a href="https://urielgre.github.io/doordash-fifty-alert/" style="color: rgba(255,255,255,0.6); text-decoration: underline;">Manage Preferences</a>
                            </p>
                            <p style="margin: 16px 0 0 0; color: rgba(255,255,255,0.3); font-size: 10px;">
                                Not affiliated with DoorDash, Inc. or the NBA.
                            </p>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>
    """


def build_email_text(performances: list) -> str:
    """Build plain text version of email."""

    if len(performances) == 1:
        perf = performances[0]
        player_text = f"{perf['player']} dropped {perf['points']} points last night!"
    else:
        player_text = f"{len(performances)} players scored 50+ last night!"

    stats = "\n".join([
        f"  - {p['player']} ({p['team']}): {p['points']} PTS"
        for p in performances
    ])

    return f"""
50-POINT ALERTS
================

🏀 $5 OFF IS LIVE!

{player_text}

HOW TO REDEEM:
1. Open the DoorDash app
2. Add items to your cart ($15+ subtotal, delivery only)
3. Apply code NBA50 at checkout

DashPass members only · Valid until 11:59 PM PT today.

LAST NIGHT'S 50+ GAMES:
{stats}

---
Share with friends: https://urielgre.github.io/doordash-fifty-alert/

---
You're receiving this because you signed up for 50-Point Alerts.
Unsubscribe: https://fifty-point-signup.urielgre.workers.dev/unsubscribe

Not affiliated with DoorDash, Inc. or the NBA.
    """


def send_alert(state: dict, test_email: str = None):
    """
    Send alert email to all subscribers (or test email).

    Uses Resend Broadcasts for production (automatic unsubscribe links).
    Uses regular email for test mode.

    Args:
        state: Alert state dict with performances
        test_email: If provided, only send to this email
    """
    import resend
    resend.api_key = RESEND_API_KEY

    performances = state.get("performances", [])
    html_content = build_email_html(performances)
    text_content = build_email_text(performances)

    # Unsubscribe URL for headers and email body
    unsubscribe_url = "https://fifty-point-signup.urielgre.workers.dev/unsubscribe"

    if test_email:
        # Test mode: send regular email to single recipient
        print(f"[TEST MODE] Sending to: {test_email}")
        try:
            response = resend.Emails.send({
                "from": EMAIL_FROM,
                "to": [test_email],
                "subject": "🏀 $5 OFF DoorDash - LIVE NOW until 11:59 PM PT!",
                "html": html_content,
                "text": text_content,
                "headers": {
                    "List-Unsubscribe": f"<{unsubscribe_url}>",
                    "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
                },
            })
            print(f"\n✅ Test email sent successfully!")
            print(f"   Email ID: {response.get('id', 'N/A')}")
        except Exception as e:
            print(f"\n❌ Error sending test email: {e}")
            raise
    else:
        # Production mode: use Broadcasts for automatic unsubscribe handling
        try:
            # Create broadcast
            broadcast = resend.Broadcasts.create({
                "audience_id": RESEND_AUDIENCE_ID,
                "from": EMAIL_FROM,
                "subject": "🏀 $5 OFF DoorDash - LIVE NOW until 11:59 PM PT!",
                "html": html_content,
                "text": text_content,
                "name": f"50-Point Alert - {datetime.now().strftime('%Y-%m-%d')}",
            })
            broadcast_id = broadcast.get("id")
            print(f"Broadcast created: {broadcast_id}")

            # Send immediately
            resend.Broadcasts.send({"broadcast_id": broadcast_id})

            print(f"\n✅ Broadcast sent successfully!")
            print(f"   Broadcast ID: {broadcast_id}")

        except Exception as e:
            print(f"\n❌ Error sending broadcast: {e}")
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
        state["performances"] = [
            {
                "player": "Anthony Edwards",
                "team": "MIN",
                "points": 55,
            },
            {
                "player": "Shai Gilgeous-Alexander",
                "team": "OKC",
                "points": 55,
            }
        ]

    html = build_email_html(state["performances"])
    text = build_email_text(state["performances"])

    print("\n" + "=" * 60)
    print("  EMAIL PREVIEW (Plain Text)")
    print("=" * 60)
    safe_print(text)

    # Save HTML preview
    preview_path = Path(__file__).parent.parent / "data" / "email_preview.html"
    preview_path.parent.mkdir(exist_ok=True)
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
        return

    # Load state
    state = load_alert_state()
    print(f"\nAlert state file: {ALERT_STATE_FILE}")

    # Test mode
    if args.test:
        print(f"\n[TEST MODE]")
        # Use mock data if no real performances
        if not state.get("performances"):
            state["performances"] = [
                {
                    "player": "Anthony Edwards",
                    "team": "MIN",
                    "points": 55,
                },
                {
                    "player": "Shai Gilgeous-Alexander",
                    "team": "OKC",
                    "points": 55,
                }
            ]
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
