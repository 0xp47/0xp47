#!/usr/bin/env python3
import os
import sys
import io
import time
import subprocess

# Configure UTF-8 encoding for Windows terminals
if sys.platform.startswith("win"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

ACTIVITY_FILE = "stats/activity_log.txt"


def run_cmd(args):
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        shell=sys.platform.startswith("win"),
    )
    if result.returncode != 0:
        print(f"Error running command: {' '.join(args)}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        return False
    return True


def make_daily_commits():
    print("🚀 Initializing daily contribution generator...")

    # Configure git
    run_cmd(["git", "config", "--global", "user.name", "github-actions[bot]"])
    run_cmd(
        [
            "git",
            "config",
            "--global",
            "user.email",
            "github-actions[bot]@users.noreply.github.com",
        ]
    )

    os.makedirs(os.path.dirname(ACTIVITY_FILE), exist_ok=True)

    # Create 5 commits
    for i in range(1, 6):
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        log_entry = f"Auto-commit {i}/5 on {timestamp}\n"

        try:
            with open(ACTIVITY_FILE, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Failed to update activity log: {e}")
            sys.exit(1)

        if not run_cmd(["git", "add", ACTIVITY_FILE]):
            sys.exit(1)

        commit_msg = (
            f"chore(activity): log daily developer contribution {i}/5 [skip ci]"
        )
        if not run_cmd(["git", "commit", "-m", commit_msg]):
            sys.exit(1)

        print(f"   Created commit {i}/5: {commit_msg}")
        time.sleep(1)

    print("✅ Successfully generated 5 local activity commits.")

    # Pull remote changes to prevent conflicts
    run_cmd(["git", "pull", "--rebase", "origin", "main"])

    # Push commits to remote repo
    if run_cmd(["git", "push", "origin", "main"]):
        print("🎉 Successfully pushed all 5 commits to origin/main!")
        return True
    else:
        print("❌ Failed to push commits to remote.")
        sys.exit(1)


if __name__ == "__main__":
    make_daily_commits()
