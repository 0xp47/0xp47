#!/usr/bin/env python3
import os
import sys
import re
import requests
import json
import base64

SVG_PATH = "images/coding_stats.svg"


def fetch_wakatime_stats(api_key):
    url = "https://wakatime.com/api/v1/users/current/stats/last_7_days"
    headers = {"Authorization": f"Basic {api_key}"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json().get("data", {})
    except Exception:
        pass
    return None


def generate_mock_data():
    return {
        "human_readable_total": "28 hrs 45 mins",
        "human_readable_daily_average": "4 hrs 6 mins",
        "languages": [
            {"name": "Python", "percent": 42.5},
            {"name": "JavaScript", "percent": 24.3},
            {"name": "TypeScript", "percent": 18.2},
            {"name": "HTML/CSS", "percent": 10.0},
            {"name": "Markdown", "percent": 5.0},
        ],
    }


def get_color(lang_name):
    # Modern neon palette for coding languages
    colors = {
        "python": "#306998",
        "javascript": "#f7df1e",
        "typescript": "#3178c6",
        "html/css": "#e34c26",
        "css": "#563d7c",
        "markdown": "#083fa1",
        "php": "#4f5d95",
        "c#": "#178600",
        "java": "#b07219",
        "go": "#00add8",
        "ruby": "#701516",
        "rust": "#dea584",
        "c++": "#f34b7d",
        "shell": "#89e051",
    }
    return colors.get(lang_name.lower(), "#8e2de2")


def build_svg_card(data):
    total_time = data.get("human_readable_total", "0 hrs")
    daily_avg = data.get("human_readable_daily_average", "0 mins")
    languages = data.get("languages", [])[:5]  # Limit to top 5

    # SVG Dimensions
    width = 450
    height = 280

    # Start building SVG
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none">
    <style>
        .card {{
            fill: #0d1117;
            stroke: #30363d;
            stroke-width: 1.5;
            rx: 10px;
        }}
        .title {{
            font: 600 18px 'Inter', -apple-system, sans-serif;
            fill: #58a6ff;
        }}
        .subtitle {{
            font: 500 12px 'Inter', -apple-system, sans-serif;
            fill: #8b949e;
        }}
        .label {{
            font: 600 13px 'Inter', -apple-system, sans-serif;
            fill: #c9d1d9;
        }}
        .value {{
            font: 400 12px 'Inter', -apple-system, sans-serif;
            fill: #8b949e;
        }}
        .stat-value {{
            font: 700 16px 'Inter', -apple-system, sans-serif;
            fill: #ffffff;
        }}
        .bar-bg {{
            fill: #161b22;
            rx: 3px;
        }}
        .bar-fill {{
            rx: 3px;
            animation: grow 1s ease-out forwards;
        }}
        @keyframes grow {{
            from {{ width: 0; }}
        }}
    </style>
    
    <!-- Background Card -->
    <rect class="card" width="{width - 2}" height="{height - 2}" x="1" y="1" />
    
    <!-- Header -->
    <text x="25" y="35" class="title">WakaTime Dev Stats</text>
    <text x="25" y="52" class="subtitle">Last 7 Days Activity</text>
    
    <!-- Summary stats side by side -->
    <text x="280" y="32" class="value">Total Coding Time</text>
    <text x="280" y="52" class="stat-value">{total_time}</text>
    
    <!-- Separator -->
    <line x1="25" y1="68" x2="{width - 25}" y2="68" stroke="#21262d" stroke-width="1" />
    """

    # Draw language stats
    y_start = 90
    y_gap = 35
    bar_max_width = 250

    for i, lang in enumerate(languages):
        y = y_start + (i * y_gap)
        name = lang.get("name", "Unknown")
        pct = lang.get("percent", 0.0)
        color = get_color(name)
        bar_fill_width = int((pct / 100.0) * bar_max_width)

        svg += f"""
    <!-- {name} -->
    <text x="25" y="{y + 12}" class="label">{name}</text>
    <rect x="130" y="{y}" width="{bar_max_width}" height="12" class="bar-bg" />
    <rect x="130" y="{y}" width="{bar_fill_width}" height="12" fill="{color}" class="bar-fill" />
    <text x="{130 + bar_max_width + 12}" y="{y + 11}" class="value">{pct:.1f}%</text>
        """

    # Footer
    svg += f"""
    <!-- Separator -->
    <line x1="25" y1="245" x2="{width - 25}" y2="245" stroke="#21262d" stroke-width="1" />
    <text x="25" y="262" class="subtitle">Daily Average: {daily_avg}</text>
</svg>
"""
    return svg


def main():
    api_key_raw = os.environ.get("WAKATIME_API_KEY")
    os.makedirs(os.path.dirname(SVG_PATH), exist_ok=True)

    if not api_key_raw:
        print(
            "Warning: WAKATIME_API_KEY not found. Generating SVG card with mock data..."
        )
        data = generate_mock_data()
    else:
        if not api_key_raw.startswith("waka_"):
            try:
                api_key = base64.b64encode(api_key_raw.encode()).decode()
            except:
                api_key = api_key_raw
        else:
            api_key = base64.b64encode(api_key_raw.encode()).decode()

        print("Fetching WakaTime statistics for SVG...")
        waka_data = fetch_wakatime_stats(api_key)
        if waka_data:
            data = waka_data
        else:
            print("Failed to fetch, falling back to mock data for SVG...")
            data = generate_mock_data()

    svg_content = build_svg_card(data)
    with open(SVG_PATH, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Stats SVG generated successfully at {SVG_PATH}")


if __name__ == "__main__":
    main()
