#!/usr/bin/env python3
import os
import sys
import io
import shutil
import stat
import subprocess

# Configure UTF-8 encoding for Windows terminals
if sys.platform.startswith("win"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

USER_HOME = os.path.expanduser("~")
GLOBAL_TEMPLATE_DIR = os.path.join(USER_HOME, ".git_templates")
GLOBAL_HOOKS_DIR = os.path.join(GLOBAL_TEMPLATE_DIR, "hooks")

# Use forward slashes to avoid path escaping issues in git hooks on Windows
SCANNER_PATH = "C:/Users/0xp47/.git_templates/pre_commit_scanner.py"

HOOK_CONTENT = f"""#!/bin/sh
# Globally scan staged changes for secrets before committing
python "{SCANNER_PATH}"
"""


def setup_global_hook():
    print("🏥 Starting Global Git Hook Configuration...")
    os.makedirs(GLOBAL_HOOKS_DIR, exist_ok=True)

    # 1. Copy pre_commit_scanner.py to global folder
    src_scanner = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "scripts",
        "pre_commit_scanner.py",
    )
    dest_scanner = os.path.join(GLOBAL_TEMPLATE_DIR, "pre_commit_scanner.py")

    try:
        shutil.copy2(src_scanner, dest_scanner)
        print(f"   ✅ Copied pre-commit scanner globally: {dest_scanner}")
    except Exception as e:
        print(f"   ❌ Failed to copy pre-commit scanner globally: {e}")
        return

    # 2. Write pre-commit hook file in global templates
    hook_file = os.path.join(GLOBAL_HOOKS_DIR, "pre-commit")
    try:
        with open(hook_file, "w", encoding="utf-8", newline="\n") as f:
            f.write(HOOK_CONTENT)

        # Make executable
        st = os.stat(hook_file)
        os.chmod(hook_file, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        print(f"   ✅ Created global pre-commit hook file: {hook_file}")
    except Exception as e:
        print(f"   ❌ Failed to write global pre-commit hook: {e}")
        return

    # 3. Configure Git globally
    git_template_path = GLOBAL_TEMPLATE_DIR.replace("\\", "/")
    result = subprocess.run(
        ["git", "config", "--global", "init.templateDir", git_template_path],
        capture_output=True,
        text=True,
        shell=sys.platform.startswith("win"),
    )
    if result.returncode == 0:
        print(f"   ✅ Configured git global init.templateDir to: {git_template_path}")
        print(
            "\n🎉 Success! Every new local git repository you create in the future will automatically have this hook configured."
        )
    else:
        print(f"   ❌ Failed to configure git templateDir globally: {result.stderr}")


if __name__ == "__main__":
    setup_global_hook()
