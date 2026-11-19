
# Lessons Map

| Stage | Lesson Concept | Where Applied in Code | Key Takeaway |
| :--- | :--- | :--- | :--- |
| **Stage 1** | **Git & Branching** | `.gitignore`, `feature/check-env` branch | Ignore virtual environments, `.env` secrets, and build artifacts; commit small, tested pieces. |
| **Stage 1** | **Python Packaging & CLI** | `pyproject.toml` (`[project.scripts]`), `src/` layout | Installing in editable mode (`pip install -e .`) registers the `ailab` entry point cleanly. |
| **Stage 1** | **Subprocesses & Failure Modes** | `check_git()`, `check_gpu()` (`subprocess.run`) | Always set `timeout`, catch missing/broken binaries, and separate system probes from decision logic. |
| **Stage 1** | **Safe Secret Handling** | `evaluate_api_keys()`, `test_check_api_keys.py` | Check `os.environ` without ever printing secret values, substrings, or character lengths. |