# CI Repo (jenkinsfiles-test-app-ci)

CI step definitions and shared tooling for the [jenkinsfiles-test-app](https://github.com/gosuwachu/jenkinsfiles-test-app) mobile pipeline.

## Project Structure

```
├── ci/
│   ├── ios/                         # iOS child Jenkinsfiles
│   │   ├── ios-build.Jenkinsfile
│   │   ├── ios-deploy.Jenkinsfile
│   │   ├── ios-linter.Jenkinsfile
│   │   ├── ios-ui-tests.Jenkinsfile
│   │   └── ios-unit-tests.Jenkinsfile
│   └── android/                     # Android child Jenkinsfiles
│       ├── android-build.Jenkinsfile
│       ├── android-deploy.Jenkinsfile
│       ├── android-linter.Jenkinsfile
│       └── android-unit-tests.Jenkinsfile
├── src/company/ci/                  # Python CLI package
│   ├── __main__.py                  # Entrypoint
│   ├── cli.py                       # Argument parsing
│   ├── checkout.py                  # Git clone/checkout logic
│   ├── github.py                    # GitHub API (commit statuses, collaborator checks)
│   └── steps.py                     # CI step definitions and orchestration
├── tests/                           # Pytest test suite
├── ci-cli                           # Shell wrapper — bootstraps venv, runs company.ci
├── run-tests                        # Shell wrapper — runs mypy, pylint, vulture, pytest
├── lint-jenkinsfiles                # Shell wrapper — runs npm-groovy-lint on all Jenkinsfiles
├── Jenkinsfile                      # CI pipeline for this repo (runs on PRs and main)
├── requirements.txt                 # Runtime deps (stdlib only)
├── requirements-dev.txt             # Dev deps (pytest, mypy, pylint, vulture)
├── pyproject.toml                   # Tool config (mypy, pylint, vulture)
└── .groovylintrc.json               # npm-groovy-lint config
```

## How It Works

Child Jenkinsfiles are minimal wrappers that call `./ci-cli <platform> <step>` with explicit arguments. The CLI handles:
1. Checking out the app repo at the pinned `COMMIT_SHA`
2. Setting GitHub commit status to `pending`
3. Running the step (currently prints a placeholder message)
4. Setting GitHub commit status to `success` or `failure`

The omnibus job in Jenkins (`pipeline/omnibus`) checks out this repo at `main` and runs whichever Jenkinsfile is specified by the `JENKINSFILE` parameter.

## Common Commands

```bash
# Run all checks (mypy, pylint, vulture, pytest)
./run-tests -v

# Run only pytest
PYTHONPATH=src .venv/bin/pytest -v

# Lint Jenkinsfiles
./lint-jenkinsfiles

# Run CLI locally (requires GitHub token)
./ci-cli ios build --commit-sha <sha> --gh-token <token> --build-url <url>
```

## Adding a New CI Step

1. Add entry to `STEPS` dict in `src/company/ci/steps.py`
2. Create Jenkinsfile in `ci/<platform>/<platform>-<step>.Jenkinsfile`
3. Add the step to the trigger orchestrator in the app repo (`ci/trigger.Jenkinsfile`)
4. Add the context name to `IOS_CONTEXTS` or `ANDROID_CONTEXTS` in the trigger

## Linting

All checks run via `./run-tests` (Python) and `./lint-jenkinsfiles` (Groovy):

| Tool | What it checks |
|------|---------------|
| mypy | Type errors in `src/` and `tests/` |
| pylint | Code quality (10.00/10 target) |
| vulture | Dead code detection (min confidence 80%) |
| npm-groovy-lint | Jenkinsfile syntax and style (`recommended-jenkinsfile` preset) |

Config lives in `pyproject.toml` (Python tools) and `.groovylintrc.json` (Groovy).

## Companion Repos

- [jenkinsfiles-test](https://github.com/gosuwachu/jenkinsfiles-test) — Jenkins Docker environment, Job DSL, seed job
- [jenkinsfiles-test-app](https://github.com/gosuwachu/jenkinsfiles-test-app) — app repo with trigger Jenkinsfile and platform directories
