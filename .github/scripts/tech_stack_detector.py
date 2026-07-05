#!/usr/bin/env python3
import os
import sys
import io
import json
import re

if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

README_PATH = "README.md"

# Visual Badges Mapping
TECH_BADGES = {
    # Languages
    "python": ("Languages", "https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white"),
    "javascript": ("Languages", "https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black"),
    "typescript": ("Languages", "https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white"),
    "php": ("Languages", "https://img.shields.io/badge/PHP-777BB4?style=flat-square&logo=php&logoColor=white"),
    "rust": ("Languages", "https://img.shields.io/badge/Rust-000000?style=flat-square&logo=rust&logoColor=white"),
    "go": ("Languages", "https://img.shields.io/badge/Go-00ADD8?style=flat-square&logo=go&logoColor=white"),
    "bash": ("Languages", "https://img.shields.io/badge/Shell_Script-4EAA25?style=flat-square&logo=gnu-bash&logoColor=white"),
    
    # Frameworks / Libraries
    "react": ("Frameworks & Libraries", "https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB"),
    "nextjs": ("Frameworks & Libraries", "https://img.shields.io/badge/Next.js-000000?style=flat-square&logo=nextdotjs&logoColor=white"),
    "vue": ("Frameworks & Libraries", "https://img.shields.io/badge/Vue.js-35495E?style=flat-square&logo=vuedotjs&logoColor=4FC08D"),
    "laravel": ("Frameworks & Libraries", "https://img.shields.io/badge/Laravel-FF2D20?style=flat-square&logo=laravel&logoColor=white"),
    "django": ("Frameworks & Libraries", "https://img.shields.io/badge/Django-092E20?style=flat-square&logo=django&logoColor=white"),
    "flask": ("Frameworks & Libraries", "https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white"),
    "fastapi": ("Frameworks & Libraries", "https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white"),
    "express": ("Frameworks & Libraries", "https://img.shields.io/badge/Express-000000?style=flat-square&logo=express&logoColor=white"),
    
    # Databases / DevOps / Tools
    "mongodb": ("Databases & DevOps", "https://img.shields.io/badge/MongoDB-47A248?style=flat-square&logo=mongodb&logoColor=white"),
    "mysql": ("Databases & DevOps", "https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white"),
    "postgresql": ("Databases & DevOps", "https://img.shields.io/badge/PostgreSQL-316192?style=flat-square&logo=postgresql&logoColor=white"),
    "redis": ("Databases & DevOps", "https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white"),
    "firebase": ("Databases & DevOps", "https://img.shields.io/badge/Firebase-FFCA28?style=flat-square&logo=firebase&logoColor=black"),
    "supabase": ("Databases & DevOps", "https://img.shields.io/badge/Supabase-1C1C1C?style=flat-square&logo=supabase&logoColor=3ECF8E"),
    "docker": ("Databases & DevOps", "https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white"),
    "githubactions": ("Databases & DevOps", "https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat-square&logo=github-actions&logoColor=white"),
}


def detect_technologies():
    detected = set()

    # 1. Scan file extensions in workspace
    for root, _, files in os.walk("."):
        # Exclude directories by checking exact path components
        path_parts = re.split(r"[\\/]", root)
        if any(
            exc in path_parts
            for exc in [".git", "node_modules", "__pycache__", ".gemini", "dotfiles"]
        ):
            continue
            
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext == ".py":
                detected.add("python")
            elif ext in [".js", ".jsx"]:
                detected.add("javascript")
            elif ext in [".ts", ".tsx"]:
                detected.add("typescript")
            elif ext == ".php":
                detected.add("php")
            elif ext == ".rs":
                detected.add("rust")
            elif ext == ".go":
                detected.add("go")
            elif ext in [".sh", ".ps1"]:
                detected.add("bash")
            elif file.lower() == "dockerfile" or file.startswith("docker-compose"):
                detected.add("docker")

    # 2. Scan package.json for frameworks
    if os.path.exists("package.json"):
        try:
            with open("package.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            if "react" in deps:
                detected.add("react")
            if "next" in deps:
                detected.add("nextjs")
            if "vue" in deps:
                detected.add("vue")
            if "express" in deps:
                detected.add("express")
        except Exception:
            pass

    # 3. Scan requirements.txt for python frameworks
    if os.path.exists("requirements.txt"):
        try:
            with open("requirements.txt", "r", encoding="utf-8") as f:
                content = f.read().lower()
            if "django" in content:
                detected.add("django")
            if "flask" in content:
                detected.add("flask")
            if "fastapi" in content:
                detected.add("fastapi")
            if "redis" in content:
                detected.add("redis")
            if "pymongo" in content:
                detected.add("mongodb")
            if "psycopg2" in content or "postgresql" in content:
                detected.add("postgresql")
            if "mysql-connector" in content or "mysqlclient" in content:
                detected.add("mysql")
        except Exception:
            pass

    # 4. Check for GitHub Actions workflow directory
    if os.path.exists(".github/workflows"):
        detected.add("githubactions")

    # 5. Let's make sure that if a framework is detected, its base language is also added
    if "nextjs" in detected or "react" in detected or "express" in detected:
        if "typescript" not in detected:
            detected.add("javascript")
    if "django" in detected or "flask" in detected or "fastapi" in detected:
        detected.add("python")
    if "laravel" in detected:
        detected.add("php")

    return list(detected)


def build_markdown_badges(detected_techs):
    # Group detected tech by categories
    groups = {
        "Languages": [],
        "Frameworks & Libraries": [],
        "Databases & DevOps": []
    }

    for tech in sorted(detected_techs):
        if tech in TECH_BADGES:
            category, badge_url = TECH_BADGES[tech]
            name_display = tech.capitalize()
            if tech == "nextjs":
                name_display = "Next.js"
            elif tech == "fastapi":
                name_display = "FastAPI"
            elif tech == "githubactions":
                name_display = "GitHub Actions"
            elif tech == "mongodb":
                name_display = "MongoDB"
            elif tech == "postgresql":
                name_display = "PostgreSQL"
                
            groups[category].append(f'<img src="{badge_url}" alt="{name_display}" valign="middle" height="20">')

    # Construct the markdown string
    markdown_lines = []
    for category, badges in groups.items():
        if badges:
            badges_line = " ".join(badges)
            markdown_lines.append(f"**{category}**\n\n{badges_line}\n")

    return "\n".join(markdown_lines).strip()


def patch_readme(badges_md):
    if not os.path.exists(README_PATH):
        print(f"Error: README.md not found at {README_PATH}")
        sys.exit(1)

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    start_tag = "<!-- TECH_STACK:START -->"
    end_tag = "<!-- TECH_STACK:END -->"

    pattern = re.compile(
        rf"{re.escape(start_tag)}.*?{re.escape(end_tag)}",
        re.DOTALL
    )

    replacement = f"{start_tag}\n{badges_md}\n{end_tag}"

    if pattern.search(content):
        new_content = pattern.sub(replacement, content)
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("README.md successfully updated with tech stack badges!")
    else:
        print("Error: Tech stack comment tags not found in README.md.")
        print("Make sure you add '<!-- TECH_STACK:START -->' and '<!-- TECH_STACK:END -->' to your README.md.")
        sys.exit(1)


def main():
    print("Scanning repository for active technologies...")
    detected = detect_technologies()
    print(f"Detected technologies: {', '.join(detected)}")
    
    badges_md = build_markdown_badges(detected)
    patch_readme(badges_md)


if __name__ == "__main__":
    main()
