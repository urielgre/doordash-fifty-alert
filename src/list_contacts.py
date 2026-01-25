"""
List all contacts in Resend audience.
Usage: python list_contacts.py
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from config import RESEND_API_KEY, RESEND_AUDIENCE_ID


def main():
    import resend
    resend.api_key = RESEND_API_KEY

    if not RESEND_API_KEY or not RESEND_AUDIENCE_ID:
        print("Error: RESEND_API_KEY or RESEND_AUDIENCE_ID not set")
        sys.exit(1)

    print("Fetching contacts...")
    print("=" * 50)

    try:
        response = resend.Contacts.list(audience_id=RESEND_AUDIENCE_ID)
        contacts = response.get("data", [])

        subscribed = 0
        unsubscribed = 0

        print(f"Total contacts: {len(contacts)}\n")

        for c in contacts:
            email = c.get("email", "unknown")
            is_unsubscribed = c.get("unsubscribed", False)
            status = "unsubscribed" if is_unsubscribed else "subscribed"

            if is_unsubscribed:
                unsubscribed += 1
            else:
                subscribed += 1

            print(f"  {email} ({status})")

        print("=" * 50)
        print(f"Summary:")
        print(f"  Subscribed: {subscribed}")
        print(f"  Unsubscribed: {unsubscribed}")
        print(f"  Total: {len(contacts)}")

    except Exception as e:
        print(f"Error fetching contacts: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
