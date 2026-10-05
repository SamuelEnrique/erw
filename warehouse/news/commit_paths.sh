#!/usr/bin/env bash
# Energy Research Warehouse (ERW), session 119: commit the files under some paths to main from a scheduled run, safely.
#
#   bash warehouse/news/commit_paths.sh "<subject>" "<body>" <path> [<path> ...]
#
# A scheduled run's checkout holds more changes than the ones it means to commit (restored tables' metadata, logs).
# "git pull --rebase" refuses to run over them. On Sunday 4 October 2026 the Roundup's send step pulled that way after
# committing the rendered email: "cannot pull with rebase: You have unstaged changes", exit 128, and the run failed
# after its email had been delivered. This script is that commit done in the order that cannot fail on other files:
#
#   1. stage only the paths named; if nothing under them changed, say so and exit 0;
#   2. commit them;
#   3. set every other change aside (tracked and untracked; ignored files, such as warehouse/output, stay);
#   4. pull main with rebase and push; a push that loses a race pulls and pushes once more;
#   5. put the other changes back, whatever happened in 4. If they cannot be put back cleanly they stay in the stash,
#      named, and the script says so: they were never this commit's.
#
# Exit 0 when the commit is on main or there was nothing to commit; 1 when the push did not go through (the commit is
# then local only, and the next scheduled commit carries it). Never a force push.
set -uo pipefail
subject="$1"; body="$2"; shift 2
if [ "$#" -eq 0 ]; then echo "commit_paths: no path given" >&2; exit 2; fi

git config user.name >/dev/null 2>&1 || git config user.name "github-actions[bot]"
git config user.email >/dev/null 2>&1 || git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

git add -- "$@"
if git diff --cached --quiet; then
  echo "commit_paths: nothing changed under $*; nothing to commit"
  exit 0
fi
git commit --quiet -m "$subject" -m "$body" || { echo "commit_paths: the commit failed" >&2; exit 1; }

mark="commit_paths $(date -u +%Y%m%dT%H%M%SZ) $$"
stashed=0
if [ -n "$(git status --porcelain)" ]; then
  if git stash push --include-untracked --quiet -m "$mark"; then stashed=1; fi
fi

pushed=1
for try in 1 2; do
  if git pull --rebase --quiet origin main && git push --quiet origin HEAD:main; then pushed=0; break; fi
  git rebase --abort >/dev/null 2>&1 || true
  echo "commit_paths: pull and push, try $try, did not go through"
done

if [ "$stashed" -eq 1 ]; then
  if ! git stash pop --quiet; then
    git checkout -- . >/dev/null 2>&1 || true
    echo "commit_paths: the run's other changes could not be put back cleanly; they are in the stash \"$mark\""
  fi
fi

if [ "$pushed" -ne 0 ]; then
  echo "commit_paths FAILED: \"$subject\" is committed here and not on main" >&2
  exit 1
fi
echo "commit_paths: \"$subject\" is on main"
