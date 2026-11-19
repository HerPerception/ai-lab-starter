# AI-LAB-STARTER

> A one-command health check and speed test that verifies if a machine is ready for AI work, measures CPU/GPU performance, and estimates the largest model it can hold.

## How to Run

1. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install the package in editable mode:**
   ```bash
   pip install -e .
   ```

3. **Run the environment check:**
   ```bash
   ailab
   ```

4. **Run the unit test suite:**
   ```bash
   python -m unittest discover -s tests -v
   ```

### Exit Codes

| Exit Code | Meaning | When It Happens |
| :--- | :--- | :--- |
| `0` | Ready to run | All checks passed, or only non-blocking warnings occurred (such as no GPU or optional API keys unset). |
| `1` | Environment broken | One or more checks failed (such as missing Git or an unsupported Python version). |
| `2` | Inconclusive | No checks failed, but at least one check could not complete or determine a result. |


***Note:** On a fresh setup without PyTorch installed, the GPU check reports COULDN'T DETERMINE (exit code 2) and provides a link to install the right PyTorch build for your hardware.*

### Current Scope (Stage 1)
* **Included:** Environment diagnostics for Python version, Git, active virtual environment, GPU/PyTorch visibility, and environment variables.
* **Not yet implemented:** CPU/GPU matrix multiplication benchmarks, VRAM model capacity estimation, and automatic `.env` file loading.

## Results

## What Broke

## Structure
