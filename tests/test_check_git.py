import unittest

from ailab.check_env import Status, check_python, evaluate_git


class TestCheckGit(unittest.TestCase):
    """Tests for Git environment evaluation and failure contracts."""

    def test_evaluate_git_pass(self) -> None:
        """Verify PASS when Git is found and returns a valid version string."""
        result = evaluate_git(
            git_path="/usr/bin/git",
            version_output="git version 2.43.0\n",
        )

        self.assertEqual(result.name, "Git")
        self.assertEqual(result.status, Status.PASS)
        self.assertEqual(result.detail, "2.43.0")
        self.assertIsNone(result.fix_hint)

    def test_evaluate_git_fail_when_missing(self) -> None:
        """Verify FAIL with a fix hint when Git is not found on PATH."""
        result = evaluate_git(git_path=None)

        self.assertEqual(result.name, "Git")
        self.assertEqual(result.status, Status.FAIL)
        self.assertIsNotNone(result.fix_hint)
        self.assertIn("git-scm.com", result.fix_hint or "")

    def test_evaluate_git_fail_when_permission_denied(self) -> None:
        """Verify UNDETERMINED with a fix hint when Git lacks execution permissions."""
        result = evaluate_git(
            git_path="/usr/bin/git",
            error="Permission denied",
        )

        self.assertEqual(result.name, "Git")
        self.assertEqual(result.status, Status.UNDETERMINED)
        self.assertIsNotNone(result.fix_hint)
        self.assertTrue(len((result.fix_hint or "").strip()) > 0)

    def test_evaluate_git_undetermined_on_timeout_or_error(self) -> None:
        """Verify UNDETERMINED when Git hangs or returns empty output."""
        timeout_result = evaluate_git(
            git_path="/usr/bin/git",
            error="Command timed out after 5s",
        )
        empty_result = evaluate_git(
            git_path="/usr/bin/git",
            version_output="",
        )

        self.assertEqual(timeout_result.status, Status.UNDETERMINED)
        self.assertIsNotNone(timeout_result.fix_hint)

        self.assertEqual(empty_result.status, Status.UNDETERMINED)
        self.assertIsNotNone(empty_result.fix_hint)

    def test_all_failures_carry_fix_hint(self) -> None:
        """Confirm that every FAIL outcome includes a helpful fix hint."""
        failing_results = [
            check_python(version_info=(3, 8, 0), min_version="3.10.2"),
            evaluate_git(git_path=None),
        ]

        for result in failing_results:
            with self.subTest(result=result):
                self.assertEqual(result.status, Status.FAIL)
                self.assertIsNotNone(result.fix_hint)
                self.assertTrue(len((result.fix_hint or "").strip()) > 0)


if __name__ == "__main__":
    unittest.main()
