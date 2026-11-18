import logging
import unittest

from ailab.check_env import (
    Result,
    Status,
    determine_exit_code,
    format_results,
    run_all_checks,
)


class TestOrchestrator(unittest.TestCase):
    """Tests for check orchestration, crash isolation, formatting, and exit codes."""

    def test_crashing_check_does_not_stop_remaining_checks(self) -> None:
        """Verify an unexpected exception becomes UNDETERMINED and subsequent checks still run."""
        logging.disable(logging.CRITICAL)
        self.addCleanup(logging.disable, logging.NOTSET)

        def passing_check() -> Result:
            return Result(name="First", status=Status.PASS, detail="ok")

        def broken_check() -> Result:
            raise RuntimeError("boom")

        def final_check() -> Result:
            return Result(name="Third", status=Status.PASS, detail="still ran")

        results = run_all_checks(
            checks=[
                ("First", passing_check),
                ("Broken", broken_check),
                ("Third", final_check),
            ]
        )

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].status, Status.PASS)
        self.assertEqual(results[1].name, "Broken")
        self.assertEqual(results[1].status, Status.UNDETERMINED)
        self.assertIn("boom", results[1].detail)
        self.assertIsNotNone(results[1].fix_hint)
        self.assertEqual(results[2].status, Status.PASS)

    def test_format_results_consistent_shape_and_summary(self) -> None:
        """Verify every line follows '[STATUS] Name: detail' and ends with summary counts."""
        sample = [
            Result(name="Python", status=Status.PASS, detail="3.12.3"),
            Result(
                name="GPU",
                status=Status.WARN,
                detail="no GPU found, using CPU",
                fix_hint="Use cloud GPU for large models",
            ),
        ]

        output = format_results(sample)
        lines = output.splitlines()

        self.assertEqual(lines[0], "[PASS] Python: 3.12.3")
        self.assertEqual(lines[1], "[WARN] GPU: no GPU found, using CPU")
        self.assertEqual(lines[2], "  -> Fix: Use cloud GPU for large models")
        self.assertEqual(
            lines[-1],
            "Summary: 1 passed, 1 warnings, 0 failed, 0 undetermined",
        )

    def test_exit_codes_for_all_outcomes(self) -> None:
        """Verify exit code rules: 0 for pass/warn, 1 for fail, 2 for undetermined."""
        pass_only = [Result(name="A", status=Status.PASS, detail="ok")]
        with_warn = [
            Result(name="A", status=Status.PASS, detail="ok"),
            Result(name="B", status=Status.WARN, detail="warn", fix_hint="hint"),
        ]
        with_undetermined = [
            Result(name="A", status=Status.WARN, detail="warn", fix_hint="hint"),
            Result(name="B", status=Status.UNDETERMINED, detail="unknown", fix_hint="hint"),
        ]
        with_fail = [
            Result(name="A", status=Status.UNDETERMINED, detail="unknown", fix_hint="hint"),
            Result(name="B", status=Status.FAIL, detail="bad", fix_hint="hint"),
        ]

        self.assertEqual(determine_exit_code(pass_only), 0)
        self.assertEqual(determine_exit_code(with_warn), 0)
        self.assertEqual(determine_exit_code(with_undetermined), 2)
        self.assertEqual(determine_exit_code(with_fail), 1)


if __name__ == "__main__":
    unittest.main()
