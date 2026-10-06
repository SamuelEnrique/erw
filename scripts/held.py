#!/usr/bin/env python3
"""The files a review freeze holds back from main (session 131; docs/freeze_hold.md).

Energy Research Warehouse (ERW). Under a freeze, with the hold switched on (scripts/freeze.py hold), a scheduled job
does not commit to main: a commit to main redeploys the site. Its files go to one branch, held/scheduled, which no
page is built from, and come to main with the first scheduled run after the freeze ends.

    python scripts/held.py restore                    # start of every scheduled run: put the held files in the working tree
    python scripts/held.py commit -m "..." -- PATHS   # a held run: commit these paths to held/scheduled, never to main
    python scripts/held.py clear                      # after the first commit to main once the freeze has ended
    python scripts/held.py status                     # what is held, read only

How it works.
  restore   When origin has no branch held/scheduled, nothing happens (the usual case). When it has, every file the
            held runs committed is written into the working tree, unstaged, over main's copy, and listed in
            runs/held_files.txt. So a run during a long freeze starts from yesterday's held state (the news already
            scored, the archive's manifest, the status history), exactly as it would have started from main; and the
            first run after the freeze commits those files to main with its own.
  commit    Builds the commit without touching the checkout: the parent is held/scheduled's tip (or main's, for the
            first held run), the tree is the parent's with the given paths as they are in the working tree, and the
            list of every path held so far is kept on the branch itself, in .held/files.txt. Pushed to
            refs/heads/held/scheduled. Nothing changed: no commit, exit 0.
  clear     Deletes origin's held/scheduled. The workflow calls it only after its push to main succeeded.

The branch holds nothing a visitor reads and Vercel must not build it (docs/freeze_hold.md, what to approve). It is
never merged: its files are copied. Only git and Python's standard library.
"""

import argparse
import os
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
BRANCH = "held/scheduled"
REMOTE = "origin"
MANIFEST = ".held/files.txt"
LIST = os.path.join("runs", "held_files.txt")


def git(*args, cwd=None, env=None, stdin=None, check=True):
    r = subprocess.run(["git", *args], cwd=cwd or ROOT, env=env, input=stdin, capture_output=True, text=True, encoding="utf-8")
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args[:3])} failed (exit {r.returncode}): {r.stderr.strip()[:300]}")
    return r.stdout.strip() if check else r


def tip(cwd=None):
    """The commit origin's held/scheduled points at, fetched, or None when origin has no such branch."""
    if not git("ls-remote", "--heads", REMOTE, BRANCH, cwd=cwd):
        return None
    git("fetch", "--quiet", "--no-tags", REMOTE, f"+refs/heads/{BRANCH}:refs/remotes/{REMOTE}/{BRANCH}", cwd=cwd)
    return git("rev-parse", f"refs/remotes/{REMOTE}/{BRANCH}", cwd=cwd)


def manifest(commit, cwd=None):
    """Every path the held runs committed, from the branch's own list."""
    r = git("show", f"{commit}:{MANIFEST}", cwd=cwd, check=False)
    return [p for p in r.stdout.splitlines() if p.strip()] if r.returncode == 0 else []


def restore(cwd=None):
    """Put every held file in the working tree, unstaged. Returns the paths (none when nothing is held)."""
    cwd = cwd or ROOT
    out = os.path.join(cwd, LIST)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    head = tip(cwd)
    files = manifest(head, cwd) if head else []
    if files:
        git("checkout", head, "--", *files, cwd=cwd)
        git("reset", "--quiet", "--", *files, cwd=cwd)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("".join(p + "\n" for p in files))
    return files


def commit(paths, message, cwd=None):
    """Commit the given paths, as they are in the working tree, to held/scheduled. Returns the commit, or None when
    nothing differs from what is already held."""
    cwd = cwd or ROOT
    parent = tip(cwd) or git("rev-parse", "HEAD", cwd=cwd)
    held = manifest(parent, cwd)
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ, GIT_INDEX_FILE=os.path.join(tmp, "index"))
        git("read-tree", parent, cwd=cwd, env=env)
        there = [p for p in paths if os.path.lexists(os.path.join(cwd, p))]
        if there:
            git("add", "--", *there, cwd=cwd, env=env)
        changed = [p for p in git("diff", "--cached", "--name-only", parent, cwd=cwd, env=env).splitlines() if p and p != MANIFEST]
        if not changed:
            return None
        listed = sorted(set(held) | set(changed))
        blob = git("hash-object", "-w", "--stdin", cwd=cwd, stdin="".join(p + "\n" for p in listed))
        git("update-index", "--add", "--cacheinfo", f"100644,{blob},{MANIFEST}", cwd=cwd, env=env)
        tree = git("write-tree", cwd=cwd, env=env)
    new = git("commit-tree", tree, "-p", parent, "-m", message, cwd=cwd)
    git("push", "--quiet", REMOTE, f"{new}:refs/heads/{BRANCH}", cwd=cwd)
    return new


def clear(cwd=None):
    """Delete origin's held/scheduled. True when there was one."""
    if not git("ls-remote", "--heads", REMOTE, BRANCH, cwd=cwd):
        return False
    git("push", "--quiet", REMOTE, "--delete", BRANCH, cwd=cwd)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser(description="The files a review freeze holds back from main")
    ap.add_argument("action", choices=["restore", "commit", "clear", "status"])
    ap.add_argument("-m", "--message", default="Held by the review freeze")
    ap.add_argument("paths", nargs="*")
    a = ap.parse_args(argv)
    try:
        if a.action == "restore":
            files = restore()
            print(f"held: {len(files)} held files put in the working tree ({LIST.replace(os.sep, '/')})" if files
                  else f"held: nothing is held (origin has no branch {BRANCH}, or it lists no file)")
        elif a.action == "commit":
            if not a.paths:
                raise RuntimeError("commit needs the paths to hold")
            new = commit(a.paths, a.message)
            print(f"held: committed {new[:7]} to {BRANCH}; nothing was pushed to main" if new
                  else f"held: nothing differs from what {BRANCH} already holds; no commit")
        elif a.action == "clear":
            print(f"held: {BRANCH} deleted from origin" if clear() else f"held: origin has no branch {BRANCH}; nothing to clear")
        else:
            head = tip()
            files = manifest(head) if head else []
            print(f"held: {len(files)} files on {BRANCH} at {head[:7]}" if head else f"held: origin has no branch {BRANCH}")
            for p in files:
                print("  " + p)
    except RuntimeError as e:
        print(f"held FAILED: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
