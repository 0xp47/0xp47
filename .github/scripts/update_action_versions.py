#!/usr/bin/env python3
import os
import sys
import io
import re
import requests

# Configure UTF-8 encoding for Windows terminals
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

WORKFLOWS_DIR = ".github/workflows"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("PROFILE_GITHUB_TOKEN")


def get_headers():
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers


# Cache to avoid repetitive API queries
version_cache = {}


def fetch_latest_major_version(action_name):
    # E.g. "actions/checkout", "github/codeql-action/init"
    # Extract owner/repo
    parts = action_name.split("/")
    if len(parts) < 2:
        return None
    
    owner, repo = parts[0], parts[1]
    repo_key = f"{owner}/{repo}"
    
    if repo_key in version_cache:
        return version_cache[repo_key]
        
    print(f"Querying GitHub API for latest version of: {repo_key}...")
    headers = get_headers()
    
    # Method 1: Get latest release
    release_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    try:
        res = requests.get(release_url, headers=headers, timeout=10)
        if res.status_code == 200:
            tag_name = res.json().get("tag_name", "")
            if tag_name:
                major_version = extract_major(tag_name)
                if major_version:
                    version_cache[repo_key] = major_version
                    return major_version
    except Exception as e:
        print(f"Error checking release for {repo_key}: {e}")

    # Method 2: Get tags list (fallback)
    tags_url = f"https://api.github.com/repos/{owner}/{repo}/tags?per_page=10"
    try:
        res = requests.get(tags_url, headers=headers, timeout=10)
        if res.status_code == 200:
            tags = res.json()
            if tags:
                # Find the first tag that looks like a version
                for t in tags:
                    name = t.get("name", "")
                    major_version = extract_major(name)
                    if major_version:
                        version_cache[repo_key] = major_version
                        return major_version
    except Exception as e:
        print(f"Error checking tags for {repo_key}: {e}")

    return None


def extract_major(tag):
    # E.g. "v4.1.7" -> "v4", "v9.0.0" -> "v9", "12.3.4" -> "v12"
    # Strip leading 'v'
    tag = tag.strip()
    match = re.match(r"^v?(\d+)", tag)
    if match:
        return f"v{match.group(1)}"
    return None


def update_workflows():
    if not os.path.exists(WORKFLOWS_DIR):
        print(f"Directory {WORKFLOWS_DIR} not found.")
        return
        
    workflow_files = [
        f for f in os.listdir(WORKFLOWS_DIR)
        if f.endswith((".yml", ".yaml"))
    ]
    
    action_use_pattern = re.compile(r"(\s+uses:\s*)([a-zA-Z0-9-_]+/[a-zA-Z0-9-_/]+)@([a-zA-Z0-9-_.]+)")
    
    for filename in workflow_files:
        filepath = os.path.join(WORKFLOWS_DIR, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            modified = False
            lines = content.splitlines()
            new_lines = []
            
            for line in lines:
                match = action_use_pattern.search(line)
                if match:
                    prefix, action, current_ver = match.groups()
                    # Skip local actions (usually don't have owner/repo pattern, or start with ./ )
                    if action.startswith(("./", ".")):
                        new_lines.append(line)
                        continue
                        
                    latest_ver = fetch_latest_major_version(action)
                    if latest_ver and latest_ver != current_ver:
                        print(f"   Updating {filename}: {action}@{current_ver} -> @{latest_ver}")
                        # Reconstruct the line preserving whitespace indentation
                        new_line = action_use_pattern.sub(f"\\1\\2@{latest_ver}", line)
                        new_lines.append(new_line)
                        modified = True
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
                    
            if modified:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write("\n".join(new_lines) + "\n")
                    
        except Exception as e:
            print(f"Error processing {filepath}: {e}")


def main():
    print("🏥 Checking and upgrading all GitHub Actions in workflows to latest stable versions...")
    update_workflows()
    print("🏥 Actions update complete!")


if __name__ == "__main__":
    main()
