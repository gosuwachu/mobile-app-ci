import os
import re


def get_build_name(name_override: str | None = None) -> str:
    jenkinsfile = os.environ.get("JENKINSFILE", "")
    if name_override:
        name = name_override
    elif jenkinsfile:
        name = re.sub(r"^ci/[^/]+/", "", jenkinsfile)
        name = re.sub(r"\.Jenkinsfile$", "", name)
    else:
        name = "build"

    parts = [name]

    commit_sha = os.environ.get("COMMIT_SHA", "")
    if commit_sha:
        parts.append(commit_sha[:7])

    pr_number = os.environ.get("PR_NUMBER", "")
    if pr_number:
        parts.append(f"PR#{pr_number}")

    ci_branch = os.environ.get("CI_BRANCH", "")
    if ci_branch and ci_branch != "main":
        parts.append(f"[ci:{ci_branch}]")

    build_number = os.environ.get("BUILD_NUMBER", "")
    if build_number:
        return f"#{build_number} {' '.join(parts)}"
    return " ".join(parts)
