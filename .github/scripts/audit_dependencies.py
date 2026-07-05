#!/usr/bin/env python3
import os
import sys
import io
import re
import requests

# Configure UTF-8 encoding for Windows terminals
if sys.platform.startswith("win"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

REQUIREMENTS_FILE = "requirements.txt"
COMPLIANCE_REPORT = "stats/compliance_report.md"

# Licenses that are copyleft/high-risk for commercial or restricted projects
RESTRICTED_LICENSES = ["agpl", "gpl", "lgpl"]
APPROVED_LICENSES = ["mit", "apache", "bsd", "psf", "isc", "unlicense", "cc0"]


def create_default_requirements():
    default_packages = ["requests>=2.31.0\n", "discord.py>=2.3.2\n", "PyYAML>=6.0.1\n"]
    with open(REQUIREMENTS_FILE, "w", encoding="utf-8") as f:
        f.writelines(default_packages)
    print(f"Created default {REQUIREMENTS_FILE}")


def fetch_package_license(package_name):
    # Fetch license info from PyPI API
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            info = res.json().get("info", {})
            license_str = info.get("license") or ""
            classifiers = info.get("classifiers") or []

            # Extract from license string
            license_name = license_str.strip().lower()

            # Fallback to classifiers if license string is empty/generic
            if not license_name or "license" in license_name:
                for c in classifiers:
                    if "license ::" in c.lower():
                        parts = c.split("::")
                        if len(parts) > 1:
                            license_name = parts[-1].strip().lower()
                            break

            return license_name
    except Exception as e:
        print(f"   ⚠️  Could not fetch PyPI data for {package_name}: {e}")
    return "unknown"


def audit_dependencies():
    if not os.path.exists(REQUIREMENTS_FILE):
        create_default_requirements()

    print(f"🏥 Auditing dependencies listed in {REQUIREMENTS_FILE}...")

    packages = []
    # Parse requirements.txt
    with open(REQUIREMENTS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Extract package name (remove version constraints like ==, >=, <=)
            match = re.match(r"^([a-zA-Z0-9-_.]+)", line)
            if match:
                packages.append(match.group(1))

    report_lines = [
        "# 🛡️ Dependency License & Compliance Report",
        f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%SZ')}\n",
        "| Package | Detected License | Compliance Status | Action Required |",
        "| --- | --- | --- | --- |",
    ]

    warnings_found = 0

    for pkg in packages:
        print(f" - Auditing: {pkg}")
        pkg_license = fetch_package_license(pkg)

        status = "✅ Approved"
        action = "None"

        # Check copyleft risk
        if any(lic in pkg_license for lic in RESTRICTED_LICENSES):
            status = "⚠️ Copyleft Warning"
            action = (
                "Verify usage; copyleft licenses may require open-sourcing child code."
            )
            warnings_found += 1
        elif "unknown" in pkg_license:
            status = "❓ Unknown License"
            action = "Audit license metadata manually."
            warnings_found += 1

        report_lines.append(
            f"| `{pkg}` | {pkg_license.upper()} | {status} | {action} |"
        )

    os.makedirs(os.path.dirname(COMPLIANCE_REPORT), exist_ok=True)
    with open(COMPLIANCE_REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")

    print(f"Compliance report saved to {COMPLIANCE_REPORT}")
    return warnings_found


if __name__ == "__main__":
    from datetime import datetime

    warnings = audit_dependencies()
    if warnings > 0:
        print(f"🏥 Audit complete with {warnings} warnings.")
    else:
        print("🏥 Audit complete! All dependencies are compliant.")
