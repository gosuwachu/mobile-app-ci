import json
import os
import sys

from company.ci.checkout import checkout_app
from company.ci.github import check_collaborator, resolve_pr, set_commit_status

STEPS = {
    ("ios", "build"): ("iOS Build", "ci/ios-build", "Building iOS..."),
    ("ios", "unit-tests"): (
        "iOS Unit Tests",
        "ci/ios-unit-tests",
        "Running iOS unit tests...",
    ),
    ("ios", "linter"): ("iOS Linter", "ci/ios-linter", "Running iOS linter..."),
    ("ios", "deploy"): ("iOS Deploy", "ci/ios-deploy", "Deploying iOS..."),
    ("ios", "ui-tests"): (
        "iOS UI Tests",
        "ci/ios-ui-tests",
        "Running iOS UI tests...",
    ),
    ("android", "build"): (
        "Android Build",
        "ci/android-build",
        "Building Android...",
    ),
    ("android", "unit-tests"): (
        "Android Unit Tests",
        "ci/android-unit-tests",
        "Running Android unit tests...",
    ),
    ("android", "linter"): (
        "Android Linter",
        "ci/android-linter",
        "Running Android linter...",
    ),
    ("android", "deploy"): (
        "Android Deploy",
        "ci/android-deploy",
        "Deploying Android...",
    ),
}


def run_step(platform, step, commit_sha, gh_token, build_url, context_json=None):  # pylint: disable=too-many-arguments,too-many-positional-arguments
    _stage_name, context, message = STEPS[(platform, step)]

    if context_json:
        ctx = json.loads(context_json)
        print(f"Triggered by: {ctx['job_name']} #{ctx['build_number']}", file=sys.stderr)

    checkout_app(commit_sha, gh_token)

    set_commit_status(commit_sha, context, "pending", "Running...", gh_token, build_url)
    try:
        print(message, file=sys.stderr)
        set_commit_status(
            commit_sha, context, "success", "Passed", gh_token, build_url
        )
    except Exception as e:
        set_commit_status(
            commit_sha, context, "failure", f"Failed: {e}", gh_token, build_url
        )
        raise

    print(json.dumps({
        "job_name": os.environ.get("JOB_NAME", ""),
        "build_number": os.environ.get("BUILD_NUMBER", ""),
        "build_url": build_url,
        "commit_sha": commit_sha,
        "platform": platform,
        "step": step,
        "context": context,
    }))


def run_ui_tests(args):
    if args.pr_number:
        if args.comment_author:
            check_collaborator(args.comment_author, args.gh_token)

        _branch, sha = resolve_pr(args.pr_number, args.gh_token)
        commit_sha = sha
    else:
        commit_sha = args.commit_sha
        if not commit_sha:
            print("Either --pr-number or --commit-sha is required", file=sys.stderr)
            sys.exit(1)

    run_step("ios", "ui-tests", commit_sha, args.gh_token, args.build_url)
