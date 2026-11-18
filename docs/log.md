## PREDICTION VS. ACTUAL RESULTS
**PREDICTION - 1:** git log would print one commit made yesterday.

**ACTUAL RESULT:** git log actually printed one commit:
```
commit 0158ec02c4abc6526ac7b580a46a6e245f2b398c (HEAD -> main, origin/main)
Date:   Wed Nov 11 17:40:29 2026 +0100

    Add project skeleton
```

**VERDICT:** The prediction matched the output, one commit was printed, date was yesterday.

**PREDICTION - 2:** git status would show an uncommitted file - LOG.md

**ACTUAL RESULT:** On branch main
```
Your branch is up to date with 'origin/main'.
Untracked files:
  (use "git add <file>..." to include in what will be committed)
        LOG.md

nothing added to commit but untracked files present (use "git add" to track)
```

**VERDICT:** The prediction did not exactly match the output, the command printed an untracked file - LOG.md. Untracked files are brand-new files that Git has never been told to watch, whereas uncommitted changes include any modified or staged files whose updates have not yet been saved in a commit.The intuition behind the prediction was correct, but the actual prediction did not match the result.


**PREDICTION - 3:** Running the mv 'LOG.md docs/' command moves the file into the docs folder.

**ACTUAL RESULT:** The folder did not exist originally, but after creating it, that command moved the file into the docs folder.
```
➜  ai-lab-starter git:(docs/add-log) ✗ mv LOG.md docs/
mv: cannot move 'LOG.md' to 'docs/': Not a directory
➜  ai-lab-starter git:(docs/add-log) ✗ mkdir docs
mv LOG.md docs/log.md
➜  ai-lab-starter git:(docs/add-log) ✗ find doc/
find: ‘doc/’: No such file or directory
➜  ai-lab-starter git:(docs/add-log) ✗ find docs/
docs/
docs/log.md
➜  ai-lab-starter git:(docs/add-log) ✗ find docs/*
docs/log.md
➜  ai-lab-starter git:(docs/add-log) ✗ 
```

**VERDICT:** The prediction did not quite match the result because the docs folder was inexistent at the time the prediction was made. The prediction was made with the assumption that the folder already exists.


# Why I Added the pyproject.toml File at Stage 1.
**What it fixes:** Python normally does not know where the local ailab folder lives unless I run commands from the exact right directory.

**How it helps the tests:** Adding pyproject.toml let me install ailab into my venv as an editable package. Now my test files can simply write 'import ailab' from anywhere, and my code edits take effect immediately.


# GIT CHECK FEATURE
## Predicting what could go wrong:
**Git works normally (Pass):** git is installed, runs git --version, and returns a version string with exit code 0.

**Git is not installed (Fail):** Your computer cannot find git anywhere on your system PATH. This is a clear failure and needs a helpful fix hint.

