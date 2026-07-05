import os
import sys
import io
import re
import subprocess

# Configure UTF-8 encoding for Windows terminals
if sys.platform.startswith("win"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Regular expressions for common secret/key formats
PATTERNS = {
    "Gemini / Google API Key": re.compile(r"AIzaSy[A-Za-z0-9_-]{35}"),
    "GitHub Token": re.compile(r"gh[oprs]_[a-zA-Z0-9]{36,255}"),
    "Generic API Key / Token Assignment": re.compile(
        r"(api_key|apikey|token|password|secret|auth|private_key)\s*[:=]\s*['\"][a-zA-Z0-9_\-+=/]{16,}['\"]",
        re.IGNORECASE,
    ),
    "Discord Bot Token": re.compile(
        r"[a-zA-Z0-9_-]{24}\.[a-zA-Z0-9_-]{6}\.[a-zA-Z0-9_-]{27}"
    ),
    "Slack Webhook URL": re.compile(
        r"https://hooks\.slack\.com/services/T[a-zA-Z0-9_]+/B[a-zA-Z0-9_]+/[a-zA-Z0-9_]+"
    ),
    "Generic Private Key Header": re.compile(r"-----BEGIN [A-Z ]+ PRIVATE KEY-----"),
}


def check_head_exists():
    # Verify if HEAD exists in the repository (i.e. has at least one commit)
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        capture_output=True,
        shell=sys.platform.startswith("win"),
    )
    return result.returncode == 0


def get_staged_files():
    # Get names of files that are currently staged (ready to commit)
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        shell=sys.platform.startswith("win"),
    )
    if result.returncode != 0:
        return []

    stdout_str = result.stdout.decode("utf-8", errors="ignore")
    staged = []
    for line in stdout_str.splitlines():
        if len(line) > 3:
            # Staged status is in the first column (index 0)
            status = line[0]
            if status in ("A", "M", "R"):
                filepath = line[3:].strip()
                # Handle renamed files "old_path -> new_path"
                if " -> " in filepath:
                    filepath = filepath.split(" -> ")[-1].strip()
                # Strip potential surrounding quotes from path
                filepath = filepath.strip("\"'")
                staged.append(filepath)
    return staged


def get_staged_changes(filepath):
    # If it is a brand new repo with no commits, the staged changes are the entire file on disk
    if not check_head_exists():
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
            except Exception:
                return ""
        return ""

    # Ordinary case: get added lines compared to HEAD
    result = subprocess.run(
        ["git", "diff", "--cached", filepath],
        capture_output=True,
        shell=sys.platform.startswith("win"),
    )
    if result.returncode != 0:
        return ""

    stdout_str = result.stdout.decode("utf-8", errors="ignore")
    added_lines = []
    for line in stdout_str.splitlines():
        # Lines starting with "+" but not "+++" are additions
        if line.startswith("+") and not line.startswith("+++"):
            added_lines.append(line[1:])  # Remove the leading "+"

    return "\n".join(added_lines)


def main():
    files = get_staged_files()
    if not files:
        sys.exit(0)

    secret_detected = False

    for filepath in files:
        # Avoid scanning files that are excluded or binary assets
        if filepath.endswith(
            (".png", ".jpg", ".jpeg", ".gif", ".ico", ".zip", ".tar.gz", ".pdf", ".pyc")
        ):
            continue

        changes = get_staged_changes(filepath)
        if not changes:
            continue

        # Scan changes for each regex pattern
        for name, pattern in PATTERNS.items():
            match = pattern.search(changes)
            if match:
                print("=" * 70)
                print(f"❌ COMMIT BLOCKED: Sensitive data detected in file: {filepath}")
                print(f"⚠️  Detected Type  : {name}")
                print(f"🔍 Leaked Content  : {match.group(0)}")
                print("=" * 70)
                print(
                    "💡 Tip: Remove the credential or use environment variables before committing."
                )
                print(
                    "💡 To force the commit anyway (not recommended), run: git commit --no-verify"
                )
                print("=" * 70)
                secret_detected = True
                break

    if secret_detected:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
