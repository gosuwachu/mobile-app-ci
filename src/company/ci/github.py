import json
import sys
import urllib.request
import urllib.error

GITHUB_OWNER = "gosuwachu"
GITHUB_REPO = "jenkinsfiles-test-app"


def github_api(path, token, method="GET", data=None):
    url = f"https://api.github.com{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read()
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        resp_body = json.loads(e.read()) if e.fp else {}
        return e.code, resp_body


def set_commit_status(sha, context, state, description, token, build_url):  # pylint: disable=too-many-arguments,too-many-positional-arguments
    status, resp = github_api(
        f"/repos/{GITHUB_OWNER}/{GITHUB_REPO}/statuses/{sha}",
        token,
        method="POST",
        data={
            "state": state,
            "context": context,
            "description": description,
            "target_url": build_url,
        },
    )
    if status >= 300:
        print(f"WARNING: Failed to set status (HTTP {status}): {resp}", file=sys.stderr)


def check_collaborator(username, token):
    print(f"Checking if {username} is a collaborator...", file=sys.stderr)
    status, _ = github_api(
        f"/repos/{GITHUB_OWNER}/{GITHUB_REPO}/collaborators/{username}",
        token,
    )
    if status == 204:
        print(f"{username} is a collaborator — proceeding", file=sys.stderr)
    else:
        print(f"User {username} is not a collaborator (HTTP {status}) — aborting", file=sys.stderr)
        sys.exit(1)


def resolve_pr(pr_number, token):
    status, data = github_api(
        f"/repos/{GITHUB_OWNER}/{GITHUB_REPO}/pulls/{pr_number}",
        token,
    )
    if status != 200 or "head" not in data:
        print(f"Failed to resolve PR #{pr_number} (HTTP {status})", file=sys.stderr)
        sys.exit(1)
    branch = data["head"]["ref"]
    sha = data["head"]["sha"]
    print(f"PR #{pr_number}: branch={branch}, sha={sha}", file=sys.stderr)
    return branch, sha
