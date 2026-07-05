#!/usr/bin/env python3
import os
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
import re
import requests


def find_markdown_files():
    md_files = []
    for root, _, files in os.walk("."):
        # Skip git and system dirs
        if any(ignored in root for ignored in [".git", "__pycache__", ".github"]):
            continue
        for file in files:
            if file.endswith(".md"):
                md_files.append(os.path.join(root, file))
    return md_files


def extract_assets(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Match markdown images: ![alt](url)
    md_images = re.findall(r"!\[.*?\]\((.*?)\)", content)
    # Match HTML images: <img src="url" ...> or src='url'
    html_images = re.findall(r'<img.*?src=["\'](.*?)["\']', content, re.IGNORECASE)

    return list(set(md_images + html_images))


def check_asset(asset_url, base_dir):
    # If it's a web URL
    if asset_url.startswith("http://") or asset_url.startswith("https://"):
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        try:
            res = requests.head(
                asset_url, headers=headers, timeout=5, allow_redirects=True
            )
            if res.status_code in [403, 405]:
                res = requests.get(
                    asset_url, headers=headers, timeout=5, allow_redirects=True
                )
            if res.status_code >= 400:
                return False, f"HTTP {res.status_code}"
            return True, "OK"
        except Exception as e:
            return False, str(e)

    # If it's a local file relative to base_dir or repo root
    else:
        # Strip query parameters or anchors if any (e.g. image.png?raw=true)
        clean_path = asset_url.split("?")[0].split("#")[0]

        # Resolve path
        path_choices = [
            os.path.abspath(os.path.join(base_dir, clean_path)),
            os.path.abspath(clean_path),
        ]

        for p in path_choices:
            if os.path.exists(p) and os.path.isfile(p):
                return True, "Local File"

        return False, "File not found locally"


def main():
    md_files = find_markdown_files()
    print(f"Auditing assets in {len(md_files)} markdown files...")

    broken_count = 0
    for md_file in md_files:
        base_dir = os.path.dirname(md_file)
        assets = extract_assets(md_file)
        if not assets:
            continue

        print(f"\nScanning: {md_file}")
        for asset in assets:
            # Skip anchor/empty refs
            if not asset.strip() or asset.startswith("#"):
                continue

            is_ok, msg = check_asset(asset, base_dir)
            if is_ok:
                print(f"  🟢 {asset} -> {msg}")
            else:
                print(f"  🔴 {asset} -> BROKEN: {msg}")
                broken_count += 1

    print("\n" + "=" * 50)
    if broken_count > 0:
        print(f"❌ Completed. Found {broken_count} broken asset(s).")
        sys.exit(1)
    else:
        print("✅ Completed. All assets are verified and healthy!")
        sys.exit(0)


if __name__ == "__main__":
    main()
