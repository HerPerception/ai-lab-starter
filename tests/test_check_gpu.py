import unittest

from ailab.check_env import Status, evaluate_gpu


class TestCheckGpu(unittest.TestCase):
    """Tests for GPU state evaluation and non-pass fix hint contracts."""

    def test_cuda_gpu_pass(self) -> None:
        """Verify PASS when PyTorch reports CUDA available."""
        result = evaluate_gpu(
            torch_installed=True,
            cuda_available=True,
            device_name="NVIDIA RTX 4090 (24.0 GB VRAM)",
        )
        self.assertEqual(result.status, Status.PASS)
        self.assertIn("RTX 4090", result.detail)
        self.assertIsNone(result.fix_hint)

    def test_apple_mps_pass(self) -> None:
        """Verify PASS when PyTorch reports Apple Silicon MPS available."""
        result = evaluate_gpu(
            torch_installed=True,
            mps_available=True,
            device_name="Apple Silicon (MPS)",
        )
        self.assertEqual(result.status, Status.PASS)
        self.assertIn("MPS", result.detail)
        self.assertIsNone(result.fix_hint)

    def test_nvidia_hardware_with_cpu_torch_warns(self) -> None:
        """Verify WARN with CUDA hint when nvidia-smi finds a GPU but CUDA is False."""
        result = evaluate_gpu(
            torch_installed=True,
            cuda_available=False,
            nvidia_smi_device="NVIDIA RTX 4090",
        )
        self.assertEqual(result.status, Status.WARN)
        self.assertIn("RTX 4090", result.detail)
        self.assertIsNotNone(result.fix_hint)
        self.assertIn("CUDA", result.fix_hint or "")

    def test_no_gpu_hardware_warns(self) -> None:
        """Verify WARN when neither PyTorch nor nvidia-smi finds a GPU."""
        result = evaluate_gpu(
            torch_installed=True,
            cuda_available=False,
            nvidia_smi_device=None,
        )
        self.assertEqual(result.status, Status.WARN)
        self.assertIn("CPU", result.detail)
        self.assertIsNotNone(result.fix_hint)

    def test_missing_pytorch_without_gpu_is_undetermined(self) -> None:
        """Verify UNDETERMINED when PyTorch is missing and no NVIDIA GPU is found."""
        result = evaluate_gpu(torch_installed=False, nvidia_smi_device=None)
        self.assertEqual(result.status, Status.UNDETERMINED)
        self.assertIn("no NVIDIA GPU detected", result.detail)
        self.assertIsNotNone(result.fix_hint)

    def test_missing_pytorch_with_nvidia_gpu_reports_hardware(self) -> None:
        """Verify UNDETERMINED includes the detected GPU name when PyTorch is missing."""
        result = evaluate_gpu(
            torch_installed=False,
            nvidia_smi_device="NVIDIA RTX 4090",
        )
        self.assertEqual(result.status, Status.UNDETERMINED)
        self.assertIn("RTX 4090", result.detail)
        self.assertIsNotNone(result.fix_hint)

    def test_driver_error_is_undetermined(self) -> None:
        """Verify UNDETERMINED when nvidia-smi errors or times out."""
        result = evaluate_gpu(
            torch_installed=True,
            cuda_available=False,
            nvidia_smi_error="timed out after 5s",
        )
        self.assertEqual(result.status, Status.UNDETERMINED)
        self.assertIsNotNone(result.fix_hint)

    def test_all_non_pass_outcomes_carry_fix_hint(self) -> None:
        """Confirm every WARN or UNDETERMINED outcome includes a fix hint."""
        non_pass_cases = [
            evaluate_gpu(torch_installed=True, nvidia_smi_device="NVIDIA RTX 4090"),
            evaluate_gpu(torch_installed=True, nvidia_smi_device=None),
            evaluate_gpu(torch_installed=False, nvidia_smi_device=None),
            evaluate_gpu(torch_installed=False, nvidia_smi_device="NVIDIA RTX 4090"),
            evaluate_gpu(torch_installed=True, nvidia_smi_error="driver error"),
        ]
        for result in non_pass_cases:
            with self.subTest(result=result):
                self.assertNotEqual(result.status, Status.PASS)
                self.assertIsNotNone(result.fix_hint)
                self.assertTrue(len((result.fix_hint or "").strip()) > 0)


if __name__ == "__main__":
    unittest.main()
