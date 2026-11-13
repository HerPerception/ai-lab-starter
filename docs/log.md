# PREDICTION VS. ACTUAL RESULTS
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

**VERDICT:** The command did not quite match the result because the docs folder was inexistent at the time the prediction was made. The prediction was made with the assumption that the folder already exists.


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