#!/usr/bin/env python3
import os
import sys
import json
import requests

def get_event_embed(event_name, event_data):
    embed = {
        "color": 3066993, # Default Green
        "fields": [],
        "footer": {
            "text": "Ground Zero GitOps Broadcast",
            "icon_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
        }
    }
    
    sender = event_data.get("sender", {}).get("login", "Unknown User")
    sender_avatar = event_data.get("sender", {}).get("avatar_url", "")
    repo_name = event_data.get("repository", {}).get("full_name", "Unknown Repository")
    repo_url = event_data.get("repository", {}).get("html_url", "")
    
    embed["author"] = {
        "name": sender,
        "icon_url": sender_avatar,
        "url": f"https://github.com/{sender}"
    }
    
    if event_name == "issues":
        action = event_data.get("action", "opened")
        issue = event_data.get("issue", {})
        title = issue.get("title", "No Title")
        url = issue.get("html_url", "")
        number = issue.get("number", "0")
        
        embed["title"] = f"📌 Issue #{number} {action.capitalize()}"
        embed["url"] = url
        embed["description"] = f"**Title:** {title}\n\n[View Issue]({url})"
        embed["color"] = 15158332 if action == "opened" else 9807270 # Red for opened, grey for closed
        
    elif event_name == "pull_request":
        action = event_data.get("action", "opened")
        pr = event_data.get("pull_request", {})
        title = pr.get("title", "No Title")
        url = pr.get("html_url", "")
        number = pr.get("number", "0")
        merged = pr.get("merged", False)
        
        if action == "closed" and merged:
            action_str = "Merged 💜"
            embed["color"] = 10181046 # Purple for merged
        else:
            action_str = action.capitalize()
            embed["color"] = 3066993 if action == "opened" else 15158332 # Green for opened, Red for closed
            
        embed["title"] = f"🔧 Pull Request #{number} {action_str}"
        embed["url"] = url
        embed["description"] = f"**Title:** {title}\n\n[View Pull Request]({url})"
        
    elif event_name == "star" or event_name == "watch":
        embed["title"] = "⭐ New Repository Star!"
        embed["url"] = repo_url
        embed["description"] = f"**{sender}** starred the repository **[{repo_name}]({repo_url})**! Thank you!"
        embed["color"] = 15844367 # Gold
        
    else:
        embed["title"] = f"🔔 Activity: {event_name}"
        embed["url"] = repo_url
        embed["description"] = f"Activity detected in repository by user {sender}."
        
    return embed

def main():
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("Error: DISCORD_WEBHOOK_URL is not set.")
        sys.exit(0)
        
    event_name = os.environ.get("GITHUB_EVENT_NAME")
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    
    if not event_name or not event_path:
        print("Error: GITHUB_EVENT_NAME or GITHUB_EVENT_PATH is missing.")
        sys.exit(1)
        
    if not os.path.exists(event_path):
        print(f"Error: Event payload file not found at {event_path}")
        sys.exit(1)
        
    with open(event_path, "r", encoding="utf-8") as f:
        event_data = json.load(f)
        
    embed = get_event_embed(event_name, event_data)
    
    payload = {
        "username": "Ground Zero Hub",
        "avatar_url": "https://avatars.githubusercontent.com/u/141019001?s=200&v=4",
        "embeds": [embed]
    }
    
    headers = {"Content-Type": "application/json"}
    response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
    if response.status_code in [200, 204]:
        print("Broadcast successful!")
    else:
        print(f"Broadcast failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    main()
