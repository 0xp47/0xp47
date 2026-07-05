#!/usr/bin/env python3
import os
import sys
import io
import stat

# Configure UTF-8 encoding for Windows terminals
if sys.platform.startswith("win"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

HOOK_CONTENT = """#!/bin/sh
# Automatically scan staged changes for secrets before committing
python .github/scripts/pre_commit_scanner.py
"""


def install_hook(repo_path="."):
    git_dir = os.path.join(repo_path, ".git")
    if not os.path.isdir(git_dir):
        print(f"❌ Error: '{repo_path}' is not a valid Git repository.")
        return False

    hooks_dir = os.path.join(git_dir, "hooks")
    os.makedirs(hooks_dir, exist_ok=True)

    hook_file = os.path.join(hooks_dir, "pre-commit")

    try:
        with open(hook_file, "w", encoding="utf-8", newline="\n") as f:
            f.write(HOOK_CONTENT)

        # Make the hook executable (crucial for macOS/Linux)
        st = os.stat(hook_file)
        os.chmod(hook_file, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

        print(f"✅ Local pre-commit hook installed successfully at: {hook_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to write pre-commit hook: {e}")
        return False


def main():
    print("🏥 Installing local pre-commit hook...")
    install_hook()


if __name__ == "__main__":
    main()
