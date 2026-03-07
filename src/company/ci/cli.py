import argparse
import os

from company.ci.build_name import get_build_name
from company.ci.changes import run_detect_changes
from company.ci.collaborator import run_check_collaborator
from company.ci.skip_statuses import run_skip_statuses
from company.ci.steps import STEPS, run_step, run_ui_tests


def main():
    parser = argparse.ArgumentParser(description="CI CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # build-name: reads env vars, prints display name to stdout
    build_name_parser = subparsers.add_parser("build-name")
    build_name_parser.add_argument(
        "--name", help="Override build name (instead of deriving from JENKINSFILE env var)",
    )

    # check-collaborator: verifies PR author is a collaborator or has approved review
    collab_parser = subparsers.add_parser("check-collaborator")
    collab_parser.add_argument("--pr-number", help="Pull request number")
    collab_parser.add_argument("--author", help="PR author username")

    # skip-statuses: publishes skipped commit statuses for a platform
    skip_parser = subparsers.add_parser("skip-statuses")
    skip_parser.add_argument("--platform", required=True, choices=["ios", "android"])
    skip_parser.add_argument("--commit-sha", required=True)
    skip_parser.add_argument("--build-url", required=True)

    # detect-changes: detects which platforms have changed files in a PR
    detect_parser = subparsers.add_parser("detect-changes")
    detect_parser.add_argument("--target-branch", help="PR target branch to diff against")

    for platform in ("ios", "android"):
        platform_parser = subparsers.add_parser(platform)
        step_parsers = platform_parser.add_subparsers(dest="step", required=True)

        steps_for_platform = [k[1] for k in STEPS if k[0] == platform]
        for step in steps_for_platform:
            step_parser = step_parsers.add_parser(step)
            step_parser.add_argument("--build-url", required=True)

            if platform == "ios" and step == "ui-tests":
                step_parser.add_argument("--pr-number")
                step_parser.add_argument("--comment-author")
                step_parser.add_argument("--commit-sha")
            else:
                step_parser.add_argument("--commit-sha", required=True)

            if step == "deploy":
                step_parser.add_argument(
                    "--context-json", help="JSON context from triggering build",
                )

            step_parser.add_argument(
                "--no-status", action="store_true",
                help="Skip GitHub commit status publishing",
            )

    args = parser.parse_args()

    if args.command != "build-name":
        args.gh_token = os.environ["GH_TOKEN"]

    if args.command == "build-name":
        print(get_build_name(args.name))
    elif args.command == "check-collaborator":
        run_check_collaborator(args)
    elif args.command == "skip-statuses":
        run_skip_statuses(args)
    elif args.command == "detect-changes":
        run_detect_changes(args)
    elif args.command == "ios" and args.step == "ui-tests":
        run_ui_tests(args)
    else:
        context_json = getattr(args, "context_json", None)
        no_status = getattr(args, "no_status", False)
        run_step(
            args.command, args.step, args.commit_sha,
            args.gh_token, args.build_url, context_json, no_status,
        )
