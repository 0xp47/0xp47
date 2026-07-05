#!/usr/bin/env python3
import os
import sys
import io
import json
import requests
import zipfile
from datetime import datetime

# Configure UTF-8 encoding for Windows terminals
if sys.platform.startswith("win"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

GITHUB_USERNAME = "0xp47"
REPO_NAME = "0xp47"
BACKUPS_DIR = "backups"


def get_headers():
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def fetch_paged_data(endpoint):
    headers = get_headers()
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/{endpoint}?state=all&per_page=100"
    results = []

    while url:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            results.extend(response.json())

            # Follow pagination links
            url = None
            if "Link" in response.headers:
                parts = response.headers["Link"].split(",")
                for part in parts:
                    if 'rel="next"' in part:
                        # Extract URL inside angle brackets <url>
                        url = part.split(";")[0].strip("< >")
        except Exception as e:
            print(f"Error fetching {endpoint}: {e}")
            break

    return results


def fetch_repo_meta():
    headers = get_headers()
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}"
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error fetching repo metadata: {e}")
        return {}


def main():
    print(f"Starting metadata backup for {GITHUB_USERNAME}/{REPO_NAME}...")

    # Fetch data
    print("Fetching repository metadata...")
    repo_meta = fetch_repo_meta()

    print("Fetching issues & pull requests...")
    issues = fetch_paged_data("issues")

    print("Fetching releases...")
    releases = fetch_paged_data("releases")

    # Create backup package structures
    os.makedirs(BACKUPS_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d")
    zip_path = os.path.join(BACKUPS_DIR, f"repo_metadata_{date_str}.zip")

    print(f"Packing data into: {zip_path}")
    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr("repository.json", json.dumps(repo_meta, indent=2))
            zipf.writestr("issues_prs.json", json.dumps(issues, indent=2))
            zipf.writestr("releases.json", json.dumps(releases, indent=2))

        print(f"Backup completed successfully! Saved to {zip_path}")
    except Exception as e:
        print(f"Failed to create backup package: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
