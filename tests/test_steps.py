from unittest.mock import patch

from company.ci.steps import run_step, STEPS


class TestRunStep:
    @patch("company.ci.steps.set_commit_status")
    @patch("company.ci.steps.checkout_app")
    def test_runs_ios_build(self, mock_checkout, mock_status, capsys):
        run_step("ios", "build", "sha123", "token", "http://build/1")

        mock_checkout.assert_called_once_with("sha123", "token")
        assert mock_status.call_count == 2
        calls = mock_status.call_args_list
        assert calls[0].args[2] == "pending"
        assert calls[1].args[2] == "success"

        output = capsys.readouterr().out
        assert "Building iOS..." in output

    @patch("company.ci.steps.set_commit_status")
    @patch("company.ci.steps.checkout_app")
    def test_runs_android_deploy(self, _mock_checkout, _mock_status, capsys):
        run_step("android", "deploy", "sha456", "token", "http://build/2")

        output = capsys.readouterr().out
        assert "Deploying Android..." in output

    def test_all_steps_have_entries(self):
        expected = [
            ("ios", "build"),
            ("ios", "unit-tests"),
            ("ios", "linter"),
            ("ios", "deploy"),
            ("ios", "ui-tests"),
            ("android", "build"),
            ("android", "unit-tests"),
            ("android", "linter"),
            ("android", "deploy"),
        ]
        for key in expected:
            assert key in STEPS, f"Missing step: {key}"
