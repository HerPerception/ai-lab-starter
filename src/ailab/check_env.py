from dataclasses import dataclass
from enum import Enum
import shutil, subprocess, sys


class Status(Enum):
  PASS = "PASS"
  WARN = "WARN"
  FAIL = "FAIL"


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


def check_git(runtime_val: str):
  re = shutil.which(' '.join(runtime_val))
  res = subprocess.run(args=runtime_val, text=True, capture_output=True, check=True, timeout=5)
  return re, res

if __name__ == "__main__":
  output = check_python()
  print(f"[{output.status.value}] {output.name} {output.detail}")
  if output.fix_hint:
    print(f"  -> Fix: {output.fix_hint}")

print(check_git(["git", "-v"]))