#!/usr/bin/env python3
import os
import re
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
import requests

README_PATH = "README.md"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def extract_links(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Match markdown links: [text](url)
    markdown_links = re.findall(r"\[.*?\]\((https?://.*?)\)", content)

    # Match HTML links: href="url" or src="url"
    html_links = re.findall(r'(?:href|src)="((?:https?://.*?))"', content)

    # Combine and deduplicate
    all_links = sorted(list(set(markdown_links + html_links)))
    return all_links


def check_link(url):
    headers = {"User-Agent": USER_AGENT}
    try:
        # Try HEAD request first for speed, fallback to GET if HEAD is not allowed
        response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
        if response.status_code in [403, 405]:
            response = requests.get(
                url, headers=headers, timeout=10, allow_redirects=True
            )

        if response.status_code >= 400:
            return False, f"HTTP {response.status_code}"
        return True, "OK"
    except requests.exceptions.RequestException as e:
        return False, str(e)


def main():
    print(f"Extracting links from {README_PATH}...")
    links = extract_links(README_PATH)
    print(f"Found {len(links)} unique links to verify.\n")

    broken_links = []
    for idx, link in enumerate(links, 1):
        print(f"[{idx}/{len(links)}] Checking: {link} ... ", end="", flush=True)
        is_ok, status = check_link(link)
        if is_ok:
            print("🟢 OK")
        else:
            print(f"🔴 BROKEN ({status})")
            broken_links.append((link, status))

    print("\n" + "=" * 50)
    if broken_links:
        print(f"⚠️ Found {len(broken_links)} broken link(s):")
        for link, status in broken_links:
            print(f"- {link} -> {status}")
        sys.exit(1)
    else:
        print("✅ All links are valid and active!")
        sys.exit(0)


if __name__ == "__main__":
    main()
