import sys

from company.ci.github import set_commit_status
from company.ci.steps import STEPS


def publish_skip_statuses(platform, commit_sha, token, build_url):
    platform_label = "iOS" if platform == "ios" else "Android"
    # Exclude ui-tests — it's comment-triggered, not part of the regular pipeline
    contexts = [
        v[1] for k, v in STEPS.items()
        if k[0] == platform and k[1] != "ui-tests"
    ]

    for context in contexts:
        print(f"Publishing skipped status for: {context}", file=sys.stderr)
        set_commit_status(
            commit_sha,
            context,
            "success",
            f"Skipped — no {platform_label} changes",
            token,
            build_url,
        )


def run_skip_statuses(args):
    publish_skip_statuses(args.platform, args.commit_sha, args.gh_token, args.build_url)
