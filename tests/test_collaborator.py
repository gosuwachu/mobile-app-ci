from unittest.mock import patch, MagicMock
import pytest

from company.ci.collaborator import check_pr_collaborator, run_check_collaborator
from company.ci.cli import main


class TestCheckPrCollaborator:
    @patch("company.ci.collaborator.github_api")
    def test_collaborator_allowed(self, mock_api):
        mock_api.return_value = (204, {})
        check_pr_collaborator("7", "alice", "tok")
        mock_api.assert_called_once()

    @patch("company.ci.collaborator.github_api")
    def test_non_collaborator_with_approved_review(self, mock_api):
        mock_api.side_effect = [
            (404, {}),  # collaborator check
            (200, [{"state": "APPROVED"}]),  # reviews
        ]
        check_pr_collaborator("7", "alice", "tok")
        assert mock_api.call_count == 2

    @patch("company.ci.collaborator.github_api")
    def test_non_collaborator_without_approval_exits(self, mock_api):
        mock_api.side_effect = [
            (404, {}),  # collaborator check
            (200, [{"state": "CHANGES_REQUESTED"}]),  # reviews
        ]
        with pytest.raises(SystemExit):
            check_pr_collaborator("7", "alice", "tok")

    @patch("company.ci.collaborator.github_api")
    def test_non_collaborator_no_reviews_exits(self, mock_api):
        mock_api.side_effect = [
            (404, {}),  # collaborator check
            (200, []),  # no reviews
        ]
        with pytest.raises(SystemExit):
            check_pr_collaborator("7", "alice", "tok")

    @patch("company.ci.collaborator.github_api")
    def test_reviews_fetch_failure_exits(self, mock_api):
        mock_api.side_effect = [
            (404, {}),  # collaborator check
            (500, {}),  # reviews fetch error
        ]
        with pytest.raises(SystemExit):
            check_pr_collaborator("7", "alice", "tok")


class TestRunCheckCollaborator:
    @patch("company.ci.collaborator.check_pr_collaborator")
    def test_no_pr_number_skips(self, mock_check, capsys):
        args = MagicMock(pr_number=None, author="alice", gh_token="tok")
        run_check_collaborator(args)
        mock_check.assert_not_called()
        assert "skipping" in capsys.readouterr().err.lower()

    @patch("company.ci.collaborator.check_pr_collaborator")
    def test_no_author_skips(self, mock_check):
        args = MagicMock(pr_number="7", author=None, gh_token="tok")
        run_check_collaborator(args)
        mock_check.assert_not_called()

    @patch("company.ci.collaborator.check_pr_collaborator")
    def test_with_pr_and_author_calls_check(self, mock_check):
        args = MagicMock(pr_number="7", author="alice", gh_token="tok")
        run_check_collaborator(args)
        mock_check.assert_called_once_with("7", "alice", "tok")


class TestCheckCollaboratorCli:
    @patch("company.ci.cli.run_check_collaborator")
    @patch.dict("os.environ", {"GH_TOKEN": "tok"})
    def test_subcommand(self, mock_run):
        argv = [
            "ci-cli", "check-collaborator",
            "--pr-number", "7", "--author", "alice",
        ]
        with patch("sys.argv", argv):
            main()
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args.pr_number == "7"
        assert args.author == "alice"

    @patch("company.ci.cli.run_check_collaborator")
    @patch.dict("os.environ", {"GH_TOKEN": "tok"})
    def test_subcommand_without_optional_args(self, mock_run):
        argv = ["ci-cli", "check-collaborator"]
        with patch("sys.argv", argv):
            main()
        args = mock_run.call_args[0][0]
        assert args.pr_number is None
        assert args.author is None
