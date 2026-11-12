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