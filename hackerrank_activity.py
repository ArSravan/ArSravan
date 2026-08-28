import json
from datetime import date, timedelta
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

ACTIVITY_FILE = Path("activity.json")
OUTPUT_FILE = Path("hackerrank_activity.svg")

WIDTH = 900
HEIGHT = 250

BG = "#0d1117"
BORDER = "#30363d"
TEXT = "#f0f6fc"
MUTED = "#8b949e"

LEVELS = [
    "#161b22",  # 0
    "#0e4429",  # 1
    "#006d32",  # 2
    "#26a641",  # 3
    "#39d353",  # 4+
]


# ============================================================
# Load activity
# ============================================================

def load_activity():
    if not ACTIVITY_FILE.exists():
        return {}

    with ACTIVITY_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


# ============================================================
# Calculate streaks
# ============================================================

def calculate_streaks(activity):
    dates = sorted(
        date.fromisoformat(d)
        for d, count in activity.items()
        if d != "_baseline" and count > 0
    )

    if not dates:
        return 0, 0

    # Longest streak
    longest = 1
    current = 1

    for i in range(1, len(dates)):
        if dates[i] == dates[i - 1] + timedelta(days=1):
            current += 1
            longest = max(longest, current)
        else:
            current = 1

    # Current streak
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


# ============================================================
# Intensity
# ============================================================

def get_level(count):
    if count <= 0:
        return 0

    if count == 1:
        return 1

    if count == 2:
        return 2

    if count == 3:
        return 3

    return 4


# ============================================================
# Generate calendar
# ============================================================

def generate_calendar(activity):

    today = date.today()

    # Show the previous 12 months + today
    start = today - timedelta(days=364)

    # Align to Sunday
    start -= timedelta(days=(start.weekday() + 1) % 7)

    end = today

    cells = []

    current = start

    while current <= end:

        count = activity.get(
            current.isoformat(),
            0
        )

        cells.append(
            (
                current,
                count
            )
        )

        current += timedelta(days=1)

    return cells


# ============================================================
# Month labels
# ============================================================

