#!/usr/bin/env python3
import os
import sys
import time
import json
import requests
from datetime import datetime, timezone, timedelta


def get_weekly_contributors(repo, token):
    since_date = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    url = f"https://api.github.com/repos/{repo}/commits"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}" if token else "",
    }
    params = {"since": since_date}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        if response.status_code != 200:
            print(f"Error fetching commits: {response.status_code} - {response.text}")
            return {}

        commits = response.json()
        contributors = {}
        for commit in commits:
            author_info = commit.get("author") or commit.get("commit", {}).get(
                "author", {}
            )
            name = author_info.get("login") or author_info.get("name")
            if name:
                contributors[name] = contributors.get(name, 0) + 1
        return contributors
    except Exception as e:
        print(f"Exception fetching commits: {e}")
        return {}


def send_discord_rollcall(webhook_url, repo, contributors):
    headers = {"Content-Type": "application/json"}

    embed = {
        "title": "🏆 0xp47 Weekly Contributor Roll Call!",
        "url": f"https://github.com/{repo}",
        "color": 10181046,  # Purple
        "footer": {
            "text": "0xp47 Repository Contributor Roll Call",
            "icon_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
        },
    }

    if contributors:
        contributors_list = "\n".join(
            [
                f"- **{name}** ({count} commit(s))"
                for name, count in sorted(
                    contributors.items(), key=lambda x: x[1], reverse=True
                )
            ]
        )
        embed["description"] = (
            f"A huge thank you to everyone who contributed to **[{repo}](https://github.com/{repo})** over the last 7 days! 🙌\n\n### Contributors of the week:\n{contributors_list}"
        )
    else:
        embed["description"] = (
            f"No new commits recorded in **[{repo}](https://github.com/{repo})** this week. Let's start building! 🚀"
        )

    payload = {
        "username": "0xp47 Contributor Recognition",
        "avatar_url": "https://github.com/0xp47.png",
        "embeds": [embed],
    }

    response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
    if response.status_code in [200, 204]:
        print("Roll call sent successfully!")
    else:
        print(f"Failed to send roll call: {response.status_code} - {response.text}")


def main():
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("Error: DISCORD_WEBHOOK_URL is not set.")
        sys.exit(0)

    repo = os.environ.get("GITHUB_REPOSITORY", "Unknown/Repo")
    token = os.environ.get("GITHUB_TOKEN")

    print(f"Fetching commits since 7 days ago for {repo}...")
    contributors = get_weekly_contributors(repo, token)

    print("Sending contributor recognition notification...")
    send_discord_rollcall(webhook_url, repo, contributors)


if __name__ == "__main__":
    main()
