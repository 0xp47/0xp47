#!/usr/bin/env python3
import os
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
import time
import requests
from datetime import datetime, timezone


def fetch_wakatime_stats(api_key):
    # WakaTime stats endpoint for the last 7 days
    url = "https://wakatime.com/api/v1/users/current/stats/last_7_days"
    headers = {"Authorization": f"Basic {api_key}"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json().get("data", {})
        else:
            print(
                f"Error fetching WakaTime stats: {response.status_code} - {response.text}"
            )
            return None
    except Exception as e:
        print(f"Exception during WakaTime fetch: {e}")
        return None


def generate_mock_data():
    return {
        "total_seconds": 32400,
        "human_readable_total": "9 hrs total",
        "human_readable_daily_average": "1 hr 17 mins daily avg",
        "languages": [
            {"name": "Python", "percent": 45.5, "total_seconds": 14742},
            {"name": "JavaScript", "percent": 30.0, "total_seconds": 9720},
            {"name": "TypeScript", "percent": 24.5, "total_seconds": 7938},
        ],
        "editors": [
            {"name": "VS Code", "percent": 90.0, "total_seconds": 29160},
            {"name": "Acode", "percent": 10.0, "total_seconds": 3240},
        ],
        "operating_systems": [
            {"name": "Windows", "percent": 95.0, "total_seconds": 30780},
            {"name": "Linux", "percent": 5.0, "total_seconds": 1620},
        ],
    }


def create_report(data, is_mock=False):
    year, week_num, _ = datetime.now(timezone.utc).isocalendar()
    os.makedirs("stats", exist_ok=True)
    report_path = f"stats/weekly-report-{year}-W{week_num:02d}.md"

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    markdown = f"""# WakaTime Weekly Coding Digest - {year} Week {week_num:02d}
Generated on: `{date_str}` {"(MOCK DATA)" if is_mock else ""}

## 📊 Summary
- **Total Coding Time**: {data.get('human_readable_total', 'n/a')}
- **Daily Average**: {data.get('human_readable_daily_average', 'n/a')}

## 💻 Top Languages
| Language | Percentage | Time spent |
| :--- | :--- | :--- |
"""
    for lang in data.get("languages", []):
        markdown += f"| {lang['name']} | {lang['percent']}% | {int(lang['total_seconds']/3600)}h {int((lang['total_seconds']%3600)/60)}m |\n"

    markdown += """
## ✍️ Editors
| Editor | Percentage | Time spent |
| :--- | :--- | :--- |
"""
    for editor in data.get("editors", []):
        markdown += f"| {editor['name']} | {editor['percent']}% | {int(editor['total_seconds']/3600)}h {int((editor['total_seconds']%3600)/60)}m |\n"

    markdown += """
## 🖥️ Operating Systems
| OS | Percentage | Time spent |
| :--- | :--- | :--- |
"""
    for os_item in data.get("operating_systems", []):
        markdown += f"| {os_item['name']} | {os_item['percent']}% | {int(os_item['total_seconds']/3600)}h {int((os_item['total_seconds']%3600)/60)}m |\n"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"Report successfully saved to {report_path}")

    # Send weekly digest to Discord if webhook URL is configured
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if webhook_url:
        send_discord_digest(webhook_url, data, is_mock)


def send_discord_digest(webhook_url, data, is_mock=False):
    lang_fields = ""
    for lang in data.get("languages", [])[:3]:
        lang_fields += f"• **{lang['name']}**: {lang['percent']}% ({int(lang['total_seconds']/3600)}h {int((lang['total_seconds']%3600)/60)}m)\n"

    editor_fields = ""
    for editor in data.get("editors", [])[:2]:
        editor_fields += f"• **{editor['name']}**: {editor['percent']}% ({int(editor['total_seconds']/3600)}h {int((editor['total_seconds']%3600)/60)}m)\n"

    embed = {
        "title": "📅 WakaTime Weekly Coding Digest",
        "description": f"Weekly coding activity breakdown for **0xp47** {'(Mock Data)' if is_mock else ''}.",
        "color": 3447003,
        "fields": [
            {
                "name": "📊 Activity Summary",
                "value": f"• **Total Time**: {data.get('human_readable_total', 'n/a')}\n• **Daily Average**: {data.get('human_readable_daily_average', 'n/a')}",
                "inline": False,
            },
            {
                "name": "💻 Top Languages",
                "value": lang_fields or "n/a",
                "inline": True,
            },
            {
                "name": "✍️ Top Editors",
                "value": editor_fields or "n/a",
                "inline": True,
            },
        ],
        "footer": {
            "text": "0xp47 WakaTime Archiver",
            "icon_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
        },
    }

    payload = {
        "username": "0xp47 Metrics Manager",
        "avatar_url": "https://github.com/0xp47.png",
        "embeds": [embed],
    }

    headers = {"Content-Type": "application/json"}
    try:
        r = requests.post(webhook_url, json=payload, headers=headers, timeout=10)
        if r.status_code in [200, 204]:
            print("Successfully sent weekly WakaTime digest to Discord.")
        else:
            print(f"Failed to send weekly digest: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Exception sending weekly digest to Discord: {e}")


def main():
    api_key_raw = os.environ.get("WAKATIME_API_KEY")
    if not api_key_raw:
        print(
            "Warning: WAKATIME_API_KEY not found in environment. Generating a mock report for local verification..."
        )
        data = generate_mock_data()
        create_report(data, is_mock=True)
        return

    # Handle base64 encoded API key or raw API key
    import base64

    if not api_key_raw.startswith("waka_"):
        try:
            # Check if it is base64 encoded (WakaTime keys can be)
            api_key = base64.b64encode(api_key_raw.encode()).decode()
        except:
            api_key = api_key_raw
    else:
        api_key = base64.b64encode(api_key_raw.encode()).decode()

    print("Fetching WakaTime statistics...")
    data = fetch_wakatime_stats(api_key)
    if data:
        create_report(data)
    else:
        print("Failed to retrieve statistics. Creating mock report as fallback...")
        create_report(generate_mock_data(), is_mock=True)


if __name__ == "__main__":
    main()
