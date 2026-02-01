"""
Check NBA games for 50+ point performances.
Runs daily at 1:30 AM PT via GitHub Actions.

Usage:
    python check_fifty.py                    # Check yesterday's games
    python check_fifty.py --date 2024-01-26  # Check specific date (Luka's 73-pt game)
    python check_fifty.py --test             # Test with known 50+ game
"""

import json
import argparse
import time
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path

# NBA API imports
from nba_api.stats.endpoints import scoreboardv2, boxscoretraditionalv3
from nba_api.stats.static import teams

# Local config
import sys
sys.path.insert(0, str(Path(__file__).parent))
from config import ALERT_STATE_FILE, DATA_DIR, NBA_API_DELAY, POINTS_THRESHOLD


def safe_print(text: str):
    """Print text safely, handling Unicode characters on Windows."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Normalize Unicode and replace problematic characters
        normalized = unicodedata.normalize('NFKD', text)
        ascii_text = normalized.encode('ascii', 'replace').decode('ascii')
        print(ascii_text)


def normalize_name(name: str) -> str:
    """Normalize player names to handle special characters."""
    # Convert accented characters to ASCII equivalents
    normalized = unicodedata.normalize('NFKD', name)
    return normalized.encode('ascii', 'ignore').decode('ascii')


def get_games_for_date(date_str: str) -> list:
    """
    Get all NBA game IDs for a specific date.

    Args:
        date_str: Date in format 'YYYY-MM-DD' or 'MM/DD/YYYY'

    Returns:
        List of game IDs
    """
    # Convert to MM/DD/YYYY format for NBA API
    if '-' in date_str:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        date_formatted = dt.strftime("%m/%d/%Y")
    else:
        date_formatted = date_str

    print(f"Fetching games for {date_formatted}...")

    try:
        scoreboard = scoreboardv2.ScoreboardV2(game_date=date_formatted)
        games_df = scoreboard.get_data_frames()[0]  # GameHeader

        if games_df.empty:
            return []

        game_ids = games_df["GAME_ID"].tolist()
        return game_ids

    except Exception as e:
        print(f"Error fetching scoreboard: {e}")
        return []


def check_box_scores_for_fifty(game_ids: list) -> list:
    """
    Check box scores for 50+ point performances.

    Args:
        game_ids: List of NBA game IDs to check

    Returns:
        List of dicts with player performances >= 50 points
    """
    fifty_club = []

    for i, game_id in enumerate(game_ids):
        print(f"  Checking game {i+1}/{len(game_ids)}: {game_id}")

        # Rate limiting
        if i > 0:
            time.sleep(NBA_API_DELAY)

        try:
            # Using V3 endpoint (V2 deprecated as of 2025-26 season)
            box = boxscoretraditionalv3.BoxScoreTraditionalV3(game_id=game_id)
            players_df = box.get_data_frames()[0]  # PlayerStats

            # V3 uses 'points' instead of 'PTS'
            if 'points' in players_df.columns:
                big_games = players_df[players_df["points"] >= POINTS_THRESHOLD]

                for _, row in big_games.iterrows():
                    # V3 uses firstName/familyName instead of PLAYER_NAME
                    # Normalize names to handle special characters (e.g., Dončić -> Doncic)
                    player_name = normalize_name(f"{row['firstName']} {row['familyName']}")
                    performance = {
                        "player": player_name,
                        "team": row["teamTricode"],
                        "points": int(row["points"]),
                        "game_id": game_id,
                        "rebounds": int(row.get("reboundsTotal", 0)),
                        "assists": int(row.get("assists", 0)),
                        "minutes": row.get("minutes", "N/A"),
                    }
                    fifty_club.append(performance)
                    safe_print(f"    Found: {performance['player']} ({performance['team']}) - {performance['points']} PTS!")

        except Exception as e:
            print(f"    Error checking game {game_id}: {e}")
            continue

    return fifty_club


def save_alert_state(fifty_club: list, check_date: str):
    """
    Save alert state to JSON file.

    Args:
        fifty_club: List of 50+ point performances
        check_date: The date that was checked
    """
    state = {
        "alert_needed": len(fifty_club) > 0,
        "performances": fifty_club,
        "check_date": check_date,
        "checked_at": datetime.now().isoformat(),
        "promo_window": {
            "start": "9:00 AM PT",
            "end": "11:59 PM PT"
        }
    }

    DATA_DIR.mkdir(exist_ok=True)

    with open(ALERT_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

    print(f"\nState saved to: {ALERT_STATE_FILE}")
    return state


def get_yesterday_date() -> str:
    """Get yesterday's date in YYYY-MM-DD format."""
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")


def main():
    parser = argparse.ArgumentParser(description="Check NBA games for 50+ point performances")
    parser.add_argument("--date", type=str, help="Date to check (YYYY-MM-DD). Default: yesterday")
    parser.add_argument("--test", action="store_true", help="Test with Luka's 73-point game (2024-01-26)")
    args = parser.parse_args()

    print("=" * 60)
    print("  DoorDash 50-Point Alert - Score Checker")
    print("=" * 60)

    # Determine which date to check
    if args.test:
        check_date = "2024-01-26"  # Luka's 73-point game (DAL @ ATL)
        print(f"\n[TEST MODE] Checking Luka's 73-point game")
    elif args.date:
        check_date = args.date
    else:
        check_date = get_yesterday_date()

    print(f"\nChecking date: {check_date}")
    print("-" * 60)

    # Get games for the date
    game_ids = get_games_for_date(check_date)

    if not game_ids:
        print(f"\nNo games found for {check_date}")
        save_alert_state([], check_date)
        return

    print(f"\nFound {len(game_ids)} games. Checking box scores...")
    print("-" * 60)

    # Check for 50+ point games
    fifty_club = check_box_scores_for_fifty(game_ids)

    # Save state
    print("-" * 60)
    state = save_alert_state(fifty_club, check_date)

    # Summary
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)

    if fifty_club:
        print(f"\n  ALERT NEEDED: YES")
        print(f"\n  50+ Point Performances:")
        for perf in fifty_club:
            safe_print(f"    - {perf['player']} ({perf['team']}): {perf['points']} PTS")
            safe_print(f"      ({perf['rebounds']} REB, {perf['assists']} AST)")
    else:
        print(f"\n  ALERT NEEDED: NO")
        print(f"  No 50+ point games on {check_date}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
