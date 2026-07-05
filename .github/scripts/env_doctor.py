#!/usr/bin/env python3
import subprocess
import shutil
import sys

# List of tools to check, their validation command, and target/installation info
TOOLS = {
    "Git": {
        "command": ["git", "--version"],
        "info": "Required for version control.",
        "url": "https://git-scm.com/"
    },
    "Python": {
        "command": ["python", "--version"],
        "info": "Required to run automation scripts.",
        "url": "https://www.python.org/"
    },
    "Node.js": {
        "command": ["node", "--version"],
        "info": "Required for frontend frameworks and prettier formatting.",
        "url": "https://nodejs.org/"
    },
    "npm": {
        "command": ["npm", "--version"],
        "info": "Node Package Manager.",
        "url": "https://nodejs.org/"
    },
    "Docker": {
        "command": ["docker", "--version"],
        "info": "Recommended for containerized development.",
        "url": "https://www.docker.com/"
    },
    "GitHub CLI (gh)": {
        "command": ["gh", "--version"],
        "info": "Used for command-line GitHub interactions and automation.",
        "url": "https://cli.github.com/"
    }
}

def run_doctor():
    print("="*60)
    print("🏥 Ground Zero Dev Environment Doctor")
    print("Checking your local system for required tools...")
    print("="*60 + "\n")
    
    missing_count = 0
    available_count = 0
    
    for tool, specs in TOOLS.items():
        print(f"🔍 Checking {tool:.<22} ", end="")
        
        # Check if executable exists in PATH first to avoid exceptions
        cmd_base = specs["command"][0]
        if not shutil.which(cmd_base):
            print("🔴 MISSING")
            print(f"   ℹ️  {specs['info']}")
            print(f"   🔗 Download here: {specs['url']}\n")
            missing_count += 1
            continue
            
        try:
            res = subprocess.run(specs["command"], capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                # Extract first line of version info
                version = res.stdout.strip().split("\n")[0]
                print(f"🟢 FOUND ({version})")
                available_count += 1
            else:
                print("⚠️  ERROR STATUS")
                print(f"   Stderr: {res.stderr.strip()}\n")
                missing_count += 1
        except Exception as e:
            print("🔴 FAILED TO EXECUTE")
            print(f"   Details: {e}\n")
            missing_count += 1
            
    print("="*60)
    print("📋 Diagnostic Summary:")
    print(f"   🟢 Available Tools: {available_count}/{len(TOOLS)}")
    if missing_count > 0:
        print(f"   🔴 Missing/Faulty:  {missing_count}/{len(TOOLS)}")
        print("\n💡 Tip: Install the missing tools using the links above to set up a complete workspace.")
        sys.exit(1)
    else:
        print("   🎉 Everything is fully configured and ready! Happy coding!")
        sys.exit(0)

if __name__ == "__main__":
    run_doctor()
