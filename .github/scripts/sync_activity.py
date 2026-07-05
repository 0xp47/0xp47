#!/usr/bin/env python3
import os
import sys
import io
import re
import requests

# Configure UTF-8 encoding for Windows terminals
if sys.platform.startswith("win"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

GITHUB_USERNAME = "0xp47"
README_FILES = ["README.md", "README.fil.md"]
START_MARKER = "<!-- START_SECTION:activity -->"
END_MARKER = "<!-- END_SECTION:activity -->"


def fetch_recent_activity():
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/events/public?per_page=15"
    headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        events = response.json()
    except Exception as e:
        print(f"Error fetching GitHub events: {e}")
        return []

    activity_items = []
    seen_ids = set()

    # Format and filter events
    for event in events:
        if len(activity_items) >= 5:
            break

        event_id = event.get("id")
        if event_id in seen_ids:
            continue
        seen_ids.add(event_id)

        event_type = event.get("type")
        repo_name = event.get("repo", {}).get("name", "")
        # Remove username prefix from repo name if present
        repo_short = repo_name.replace(f"{GITHUB_USERNAME}/", "")

        payload = event.get("payload", {})

        if event_type == "PushEvent":
            commits = payload.get("commits", [])
            if not commits:
                continue
            commit_count = len(commits)
            commit_msg = commits[0].get("message", "").split("\n")[0]
            # Truncate long messages
            if len(commit_msg) > 50:
                commit_msg = commit_msg[:47] + "..."

            # Singular/plural
            commit_text = "commit" if commit_count == 1 else "commits"
            activity_items.append(
                f'📝 Pushed {commit_count} {commit_text} to [`{repo_short}`](https://github.com/{repo_name}): "*{commit_msg}*"'
            )

        elif event_type == "PullRequestEvent":
            action = payload.get("action", "")
            pr = payload.get("pull_request", {})
            pr_num = pr.get("number", "")
            pr_title = pr.get("title", "")
            pr_url = pr.get("html_url", "")

            if action == "opened":
                activity_items.append(
                    f'🚀 Opened Pull Request [#{pr_num}]({pr_url}) in [`{repo_short}`](https://github.com/{repo_name}): "*{pr_title}*"'
                )
            elif action == "closed":
                merged = pr.get("merged", False)
                status_text = "Merged" if merged else "Closed"
                emoji = "💜" if merged else "❌"
                activity_items.append(
                    f'{emoji} {status_text} Pull Request [#{pr_num}]({pr_url}) in [`{repo_short}`](https://github.com/{repo_name}): "*{pr_title}*"'
                )

        elif event_type == "IssuesEvent":
            action = payload.get("action", "")
            issue = payload.get("issue", {})
            issue_num = issue.get("number", "")
            issue_title = issue.get("title", "")
            issue_url = issue.get("html_url", "")

            if action == "opened":
                activity_items.append(
                    f'⚠️ Opened Issue [#{issue_num}]({issue_url}) in [`{repo_short}`](https://github.com/{repo_name}): "*{issue_title}*"'
                )
            elif action == "closed":
                activity_items.append(
                    f'✅ Closed Issue [#{issue_num}]({issue_url}) in [`{repo_short}`](https://github.com/{repo_name}): "*{issue_title}*"'
                )

        elif event_type == "CreateEvent":
            ref_type = payload.get("ref_type", "")
            ref = payload.get("ref", "")
            if ref_type == "repository":
                activity_items.append(
                    f"✨ Created repository [`{repo_short}`](https://github.com/{repo_name})"
                )
            elif ref_type == "branch":
                activity_items.append(
                    f"🌱 Created branch `{ref}` in [`{repo_short}`](https://github.com/{repo_name})"
                )

        elif event_type == "WatchEvent":
            # Starred a repo
            activity_items.append(
                f"⭐ Starred [`{repo_short}`](https://github.com/{repo_name})"
            )

    return activity_items


def update_readme_files(activity_list):
    if not activity_list:
        print("No recent activities fetched.")
        return

    formatted_content = "\n" + "\n".join([f"- {item}" for item in activity_list]) + "\n"

    for filename in README_FILES:
        if not os.path.exists(filename):
            print(f"File {filename} not found.")
            continue

        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()

        # Regex to locate the start and end markers
        pattern = re.compile(
            rf"({re.escape(START_MARKER)})(.*?)({re.escape(END_MARKER)})", re.DOTALL
        )

        if pattern.search(content):
            new_content = pattern.sub(f"\\1{formatted_content}\\3", content)
            print(f"Updating activity block in {filename}...")
        else:
            # If markers don't exist, append to end
            print(f"Adding activity block to end of {filename}...")
            new_content = (
                content
                + f"\n\n## 📈 Recent Activity\n{START_MARKER}{formatted_content}{END_MARKER}\n"
            )

        with open(filename, "w", encoding="utf-8") as f:
            f.write(new_content)


def main():
    print("🏥 Syncing recent GitHub activity to README files...")
    activities = fetch_recent_activity()
    update_readme_files(activities)
    print("🏥 Activity sync complete!")


if __name__ == "__main__":
    main()
