# CI Repo (mobile-app-ci)

CI step definitions and shared tooling for the [mobile-app](https://github.com/gosuwachu/mobile-app) mobile pipeline.

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

Child Jenkinsfiles are minimal wrappers that call `./ci-cli <platform> <step>` with explicit arguments. Each step has its own function in `steps.py` (e.g. `run_build`, `run_deploy`). The `commit_status` context manager handles the pending/success/failure lifecycle. Steps that run build scripts call `_run_script()` with the hardcoded path to the script in the app repo.

The omnibus job in Jenkins (`mobile-app-support/omnibus`) checks out this repo at `main` and runs whichever Jenkinsfile is specified by the `JENKINSFILE` parameter.

## Common Commands

```bash
# Run all checks (mypy, pylint, vulture, pytest)
./run-tests -v

# Run only pytest
PYTHONPATH=src .venv/bin/pytest -v

# Lint Jenkinsfiles
./lint-jenkinsfiles

# Run CLI locally (requires GitHub token)
GH_TOKEN=<token> ./ci-cli ios build --commit-sha <sha> --build-url <url>
```

## Adding a New CI Step

1. Add `StepConfig` entry to `STEPS` dict in `src/company/ci/steps.py`
2. Add a `run_<step>` function in `steps.py` with the script path hardcoded
3. Add the function to `STEP_FUNCTIONS` in `cli.py` and update the dispatch logic
4. Create build script in app repo: `{platform}/{platform}_build/{script}.sh`
5. Create Jenkinsfile in `ci/<platform>/<platform>-<step>.Jenkinsfile`
6. Add the step to the trigger orchestrator in the app repo (`ci/trigger.Jenkinsfile`)
7. Add the context name to `IOS_CONTEXTS` or `ANDROID_CONTEXTS` in the trigger

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

- [jenkins-setup](https://github.com/gosuwachu/jenkins-setup) — Jenkins Docker environment, Job DSL, seed job
- [mobile-app](https://github.com/gosuwachu/mobile-app) — app repo with trigger Jenkinsfile and platform directories
