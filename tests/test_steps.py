import json
from unittest.mock import patch

from company.ci.steps import run_step, STEPS


class TestRunStep:
    @patch("company.ci.steps._run_build_script")
    @patch("company.ci.steps.set_commit_status")
    @patch("company.ci.steps.checkout_app")
    def test_runs_ios_build(self, mock_checkout, mock_status, mock_script, capsys):
        run_step("ios", "build", "sha123", "token", "http://build/1")

        mock_checkout.assert_called_once_with("sha123", "token")
        mock_script.assert_called_once_with("ios", "build")
        assert mock_status.call_count == 2
        calls = mock_status.call_args_list
        assert calls[0].args[2] == "pending"
        assert calls[1].args[2] == "success"

        captured = capsys.readouterr()
        assert "Building iOS..." in captured.err
        result = json.loads(captured.out.strip())
        assert result["platform"] == "ios"
        assert result["step"] == "build"
        assert result["context"] == "ci/ios-build"
        assert result["commit_sha"] == "sha123"

    @patch("company.ci.steps._run_build_script")
    @patch("company.ci.steps.set_commit_status")
    @patch("company.ci.steps.checkout_app")
    def test_runs_android_deploy(self, _mock_checkout, _mock_status, _mock_script, capsys):
        run_step("android", "deploy", "sha456", "token", "http://build/2")

        captured = capsys.readouterr()
        assert "Deploying Android..." in captured.err
        result = json.loads(captured.out.strip())
        assert result["platform"] == "android"
        assert result["step"] == "deploy"

    @patch("company.ci.steps._run_build_script")
    @patch("company.ci.steps.set_commit_status")
    @patch("company.ci.steps.checkout_app")
    def test_outputs_json_with_env_vars(self, _mock_checkout, _mock_status, _mock_script, capsys):
        env = {"JOB_NAME": "mobile-app-support/omnibus", "BUILD_NUMBER": "42"}
        with patch.dict("os.environ", env):
            run_step("ios", "build", "sha1", "tok", "http://build/1")

        result = json.loads(capsys.readouterr().out.strip())
        assert result["job_name"] == "mobile-app-support/omnibus"
        assert result["build_number"] == "42"
        assert result["build_url"] == "http://build/1"

    @patch("company.ci.steps._run_build_script")
    @patch("company.ci.steps.set_commit_status")
    @patch("company.ci.steps.checkout_app")
    def test_context_json_logged(self, _mock_checkout, _mock_status, _mock_script, capsys):
        ctx = json.dumps({"job_name": "mobile-app-support/omnibus", "build_number": "99"})
        run_step("ios", "deploy", "sha1", "tok", "http://build/1", context_json=ctx)

        assert "Triggered by: mobile-app-support/omnibus #99" in capsys.readouterr().err

    @patch("company.ci.steps._run_build_script")
    @patch("company.ci.steps.set_commit_status")
    @patch("company.ci.steps.checkout_app")
    def test_no_status_skips_commit_status(self, mock_checkout, mock_status, _mock_script, capsys):
        run_step("ios", "build", "sha123", "token", "http://build/1", no_status=True)

        mock_checkout.assert_called_once_with("sha123", "token")
        mock_status.assert_not_called()

        captured = capsys.readouterr()
        assert "Building iOS..." in captured.err
        result = json.loads(captured.out.strip())
        assert result["platform"] == "ios"
        assert result["step"] == "build"

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