def generate_month_labels(start):

    labels = []

    current = start

    # Move to first day of current month
    current = current.replace(day=1)

    while current <= date.today():

        # Approximate x position
        days_from_start = (current - start).days

        x = 80 + (days_from_start // 7) * 15

        labels.append(
            (
                current.strftime("%b"),
                x
            )
        )

        if current.month == 12:
            current = current.replace(
                year=current.year + 1,
                month=1
            )
        else:
            current = current.replace(
                month=current.month + 1
            )

    return labels


# ============================================================
# SVG
# ============================================================

def generate_svg(activity):

    today = date.today()

    start = today - timedelta(days=364)

    start -= timedelta(
        days=(start.weekday() + 1) % 7
    )

    cells = generate_calendar(activity)

    current_streak, longest_streak = calculate_streaks(
        activity
    )

    total_problems = sum(
        count
        for key, count in activity.items()
        if key != "_baseline"
    )

    active_days = sum(
        1
        for key, count in activity.items()
        if key != "_baseline" and count > 0
    )

    svg = f"""<svg
xmlns="http://www.w3.org/2000/svg"
width="{WIDTH}"
height="{HEIGHT}"
viewBox="0 0 {WIDTH} {HEIGHT}">

<rect
    width="{WIDTH}"
    height="{HEIGHT}"
    rx="16"
    fill="{BG}"
    stroke="{BORDER}"
    stroke-width="1"/>


<!-- Title -->

<text
    x="35"
    y="35"
    fill="{TEXT}"
    font-family="Arial, Helvetica, sans-serif"
    font-size="18"
    font-weight="600">
    HackerRank Activity
</text>


<!-- Subtitle -->

<text
    x="35"
    y="57"
    fill="{MUTED}"
    font-family="Arial, Helvetica, sans-serif"
    font-size="12">
    Problem solving activity over the last year
</text>


<!-- Month labels -->
"""

    for label, x in generate_month_labels(start):

        svg += f"""
<text
    x="{x}"
    y="82"
    fill="{MUTED}"
    font-family="Arial, Helvetica, sans-serif"
    font-size="10">
    {label}
</text>
"""


    # Weekday labels

    weekday_labels = [
        ("Mon", 105),
        ("Wed", 135),
        ("Fri", 165),
    ]

    for label, y in weekday_labels:

        svg += f"""
<text
    x="35"
    y="{y + 9}"
    fill="{MUTED}"
    font-family="Arial, Helvetica, sans-serif"
    font-size="9">
    {label}
</text>
"""


    # Contribution squares

    CELL = 11
    GAP = 3

    GRID_X = 80
    GRID_Y = 100

    for current, count in cells:

        days = (current - start).days

        column = days // 7
        row = days % 7

        x = GRID_X + column * (CELL + GAP)
        y = GRID_Y + row * (CELL + GAP)

        level = get_level(count)

        color = LEVELS[level]

        # Don't show future cells
        if current > today:
            color = BG

        svg += f"""
<rect
    x="{x}"
    y="{y}"
    width="{CELL}"
    height="{CELL}"
    rx="3"
    fill="{color}">
    <title>
        {current.strftime("%d %b %Y")}: {count} problem{"s" if count != 1 else ""}
    </title>
</rect>
"""


    # Stats footer

    svg += f"""
<!-- Statistics -->

<text
    x="35"
    y="205"
    fill="{TEXT}"
    font-family="Arial, Helvetica, sans-serif"
    font-size="12"
    font-weight="600">
    {total_problems}
</text>

<text
    x="35"
    y="222"
    fill="{MUTED}"
    font-family="Arial, Helvetica, sans-serif"
    font-size="10">
    problems tracked
</text>


<text
    x="180"
    y="205"
    fill="{TEXT}"
    font-family="Arial, Helvetica, sans-serif"
    font-size="12"
    font-weight="600">
    {active_days}
</text>

<text
    x="180"
    y="222"
    fill="{MUTED}"
    font-family="Arial, Helvetica, sans-serif"
    font-size="10">
    active days
</text>


<text
    x="310"
    y="205"
    fill="{TEXT}"
    font-family="Arial, Helvetica, sans-serif"
    font-size="12"
    font-weight="600">
    {current_streak}
</text>

<text
    x="310"
    y="222"
    fill="{MUTED}"
    font-family="Arial, Helvetica, sans-serif"
    font-size="10">
    current streak
</text>


<text
    x="450"
    y="205"
    fill="{TEXT}"
    font-family="Arial, Helvetica, sans-serif"
    font-size="12"
    font-weight="600">
    {longest_streak}
</text>

<text
    x="450"
    y="222"
    fill="{MUTED}"
    font-family="Arial, Helvetica, sans-serif"
    font-size="10">
    longest streak
</text>


<!-- Legend -->

<text
    x="650"
    y="205"
    fill="{MUTED}"
    font-family="Arial, Helvetica, sans-serif"
    font-size="10">
    Less
</text>
"""


    legend_x = 680

    for i, color in enumerate(LEVELS):

        svg += f"""
<rect
    x="{legend_x + i * 15}"
    y="197"
    width="10"
    height="10"
    rx="2"
    fill="{color}"/>
"""


    svg += f"""
<text
    x="760"
    y="205"
    fill="{MUTED}"
    font-family="Arial, Helvetica, sans-serif"
    font-size="10">
    More
</text>

</svg>
"""

    return svg


# ============================================================
# Main
# ============================================================

def main():

    print("Generating HackerRank activity graph...")

    activity = load_activity()

    svg = generate_svg(activity)

    OUTPUT_FILE.write_text(
        svg,
        encoding="utf-8"
    )

    print(
        f"SVG generated: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()