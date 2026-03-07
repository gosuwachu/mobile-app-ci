from unittest.mock import patch, MagicMock
from pathlib import Path

from company.ci.checkout import checkout_app


class TestCheckoutApp:
    @patch("company.ci.checkout.subprocess.run")
    @patch("company.ci.checkout.APP_DIR", new_callable=lambda: MagicMock(spec=Path))
    def test_skips_when_already_at_sha(self, mock_dir, mock_run, capsys):
        mock_dir.exists.return_value = True
        mock_run.return_value = MagicMock(returncode=0, stdout="abc123\n")

        checkout_app("abc123", "token")

        output = capsys.readouterr().err
        assert "already at abc123" in output
        mock_run.assert_called_once()  # only git rev-parse, no fetch/checkout

    @patch("company.ci.checkout.subprocess.run")
    @patch("company.ci.checkout.APP_DIR", new_callable=lambda: MagicMock(spec=Path))
    def test_fetches_when_at_different_sha(self, mock_dir, mock_run):
        mock_dir.exists.return_value = True
        mock_run.return_value = MagicMock(returncode=0, stdout="old-sha\n")

        checkout_app("new-sha", "token")

        assert mock_run.call_count == 3  # rev-parse + fetch + checkout

    @patch("company.ci.checkout.subprocess.run")
    @patch("company.ci.checkout.APP_DIR", new_callable=lambda: MagicMock(spec=Path))
    def test_clones_when_dir_missing(self, mock_dir, mock_run, capsys):
        mock_dir.exists.return_value = False

        checkout_app("abc123", "token")

        output = capsys.readouterr().err
        assert "Cloning" in output
        assert mock_run.call_count == 2  # clone + checkout
