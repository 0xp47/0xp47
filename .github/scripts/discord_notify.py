#!/usr/bin/env python3
import os
import sys
import re
import json
import requests


def extract_metrics():
    readme_path = "README.md"
    if not os.path.exists(readme_path):
        return None

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract the WakaTime / Dev Metrics block
    match = re.search(
        r"<!-- STATS:START -->\s*```text\s*(.*?)\s*```\s*<!-- STATS:END -->",
        content,
        re.DOTALL,
    )
    if not match:
        return None

    lines = match.group(1).splitlines()
    if len(lines) < 5:
        return None

    # Extract some key stats using regex or layout indices
    stats = {}

    # Line 1: Header/Insights
    # Line 2: e.g., "From: 2020 - To: 2026   | Top Lang : Python (26.03%)"
    # Line 3: e.g., "123 repos (50 public, 73 private)   |   60 stars  | Top Editor: VS Code"
    # Line 4: WakaTime totals

    content_text = match.group(1)

    top_lang = re.search(r"Top Lang\s*:\s*([^\n|]+)", content_text)
    top_editor = re.search(r"Top Editor\s*:\s*([^\n|]+)", content_text)
    peak_time = re.search(r"Peak Time\s*:\s*([^\n|]+)", content_text)
    wakatime_total = re.search(r"WakaTime \(all time\)\s*:\s*([^\n|]+)", content_text)
    repos_stars = re.search(r"(\d+ repos \([^)]+\))\s*\|\s*(\d+ stars)", content_text)

    if top_lang:
        stats["top_lang"] = top_lang.group(1).strip()
    if top_editor:
        stats["top_editor"] = top_editor.group(1).strip()
    if peak_time:
        stats["peak_time"] = peak_time.group(1).strip()
    if wakatime_total:
        stats["wakatime_total"] = wakatime_total.group(1).strip()
    if repos_stars:
        stats["repos"] = repos_stars.group(1).strip()
        stats["stars"] = repos_stars.group(2).strip()

    return stats


def send_discord_notification(webhook_url, stats):
    headers = {"Content-Type": "application/json"}

    embed = {
        "title": "📊 GitHub Profile Dev Metrics Updated!",
        "description": "Your profile stats and metrics have been compiled and refreshed.",
        "color": 3447003,  # Premium Blue
        "fields": [],
        "footer": {
            "text": "0xp47 Profile DevOps Automation",
            "icon_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
        },
    }

    if stats:
        embed["fields"].extend(
            [
                {
                    "name": "💻 Top Language",
                    "value": stats.get("top_lang", "Unknown"),
                    "inline": True,
                },
                {
                    "name": "✍️ Top Editor",
                    "value": stats.get("top_editor", "Unknown"),
                    "inline": True,
                },
                {
                    "name": "⏰ Peak Time",
                    "value": stats.get("peak_time", "Unknown"),
                    "inline": True,
                },
                {
                    "name": "⏱️ Coding Time (Total)",
                    "value": stats.get("wakatime_total", "n/a"),
                    "inline": False,
                },
                {
                    "name": "📦 Repositories",
                    "value": stats.get("repos", "n/a"),
                    "inline": True,
                },
                {
                    "name": "⭐ GitHub Stars",
                    "value": stats.get("stars", "0 stars"),
                    "inline": True,
                },
            ]
        )
    else:
        embed["description"] = "Successfully updated README metrics block."

    payload = {
        "username": "0xp47 Profile Metrics",
        "avatar_url": "https://github.com/0xp47.png",
        "embeds": [embed],
    }

    response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
    if response.status_code in [200, 204]:
        print("Successfully notified Discord!")
    else:
        print(f"Failed to notify Discord: {response.status_code} - {response.text}")


def main():
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("Error: DISCORD_WEBHOOK_URL environment variable is not set.")
        sys.exit(
            0
        )  # Exit silently so workflow doesn't fail if webhook is not configured

    print("Extracting metrics from README.md...")
    stats = extract_metrics()

    print("Sending Discord notification...")
    send_discord_notification(webhook_url, stats)


if __name__ == "__main__":
    main()
