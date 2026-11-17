import unittest

from ailab.check_env import Status, evaluate_venv


class TestCheckVenv(unittest.TestCase):
    """Tests for virtual environment detection and warning contracts."""

    def test_evaluate_venv_pass_for_standard_venv(self) -> None:
        """Verify PASS when sys.prefix differs from sys.base_prefix (venv/uv)."""
        result = evaluate_venv(
            prefix="/home/user/project/.venv",
            base_prefix="/usr",
            conda_env=None,
        )

        self.assertEqual(result.name, "Virtualenv")
        self.assertEqual(result.status, Status.PASS)
        self.assertIn("active", result.detail)
        self.assertIsNone(result.fix_hint)

    def test_evaluate_venv_pass_for_conda(self) -> None:
        """Verify PASS when a non-base Conda environment is active."""
        result = evaluate_venv(
            prefix="/opt/conda/envs/ailab",
            base_prefix="/opt/conda/envs/ailab",
            conda_env="ailab",
        )

        self.assertEqual(result.name, "Virtualenv")
        self.assertEqual(result.status, Status.PASS)
        self.assertIn("conda (ailab)", result.detail)
        self.assertIsNone(result.fix_hint)

    def test_evaluate_venv_warn_when_no_env_active(self) -> None:
        """Verify WARN with a fix hint when running in global Python."""
        result = evaluate_venv(
            prefix="/usr",
            base_prefix="/usr",
            conda_env=None,
        )

        self.assertEqual(result.name, "Virtualenv")
        self.assertEqual(result.status, Status.WARN)
        self.assertIsNotNone(result.fix_hint)
        self.assertTrue(len((result.fix_hint or "").strip()) > 0)

    def test_evaluate_venv_warn_when_only_conda_base_active(self) -> None:
        """Verify WARN when only Conda's default 'base' environment is active."""
        result = evaluate_venv(
            prefix="/opt/conda",
            base_prefix="/opt/conda",
            conda_env="base",
        )

        self.assertEqual(result.status, Status.WARN)
        self.assertIsNotNone(result.fix_hint)


if __name__ == "__main__":
    unittest.main()
