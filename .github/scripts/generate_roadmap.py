#!/usr/bin/env python3
import os
import sys
import io
import json
from datetime import datetime

# Configure UTF-8 encoding for Windows terminals
if sys.platform.startswith("win"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

ROADMAP_JSON = "stats/roadmap.json"
ROADMAP_SVG = "images/roadmap.svg"


def create_default_roadmap():
    default_data = [
        {
            "name": "Profile stats & weekly reports",
            "start": "2026-07-01",
            "end": "2026-07-08",
            "progress": 100,
            "color": "#00f0ff",
        },
        {
            "name": "Farming & Streak automation",
            "start": "2026-07-04",
            "end": "2026-07-10",
            "progress": 100,
            "color": "#00ff66",
        },
        {
            "name": "PR Linting & TODO creators",
            "start": "2026-07-05",
            "end": "2026-07-12",
            "progress": 100,
            "color": "#ffaa00",
        },
        {
            "name": "Security auditing & backups",
            "start": "2026-07-05",
            "end": "2026-07-15",
            "progress": 90,
            "color": "#ff3366",
        },
        {
            "name": "Discord Bot remote commands",
            "start": "2026-07-10",
            "end": "2026-07-25",
            "progress": 20,
            "color": "#cc33ff",
        },
    ]
    os.makedirs(os.path.dirname(ROADMAP_JSON), exist_ok=True)
    with open(ROADMAP_JSON, "w", encoding="utf-8") as f:
        json.dump(default_data, f, indent=2)
    return default_data


def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")


def draw_roadmap_svg(tasks):
    # Determine date bounds
    start_dates = [parse_date(t["start"]) for t in tasks]
    end_dates = [parse_date(t["end"]) for t in tasks]

    min_date = min(start_dates)
    max_date = max(end_dates)

    total_days = (max_date - min_date).days
    if total_days == 0:
        total_days = 1

    # Dimensions
    width = 850
    height = 50 + (len(tasks) * 45) + 30

    # SVG header
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <style>
    .bg {{ fill: #0d1117; rx: 12px; }}
    .title {{ font-family: 'Segoe UI', Ubuntu, sans-serif; font-size: 16px; fill: #58a6ff; font-weight: bold; }}
    .grid-line {{ stroke: #30363d; stroke-width: 1; stroke-dasharray: 4; }}
    .date-label {{ font-family: 'Segoe UI', Ubuntu, sans-serif; font-size: 10px; fill: #8b949e; text-anchor: middle; }}
    .task-label {{ font-family: 'Segoe UI', Ubuntu, sans-serif; font-size: 12px; fill: #c9d1d9; font-weight: 500; }}
    .bar-bg {{ rx: 4px; fill: #21262d; }}
    .bar-fill {{ rx: 4px; }}
    .progress-text {{ font-family: 'Segoe UI', Ubuntu, sans-serif; font-size: 10px; fill: #8b949e; font-weight: bold; }}
  </style>
  
  <!-- Background -->
  <rect width="{width}" height="{height}" class="bg" />
  
  <text x="25" y="32" class="title">📍 Project Roadmap &amp; Progress</text>
"""

    # Draw timeline grids (e.g. 5 columns)
    col_width_pct = 0.65  # 65% of width for the Gantt bars
    label_width = 250  # Width allocated for task labels
    gantt_width = width - label_width - 40

    num_grid_cols = 5
    for i in range(num_grid_cols + 1):
        x = label_width + (i * (gantt_width / num_grid_cols))
        svg += f'  <line x1="{x}" y1="50" x2="{x}" y2="{height - 25}" class="grid-line" />\n'

        # Calculate date label
        days_offset = int(i * (total_days / num_grid_cols))
        # Date string formatting
        from datetime import timedelta

        grid_date = min_date + timedelta(days=days_offset)
        date_str = grid_date.strftime("%b %d")
        svg += (
            f'  <text x="{x}" y="{height - 12}" class="date-label">{date_str}</text>\n'
        )

    # Draw tasks
    for idx, t in enumerate(tasks):
        y = 55 + (idx * 45)

        # Calculate bar position
        task_start = parse_date(t["start"])
        task_end = parse_date(t["end"])

        start_offset = (task_start - min_date).days
        duration = (task_end - task_start).days

        bar_x = label_width + ((start_offset / total_days) * gantt_width)
        bar_width = (duration / total_days) * gantt_width
        # Ensure minimum bar width
        if bar_width <= 0:
            bar_width = 5

        color = t.get("color", "#00ffcc")
        progress = t.get("progress", 0)
        progress_width = (progress / 100) * bar_width

        # Task label
        svg += f'  <text x="25" y="{y + 18}" class="task-label">{t["name"]}</text>\n'

        # Task bar background
        svg += f'  <rect x="{bar_x}" y="{y + 6}" width="{bar_width}" height="16" class="bar-bg" />\n'

        # Task bar fill (progress)
        if progress > 0:
            svg += f'  <rect x="{bar_x}" y="{y + 6}" width="{progress_width}" height="16" fill="{color}" class="bar-fill" />\n'

        # Progress text
        svg += f'  <text x="{bar_x + bar_width + 8}" y="{y + 18}" class="progress-text">{progress}%</text>\n'

    svg += "</svg>"

    os.makedirs(os.path.dirname(ROADMAP_SVG), exist_ok=True)
    with open(ROADMAP_SVG, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Roadmap SVG generated successfully at {ROADMAP_SVG}")


def main():
    print("🏥 Running Roadmap visual generator...")
    if not os.path.exists(ROADMAP_JSON):
        tasks = create_default_roadmap()
    else:
        try:
            with open(ROADMAP_JSON, "r", encoding="utf-8") as f:
                tasks = json.load(f)
        except Exception as e:
            print(f"Error loading roadmap.json: {e}")
            tasks = create_default_roadmap()

    draw_roadmap_svg(tasks)


if __name__ == "__main__":
    main()