**Git freezes or hangs (Couldn't determine):** Something blocks git from finishing in time (such as a stalled network drive or popup prompt), hitting your timeout limit.

**Git is broken or blocked (Couldn't determine):** A git file exists on your computer, so it is not "missing", but the OS refuses to run it due to a permission error or corrupted file.

## The Python Tools I used:
**shutil.which()**

**subprocess.run()**

*_(The uses of these tools is documented in notebooks/dependencies.md)_*


**PREDICTION - 4:** Running the script after building the git checker feature would print the names and versions of both Python and Git with a PASS status.

**ACTUAL RESULT:** When I ran 'ailab' from the project root directory, it threw errors because the venv was not correctly set up (venv was in the wrong folder and two vital lines in pyproject.toml were commented out by me and I forgot to uncomment it). But after the fix and setting up pyproject.toml and venv correctly, it gave the predicted output:
```
(venv) ➜  ai-lab-starter git:(feature/check-env) ✗ ailab
[PASS] Python 3.12.3
[PASS] Git 2.43.0
(venv) ➜  ai-lab-starter git:(feature/check-env) ✗ 
```

**VERDICT:** The prediction matched the result once the environments were set up. This has taught me to always verify and not assume the right environment needed for my project has been set up and test to make sure. It further strengthens my mindset on the usefulness of this project as it verifies that the right environment is set up and the necessary requirements are satisfied before the programmer starts building.


**PREDICTION - 5:** Running the script after building the venv_checker feature would print versions for both Python and Git and print PASS for all three checks and details for venv.

**ACTUAL RESULT:** 
```
(venv) ➜  ai-lab-starter git:(feature/check-env) ✗ ailab
[PASS] Python 3.12.3
[PASS] Git 2.43.0
[PASS] Virtualenv active (/home/recoding/ai-lab-starter/venv)
```

**VERDICT:** My prediction matched the result, output for venv_checker included the venv path (although I did not include the details for the venv_checker output).


# GPU CHECK FEATURE

## DESIGN DECISIONS
|State | PyTorch Installed? | CUDA/MPS Available? | nvidia-smi works? | Outcome | Detail and Fix_hint |
|------|------|-------|------|-------|--------|
|Everything working(NVIDIA) | Yes | CUDA = True | Yes | PASS | Report device name + VRAM(no hint). |
|Apple Silicon Mac | Yes | MPS = True | No | PASS | Report "Apple Silicon (MPS)" (no hint). |
|NVIDIA hardware present, but CPU-only PyTorch | Yes | False | Yes | WARN | Hardware  exists, but PyTorch can not see it. Hint: reinstall PyTorch with CUDA support. |
|No GPU hardware at all | Yes | False | No(missing/no devices) | WARN | "No GPU found, using CPU". Hint: Nothing needs fixing logically; Use cloud GPUs for heavy training. |
|Driver/tool broken or hanging | Yes | False | Error/Timeout | UNDETERMINED | "nvidia-smi failed or timed out". Hint: run nvidia-smi manually to check driver state. |
|PyTorch not installed | No | N/A | Yes/No | UNDETERMINED (or WARN) | "PyTorch not installed; can not check GPU runtime".Hint:pip install torch |


## PREDICTION(S)
**PREDICTION - 6:** Output after building the GPU_checker feature will include result for the GPU check.

**ACTUAL RESULT:** 
```
(venv) ➜  ai-lab-starter git:(feature/check-env) ✗ ailab
[PASS] Python 3.12.3
[PASS] Git 2.43.0
[PASS] Virtualenv active (/home/recoding/ai-lab-starter/venv)
[COULDN'T DETERMINE] GPU PyTorch not installed; cannot verify GPU access
  -> Fix: Install PyTorch to enable GPU detection: pip install torch
```

**VERDICT:** My prediction matched the output, although my predicition did not include the detail and it was vague. My prediction did not include that the status would be "COULDN'T DETEMINE".

## NOTE FOR THE GPU_CHECKER FEATURE
On my machine (at the time this feature was originally built), the “PyTorch missing” states can no longer be reached by a real run because PyTorch has been installed. Only the fake-input tests exercise them now. That’s a good reason for the asking/deciding split I built, since it lets me test states my machine can’t produce.


# API KEYS SAFETY CHECKER FEATURE
## DESIGN DECISION

|Key State | How to Detect it | Outcome | Detail and Fix_Hint |
|------|------|------|------|
|Not set | val is None (missing from os.environ) | WARN | "OPENAI_API_KEY: not set" + Hint: "Add key to .env and load it into your shell" |
|Set, but empty | val.strip() == "" (blank or spaces only) | WARN | "OPENAI_API_KEY: empty" + Hint: "Set a non-empty value for OPENAI_API_KEY" |
|Placeholder value | Heuristic match (see below) | WARN | "OPENAI_API_KEY: looks like a placeholder" + Hint: "Replace template value with your actual API key" |
|Real_looking value | Non-empty and passes placeholder checks | PASS | "OPENAI_API_KEY: set" (no fix_hint, no length, no prefix). |  

### How to detect a placeholder without hardcoding every string: Check structural patterns common to .env.example templates:
1. Bracketed/templated markers: Starts/ends with <...> or [...] or contains ... (e.g., sk-..., <your-key>).
2. Placeholder keywords (case-insensitive): Contains substrings like your_, your-, changeme, placeholder, replace, example, dummy, insert, or todo.
3. Repeated single character: All characters are identical (e.g., xxxxxxxx or 00000000).

### Test Idea in Plain Words
*"Create a fake environment containing a recognizable secret key (sk-proj-ULTRASECRET987654321XYZ). Run both the evaluation function and the full CLI main() output capture. Inspect every field of the returned Result objects and every character printed to stdout, confirming that neither the full key, any substring of it, nor its character length appears anywhere."*