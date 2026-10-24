import os
from pathlib import Path

import requests

USERNAME = "Sravan"

GRAPHQL_URL = "https://api.stratascratch.com/graphql/"

PROFILE_URL = f"https://platform.stratascratch.com/profile-code/{USERNAME}"

OUTPUT_FILE = Path("stratascratch_stats.svg")

TOKEN = os.environ.get("STRATASCRATCH_TOKEN")

HEADERS = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

DIFFICULTY_QUERY = """
query InterviewProgress(
    $username: String!,
    $questionClass: QuestionClassEnum!,
    $codeType: Int
) {
    analytics(username: $username) {
        id
        byClass(questionClass: $questionClass) {
            all {
                all
                easy
                medium
                hard
                __typename
            }
            solved(codeType: $codeType) {
                all
                easy
                medium
                hard
                __typename
            }
            __typename
        }
        __typename
    }
}
"""


def get_difficulty_breakdown():
    if not TOKEN:
        raise RuntimeError("STRATASCRATCH_TOKEN environment variable is not set.")

    payload = {
        "operationName": "InterviewProgress",
        "variables": {
            "username": USERNAME,
            "questionClass": "ALL"
        },
        "query": DIFFICULTY_QUERY
    }

    response = requests.post(GRAPHQL_URL, headers=HEADERS, json=payload, timeout=30)
    response.raise_for_status()

    data = response.json()

    if "errors" in data:
        raise RuntimeError(f"StrataScratch GraphQL error: {data['errors']}")

    analytics = data.get("data", {}).get("analytics") or {}
    by_class = analytics.get("byClass") or {}
    solved = by_class.get("solved") or {}

    return {
        "solved": solved.get("all", 0),
        "easy": solved.get("easy", 0),
        "medium": solved.get("medium", 0),
        "hard": solved.get("hard", 0)
    }


def generate_svg(stats):

    solved = stats["solved"]
    easy = stats["easy"]
    medium = stats["medium"]
    hard = stats["hard"]

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
        Data Science Practice
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

    <!-- Easy -->

    <text
        x="260"
        y="130"
        fill="#f0f6fc"
        font-family="Arial, Helvetica, sans-serif"
        font-size="26"
        font-weight="600">
        {easy}
    </text>

    <text
        x="260"
        y="153"
        fill="#8b949e"
        font-family="Arial, Helvetica, sans-serif"
        font-size="11"
        letter-spacing="1">
        EASY
    </text>

    <!-- Medium -->

    <text
        x="470"
        y="130"
        fill="#f0f6fc"
        font-family="Arial, Helvetica, sans-serif"
        font-size="26"
        font-weight="600">
        {medium}
    </text>

    <text
        x="470"
        y="153"
        fill="#8b949e"
        font-family="Arial, Helvetica, sans-serif"
        font-size="11"
        letter-spacing="1">
        MEDIUM
    </text>

    <!-- Hard -->

    <text
        x="650"
        y="130"
        fill="#f0f6fc"
        font-family="Arial, Helvetica, sans-serif"
        font-size="26"
        font-weight="600">
        {hard}
    </text>

    <text
        x="650"
        y="153"
        fill="#8b949e"
        font-family="Arial, Helvetica, sans-serif"
        font-size="11"
        letter-spacing="1">
        HARD
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

    stats = get_difficulty_breakdown()

    print("\nStrataScratch Statistics")
    print("-------------------------")
    print(f"Problems solved : {stats['solved']}")
    print(f"Easy            : {stats['easy']}")
    print(f"Medium          : {stats['medium']}")
    print(f"Hard            : {stats['hard']}")

    svg = generate_svg(stats)

    OUTPUT_FILE.write_text(svg, encoding="utf-8")

    print(f"\nSVG generated: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
