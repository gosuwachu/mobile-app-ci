from unittest.mock import patch
import pytest

from company.ci.cli import main


class TestCliParsing:
    @patch("company.ci.cli.run_step")
    def test_ios_build(self, mock_run):
        argv = [
            "ci-cli", "ios", "build",
            "--commit-sha", "abc", "--gh-token", "tok", "--build-url", "http://b",
        ]
        with patch("sys.argv", argv):
            main()
        mock_run.assert_called_once_with("ios", "build", "abc", "tok", "http://b")

    @patch("company.ci.cli.run_step")
    def test_android_linter(self, mock_run):
        argv = [
            "ci-cli", "android", "linter",
            "--commit-sha", "def", "--gh-token", "tok", "--build-url", "http://b",
        ]
        with patch("sys.argv", argv):
            main()
        mock_run.assert_called_once_with("android", "linter", "def", "tok", "http://b")

    @patch("company.ci.cli.run_ui_tests")
    def test_ios_ui_tests_with_pr(self, mock_run):
        argv = [
            "ci-cli", "ios", "ui-tests",
            "--pr-number", "42", "--comment-author", "user",
            "--gh-token", "tok", "--build-url", "http://b",
        ]
        with patch("sys.argv", argv):
            main()
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args.pr_number == "42"
        assert args.comment_author == "user"

    def test_missing_platform_exits(self):
        with patch("sys.argv", ["ci-cli"]):
            with pytest.raises(SystemExit):
                main()
