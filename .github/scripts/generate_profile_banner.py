#!/usr/bin/env python3
import os
import sys
import re
import requests
import json

BANNER_PATH = "images/profile_banner.svg"


def fetch_github_stats(username, token):
    url = f"https://api.github.com/users/{username}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}" if token else "",
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            return {
                "repos": data.get("public_repos", 0),
                "followers": data.get("followers", 0),
                "following": data.get("following", 0),
            }
    except Exception:
        pass
    return {"repos": 12, "followers": 0, "following": 0}


def fetch_total_stars(username, token):
    url = f"https://api.github.com/users/{username}/repos"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}" if token else "",
    }
    params = {"per_page": 100}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        if res.status_code == 200:
            repos = res.json()
            stars = sum(repo.get("stargazers_count", 0) for repo in repos)
            return stars
    except Exception:
        pass
    return 0


def extract_wakatime_hours():
    readme_path = "README.md"
    if not os.path.exists(readme_path):
        return "n/a"
    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.search(r"WakaTime \(all time\):\s*([^\n|]+)", content)
        if match:
            return match.group(1).strip().split(" total")[0]
        match_alt = re.search(r"WakaTime \(all time\)\s*:\s*([^\n|]+)", content)
        if match_alt:
            return match_alt.group(1).strip().split(" total")[0]
    except Exception:
        pass
    return "890 hrs"


def draw_svg_banner(username, gh_stats, stars, waka_hours):
    # Banner Dimensions
    w = 850
    h = 160

    # Modern Gradient SVG
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none">
    <style>
        .bg {{
            fill: url(#gradient);
            stroke: #30363d;
            stroke-width: 1.5;
            rx: 8px;
        }}
        .title {{
            font: 700 24px 'Inter', -apple-system, sans-serif;
            fill: #ffffff;
            letter-spacing: -0.5px;
        }}
        .subtitle {{
            font: 500 13px 'Inter', -apple-system, sans-serif;
            fill: #58a6ff;
            letter-spacing: 0.5px;
        }}
        .stat-label {{
            font: 500 11px 'Inter', -apple-system, sans-serif;
            fill: #8b949e;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .stat-val {{
            font: 700 18px 'Inter', -apple-system, sans-serif;
            fill: #ffffff;
        }}
        .glow {{
            filter: drop-shadow(0px 0px 4px rgba(88, 166, 255, 0.4));
        }}
    </style>
    
    <defs>
        <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#0d1117" />
            <stop offset="50%" stop-color="#161b22" />
            <stop offset="100%" stop-color="#0c0e12" />
        </linearGradient>
    </defs>
    
    <!-- Background -->
    <rect class="bg" width="{w-2}" height="{h-2}" x="1" y="1" />
    
    <!-- Left Logo/Text section -->
    <g transform="translate(40, 55)">
        <text class="title glow" x="0" y="20">{username}</text>
        <text class="subtitle" x="0" y="40">FULL-STACK DEVELOPER &amp; AUTOMATION BUILDER</text>
    </g>
    
    <!-- Right stats block -->
    <g transform="translate(460, 45)">
        <!-- Stat 1: Repos -->
        <g transform="translate(0, 0)">
            <text class="stat-label" x="0" y="12">Repositories</text>
            <text class="stat-val" x="0" y="34">{gh_stats['repos']}</text>
        </g>
        
        <!-- Stat 2: Stars -->
        <g transform="translate(100, 0)">
            <text class="stat-label" x="0" y="12">Stars Received</text>
            <text class="stat-val" x="0" y="34">⭐ {stars}</text>
        </g>
        
        <!-- Stat 3: Followers -->
        <g transform="translate(210, 0)">
            <text class="stat-label" x="0" y="12">Followers</text>
            <text class="stat-val" x="0" y="34">{gh_stats['followers']}</text>
        </g>
        
        <!-- Stat 4: Coding Hours -->
        <g transform="translate(295, 0)">
            <text class="stat-label" x="0" y="12">Coding Time</text>
            <text class="stat-val" x="0" y="34">⏱️ {waka_hours}</text>
        </g>
    </g>
</svg>
"""
    return svg


def main():
    username = "0xp47"
    token = os.environ.get("PROFILE_GITHUB_TOKEN")

    print("Fetching GitHub Stats for profile banner...")
    gh_stats = fetch_github_stats(username, token)
    stars = fetch_total_stars(username, token)
    waka_hours = extract_wakatime_hours()

    print(
        f"Stats loaded - Repos: {gh_stats['repos']}, Stars: {stars}, WakaTime: {waka_hours}"
    )

    svg_banner = draw_svg_banner(username, gh_stats, stars, waka_hours)

    os.makedirs(os.path.dirname(BANNER_PATH), exist_ok=True)
    with open(BANNER_PATH, "w", encoding="utf-8") as f:
        f.write(svg_banner)

    print(f"Profile banner SVG successfully written to {BANNER_PATH}")


if __name__ == "__main__":
    main()
