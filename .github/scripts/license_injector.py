#!/usr/bin/env python3
import os
import sys
import argparse
import time

LICENSE_TEMPLATES = {
    "mit": """Copyright (c) {year} {holder}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.""",

    "apache2": """Copyright {year} {holder}

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.""",

    "gpl3": """Copyright (C) {year} {holder}

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details."""
}

COMMENT_STYLES = {
    ".py": ("#", "# ", "#"),
    ".sh": ("#", "# ", "#"),
    ".js": ("/*", " * ", " */"),
    ".ts": ("/*", " * ", " */"),
    ".cs": ("/*", " * ", " */"),
    ".java": ("/*", " * ", " */"),
    ".cpp": ("/*", " * ", " */"),
    ".h": ("/*", " * ", " */"),
    ".php": ("/*", " * ", " */"),
    ".css": ("/*", " * ", " */"),
}

def format_license_comment(ext, license_text):
    start, middle, end = COMMENT_STYLES[ext]
    lines = license_text.strip().split("\n")
    
    comment_lines = []
    if start:
        comment_lines.append(start)
    for line in lines:
        if line.strip():
            comment_lines.append(f"{middle}{line}")
        else:
            # Avoid trailing spaces on empty comment lines
            comment_lines.append(middle.rstrip())
    if end:
        comment_lines.append(end)
        
    return "\n".join(comment_lines) + "\n\n"

def inject_license(file_path, license_text, dry_run=False):
    _, ext = os.path.splitext(file_path)
    if ext not in COMMENT_STYLES:
        return False
        
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    # Check if license is already injected (check if holder name is in the first 500 chars)
    # or if copyright string is already present.
    first_block = content[:500].lower()
    if "copyright" in first_block and ("mit license" in first_block or "apache" in first_block or "gpl" in first_block):
        print(f"   ℹ️  Skipping (header already present): {file_path}")
        return False
        
    license_comment = format_license_comment(ext, license_text)
    
    # Handle shebangs or PHP opening tag (e.g. #!/usr/bin/env python or <?php)
    header_offset = 0
    shebang = ""
    lines = content.splitlines(keepends=True)
    
    if lines:
        first_line = lines[0]
        if first_line.startswith("#!"):
            shebang = first_line + "\n"
            header_offset = len(first_line)
        elif first_line.startswith("<?php"):
            shebang = first_line + "\n"
            header_offset = len(first_line)
            
    new_content = shebang + license_comment + content[header_offset:]
    
    if not dry_run:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"   🟢 Injected: {file_path}")
    else:
        print(f"   🟡 (Dry-run) Would inject: {file_path}")
        
    return True

def main():
    parser = argparse.ArgumentParser(description="Inject Open Source license headers into code files.")
    parser.add_argument("--dir", default=".", help="Directory to scan (default: current)")
    parser.add_argument("--license", default="mit", choices=["mit", "apache2", "gpl3"], help="License type (default: mit)")
    parser.add_argument("--holder", required=True, help="Copyright holder name (e.g. 'Jay Patrick Cano')")
    parser.add_argument("--year", default=str(time.localtime().tm_year), help="Copyright year (default: current year)")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without modifying files")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.dir):
        print(f"Error: Directory '{args.dir}' does not exist.")
        sys.exit(1)
        
    template = LICENSE_TEMPLATES[args.license]
    license_text = template.format(year=args.year, holder=args.holder)
    
    print("="*60)
    print(f"📝 Injecting {args.license.upper()} License Header")
    print(f"   Holder: {args.holder} © {args.year}")
    print(f"   Target Directory: {args.dir}")
    print("="*60 + "\n")
    
    injected_count = 0
    scanned_count = 0
    
    for root, _, files in os.walk(args.dir):
        # Skip git folders and external deps
        if any(ignored in root for ignored in [".git", "node_modules", "venv", "__pycache__"]):
            continue
            
        for file in files:
            _, ext = os.path.splitext(file)
            if ext in COMMENT_STYLES:
                scanned_count += 1
                full_path = os.path.join(root, file)
                if inject_license(full_path, license_text, args.dry_run):
                    injected_count += 1
                    
    print("\n" + "="*60)
    print(f"Summary:")
    print(f"   Files Scanned:   {scanned_count}")
    print(f"   Headers Injected: {injected_count}")
    print("="*60)

if __name__ == "__main__":
    main()
