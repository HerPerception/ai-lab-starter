import unittest
from ailab.check_env import Result, Status, check_python


class TestCheckEnv(unittest.TestCase):

  def test_python_version_at_minimum(self):
    result = check_python(version_info=(3, 10, 2), min_version="3.10.2")
    self.assertEqual(
        result,
        Result(
            name="Python",
            status=Status.PASS,
            detail="3.10.2",
            fix_hint=None,
        ),
    )

  def test_python_version_above_minimum(self):
    result = check_python(version_info=(3, 12, 3), min_version="3.10.2")
    self.assertEqual(result.status, Status.PASS)
    self.assertEqual(result.detail, "3.12.3")
    self.assertIsNone(result.fix_hint)

  def test_python_version_below_minimum(self):
    result = check_python(version_info=(3, 9, 18), min_version="3.10.2")
    self.assertEqual(result.status, Status.FAIL)
    self.assertIn("3.9.18", result.detail)
    self.assertIsNotNone(result.fix_hint)


if __name__ == "__main__":
  unittest.main()
