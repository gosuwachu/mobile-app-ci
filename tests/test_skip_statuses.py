from unittest.mock import patch

from company.ci.skip_statuses import publish_skip_statuses
from company.ci.cli import main


class TestPublishSkipStatuses:
    @patch("company.ci.skip_statuses.set_commit_status")
    def test_ios_publishes_four_statuses(self, mock_status):
        publish_skip_statuses("ios", "sha1", "tok", "http://build/1")
        assert mock_status.call_count == 4
        contexts = [c[0][1] for c in mock_status.call_args_list]
        assert "ci/ios-build" in contexts
        assert "ci/ios-unit-tests" in contexts
        assert "ci/ios-linter" in contexts
        assert "ci/ios-deploy" in contexts

    @patch("company.ci.skip_statuses.set_commit_status")
    def test_android_publishes_four_statuses(self, mock_status):
        publish_skip_statuses("android", "sha1", "tok", "http://build/1")
        assert mock_status.call_count == 4
        contexts = [c[0][1] for c in mock_status.call_args_list]
        assert "ci/android-build" in contexts
        assert "ci/android-unit-tests" in contexts
        assert "ci/android-linter" in contexts
        assert "ci/android-deploy" in contexts

    @patch("company.ci.skip_statuses.set_commit_status")
    def test_status_is_success_with_skipped_description(self, mock_status):
        publish_skip_statuses("ios", "sha1", "tok", "http://build/1")
        for call in mock_status.call_args_list:
            assert call[0][2] == "success"
            assert "Skipped" in call[0][3]
            assert "iOS" in call[0][3]

    @patch("company.ci.skip_statuses.set_commit_status")
    def test_android_description_says_android(self, mock_status):
        publish_skip_statuses("android", "sha1", "tok", "http://build/1")
        for call in mock_status.call_args_list:
            assert "Android" in call[0][3]


class TestSkipStatusesCli:
    @patch("company.ci.cli.run_skip_statuses")
    @patch.dict("os.environ", {"GH_TOKEN": "tok"})
    def test_subcommand(self, mock_run):
        argv = [
            "ci-cli", "skip-statuses",
            "--platform", "ios",
            "--commit-sha", "sha1",
            "--build-url", "http://build/1",
        ]
        with patch("sys.argv", argv):
            main()
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args.platform == "ios"
        assert args.commit_sha == "sha1"
