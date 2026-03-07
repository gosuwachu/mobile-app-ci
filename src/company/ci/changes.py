import json
import subprocess
import sys

from company.ci.checkout import APP_REPO_URL


def detect_changes(target_branch, token):
    auth_url = APP_REPO_URL.replace(
        "https://", f"https://x-access-token:{token}@"
    )
    print(f"Fetching {target_branch} for diff...", file=sys.stderr)
    subprocess.run(
        [
            "git", "fetch", auth_url,
            f"{target_branch}:refs/remotes/origin/{target_branch}",
            "--quiet",
        ],
        check=True,
    )

    result = subprocess.run(
        ["git", "diff", "--name-only", f"origin/{target_branch}...HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    changed_files = result.stdout.strip()

    if not changed_files:
        print("No changed files detected — running all platforms", file=sys.stderr)
        return {"ios": True, "android": True}

    print(f"Changed files:\n{changed_files}", file=sys.stderr)

    has_ios = False
    has_android = False
    has_other = False

    for f in changed_files.split("\n"):
        if f.startswith("ios/"):
            has_ios = True
        elif f.startswith("android/"):
            has_android = True
        else:
            has_other = True

    if has_other:
        print("Files outside ios/ and android/ changed — running all platforms", file=sys.stderr)
        return {"ios": True, "android": True}

    print(f"Platform detection: iOS={has_ios}, Android={has_android}", file=sys.stderr)
    return {"ios": has_ios, "android": has_android}


def run_detect_changes(args):
    if not args.target_branch:
        print("No target branch — running all platforms", file=sys.stderr)
        result = {"ios": True, "android": True}
    else:
        result = detect_changes(args.target_branch, args.gh_token)
    print(json.dumps(result))
