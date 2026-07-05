#!/usr/bin/env python3
import os
import sys
import io
import shutil

# Configure UTF-8 encoding for Windows terminals
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

SOURCE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Path to current .github folder


def copy_config_to_repo(dest_repo_path):
    dest_repo_path = os.path.abspath(dest_repo_path)
    
    # Check if target directory is a Git repository
    git_dir = os.path.join(dest_repo_path, ".git")
    if not os.path.isdir(git_dir):
        print(f"❌ Error: '{dest_repo_path}' is not a valid Git repository (missing .git directory).")
        return False
        
    dest_github_dir = os.path.join(dest_repo_path, ".github")
    print(f"⚙️  Propagating configurations to: {dest_repo_path}...")
    
    # Define files/directories to copy
    items_to_copy = [
        os.path.join("workflows", "gitleaks.yml"),
        os.path.join("workflows", "codeql.yml"),
        os.path.join("workflows", "pr_linter_labeler.yml"),
        os.path.join("workflows", "todo_issue_creator.yml"),
        "labeler.yml",
        "dependabot.yml",
        "ISSUE_TEMPLATE",
    ]
    
    success_count = 0
    for item in items_to_copy:
        src_path = os.path.join(SOURCE_DIR, item)
        dest_path = os.path.join(dest_github_dir, item)
        
        if not os.path.exists(src_path):
            continue
            
        try:
            # Ensure target parent directory exists
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            if os.path.isdir(src_path):
                # Copy directory
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                shutil.copytree(src_path, dest_path)
            else:
                # Copy file
                shutil.copy2(src_path, dest_path)
            
            print(f"   ✅ Copied: .github/{item}")
            success_count += 1
        except Exception as e:
            print(f"   ❌ Failed to copy .github/{item}: {e}")
            
    print(f"🎉 Configuration propagation complete! Successfully copied {success_count} files/folders.\n")
    return True


def scan_and_propagate_sibling_repos():
    # Look at parent directory of the current repository (usually Desktop or work folder)
    parent_dir = os.path.dirname(os.path.dirname(SOURCE_DIR))
    print(f"🔍 Scanning parent directory for sibling repositories: {parent_dir}...")
    
    siblings = []
    try:
        for entry in os.listdir(parent_dir):
            full_path = os.path.join(parent_dir, entry)
            # Avoid copying to ourselves
            if full_path == os.path.dirname(SOURCE_DIR):
                continue
            if os.path.isdir(full_path) and os.path.isdir(os.path.join(full_path, ".git")):
                siblings.append(full_path)
    except Exception as e:
        print(f"❌ Error scanning parent directory: {e}")
        return
        
    if not siblings:
        print("ℹ️  No other local Git repositories found in the sibling folder.")
        return
        
    print(f"Found {len(siblings)} sibling Git repository folders:")
    for idx, path in enumerate(siblings):
        print(f"  [{idx + 1}] {os.path.basename(path)} ({path})")
        
    print("\n👉 To copy configuration to a specific repository, enter its number (e.g. 1), or 'all' to copy to all, or 'q' to quit:")
    choice = input("Enter option: ").strip().lower()
    
    if choice == "q" or not choice:
        print("Cancelled.")
        return
    elif choice == "all":
        confirm = input("Are you sure you want to copy to ALL sibling repositories? (y/n): ").strip().lower()
        if confirm == "y":
            for path in siblings:
                copy_config_to_repo(path)
    else:
        try:
            val = int(choice)
            if 1 <= val <= len(siblings):
                copy_config_to_repo(siblings[val - 1])
            else:
                print("❌ Invalid number option.")
        except ValueError:
            print("❌ Invalid input option.")


def main():
    print("=" * 60)
    print("📋  GitHub Workflow & Config Propagation Utility")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # User supplied a path as command argument
        target_path = sys.argv[1]
        copy_config_to_repo(target_path)
    else:
        # Interactive mode scanning sibling directories
        scan_and_propagate_sibling_repos()


if __name__ == "__main__":
    main()
