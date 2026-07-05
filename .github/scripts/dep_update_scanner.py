#!/usr/bin/env python3
import os
import sys
import io

if sys.platform.startswith("win"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
import json
import re
import requests


def check_pypi_version(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json().get("info", {}).get("version")
    except Exception:
        pass
    return None


def check_npm_version(package_name):
    url = f"https://registry.npmjs.org/{package_name}/latest"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json().get("version")
    except Exception:
        pass
    return None


def scan_python_requirements(file_path):
    outdated = []
    if not os.path.exists(file_path):
        return outdated

    print(f"Scanning Python requirements: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue
            # Match package==version
            match = re.match(r"^([a-zA-Z0-9_\-]+)\s*==\s*([0-9a-zA-Z\.\-]+)", line)
            if match:
                package, current_version = match.groups()
                latest_version = check_pypi_version(package)
                if latest_version and latest_version != current_version:
                    outdated.append(
                        ("Python", package, current_version, latest_version)
                    )
    return outdated


def scan_node_dependencies(file_path):
    outdated = []
    if not os.path.exists(file_path):
        return outdated

    print(f"Scanning Node dependencies: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            for package, version_spec in deps.items():
                # Extract simple version number (e.g. ^1.2.3 -> 1.2.3)
                current_version = re.sub(r"^[~^>=<]+", "", version_spec)
                latest_version = check_npm_version(package)
                if latest_version and latest_version != current_version:
                    outdated.append(("Node", package, current_version, latest_version))
        except Exception as e:
            print(f"Error reading package.json: {e}")
    return outdated


def main():
    outdated_all = []

    # Scan standard files in repository
    if os.path.exists("requirements.txt"):
        outdated_all.extend(scan_python_requirements("requirements.txt"))

    if os.path.exists("package.json"):
        outdated_all.extend(scan_node_dependencies("package.json"))

    # Walk directory to find nested configuration files (e.g. in other repos)
    for root, _, files in os.walk("."):
        if any(ignored in root for ignored in [".git", "node_modules", "__pycache__"]):
            continue
        for file in files:
            if file == "requirements.txt" and root != ".":
                outdated_all.extend(scan_python_requirements(os.path.join(root, file)))
            elif file == "package.json" and root != ".":
                outdated_all.extend(scan_node_dependencies(os.path.join(root, file)))

    print("\n" + "=" * 50)
    if outdated_all:
        print(f"⚠️ Outdated dependencies found ({len(outdated_all)}):")
        print(f"{'Type':<8} | {'Package':<25} | {'Current':<12} | {'Latest':<12}")
        print("-" * 65)
        for dtype, pkg, curr, late in outdated_all:
            print(f"{dtype:<8} | {pkg:<25} | {curr:<12} | {late:<12}")
        sys.exit(0)  # Don't crash the workflow, just report it
    else:
        print("✅ All dependencies are up to date!")
        sys.exit(0)


if __name__ == "__main__":
    main()
