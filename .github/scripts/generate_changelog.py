#!/usr/bin/env python3
import subprocess
import sys
import io
import re
from collections import defaultdict

# Configure UTF-8 encoding for Windows terminals
if sys.platform.startswith("win"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

CHANGELOG_PATH = "CHANGELOG.md"


def run_cmd(args):
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        shell=sys.platform.startswith("win"),
        encoding="utf-8",
        errors="ignore",
    )
    if result.returncode != 0:
        return False, result.stdout, result.stderr
    return True, result.stdout, result.stderr


def get_commit_log():
    # Fetch hashes and subject lines
    success, stdout, _ = run_cmd(
        ["git", "log", "--pretty=format:%h__DELIM__%s__DELIM__%an"]
    )
    if not success or not stdout:
        return []

    commits = []
    for line in stdout.splitlines():
        parts = line.strip().split("__DELIM__")
        if len(parts) >= 3:
            commits.append({"hash": parts[0], "subject": parts[1], "author": parts[2]})
    return commits


def parse_commits(commits):
    categories = {
        "feat": "🚀 Features",
        "fix": "🐛 Bug Fixes",
        "docs": "📝 Documentation",
        "chore": "🔧 Maintenance & Chores",
        "style": "🔧 Maintenance & Chores",
        "refactor": "♻️ Code Refactoring",
        "perf": "⚡ Performance Improvements",
        "test": "🧪 Testing",
    }

    grouped = defaultdict(list)
    # Match conventional commit patterns like "feat(scope): message" or "feat: message"
    pattern = re.compile(r"^(\w+)(?:\(([^)]+)\))?\s*:\s*(.*)$")

    for c in commits:
        subj = c["subject"]
        # Clean forbidden brand terms from git logs automatically
        subj = re.sub(r"Ground\s*Zero", "profile repository", subj, flags=re.IGNORECASE)
        match = pattern.match(subj)
        if match:
            c_type, scope, msg = match.groups()
            c_type = c_type.lower()
            if c_type in categories:
                cat_name = categories[c_type]
                scope_str = f"**{scope}**: " if scope else ""
                entry = f"- {scope_str}{msg} ({c['hash']}) - by @{c['author']}"
                grouped[cat_name].append(entry)
            else:
                grouped["Other Changes"].append(
                    f"- {subj} ({c['hash']}) - by @{c['author']}"
                )
        else:
            # If not following conventional commit style, place under other changes
            # Ignore automated update commits to prevent cluttering the log
            if "[skip ci]" in subj or "auto-update" in subj:
                continue
            grouped["Other Changes"].append(
                f"- {subj} ({c['hash']}) - by @{c['author']}"
            )

    return grouped


def main():
    print("Generating CHANGELOG.md...")
    commits = get_commit_log()
    if not commits:
        print("No commits found.")
        sys.exit(0)

    grouped = parse_commits(commits)

    changelog_content = []
    changelog_content.append("# Changelog\n")
    changelog_content.append(
        "All notable changes to this repository will be documented in this file.\n"
    )
    changelog_content.append("<!-- START_CHANGES -->\n")

    # Priority sorting for categories
    priority = [
        "🚀 Features",
        "🐛 Bug Fixes",
        "♻️ Code Refactoring",
        "⚡ Performance Improvements",
        "📝 Documentation",
        "🧪 Testing",
        "🔧 Maintenance & Chores",
        "Other Changes",
    ]

    for cat in priority:
        if cat in grouped and grouped[cat]:
            changelog_content.append(f"## {cat}\n")
            for entry in grouped[cat]:
                changelog_content.append(f"{entry}\n")
            changelog_content.append("")

    changelog_content.append("<!-- END_CHANGES -->\n")

    with open(CHANGELOG_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(changelog_content))

    print(f"CHANGELOG.md generated successfully at {CHANGELOG_PATH}")


if __name__ == "__main__":
    main()
