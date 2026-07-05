#!/usr/bin/env python3
import os
import sys
import io
import requests
from collections import defaultdict

# Configure UTF-8 encoding for Windows terminals
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

GITHUB_USERNAME = "0xp47"
SVG_PATH = "images/multi_repo_languages.svg"

# Common language colors
LANG_COLORS = {
    "Python": "#3572A5",
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Shell": "#89e051",
    "C++": "#f34b7d",
    "C": "#555555",
    "Go": "#00ADD8",
    "Rust": "#dea584",
    "Java": "#b07219",
    "C#": "#178600",
    "PHP": "#4F5D95",
    "Ruby": "#701516",
    "Swift": "#F05138",
    "Kotlin": "#A97BFF",
    "Dart": "#00B4AB",
}
DEFAULT_COLOR = "#858585"


def get_headers():
    token = os.environ.get("PROFILE_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def fetch_public_repos():
    headers = get_headers()
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?per_page=100"
    repos = []
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Filter for public, non-fork repos
        for repo in data:
            if not repo.get("fork") and not repo.get("private"):
                repos.append(repo.get("name"))
    except Exception as e:
        print(f"Error fetching repositories: {e}")
        
    return repos


def fetch_languages_for_repos(repo_names):
    headers = get_headers()
    lang_bytes = defaultdict(int)
    
    for idx, repo in enumerate(repo_names):
        url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo}/languages"
        try:
            print(f"[{idx+1}/{len(repo_names)}] Fetching languages for: {repo}")
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                for lang, bytes_count in data.items():
                    lang_bytes[lang] += bytes_count
        except Exception as e:
            print(f"Error fetching languages for {repo}: {e}")
            
    return dict(lang_bytes)


def generate_svg(lang_stats):
    total_bytes = sum(lang_stats.values())
    if total_bytes == 0:
        # Fallback empty SVG
        return """<svg xmlns="http://www.w3.org/2000/svg" width="850" height="180">
            <rect width="100%" height="100%" fill="#0d1117" rx="12"/>
            <text x="50%" y="50%" fill="#8b949e" dominant-baseline="middle" text-anchor="middle" font-family="Segoe UI, sans-serif">No public repository stats available</text>
        </svg>"""

    sorted_langs = sorted(lang_stats.items(), key=lambda x: -x[1])
    
    # Calculate percentages
    formatted_langs = []
    other_bytes = 0
    
    for idx, (lang, bytes_count) in enumerate(sorted_langs):
        pct = (bytes_count / total_bytes) * 100
        # If it's less than 1% and not in top 6, bucket it under "Other"
        if idx >= 6 and pct < 1.5:
            other_bytes += bytes_count
        else:
            formatted_langs.append({
                "name": lang,
                "bytes": bytes_count,
                "pct": pct,
                "color": LANG_COLORS.get(lang, DEFAULT_COLOR)
            })
            
    if other_bytes > 0:
        formatted_langs.append({
            "name": "Other",
            "bytes": other_bytes,
            "pct": (other_bytes / total_bytes) * 100,
            "color": DEFAULT_COLOR
        })
        
    # Re-sort to maintain order
    formatted_langs.sort(key=lambda x: -x["bytes"])

    # Draw stacked progress bar details
    bar_x = 0
    bar_segments = []
    for item in formatted_langs:
        width = item["pct"]
        bar_segments.append(
            f'<rect x="{bar_x:.2f}%" y="0" width="{width:.2f}%" height="16" fill="{item["color"]}" rx="2"/>'
        )
        bar_x += width

    # Draw legends (grid of languages)
    legends = []
    # Up to 2 rows of legends, 4 columns
    cols = 4
    for idx, item in enumerate(formatted_langs[:8]):
        row = idx // cols
        col = idx % cols
        x_pos = 45 + col * 190
        y_pos = 110 + row * 30
        legends.append(f"""
            <g transform="translate({x_pos}, {y_pos})">
                <circle cx="0" cy="0" r="6" fill="{item["color"]}"/>
                <text x="16" y="5" fill="#c9d1d9" font-size="13" font-family="Segoe UI, sans-serif" font-weight="600">{item["name"]}</text>
                <text x="135" y="5" fill="#8b949e" font-size="12" font-family="Segoe UI, sans-serif" text-anchor="end">{item["pct"]:.1f}%</text>
            </g>
        """)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="850" height="180" viewBox="0 0 850 180">
    <style>
        .card {{
            fill: #0d1117;
            stroke: rgba(255, 255, 255, 0.08);
            stroke-width: 1.5;
        }}
        .title {{
            fill: #58a6ff;
            font-family: 'Segoe UI', Ubuntu, sans-serif;
            font-size: 15px;
            font-weight: 700;
        }}
        .bar-container {{
            mask: url(#bar-mask);
        }}
        .legend-text {{
            font-family: 'Segoe UI', Ubuntu, sans-serif;
            font-size: 13px;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        .animated {{
            animation: fadeIn 0.8s ease-in-out forwards;
        }}
    </style>

    <rect class="card" width="848" height="178" rx="12" x="1" y="1"/>
    
    <g transform="translate(30, 30)" class="animated">
        <!-- Title -->
        <text x="0" y="5" class="title">📊 Multi-Repository Language Distribution</text>
        
        <!-- Stacked Progress Bar -->
        <mask id="bar-mask">
            <rect x="0" y="25" width="790" height="16" rx="8" fill="white"/>
        </mask>
        <g class="bar-container" mask="url(#bar-mask)">
            {"".join(bar_segments)}
        </g>
        
        <!-- Legend Grid -->
        <g class="legend-text">
            {"".join(legends)}
        </g>
    </g>
</svg>"""
    return svg


def main():
    print("Fetching public repos...")
    repos = fetch_public_repos()
    if not repos:
        print("No public repositories found (or error). Generating mock stats card...")
        # Fallback mock data in case of rate limit/no public repos
        lang_stats = {"Python": 45000, "JavaScript": 30000, "HTML": 12000, "CSS": 8000, "TypeScript": 5000}
    else:
        print(f"Found {len(repos)} public repositories. Fetching language bytes...")
        lang_stats = fetch_languages_for_repos(repos)
        
    print("Generating SVG stats card...")
    svg_content = generate_svg(lang_stats)
    
    os.makedirs(os.path.dirname(SVG_PATH), exist_ok=True)
    with open(SVG_PATH, "w", encoding="utf-8") as f:
        f.write(svg_content)
        
    print(f"Multi-repository language stats SVG successfully written to {SVG_PATH}")


if __name__ == "__main__":
    main()
