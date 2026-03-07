import subprocess
import sys
from pathlib import Path

GITHUB_OWNER = "gosuwachu"
GITHUB_REPO = "mobile-app"
APP_REPO_URL = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}.git"
APP_DIR = Path("app")


def checkout_app(sha, token):
    if APP_DIR.exists():
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=APP_DIR,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip() == sha:
            print(f"App repo already at {sha}", file=sys.stderr)
            return
        print(f"Checking out {sha}...", file=sys.stderr)
        subprocess.run(["git", "fetch", "origin"], check=True, cwd=APP_DIR)
        subprocess.run(["git", "checkout", "-f", sha], check=True, cwd=APP_DIR)
    else:
        clone_url = APP_REPO_URL.replace(
            "https://", f"https://x-access-token:{token}@"
        )
        print(f"Cloning app repo at {sha}...", file=sys.stderr)
        subprocess.run(["git", "clone", clone_url, str(APP_DIR)], check=True)
        subprocess.run(["git", "checkout", "-f", sha], check=True, cwd=APP_DIR)
