#!/usr/bin/env python3
import os
import sys
import re
import requests
import html

TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"

def translate_text(text, source_lang="en", target_lang="tl"):
    if not text.strip():
        return text
        
    params = {
        "client": "gtx",
        "sl": source_lang,
        "tl": target_lang,
        "dt": "t",
        "q": text
    }
    
    try:
        res = requests.get(TRANSLATE_URL, params=params, timeout=10)
        if res.status_code == 200:
            result = res.json()
            translated_segments = []
            for segment in result[0]:
                if segment[0]:
                    translated_segments.append(segment[0])
            return "".join(translated_segments)
    except Exception as e:
        print(f"Translation API error: {e}")
        
    return text

def translate_markdown(content, target_lang="tl"):
    lines = content.splitlines(keepends=True)
    translated_lines = []
    
    in_code_block = False
    
    for line in lines:
        stripped = line.strip()
        
        # 1. Code blocks check
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            translated_lines.append(line)
            continue
            
        if in_code_block:
            translated_lines.append(line)
            continue
            
        # 2. Skip translating markup metadata comments, empty lines, HTML boundaries
        if not stripped or stripped.startswith("<!--") or stripped.startswith("<div") or stripped.startswith("</div") or stripped.startswith("<img") or stripped.startswith("</a>") or stripped.startswith("<a "):
            translated_lines.append(line)
            continue
            
        # 3. For headers, preserve markdown headers
        header_match = re.match(r'^(#+)\s+(.*)', stripped)
        if header_match:
            hashes, title = header_match.groups()
            translated_title = translate_text(title, target_lang=target_lang)
            translated_lines.append(f"{hashes} {translated_title}\n")
            continue
            
        # 4. For bullet points
        bullet_match = re.match(r'^([\*\-\+])\s+(.*)', stripped)
        if bullet_match:
            bullet, text = bullet_match.groups()
            translated_text = translate_text(text, target_lang=target_lang)
            translated_lines.append(f"{bullet} {translated_text}\n")
            continue
            
        # 5. Regular paragraph line
        translated_line = translate_text(stripped, target_lang=target_lang)
        # Restore line ending
        translated_lines.append(translated_line + "\n")
        
    return "".join(translated_lines)

def main():
    src_file = "README.md"
    dest_file = "README.fil.md"
    
    if not os.path.exists(src_file):
        print(f"Error: Source file '{src_file}' not found.")
        sys.exit(1)
        
    print(f"Reading {src_file}...")
    with open(src_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    print("Translating to Filipino (Tagalog)... This might take a few moments.")
    translated_content = translate_markdown(content, target_lang="tl")
    
    # Prepend translation warning header
    warning_header = """<!-- AUTOMATICALLY GENERATED FILE - DO NOT EDIT MANUALLY -->
> [!NOTE]
> Ito ay isang awtomatikong salin ng [README.md](README.md) sa Wikang Filipino.

---

"""
    final_output = warning_header + translated_content
    
    print(f"Saving translation to {dest_file}...")
    with open(dest_file, "w", encoding="utf-8") as f:
        f.write(final_output)
        
    print("Translation complete!")

if __name__ == "__main__":
    main()
