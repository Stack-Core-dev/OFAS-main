# Git Workflow

This guide explains how to save OFAS changes in Git and upload them to GitHub.

## Open the project

Open a new PowerShell window and run:

```powershell
cd D:\Projects\OFAS
```

Opening a new window ensures that Git is available after it was added to the
Windows user `PATH`.

## Check the current state

Before committing, review the changed files:

```powershell
git status
git diff
```

Do not commit passwords, access tokens, local credentials, virtual
environments, build folders, or generated files. The repository `.gitignore`
already excludes the main local and generated artifacts.

## Stage changes

Stage all intended changes:

```powershell
git add -A
```

Review the staged files before creating the commit:

```powershell
git diff --cached --stat
git diff --cached
```

If an unintended file was staged, remove it from the commit while keeping it
on your computer:

```powershell
git restore --staged path\to\file
```

## Create a commit

Use a short, descriptive message:

```powershell
git commit -m "Update field assignment status labels"
```

Examples:

```text
Add user management controls
Fix surveyor assignment validation
Update production documentation
Update field assignment status labels
```

## Upload the commit

Push the commit to GitHub:

```powershell
git push
```

The first push for a new branch may require:

```powershell
git push -u origin master
```

For HTTPS authentication, use your GitHub username and a GitHub Personal
Access Token instead of your GitHub account password.

## Normal workflow for future changes

Run this sequence whenever you finish a change:

```powershell
cd D:\Projects\OFAS
git status
git add -A
git diff --cached --stat
git commit -m "Describe the completed change"
git push
```

## If the remote contains newer changes

If `git push` is rejected because GitHub has commits that are not present
locally, update the local branch first:

```powershell
git pull --rebase origin master
git push
```

If conflicts occur, resolve the marked files, then run:

```powershell
git add path\to\resolved-file
git rebase --continue
git push
```

## Verify the result

After pushing, confirm that the local working tree is clean:

```powershell
git status
git log -1 --oneline
git remote -v
```

The latest commit should appear in the GitHub repository:

```text
https://github.com/Stack-Core-dev/OFAS-main
```
