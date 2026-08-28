import json
from datetime import datetime, timezone
from pathlib import Path

import requests


# ============================================================
# Configuration
# ============================================================

USERNAME = "arsravan88"

BADGES_URL = (
    f"https://www.hackerrank.com/rest/hackers/"
    f"{USERNAME}/badges"
)

ACTIVITY_FILE = Path("activity.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# ============================================================
# HackerRank
# ============================================================

def get_hackerrank_stats():
    response = requests.get(
        BADGES_URL,
        headers=HEADERS,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    for badge in data.get("models", []):
        if badge.get("badge_name") == "Python":
            return {
                "solved": badge.get("solved", 0),
                "stars": badge.get("stars", 0),
                "points": badge.get("current_points", 0),
                "rank": badge.get("hacker_rank", 0)
            }

    raise ValueError("Python badge not found.")


# ============================================================
# Activity history
# ============================================================

def load_activity():
    if not ACTIVITY_FILE.exists():
        return {}

    with ACTIVITY_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_activity(activity):
    with ACTIVITY_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            activity,
            file,
            indent=2,
            sort_keys=True
        )


def update_activity(activity, solved):
    today = datetime.now(timezone.utc).date().isoformat()

    # First run: establish the starting point.
    if "_baseline" not in activity:
        activity["_baseline"] = solved
        return 0

    previous_total = activity["_baseline"]

    difference = solved - previous_total

    if difference > 0:
        activity[today] = activity.get(today, 0) + difference

    # Always update the latest known total.
    activity["_baseline"] = solved

    return difference

# ============================================================
# Main
# ============================================================

def main():

    print("Fetching HackerRank statistics...")

    stats = get_hackerrank_stats()

    print(f"Problems solved : {stats['solved']}")
    print(f"Stars           : {stats['stars']}")
    print(f"Points          : {stats['points']}")
    print(f"Rank            : {stats['rank']:,}")

    activity = load_activity()

    difference = update_activity(
        activity,
        stats["solved"]
    )

    save_activity(activity)

    print()

    if difference > 0:
        print(f"New problems detected: +{difference}")
    else:
        print("No new problems detected.")

    activity_days = len([
        date for date in activity
        if date != "_baseline"
    ])
    print(f"Activity days: {activity_days}")

    print("\nActivity history:")

    for date, count in activity.items():
        if date != "_baseline":
            print(f"{date}: {count}")


if __name__ == "__main__":
    main()  