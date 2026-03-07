import argparse

from company.ci.build_name import get_build_name
from company.ci.steps import STEPS, run_step, run_ui_tests


def main():
    parser = argparse.ArgumentParser(description="CI CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # build-name: reads env vars, prints display name to stdout
    build_name_parser = subparsers.add_parser("build-name")
    build_name_parser.add_argument(
        "--name", help="Override build name (instead of deriving from JENKINSFILE env var)",
    )

    for platform in ("ios", "android"):
        platform_parser = subparsers.add_parser(platform)
        step_parsers = platform_parser.add_subparsers(dest="step", required=True)

        steps_for_platform = [k[1] for k in STEPS if k[0] == platform]
        for step in steps_for_platform:
            step_parser = step_parsers.add_parser(step)
            step_parser.add_argument("--gh-token", required=True)
            step_parser.add_argument("--build-url", required=True)

            if platform == "ios" and step == "ui-tests":
                step_parser.add_argument("--pr-number")
                step_parser.add_argument("--comment-author")
                step_parser.add_argument("--commit-sha")
            else:
                step_parser.add_argument("--commit-sha", required=True)

    args = parser.parse_args()

    if args.command == "build-name":
        print(get_build_name(args.name))
    elif args.command == "ios" and args.step == "ui-tests":
        run_ui_tests(args)
    else:
        run_step(args.command, args.step, args.commit_sha, args.gh_token, args.build_url)
