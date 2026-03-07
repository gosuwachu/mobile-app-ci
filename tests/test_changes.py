import json
from unittest.mock import patch, MagicMock

from company.ci.changes import detect_changes, run_detect_changes
from company.ci.cli import main


def _mock_diff(changed_files):
    """Create side_effect for subprocess.run: first call is fetch, second is diff."""
    diff_result = MagicMock(stdout=changed_files, returncode=0)
    return [MagicMock(returncode=0), diff_result]  # fetch, diff


class TestDetectChanges:
    @patch("company.ci.changes.subprocess.run")
    def test_ios_only(self, mock_run):
        mock_run.side_effect = _mock_diff("ios/App.swift\nios/Info.plist")
        result = detect_changes("main", "token")
        assert result == {"ios": True, "android": False}

    @patch("company.ci.changes.subprocess.run")
    def test_android_only(self, mock_run):
        mock_run.side_effect = _mock_diff("android/build.gradle")
        result = detect_changes("main", "token")
        assert result == {"ios": False, "android": True}

    @patch("company.ci.changes.subprocess.run")
    def test_both_platforms(self, mock_run):
        mock_run.side_effect = _mock_diff("ios/App.swift\nandroid/build.gradle")
        result = detect_changes("main", "token")
        assert result == {"ios": True, "android": True}

    @patch("company.ci.changes.subprocess.run")
    def test_files_outside_platforms_runs_all(self, mock_run):
        mock_run.side_effect = _mock_diff("README.md")
        result = detect_changes("main", "token")
        assert result == {"ios": True, "android": True}

    @patch("company.ci.changes.subprocess.run")
    def test_mixed_with_other_files_runs_all(self, mock_run):
        mock_run.side_effect = _mock_diff("ios/App.swift\nREADME.md")
        result = detect_changes("main", "token")
        assert result == {"ios": True, "android": True}

    @patch("company.ci.changes.subprocess.run")
    def test_no_changed_files_runs_all(self, mock_run):
        mock_run.side_effect = _mock_diff("")
        result = detect_changes("main", "token")
        assert result == {"ios": True, "android": True}

    @patch("company.ci.changes.subprocess.run")
    def test_fetch_uses_auth_url(self, mock_run):
        mock_run.side_effect = _mock_diff("ios/App.swift")
        detect_changes("develop", "my-secret-token")

        fetch_call = mock_run.call_args_list[0]
        fetch_args = fetch_call[0][0]
        assert "x-access-token:my-secret-token@" in fetch_args[2]
        assert "develop:refs/remotes/origin/develop" in fetch_args[3]


class TestRunDetectChanges:
    @patch("company.ci.changes.detect_changes")
    def test_no_target_branch(self, mock_detect, capsys):
        args = MagicMock(target_branch=None, gh_token="tok")
        run_detect_changes(args)

        mock_detect.assert_not_called()
        captured = capsys.readouterr()
        assert "No target branch" in captured.err
        parsed = json.loads(captured.out.strip())
        assert parsed == {"ios": True, "android": True}

    @patch("company.ci.changes.detect_changes", return_value={"ios": True, "android": False})
    def test_with_target_branch(self, mock_detect, capsys):
        args = MagicMock(target_branch="main", gh_token="tok")
        run_detect_changes(args)

        mock_detect.assert_called_once_with("main", "tok")
        parsed = json.loads(capsys.readouterr().out.strip())
        assert parsed == {"ios": True, "android": False}


class TestDetectChangesCli:
    @patch("company.ci.cli.run_detect_changes")
    @patch.dict("os.environ", {"GH_TOKEN": "tok"})
    def test_detect_changes_subcommand(self, mock_run):
        with patch("sys.argv", ["ci-cli", "detect-changes"]):
            main()
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args.gh_token == "tok"
        assert args.target_branch is None

    @patch("company.ci.cli.run_detect_changes")
    @patch.dict("os.environ", {"GH_TOKEN": "tok"})
    def test_detect_changes_with_target_branch(self, mock_run):
        argv = ["ci-cli", "detect-changes", "--target-branch", "develop"]
        with patch("sys.argv", argv):
            main()
        args = mock_run.call_args[0][0]
        assert args.target_branch == "develop"
