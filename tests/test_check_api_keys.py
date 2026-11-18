from contextlib import redirect_stdout
import io
import os
import unittest
from unittest.mock import patch

from ailab.check_env import Status, check_api_keys, evaluate_api_keys


class TestCheckApiKeys(unittest.TestCase):
    """Tests for API key evaluation, warning hints, and secret non-leakage."""

    def test_missing_key_warns_with_fix_hint(self) -> None:
        """Verify WARN with a fix hint when an expected key is not set."""
        results = evaluate_api_keys(env={}, keys=("OPENAI_API_KEY",))

        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertEqual(result.name, "OPENAI_API_KEY")
        self.assertEqual(result.status, Status.WARN)
        self.assertIn("not set", result.detail)
        self.assertIsNotNone(result.fix_hint)
        self.assertTrue(len((result.fix_hint or "").strip()) > 0)

    def test_empty_key_warns_with_fix_hint(self) -> None:
        """Verify WARN with a fix hint when a key is set to empty or whitespace."""
        results = evaluate_api_keys(
            env={"OPENAI_API_KEY": "   "},
            keys=("OPENAI_API_KEY",),
        )

        result = results[0]
        self.assertEqual(result.status, Status.WARN)
        self.assertIn("empty", result.detail)
        self.assertIsNotNone(result.fix_hint)

    def test_placeholder_values_warn_with_fix_hint(self) -> None:
        """Verify WARN when a key matches common template placeholder patterns."""
        placeholders = [
            "<your-openai-key>",
            "[INSERT_KEY_HERE]",
            "sk-your_api_key_here",
            "sk-proj-...",
            "changeme",
            "xxxxxxxxxxxxxxxx",
        ]

        for fake_placeholder in placeholders:
            with self.subTest(placeholder=fake_placeholder):
                results = evaluate_api_keys(
                    env={"OPENAI_API_KEY": fake_placeholder},
                    keys=("OPENAI_API_KEY",),
                )
                result = results[0]
                self.assertEqual(result.status, Status.WARN)
                self.assertIn("placeholder", result.detail)
                self.assertIsNotNone(result.fix_hint)

    def test_real_looking_key_passes_without_hint(self) -> None:
        """Verify PASS with no fix hint when a non-placeholder key is set."""
        results = evaluate_api_keys(
            env={"OPENAI_API_KEY": "sk-proj-99a8b7c6d5e4f3a2b1"},
            keys=("OPENAI_API_KEY",),
        )

        result = results[0]
        self.assertEqual(result.status, Status.PASS)
        self.assertEqual(result.detail, "set")
        self.assertIsNone(result.fix_hint)

    def test_secret_never_leaks_in_results_or_stdout(self) -> None:
        """Prove that full values, partial chunks, and key lengths never appear anywhere."""
        fake_secret = "sk-proj-ULTRASECRET987654321XYZ"
        secret_len_str = str(len(fake_secret))
        forbidden_fragments = [
            fake_secret,
            fake_secret[:6],
            fake_secret[-4:],
            "ULTRASECRET",
            "987654321",
            secret_len_str,
        ]

        with patch.dict(os.environ, {"OPENAI_API_KEY": fake_secret}, clear=True):
            results = check_api_keys(keys=("OPENAI_API_KEY",))
            stdout_buffer = io.StringIO()
            with redirect_stdout(stdout_buffer):
                for res in results:
                    print(f"[{res.status.value}] {res.name}: {res.detail}")
                    if res.fix_hint:
                        print(f"  -> Fix: {res.fix_hint}")

        printed_output = stdout_buffer.getvalue()
        inspected_texts = [printed_output]
        for res in results:
            inspected_texts.extend([res.name, res.detail, res.fix_hint or ""])

        for text in inspected_texts:
            for fragment in forbidden_fragments:
                with self.subTest(fragment=fragment, text=text):
                    self.assertNotIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
