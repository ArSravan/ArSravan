import json
import os
from pathlib import Path

import requests

USERNAME = "Sravan"

GRAPHQL_URL = "https://api.stratascratch.com/graphql/"

PROFILE_URL = f"https://platform.stratascratch.com/profile-code/{USERNAME}"

ACTIVITY_FILE = Path("stratascratch_activity.json")
OUTPUT_FILE = Path("stratascratch_stats.svg")

TOKEN = os.environ.get("STRATASCRATCH_TOKEN")

HEADERS = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

CATEGORY_QUERY = """
query CategoryBreakdown($username: String!) {
    analytics(username: $username) {
        id
        solvedByType
        solvedNonCodingByType {
            systemDesign
            probability
            businessCase
            statistics
            modeling
            technical
            product
            __typename
        }
        __typename
    }
}
"""


def load_activity():
    if not ACTIVITY_FILE.exists():
        return {}

    with ACTIVITY_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_category_breakdown():
    if not TOKEN:
        raise RuntimeError("STRATASCRATCH_TOKEN environment variable is not set.")

    payload = {
        "operationName": "CategoryBreakdown",
        "variables": {"username": USERNAME},
        "query": CATEGORY_QUERY
    }

    response = requests.post(GRAPHQL_URL, headers=HEADERS, json=payload, timeout=30)
    response.raise_for_status()

    data = response.json()

    if "errors" in data:
        raise RuntimeError(f"StrataScratch GraphQL error: {data['errors']}")

    analytics = data.get("data", {}).get("analytics") or {}

    solved_by_type = json.loads(analytics.get("solvedByType") or "{}")
    non_coding = analytics.get("solvedNonCodingByType") or {}

    concept_total = sum(
        value
        for key, value in non_coding.items()
        if key != "__typename"
    )

    return {
        "analytical": solved_by_type.get("analytics", 0),
        "algorithmic": solved_by_type.get("algorithms", 0),
        "visualization": solved_by_type.get("visualizations", 0),
        "concept": concept_total
    }


def get_stratascratch_stats():
    activity = load_activity()
    categories = get_category_breakdown()

    return {
        "solved": sum(activity.values()),
        "categories": categories
    }


def generate_svg(stats):

    solved = stats["solved"]
    categories = stats["categories"]

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

    <!-- By category -->

    <text
        x="260"
        y="110"
        fill="#8b949e"
        font-family="Arial, Helvetica, sans-serif"
        font-size="11"
        letter-spacing="1">
        BY CATEGORY
    </text>

    <text
        x="260"
        y="135"
        fill="#f0f6fc"
        font-family="Arial, Helvetica, sans-serif"
        font-size="13"
        font-weight="600">
        Analytical: {categories['analytical']}
    </text>

    <text
        x="260"
        y="158"
        fill="#f0f6fc"
        font-family="Arial, Helvetica, sans-serif"
        font-size="13"
        font-weight="600">
        Algorithmic: {categories['algorithmic']}
    </text>

    <text
        x="530"
        y="135"
        fill="#f0f6fc"
        font-family="Arial, Helvetica, sans-serif"
        font-size="13"
        font-weight="600">
        Visualization: {categories['visualization']}
    </text>

    <text
        x="530"
        y="158"
        fill="#f0f6fc"
        font-family="Arial, Helvetica, sans-serif"
        font-size="13"
        font-weight="600">
        Concept: {categories['concept']}
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
    print(f"Analytical      : {stats['categories']['analytical']}")
    print(f"Algorithmic     : {stats['categories']['algorithmic']}")
    print(f"Visualization   : {stats['categories']['visualization']}")
    print(f"Concept         : {stats['categories']['concept']}")

    svg = generate_svg(stats)

    OUTPUT_FILE.write_text(svg, encoding="utf-8")

    print(f"\nSVG generated: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
