from unittest.mock import patch, MagicMock
import json

import pytest

from company.ci.github import github_api, set_commit_status, check_collaborator


class TestGithubApi:
    @patch("company.ci.github.urllib.request.urlopen")
    def test_get_request(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({"ok": True}).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        status, data = github_api("/repos/owner/repo", "fake-token")

        assert status == 200
        assert data == {"ok": True}

    @patch("company.ci.github.urllib.request.urlopen")
    def test_post_request_with_data(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 201
        mock_resp.read.return_value = json.dumps({"id": 1}).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        status, _data = github_api(
            "/repos/owner/repo/statuses/abc123",
            "fake-token",
            method="POST",
            data={"state": "success"},
        )

        assert status == 201
        req = mock_urlopen.call_args[0][0]
        assert req.method == "POST"
        assert json.loads(req.data) == {"state": "success"}


class TestSetCommitStatus:
    @patch("company.ci.github.github_api")
    def test_posts_status(self, mock_api):
        mock_api.return_value = (201, {"id": 1})

        set_commit_status(
            "abc123", "ci/ios-build", "success", "Passed", "token", "http://build/1"
        )

        mock_api.assert_called_once_with(
            "/repos/gosuwachu/jenkinsfiles-test-app/statuses/abc123",
            "token",
            method="POST",
            data={
                "state": "success",
                "context": "ci/ios-build",
                "description": "Passed",
                "target_url": "http://build/1",
            },
        )

    @patch("company.ci.github.github_api")
    def test_warns_on_failure(self, mock_api, capsys):
        mock_api.return_value = (422, {"message": "not found"})

        set_commit_status(
            "bad", "ci/ios-build", "pending", "Running...", "token", "http://build/1"
        )

        output = capsys.readouterr().out
        assert "WARNING" in output


class TestCheckCollaborator:
    @patch("company.ci.github.github_api")
    def test_collaborator_passes(self, mock_api, capsys):
        mock_api.return_value = (204, {})

        check_collaborator("user1", "token")

        output = capsys.readouterr().out
        assert "collaborator" in output
        assert "proceeding" in output

    @patch("company.ci.github.github_api")
    def test_non_collaborator_exits(self, mock_api):
        mock_api.return_value = (404, {})

        with pytest.raises(SystemExit):
            check_collaborator("outsider", "token")
