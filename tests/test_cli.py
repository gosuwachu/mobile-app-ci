from unittest.mock import patch
import pytest

from company.ci.cli import main


class TestCliParsing:
    @patch("company.ci.cli.run_step")
    @patch.dict("os.environ", {"GH_TOKEN": "tok"})
    def test_ios_build(self, mock_run):
        argv = [
            "ci-cli", "ios", "build",
            "--commit-sha", "abc", "--build-url", "http://b",
        ]
        with patch("sys.argv", argv):
            main()
        mock_run.assert_called_once_with("ios", "build", "abc", "tok", "http://b", None)

    @patch("company.ci.cli.run_step")
    @patch.dict("os.environ", {"GH_TOKEN": "tok"})
    def test_android_linter(self, mock_run):
        argv = [
            "ci-cli", "android", "linter",
            "--commit-sha", "def", "--build-url", "http://b",
        ]
        with patch("sys.argv", argv):
            main()
        mock_run.assert_called_once_with("android", "linter", "def", "tok", "http://b", None)

    @patch("company.ci.cli.run_step")
    @patch.dict("os.environ", {"GH_TOKEN": "tok"})
    def test_deploy_with_context_json(self, mock_run):
        ctx = '{"job_name": "pipeline/omnibus", "build_number": "42"}'
        argv = [
            "ci-cli", "ios", "deploy",
            "--commit-sha", "abc", "--build-url", "http://b",
            "--context-json", ctx,
        ]
        with patch("sys.argv", argv):
            main()
        mock_run.assert_called_once_with("ios", "deploy", "abc", "tok", "http://b", ctx)

    @patch("company.ci.cli.run_ui_tests")
    @patch.dict("os.environ", {"GH_TOKEN": "tok"})
    def test_ios_ui_tests_with_pr(self, mock_run):
        argv = [
            "ci-cli", "ios", "ui-tests",
            "--pr-number", "42", "--comment-author", "user",
            "--build-url", "http://b",
        ]
        with patch("sys.argv", argv):
            main()
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args.pr_number == "42"
        assert args.comment_author == "user"

    def test_missing_command_exits(self):
        with patch("sys.argv", ["ci-cli"]):
            with pytest.raises(SystemExit):
                main()

    @patch("company.ci.cli.get_build_name", return_value="#7 ios-build abc1234")
    def test_build_name(self, mock_get, capsys):
        with patch("sys.argv", ["ci-cli", "build-name"]):
            main()
        mock_get.assert_called_once_with(None)
        assert capsys.readouterr().out.strip() == "#7 ios-build abc1234"

    @patch("company.ci.cli.get_build_name", return_value="#7 ios-ui-tests PR#42")
    def test_build_name_with_override(self, mock_get):
        with patch("sys.argv", ["ci-cli", "build-name", "--name", "ios-ui-tests"]):
            main()
        mock_get.assert_called_once_with("ios-ui-tests")
