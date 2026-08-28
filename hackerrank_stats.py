import requests
from pathlib import Path

USERNAME = "arsravan88"

API_URL = f"https://www.hackerrank.com/rest/hackers/{USERNAME}/badges"
OUTPUT_FILE = Path("hackerrank_stats.svg")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_hackerrank_data():
    response = requests.get(
        API_URL,
        headers=HEADERS,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def get_python_stats(data):
    for badge in data.get("models", []):
        if badge.get("badge_name") == "Python":
            return {
                "solved": badge.get("solved", 0),
                "stars": badge.get("stars", 0),
                "points": badge.get("current_points", 0),
                "rank": badge.get("hacker_rank", 0)
            }

    raise ValueError("Python badge not found.")


def generate_svg(stats):

    solved = stats["solved"]
    stars = stats["stars"]
    points = stats["points"]
    rank = stats["rank"]

    star_display = "★" * stars

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
        HACKERRANK
    </text>

    <text
        x="40"
        y="69"
        fill="#8b949e"
        font-family="Arial, Helvetica, sans-serif"
        font-size="13">
        Python · Problem Solving
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

    <!-- Stars -->

    <text
        x="260"
        y="130"
        fill="#d29922"
        font-family="Arial, Helvetica, sans-serif"
        font-size="23">
        {star_display}
    </text>

    <text
        x="260"
        y="153"
        fill="#8b949e"
        font-family="Arial, Helvetica, sans-serif"
        font-size="11"
        letter-spacing="1">
        STARS
    </text>

    <!-- Points -->

    <text
        x="470"
        y="130"
        fill="#f0f6fc"
        font-family="Arial, Helvetica, sans-serif"
        font-size="26"
        font-weight="600">
        {points:g}
    </text>

    <text
        x="470"
        y="153"
        fill="#8b949e"
        font-family="Arial, Helvetica, sans-serif"
        font-size="11"
        letter-spacing="1">
        POINTS
    </text>

    <!-- Rank -->

    <text
        x="650"
        y="130"
        fill="#f0f6fc"
        font-family="Arial, Helvetica, sans-serif"
        font-size="26"
        font-weight="600">
        #{rank:,}
    </text>

    <text
        x="650"
        y="153"
        fill="#8b949e"
        font-family="Arial, Helvetica, sans-serif"
        font-size="11"
        letter-spacing="1">
        RANK
    </text>

    <!-- Footer -->

    <text
        x="40"
        y="190"
        fill="#6e7681"
        font-family="Arial, Helvetica, sans-serif"
        font-size="11">
        arsravan88
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

    print("Fetching HackerRank data...")

    data = get_hackerrank_data()

    stats = get_python_stats(data)

    print("\nHackerRank Statistics")
    print("---------------------")
    print(f"Problems solved : {stats['solved']}")
    print(f"Stars           : {stats['stars']}")
    print(f"Points          : {stats['points']}")
    print(f"Rank            : {stats['rank']:,}")

    svg = generate_svg(stats)

    OUTPUT_FILE.write_text(
        svg,
        encoding="utf-8"
    )

    print(f"\nSVG generated: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()