"""
setup.py — One-click setup for Job AI Agent FREE
Run this first: python setup.py
"""
import subprocess
import sys
import shutil
from pathlib import Path


def run(cmd, label):
    print(f"  >>> {label}")
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ⚠️  Warning: {r.stderr.strip()[:150]}")
    else:
        print("  ✅ Done")


def main():
    print("\n" + "=" * 55)
    print("  JOB AI AGENT FREE — SETUP")
    print("=" * 55 + "\n")

    # Create folders
    for folder in ["assets", "logs", "agents", "db", "api", "frontend"]:
        Path(folder).mkdir(exist_ok=True)
    print("✅ Folders created\n")

    # Create .env
    if not Path(".env").exists():
        if Path(".env.example").exists():
            shutil.copy(".env.example", ".env")
            print("✅ .env file created from template")
        else:
            Path(".env").write_text(
                "GROQ_API_KEY=your_groq_api_key_here\n"
                "GMAIL_ADDRESS=your@gmail.com\n"
                "GMAIL_APP_PASSWORD=xxxxxxxxxxxxxxxx\n"
                "CV_PATH=./assets/YourName_CV.pdf\n"
            )
            print("✅ .env file created")
    else:
        print("✅ .env already exists")

    # Create __init__.py files
    for pkg in ["agents", "db", "api"]:
        init = Path(pkg) / "__init__.py"
        if not init.exists():
            init.touch()
    print("✅ Package structure ready\n")

    # Install packages
    run(f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python packages...")

    print("\n" + "=" * 55)
    print("  SETUP COMPLETE!")
    print("=" * 55)
    print("""
BEFORE YOU RUN THE BOT — do these 3 things:

1. Open .env and fill in:
     GROQ_API_KEY      → free key from console.groq.com
     GMAIL_ADDRESS     → your Gmail address
     GMAIL_APP_PASSWORD→ from myaccount.google.com/apppasswords
     CV_PATH           → path to your CV PDF

2. Copy your CV PDF into the assets/ folder

3. Open config.py and update your name, skills, and experience

THEN RUN:
  python main.py server      ← launches web dashboard (easiest)
  python main.py run         ← full cycle from terminal
  python main.py scrape      ← just find jobs
  python main.py dashboard   ← check your stats
""")


if __name__ == "__main__":
    main()
