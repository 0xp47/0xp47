#!/usr/bin/env python3
import subprocess
import time
import sys
import io

if sys.platform.startswith("win"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
import os
import random

# File to commit dummy changes to
PROGRESS_FILE = "achievements/pull-shark-progress.md"


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
        return False, result.stdout, result.stderr
    return True, result.stdout, result.stderr


def check_requirements():
    # Verify git is configured
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

    # Check if gh CLI is installed
    success, _, _ = run_cmd(["gh", "--version"])
    if not success:
        print("Error: GitHub CLI ('gh') is not installed or not in PATH.")
        sys.exit(1)


def farm_one_pr(pr_number):
    branch_name = f"farm-pr-{pr_number}-{random.randint(1000, 9999)}"
    print(f"\n--- Starting PR #{pr_number} on branch '{branch_name}' ---")

    # 1. Checkout main and pull latest changes
    success, _, _ = run_cmd(["git", "checkout", "main"])
    if not success:
        return False
    success, _, _ = run_cmd(["git", "pull", "origin", "main"])
    if not success:
        return False

    # 2. Create and checkout new branch
    success, _, _ = run_cmd(["git", "checkout", "-b", branch_name])
    if not success:
        return False

    # 3. Append progress to achievements file
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    entry = f"pr-farm-{pr_number} {timestamp}\n"
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    with open(PROGRESS_FILE, "a") as f:
        f.write(entry)

    # 4. Commit change
    success, _, _ = run_cmd(["git", "add", PROGRESS_FILE])
    if not success:
        return False
    commit_msg = (
        f"achievement(farm): add pr-{pr_number} progress entry [skip ci]\n\n"
        f"Co-authored-by: 0xp47 <0xp47.dev@gmail.com>"
    )
    success, _, _ = run_cmd(["git", "commit", "-m", commit_msg])
    if not success:
        return False

    # 5. Push branch
    success, _, _ = run_cmd(["git", "push", "origin", branch_name])
    if not success:
        return False

    # 6. Create PR using GitHub CLI
    # Use -B main to ensure it targets main branch
    success, stdout, stderr = run_cmd(
        [
            "gh",
            "pr",
            "create",
            "--title",
            f"chore(farm): merge pr-{pr_number} progress tracking",
            "--body",
            f"Automated progress commit for pull request #{pr_number}.",
            "--head",
            branch_name,
            "--base",
            "main",
        ]
    )
    if not success:
        print("❌ Failed to create PR.")
        if (
            "not allowed" in stderr.lower()
            or "permission" in stderr.lower()
            or "403" in stderr
        ):
            print(
                "\n💡 TIP: GitHub Actions is likely not allowed to create pull requests."
            )
            print(
                "To fix this, go to your repository Settings -> Actions -> General -> 'Workflow permissions' and check 'Allow GitHub Actions to create and approve pull requests'.\n"
            )
        return False

    # Extract PR URL from output
    pr_url = stdout.strip()
    print(f"Created PR: {pr_url}")

    # Sleep briefly to let GitHub process the PR
    time.sleep(2)

    # 7. Merge PR using GitHub CLI
    success, _, stderr = run_cmd(
        ["gh", "pr", "merge", pr_url, "--merge", "--delete-branch"]
    )
    if not success:
        print("Trying fallback admin merge...")
        success, _, stderr = run_cmd(
            ["gh", "pr", "merge", pr_url, "--admin", "--merge", "--delete-branch"]
        )

    if success:
        print(f"Successfully merged PR #{pr_number}!")
        return True
    else:
        print(f"Failed to merge PR #{pr_number}.")
        if (
            "not allowed" in stderr.lower()
            or "permission" in stderr.lower()
            or "403" in stderr
        ):
            print(
                "\n💡 TIP: GitHub Actions is likely not allowed to merge pull requests."
            )
            print(
                "To fix this, go to your repository Settings -> Actions -> General -> 'Workflow permissions' and check 'Allow GitHub Actions to create and approve pull requests'.\n"
            )
        return False


def farm_quickdraw():
    print("\n--- Farming Quickdraw Achievement ---")
    # 1. Create a dummy issue using GitHub CLI
    success, stdout, _ = run_cmd(
        [
            "gh",
            "issue",
            "create",
            "--title",
            "chore(farm): temporary quickdraw milestone",
            "--body",
            "This issue is automatically created to farm the Quickdraw achievement and will be closed immediately.",
        ]
    )
    if not success:
        print("Failed to create issue for Quickdraw.")
        return False

    # Extract issue URL or number from stdout
    issue_url = stdout.strip()
    print(f"Created Issue: {issue_url}")

    # 2. Close the issue immediately
    success, _, _ = run_cmd(["gh", "issue", "close", issue_url])
    if success:
        print("Successfully closed issue immediately! Quickdraw achievement unlocked.")
        return True
    else:
        print("Failed to close issue.")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python farm_achievements.py <count>")
        sys.exit(1)

    try:
        count = int(sys.argv[1])
    except ValueError:
        print("Error: Count must be an integer.")
        sys.exit(1)

    check_requirements()

    success_count = 0
    for i in range(1, count + 1):
        if farm_one_pr(i):
            success_count += 1
            # Sleep between PRs to avoid triggering GitHub abuse limits
            time.sleep(3)
        else:
            print(f"Aborting farming loop due to failure at step {i}.")
            break

    print(
        f"\nFarming complete. Successfully merged {success_count}/{count} pull requests."
    )

    # Automatically run Quickdraw farming step
    quickdraw_success = farm_quickdraw()

    if success_count < count:
        print(
            "\n❌ Error: Some pull requests failed to be created/merged. Check warnings above."
        )
        sys.exit(1)

    if not quickdraw_success:
        print("\n❌ Error: Quickdraw achievement farming step failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
