import json
from unittest.mock import patch

import pytest

from company.ci.steps import (
    STEPS, StepConfig, commit_status, run_build, run_deploy, run_alpha_build,
)


class TestCommitStatus:
    @patch("company.ci.steps.set_commit_status")
    def test_sets_pending_and_success(self, mock_status):
        with commit_status("sha1", "ci/ios-build", "tok", "http://b"):
            pass
        assert mock_status.call_count == 2
        assert mock_status.call_args_list[0].args[2] == "pending"
        assert mock_status.call_args_list[1].args[2] == "success"

    @patch("company.ci.steps.set_commit_status")
    def test_sets_pending_and_failure_on_error(self, mock_status):
        with pytest.raises(RuntimeError):
            with commit_status("sha1", "ci/ios-build", "tok", "http://b"):
                raise RuntimeError("boom")
        assert mock_status.call_count == 2
        assert mock_status.call_args_list[0].args[2] == "pending"
        assert mock_status.call_args_list[1].args[2] == "failure"
        assert "boom" in mock_status.call_args_list[1].args[3]

    @patch("company.ci.steps.set_commit_status")
    def test_no_status_skips_all(self, mock_status):
        with commit_status("sha1", "ci/ios-build", "tok", "http://b", no_status=True):
            pass
        mock_status.assert_not_called()


class TestRunBuild:
    @patch("company.ci.steps._run_script")
    @patch("company.ci.steps.set_commit_status")
    @patch("company.ci.steps.checkout_app")
    def test_runs_ios_build(self, mock_checkout, mock_status, mock_script, capsys):
        run_build("ios", "sha123", "token", "http://build/1")

        mock_checkout.assert_called_once_with("sha123", "token")
        mock_script.assert_called_once_with("ios/ios_build/build.sh")
        assert mock_status.call_count == 2
        assert mock_status.call_args_list[0].args[2] == "pending"
        assert mock_status.call_args_list[1].args[2] == "success"

        result = json.loads(capsys.readouterr().out.strip())
        assert result["platform"] == "ios"
        assert result["step"] == "build"
        assert result["context"] == "ci/ios-build"
        assert result["commit_sha"] == "sha123"

    @patch("company.ci.steps._run_script")
    @patch("company.ci.steps.set_commit_status")
    @patch("company.ci.steps.checkout_app")
    def test_no_status_skips_commit_status(self, mock_checkout, mock_status, _mock_script, capsys):
        run_build("ios", "sha123", "token", "http://build/1", no_status=True)

        mock_checkout.assert_called_once_with("sha123", "token")
        mock_status.assert_not_called()

        result = json.loads(capsys.readouterr().out.strip())
        assert result["platform"] == "ios"
        assert result["step"] == "build"

    @patch("company.ci.steps._run_script")
    @patch("company.ci.steps.set_commit_status")
    @patch("company.ci.steps.checkout_app")
    def test_outputs_json_with_env_vars(self, _mock_checkout, _mock_status, _mock_script, capsys):
        env = {"JOB_NAME": "mobile-app-support/omnibus", "BUILD_NUMBER": "42"}
        with patch.dict("os.environ", env):
            run_build("ios", "sha1", "tok", "http://build/1")

        result = json.loads(capsys.readouterr().out.strip())
        assert result["job_name"] == "mobile-app-support/omnibus"
        assert result["build_number"] == "42"
        assert result["build_url"] == "http://build/1"


class TestRunDeploy:
    @patch("company.ci.steps.set_commit_status")
    def test_runs_android_deploy(self, _mock_status, capsys):
        run_deploy("android", "sha456", "token", "http://build/2")

        result = json.loads(capsys.readouterr().out.strip())
        assert result["platform"] == "android"
        assert result["step"] == "deploy"

    @patch("company.ci.steps.set_commit_status")
    def test_context_json_logged(self, _mock_status, capsys):
        ctx = json.dumps({"job_name": "mobile-app-support/omnibus", "build_number": "99"})
        run_deploy("ios", "sha1", "tok", "http://build/1", context_json=ctx)

        assert "Triggered by: mobile-app-support/omnibus #99" in capsys.readouterr().err


class TestRunAlphaBuild:
    @patch("company.ci.steps._run_script")
    @patch("company.ci.steps.set_commit_status")
    @patch("company.ci.steps.checkout_app")
    def test_no_commit_status(self, _mock_checkout, mock_status, _mock_script, capsys):
        run_alpha_build("ios", "sha1", "tok", "http://build/1")

        mock_status.assert_not_called()
        result = json.loads(capsys.readouterr().out.strip())
        assert result["platform"] == "ios"
        assert result["step"] == "alpha-build"


class TestAllSteps:
    def test_all_steps_have_entries(self):
        expected = [
            ("ios", "build"),
            ("ios", "unit-tests"),
            ("ios", "linter"),
            ("ios", "deploy"),
            ("ios", "ui-tests"),
            ("ios", "alpha-build"),
            ("ios", "production-build"),
            ("android", "build"),
            ("android", "unit-tests"),
            ("android", "linter"),
            ("android", "deploy"),
            ("android", "alpha-build"),
            ("android", "production-build"),
        ]
        for key in expected:
            assert key in STEPS, f"Missing step: {key}"
            assert isinstance(STEPS[key], StepConfig)
