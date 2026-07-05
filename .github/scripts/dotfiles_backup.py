#!/usr/bin/env python3
import os
import sys
import shutil
import platform
import subprocess

DOTFILES_DIR = "dotfiles"


def run_cmd(args):
    try:
        res = subprocess.run(args, capture_output=True, text=True, timeout=10)
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return None


def backup_vscode():
    print("📦 Backing up VS Code configs...")
    os.makedirs(os.path.join(DOTFILES_DIR, "vscode"), exist_ok=True)

    # 1. Backup extensions list
    extensions = run_cmd(["code", "--list-extensions"])
    if extensions:
        with open(
            os.path.join(DOTFILES_DIR, "vscode", "extensions.txt"),
            "w",
            encoding="utf-8",
        ) as f:
            f.write(extensions)
        print("   ✅ VS Code extensions list backed up.")
    else:
        print("   ⚠️  VS Code CLI ('code') not found or returned empty extension list.")

    # 2. Find settings path based on OS
    system = platform.system()
    settings_src = None

    if system == "Windows":
        appdata = os.environ.get("APPDATA")
        if appdata:
            settings_src = os.path.join(appdata, "Code", "User")
    elif system == "Darwin":  # macOS
        settings_src = os.path.expanduser("~/Library/Application Support/Code/User")
    elif system == "Linux":
        settings_src = os.path.expanduser("~/.config/Code/User")

    if settings_src and os.path.exists(settings_src):
        for file in ["settings.json", "keybindings.json"]:
            src = os.path.join(settings_src, file)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(DOTFILES_DIR, "vscode", file))
                print(f"   ✅ VS Code {file} backed up.")
    else:
        print("   ⚠️  VS Code configuration folder not found.")


def backup_shell_configs():
    print("🐚 Backing up shell profiles...")
    os.makedirs(os.path.join(DOTFILES_DIR, "shell"), exist_ok=True)
    system = platform.system()

    # 1. Linux/macOS Shell Profiles
    if system in ["Linux", "Darwin"]:
        for file in [".bashrc", ".zshrc", ".bash_profile", ".profile", ".gitconfig"]:
            path = os.path.expanduser(f"~/{file}")
            if os.path.exists(path):
                shutil.copy2(
                    path, os.path.join(DOTFILES_DIR, "shell", file.replace(".", ""))
                )
                print(f"   ✅ Shell profile {file} backed up.")

    # 2. Windows PowerShell Profiles
    elif system == "Windows":
        # Check standard Git config
        gitconfig = os.path.expanduser("~/.gitconfig")
        if os.path.exists(gitconfig):
            shutil.copy2(gitconfig, os.path.join(DOTFILES_DIR, "shell", "gitconfig"))
            print("   ✅ Git configuration (.gitconfig) backed up.")

        # Try retrieving PowerShell Profile path via shell command
        ps_profile = run_cmd(["powershell", "-NoProfile", "-Command", "$PROFILE"])
        if ps_profile and os.path.exists(ps_profile):
            shutil.copy2(
                ps_profile,
                os.path.join(DOTFILES_DIR, "shell", "Microsoft.PowerShell_profile.ps1"),
            )
            print("   ✅ PowerShell Profile backed up.")


def main():
    print("=" * 60)
    print("🗂️  Ground Zero Dotfiles Backup Manager")
    print("Starting backup of your system configurations...")
    print("=" * 60 + "\n")

    os.makedirs(DOTFILES_DIR, exist_ok=True)

    backup_shell_configs()
    print()
    backup_vscode()

    print("\n" + "=" * 60)
    print("🎉 Backup complete! All configuration assets saved to 'dotfiles/'.")
    print("   Review the files and commit them to your repository to save them online.")
    print("=" * 60)


if __name__ == "__main__":
    main()
