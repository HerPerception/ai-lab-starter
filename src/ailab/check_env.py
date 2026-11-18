from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
import os
import shutil
import subprocess
import sys

from ailab.logging_setup import configure_logging

logger = configure_logging()


class Status(Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    UNDETERMINED = "COULDN'T DETERMINE"


@dataclass
class Result:
    name: str
    status: Status
    detail: str
    fix_hint: str | None = None


MIN_VERSION = "3.10.2"
EXPECTED_API_KEYS: tuple[str, ...] = ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")
PLACEHOLDER_TOKENS: tuple[str, ...] = (
    "your_",
    "your-",
    "changeme",
    "placeholder",
    "replace",
    "example",
    "dummy",
    "insert",
    "todo",
    "...",
)


def check_python(
    version_info: tuple[int, int, int] = sys.version_info[:3],
    min_version: str = MIN_VERSION,
) -> Result:
    """Verify that the active Python version meets the minimum requirement."""
    version_str = ".".join(str(part) for part in version_info)
    min_tuple = tuple(int(part) for part in min_version.split("."))

    if version_info < min_tuple:
        return Result(
            name="Python",
            status=Status.FAIL,
            detail=f"{version_str} (requires {min_version}+)",
            fix_hint=(
                f"Upgrade Python to {min_version} or newer from https://python.org"
            ),
        )

    return Result(name="Python", status=Status.PASS, detail=version_str)


def evaluate_git(
    git_path: str | None,
    version_output: str | None = None,
    error: str | None = None,
) -> Result:
    """Interpret Git discovery and version output into a structured Result."""
    if git_path is None:
        return Result(
            name="Git",
            status=Status.FAIL,
            detail="not found on PATH",
            fix_hint="Install Git from https://git-scm.com",
        )

    if error is not None:
        if "Permission denied" in error:
            return Result(
                name="Git",
                status=Status.UNDETERMINED,
                detail=error,
                fix_hint="Check file permissions for your Git executable",
            )
        return Result(
            name="Git",
            status=Status.UNDETERMINED,
            detail=error,
            fix_hint="Run 'git -v' in your terminal to diagnose the issue",
        )

    clean_version = (version_output or "").replace("git version", "").strip()
    if not clean_version:
        return Result(
            name="Git",
            status=Status.UNDETERMINED,
            detail="found, but version output was empty",
            fix_hint="Run 'git -v' manually to verify your Git installation",
        )

    return Result(name="Git", status=Status.PASS, detail=clean_version)


def check_git(command: list[str] | None = None) -> Result:
    """Locate Git on PATH and verify its version."""
    cmd = command or ["git", "-v"]
    git_path = shutil.which(cmd[0])

    if git_path is None:
        return evaluate_git(git_path=None)

    try:
        completed = subprocess.run(
            args=cmd,
            text=True,
            capture_output=True,
            check=True,
            timeout=5,
        )
        return evaluate_git(git_path=git_path, version_output=completed.stdout)
    except PermissionError:
        return evaluate_git(git_path=git_path, error="Permission denied")
    except subprocess.TimeoutExpired:
        return evaluate_git(git_path=git_path, error="Command timed out after 5s")
    except subprocess.CalledProcessError as exc:
        return evaluate_git(
            git_path=git_path,
            error=f"Exited with status {exc.returncode}",
        )
    except FileNotFoundError:
        return evaluate_git(git_path=None)


def evaluate_venv(
    prefix: str,
    base_prefix: str,
    conda_env: str | None = None,
) -> Result:
    """Determine if an isolated virtual or Conda environment is active."""
    if prefix != base_prefix:
        return Result(
            name="Virtualenv",
            status=Status.PASS,
            detail=f"active ({prefix})",
        )

    if conda_env and conda_env != "base":
        return Result(
            name="Virtualenv",
            status=Status.PASS,
            detail=f"conda ({conda_env})",
        )

    return Result(
        name="Virtualenv",
        status=Status.WARN,
        detail="no active virtual environment detected",
        fix_hint="Create and activate one: python -m venv .venv && source .venv/bin/activate",
    )


def check_venv() -> Result:
    """Inspect Python's runtime prefixes and environment variables for a venv."""
    return evaluate_venv(
        prefix=sys.prefix,
        base_prefix=sys.base_prefix,
        conda_env=os.environ.get("CONDA_DEFAULT_ENV"),
    )


def evaluate_gpu(
    torch_installed: bool,
    cuda_available: bool = False,
    mps_available: bool = False,
    device_name: str | None = None,
    nvidia_smi_device: str | None = None,
    nvidia_smi_error: str | None = None,
) -> Result:
    """Interpret PyTorch and NVIDIA driver facts into a structured Result."""
    if torch_installed and cuda_available:
        return Result(
            name="GPU",
            status=Status.PASS,
            detail=device_name or "CUDA GPU",
        )

    if torch_installed and mps_available:
        return Result(
            name="GPU",
            status=Status.PASS,
            detail=device_name or "Apple Silicon (MPS)",
        )

    if nvidia_smi_error is not None:
        return Result(
            name="GPU",
            status=Status.UNDETERMINED,
            detail=f"nvidia-smi error ({nvidia_smi_error})",
            fix_hint="Run 'nvidia-smi' in your terminal to check driver health",
        )

    if not torch_installed:
        if nvidia_smi_device:
            return Result(
                name="GPU",
                status=Status.UNDETERMINED,
                detail=f"NVIDIA GPU detected ({nvidia_smi_device}), but PyTorch is not installed",
                fix_hint="Install PyTorch with CUDA support using the selector at https://pytorch.org",
            )
        return Result(
            name="GPU",
            status=Status.UNDETERMINED,
            detail="PyTorch not installed and no NVIDIA GPU detected",
            fix_hint="Install the right PyTorch build (CPU, CUDA, or MPS) via https://pytorch.org",
        )

    if nvidia_smi_device:
        return Result(
            name="GPU",
            status=Status.WARN,
            detail=f"NVIDIA GPU detected ({nvidia_smi_device}), but PyTorch is running on CPU",
            fix_hint="Reinstall PyTorch with CUDA enabled using https://pytorch.org",
        )

    return Result(
        name="GPU",
        status=Status.WARN,
        detail="no GPU found, using CPU",
        fix_hint="Nothing needs fixing for CPU work; use a cloud GPU for large models",
    )


def _probe_nvidia_smi() -> tuple[str | None, str | None]:
    """Return (gpu_name, error_message) from nvidia-smi without requiring PyTorch."""
    smi_path = shutil.which("nvidia-smi")
    if smi_path is None:
        return None, None

    try:
        completed = subprocess.run(
            args=[smi_path, "--query-gpu=name", "--format=csv,noheader"],
            text=True,
            capture_output=True,
            check=True,
            timeout=5,
        )
        first_line = completed.stdout.strip().splitlines()
        gpu_name = first_line[0].strip() if first_line else "NVIDIA GPU"
        return gpu_name, None
    except subprocess.TimeoutExpired:
        return None, "timed out after 5s"
    except (subprocess.CalledProcessError, PermissionError, OSError) as exc:
        return None, str(exc)


def check_gpu() -> Result:
    """Probe PyTorch and nvidia-smi to determine GPU availability."""
    try:
        import torch  # type: ignore[import-not-found]

        if torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            return evaluate_gpu(
                torch_installed=True,
                cuda_available=True,
                device_name=f"{name} ({vram_gb:.1f} GB VRAM)",
            )

        mps_backend = getattr(torch.backends, "mps", None)
        if mps_backend is not None and mps_backend.is_available():
            return evaluate_gpu(
                torch_installed=True,
                mps_available=True,
                device_name="Apple Silicon (MPS)",
            )

        gpu_name, smi_error = _probe_nvidia_smi()
        return evaluate_gpu(
            torch_installed=True,
            nvidia_smi_device=gpu_name,
            nvidia_smi_error=smi_error,
        )
    except ImportError:
        gpu_name, smi_error = _probe_nvidia_smi()
        return evaluate_gpu(
            torch_installed=False,
            nvidia_smi_device=gpu_name,
            nvidia_smi_error=smi_error,
        )


def _looks_like_placeholder(value: str) -> bool:
    """Detect common template placeholders without hardcoding every exact string."""
    stripped = value.strip()
    lowered = stripped.lower()

    if (stripped.startswith("<") and stripped.endswith(">")) or (
        stripped.startswith("[") and stripped.endswith("]")
    ):
        return True

    if any(token in lowered for token in PLACEHOLDER_TOKENS):
        return True

    if len(stripped) >= 4 and len(set(stripped)) == 1:
        return True

    return False


def evaluate_api_keys(
    env: Mapping[str, str],
    keys: Sequence[str] = EXPECTED_API_KEYS,
) -> list[Result]:
    """Evaluate expected API keys from an environment mapping without leaking values."""
    results: list[Result] = []

    for key in keys:
        raw_value = env.get(key)

        if raw_value is None:
            results.append(
                Result(
                    name=key,
                    status=Status.WARN,
                    detail="not set (optional for now)",
                    fix_hint=f"Add {key} to your .env file and load it into your environment",
                )
            )
            continue

        if raw_value.strip() == "":
            results.append(
                Result(
                    name=key,
                    status=Status.WARN,
                    detail="set, but empty",
                    fix_hint=f"Provide a non-empty secret value for {key} in your .env file",
                )
            )
            continue

        if _looks_like_placeholder(raw_value):
            results.append(
                Result(
                    name=key,
                    status=Status.WARN,
                    detail="looks like a template placeholder",
                    fix_hint=f"Replace the placeholder in {key} with your real API key",
                )
            )
            continue

        results.append(
            Result(
                name=key,
                status=Status.PASS,
                detail="set",
            )
        )

    return results


def check_api_keys(keys: Sequence[str] = EXPECTED_API_KEYS) -> list[Result]:
    """Read process environment variables and verify expected API keys safely."""
    return evaluate_api_keys(env=os.environ, keys=keys)


CheckFn = Callable[[], Result | list[Result]]


def run_all_checks(
    checks: Sequence[tuple[str, CheckFn]] | None = None,
) -> list[Result]:
    """Execute all configured checks safely so one crash never halts the rest."""
    default_checks: list[tuple[str, CheckFn]] = [
        ("Python", check_python),
        ("Git", check_git),
        ("Virtualenv", check_venv),
        ("GPU", check_gpu),
        ("API Keys", check_api_keys),
    ]
    active_checks = checks if checks is not None else default_checks
    collected: list[Result] = []

    for check_name, check_fn in active_checks:
        try:
            outcome = check_fn()
            if isinstance(outcome, list):
                collected.extend(outcome)
            else:
                collected.append(outcome)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Check '%s' raised an unexpected error", check_name)
            collected.append(
                Result(
                    name=check_name,
                    status=Status.UNDETERMINED,
                    detail=f"unexpected error: {exc}",
                    fix_hint="Re-run with AILAB_LOG_LEVEL=DEBUG to inspect the full traceback",
                )
            )

    return collected


def format_results(results: Sequence[Result]) -> str:
    """Format all check results into a consistent report with a summary footer."""
    lines: list[str] = []

    for result in results:
        lines.append(f"[{result.status.value}] {result.name}: {result.detail}")
        if result.fix_hint:
            lines.append(f"  -> Fix: {result.fix_hint}")

    passed = sum(1 for r in results if r.status == Status.PASS)
    warned = sum(1 for r in results if r.status == Status.WARN)
    failed = sum(1 for r in results if r.status == Status.FAIL)
    undetermined = sum(1 for r in results if r.status == Status.UNDETERMINED)

    lines.append("")
    lines.append(
        f"Summary: {passed} passed, {warned} warnings, {failed} failed, {undetermined} undetermined"
    )
    return "\n".join(lines)


def determine_exit_code(results: Sequence[Result]) -> int:
    """Return 1 if any check failed, 2 if any is undetermined, or 0 otherwise."""
    if any(r.status == Status.FAIL for r in results):
        return 1
    if any(r.status == Status.UNDETERMINED for r in results):
        return 2
    return 0


def main() -> int:
    """Run all environment checks, print the formatted report, and return an exit code."""
    results = run_all_checks()
    print(format_results(results))
    return determine_exit_code(results)


if __name__ == "__main__":
    sys.exit(main())
