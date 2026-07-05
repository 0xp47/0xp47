#!/usr/bin/env python3
import os
import sys
import subprocess
import json
import requests
from datetime import datetime, timezone, timedelta

def has_commit_today():
    # Get commits from today (since midnight local time)
    local_midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    since_timestamp = int(local_midnight.timestamp())
    
    cmd = ["git", "log", f"--since={since_timestamp}", "--oneline"]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if res.returncode == 0:
            commits = res.stdout.strip()
            return len(commits) > 0
    except Exception as e:
        print(f"Error checking git log: {e}")
        
    return False

def send_streak_warning(webhook_url, repo):
    headers = {"Content-Type": "application/json"}
    embed = {
        "title": "🔥 GitHub Contribution Streak Alert!",
        "description": f"⚠️ You haven't made any commits to **[{repo}](https://github.com/{repo})** today yet!\n\nMake sure to push some changes soon to keep your green square streak alive! 🟩💪",
        "color": 16730624, # Orange/Red warning
        "footer": {
            "text": "Ground Zero Productivity Bot",
            "icon_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
        }
    }
    
    payload = {
        "username": "Streak Protector",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/864/864685.png",
        "embeds": [embed]
    }
    
    response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
    if response.status_code in [200, 204]:
        print("Streak warning sent to Discord!")
    else:
        print(f"Failed to send streak warning: {response.status_code} - {response.text}")

def main():
    print("Checking daily commit activity...")
    if has_commit_today():
        print("🟢 You have already made a commit today! Your contribution streak is safe.")
        sys.exit(0)
        
    print("🔴 No commits detected today yet.")
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    repo = os.environ.get("GITHUB_REPOSITORY", "your-profile-repo")
    
    if webhook_url:
        send_streak_warning(webhook_url, repo)
    else:
        print("💡 Setup a DISCORD_WEBHOOK_URL environment variable to receive automated alerts.")
        
    # Exit with code 0 since this is just an informational check
    sys.exit(0)

if __name__ == "__main__":
    main()
