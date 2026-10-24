import json
import os
from pathlib import Path

import requests


# ============================================================
# Configuration
# ============================================================

USERNAME = "Sravan"

GRAPHQL_URL = "https://api.stratascratch.com/graphql/"

ACTIVITY_FILE = Path("stratascratch_activity.json")

TOKEN = os.environ.get("STRATASCRATCH_TOKEN")

HEADERS = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}


# ============================================================
# GraphQL Query
# ============================================================

QUERY = """
query Heatmap(
    $username: String!,
    $questionClass: QuestionClassEnum!,
    $codeType: Int,
    $questionType: NonCodingQuestionTypeEnum,
    $startDate: Date,
    $endDate: Date
) {
    analytics(username: $username) {
        id

        solvedByDate(
            questionClass: $questionClass
            codeType: $codeType
            questionType: $questionType
            startDate: $startDate
            endDate: $endDate
        ) {
            date
            count
            questionClass
            __typename
        }

        __typename
    }
}
"""


# ============================================================
# Load activity
# ============================================================

def load_activity():

    if not ACTIVITY_FILE.exists():
        return {}

    with ACTIVITY_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# Save activity
# ============================================================

def save_activity(activity):

    with ACTIVITY_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            activity,
            file,
            indent=2,
            sort_keys=True
        )


# ============================================================
# StrataScratch
# ============================================================

def get_stratascratch_activity():

    if not TOKEN:
        raise RuntimeError(
            "STRATASCRATCH_TOKEN environment variable is not set."
        )

    payload = {
        "operationName": "Heatmap",

        "variables": {
            "username": USERNAME,
            "questionClass": "ALL"
        },

        "query": QUERY
    }

    response = requests.post(
        GRAPHQL_URL,
        headers=HEADERS,
        json=payload,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if "errors" in data:
        raise RuntimeError(
            f"StrataScratch GraphQL error: {data['errors']}"
        )

    return (
        data
        .get("data", {})
        .get("analytics", {})
        .get("solvedByDate", [])
    )


# ============================================================
# Update activity
# ============================================================

def update_activity(activity, solved_by_date):

    for entry in solved_by_date:

        activity_date = entry.get("date")
        count = entry.get("count", 0)

        if activity_date is None:
            continue

        activity[activity_date] = count


# ============================================================
# Main
# ============================================================

def main():

    print("Fetching StrataScratch activity...")

    solved_by_date = get_stratascratch_activity()

    activity = load_activity()

    update_activity(
        activity,
        solved_by_date
    )

    save_activity(activity)

    print()

    print("StrataScratch activity")
    print("----------------------")

    total = 0

    for activity_date in sorted(activity):

        count = activity[activity_date]

        total += count

        print(
            f"{activity_date}: {count}"
        )

    print()
    print(f"Days tracked: {len(activity)}")
    print(f"Problems tracked: {total}")

    print(
        f"\nActivity saved to: {ACTIVITY_FILE}"
    )


if __name__ == "__main__":
    main()
