import sys

from company.ci.github import github_api, GITHUB_OWNER, GITHUB_REPO


def check_pr_collaborator(pr_number, author, token):
    print(f"PR #{pr_number} by {author} — checking collaborator status")

    status, _ = github_api(
        f"/repos/{GITHUB_OWNER}/{GITHUB_REPO}/collaborators/{author}",
        token,
    )
    if status == 204:
        print(f"{author} is a collaborator — CI allowed")
        return

    print(f"{author} is NOT a collaborator — checking for approved reviews")
    status, reviews = github_api(
        f"/repos/{GITHUB_OWNER}/{GITHUB_REPO}/pulls/{pr_number}/reviews",
        token,
    )
    if status != 200:
        print(f"Failed to fetch reviews (HTTP {status}) — aborting")
        sys.exit(1)

    approved = any(r.get("state") == "APPROVED" for r in reviews)
    if approved:
        print(f"PR has an approved review — CI allowed for non-collaborator {author}")
    else:
        print(f"PR has no approved reviews — aborting CI for non-collaborator {author}")
        sys.exit(1)


def run_check_collaborator(args):
    if not args.pr_number or not args.author:
        print("Not a PR build — skipping collaborator check")
        return
    check_pr_collaborator(args.pr_number, args.author, args.gh_token)
