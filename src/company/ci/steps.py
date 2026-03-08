import json
import os
import subprocess
import sys
from contextlib import contextmanager
from dataclasses import dataclass

from company.ci.checkout import APP_DIR
from company.ci.checkout import checkout_app
from company.ci.github import check_collaborator, resolve_pr, set_commit_status


@dataclass
class StepConfig:
    name: str
    context: str


STEPS = {
    ("ios", "build"): StepConfig("iOS Build", "ci/ios-build"),
    ("ios", "unit-tests"): StepConfig("iOS Unit Tests", "ci/ios-unit-tests"),
    ("ios", "linter"): StepConfig("iOS Linter", "ci/ios-linter"),
    ("ios", "deploy"): StepConfig("iOS Deploy", "ci/ios-deploy"),
    ("ios", "ui-tests"): StepConfig("iOS UI Tests", "ci/ios-ui-tests"),
    ("android", "build"): StepConfig("Android Build", "ci/android-build"),
    ("android", "unit-tests"): StepConfig("Android Unit Tests", "ci/android-unit-tests"),
    ("android", "linter"): StepConfig("Android Linter", "ci/android-linter"),
    ("android", "deploy"): StepConfig("Android Deploy", "ci/android-deploy"),
    ("ios", "alpha-build"): StepConfig("iOS Alpha Build", "ci/ios-alpha-build"),
    ("android", "alpha-build"): StepConfig("Android Alpha Build", "ci/android-alpha-build"),
    ("ios", "production-build"): StepConfig("iOS Production Build", "ci/ios-production-build"),
    ("android", "production-build"): StepConfig(
        "Android Production Build", "ci/android-production-build",
    ),
}


def _run_script(script_path):
    full_path = APP_DIR / script_path
    if not full_path.exists():
        raise FileNotFoundError(f"Build script not found: {full_path}")
    subprocess.run(["bash", script_path], check=True, cwd=APP_DIR)


@contextmanager
def commit_status(commit_sha, context, gh_token, build_url, no_status=False):
    if not no_status:
        set_commit_status(commit_sha, context, "pending", "Running...", gh_token, build_url)
    try:
        yield
        if not no_status:
            set_commit_status(commit_sha, context, "success", "Passed", gh_token, build_url)
    except Exception as e:
        if not no_status:
            set_commit_status(commit_sha, context, "failure", f"Failed: {e}", gh_token, build_url)
        raise


def _step_result_json(platform, step, context, commit_sha, build_url):
    print(json.dumps({
        "job_name": os.environ.get("JOB_NAME", ""),
        "build_number": os.environ.get("BUILD_NUMBER", ""),
        "build_url": build_url,
        "commit_sha": commit_sha,
        "platform": platform,
        "step": step,
        "context": context,
    }))


def run_build(platform, commit_sha, gh_token, build_url, no_status=False):
    step = STEPS[(platform, "build")]
    with commit_status(commit_sha, step.context, gh_token, build_url, no_status):
        checkout_app(commit_sha, gh_token)
        _run_script(f"{platform}/{platform}_build/build.sh")
    _step_result_json(platform, "build", step.context, commit_sha, build_url)


def run_unit_tests(platform, commit_sha, gh_token, build_url, no_status=False):
    step = STEPS[(platform, "unit-tests")]
    with commit_status(commit_sha, step.context, gh_token, build_url, no_status):
        checkout_app(commit_sha, gh_token)
        _run_script(f"{platform}/{platform}_build/unit-tests.sh")
    _step_result_json(platform, "unit-tests", step.context, commit_sha, build_url)


def run_linter(platform, commit_sha, gh_token, build_url, no_status=False):
    step = STEPS[(platform, "linter")]
    with commit_status(commit_sha, step.context, gh_token, build_url, no_status):
        checkout_app(commit_sha, gh_token)
        _run_script(f"{platform}/{platform}_build/lint.sh")
    _step_result_json(platform, "linter", step.context, commit_sha, build_url)


def run_deploy(platform, commit_sha, gh_token, build_url, context_json=None, no_status=False):  # pylint: disable=too-many-arguments,too-many-positional-arguments
    step = STEPS[(platform, "deploy")]
    if context_json:
        ctx = json.loads(context_json)
        print(f"Triggered by: {ctx['job_name']} #{ctx['build_number']}", file=sys.stderr)
    with commit_status(commit_sha, step.context, gh_token, build_url, no_status):
        pass
    _step_result_json(platform, "deploy", step.context, commit_sha, build_url)


def run_alpha_build(platform, commit_sha, gh_token, build_url):
    step = STEPS[(platform, "alpha-build")]
    checkout_app(commit_sha, gh_token)
    _run_script(f"{platform}/{platform}_build/build.sh")
    _step_result_json(platform, "alpha-build", step.context, commit_sha, build_url)


def run_production_build(platform, commit_sha, gh_token, build_url):
    step = STEPS[(platform, "production-build")]
    checkout_app(commit_sha, gh_token)
    _run_script(f"{platform}/{platform}_build/build.sh")
    _step_result_json(platform, "production-build", step.context, commit_sha, build_url)


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

    step = STEPS[("ios", "ui-tests")]
    no_status = getattr(args, "no_status", False)
    with commit_status(commit_sha, step.context, args.gh_token, args.build_url, no_status):
        checkout_app(commit_sha, args.gh_token)
        _run_script("ios/ios_build/ui-tests.sh")
    _step_result_json("ios", "ui-tests", step.context, commit_sha, args.build_url)
