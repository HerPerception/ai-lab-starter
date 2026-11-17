from dataclasses import dataclass
from enum import Enum
import shutil
import subprocess
import sys


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


def main() -> None:
    """Run all environment checks and print formatted results."""
    checks = [check_python(), check_git()]
    for result in checks:
        print(f"[{result.status.value}] {result.name} {result.detail}")
        if result.fix_hint:
            print(f"  -> Fix: {result.fix_hint}")


if __name__ == "__main__":
    main()
