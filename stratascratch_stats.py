import json
from datetime import date, timedelta
from pathlib import Path

USERNAME = "Sravan"

PROFILE_URL = f"https://platform.stratascratch.com/profile-code/{USERNAME}"

ACTIVITY_FILE = Path("stratascratch_activity.json")
OUTPUT_FILE = Path("stratascratch_stats.svg")


def load_activity():
    if not ACTIVITY_FILE.exists():
        return {}

    with ACTIVITY_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def calculate_streaks(activity):
    dates = sorted(
        date.fromisoformat(d)
        for d, count in activity.items()
        if count > 0
    )

    if not dates:
        return 0, 0

    longest = 1
    current = 1

    for i in range(1, len(dates)):
        if dates[i] == dates[i - 1] + timedelta(days=1):
            current += 1
            longest = max(longest, current)
        else:
            current = 1

    today = date.today()

    if today not in dates:
        current_streak = 0
    else:
        current_streak = 1

        check = today - timedelta(days=1)

        while check in dates:
            current_streak += 1
            check -= timedelta(days=1)

    return current_streak, longest


def get_stratascratch_stats():
    activity = load_activity()

    current_streak, longest_streak = calculate_streaks(activity)

    return {
        "solved": sum(activity.values()),
        "active_days": sum(1 for count in activity.values() if count > 0),
        "current_streak": current_streak,
        "longest_streak": longest_streak
    }


def generate_svg(stats):

    solved = stats["solved"]
    active_days = stats["active_days"]
    current_streak = stats["current_streak"]
    longest_streak = stats["longest_streak"]

    svg = f"""<svg
    width="850"
    height="220"
    viewBox="0 0 850 220"
    xmlns="http://www.w3.org/2000/svg">

    <rect
        width="850"
        height="220"
        rx="16"
        fill="#0d1117"
        stroke="#30363d"
        stroke-width="1"/>

    <!-- Header -->

    <text
        x="40"
        y="45"
        fill="#f0f6fc"
        font-family="Arial, Helvetica, sans-serif"
        font-size="21"
        font-weight="600">
        STRATASCRATCH
    </text>

    <text
        x="40"
        y="69"
        fill="#8b949e"
        font-family="Arial, Helvetica, sans-serif"
        font-size="13">
        SQL · Data Science Practice
    </text>

    <!-- Divider -->

    <line
        x1="40"
        y1="90"
        x2="810"
        y2="90"
        stroke="#21262d"
        stroke-width="1"/>

    <!-- Solved -->

    <text
        x="70"
        y="130"
        fill="#f0f6fc"
        font-family="Arial, Helvetica, sans-serif"
        font-size="26"
        font-weight="600">
        {solved}
    </text>

    <text
        x="70"
        y="153"
        fill="#8b949e"
        font-family="Arial, Helvetica, sans-serif"
        font-size="11"
        letter-spacing="1">
        SOLVED
    </text>

    <!-- Active days -->

    <text
        x="260"
        y="130"
        fill="#f0f6fc"
        font-family="Arial, Helvetica, sans-serif"
        font-size="26"
        font-weight="600">
        {active_days}
    </text>

    <text
        x="260"
        y="153"
        fill="#8b949e"
        font-family="Arial, Helvetica, sans-serif"
        font-size="11"
        letter-spacing="1">
        ACTIVE DAYS
    </text>

    <!-- Current streak -->

    <text
        x="470"
        y="130"
        fill="#f0f6fc"
        font-family="Arial, Helvetica, sans-serif"
        font-size="26"
        font-weight="600">
        {current_streak}
    </text>

    <text
        x="470"
        y="153"
        fill="#8b949e"
        font-family="Arial, Helvetica, sans-serif"
        font-size="11"
        letter-spacing="1">
        CURRENT STREAK
    </text>

    <!-- Longest streak -->

    <text
        x="650"
        y="130"
        fill="#f0f6fc"
        font-family="Arial, Helvetica, sans-serif"
        font-size="26"
        font-weight="600">
        {longest_streak}
    </text>

    <text
        x="650"
        y="153"
        fill="#8b949e"
        font-family="Arial, Helvetica, sans-serif"
        font-size="11"
        letter-spacing="1">
        LONGEST STREAK
    </text>

    <!-- Footer -->

    <text
        x="40"
        y="190"
        fill="#6e7681"
        font-family="Arial, Helvetica, sans-serif"
        font-size="11">
        {USERNAME}
    </text>

    <text
        x="810"
        y="190"
        fill="#58a6ff"
        text-anchor="end"
        font-family="Arial, Helvetica, sans-serif"
        font-size="11">
        VIEW PROFILE ↗
    </text>

</svg>
"""

    return svg


def main():

    print("Generating StrataScratch stats card...")

    stats = get_stratascratch_stats()

    print("\nStrataScratch Statistics")
    print("-------------------------")
    print(f"Problems solved : {stats['solved']}")
    print(f"Active days     : {stats['active_days']}")
    print(f"Current streak  : {stats['current_streak']}")
    print(f"Longest streak  : {stats['longest_streak']}")

    svg = generate_svg(stats)

    OUTPUT_FILE.write_text(svg, encoding="utf-8")

    print(f"\nSVG generated: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
