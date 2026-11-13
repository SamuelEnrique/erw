# Session 5175 report: the repository at GitHub: two things for the owner (rows 33 and 34)

13 November 2026, unattended, `portable-laptop` window P2. Branch `wip/5166-security`, worktree `erw-p2-5150`. Model spend USD 0. Pulls: eleven GET requests of GitHub's API for this repository, with the machine's token (never printed). Nothing built, nothing landed, no warehouse data written; nothing changed at GitHub.

Clock: precheck 20:37 UTC, the read 20:39 UTC, the records by 20:42 UTC. Inside the long end of 1:00.

## Read these first

- **Row 33: Dependabot alerts are off.** GitHub's own words: "Dependabot alerts are disabled for this repository." So a new advisory on a package the site or the warehouse uses is seen only when a session runs the audits by hand. This morning's `certifi` (a compromised root in the bundle) is the kind of thing an alert would have shown weeks earlier.
  - **Yours to turn on**: GitHub, the repository, Settings, Advanced Security: "Dependabot alerts". On the same page, look that "Secret scanning" and "Push protection" are on. They cost nothing on a public repository. No session's token can change or even read them.
- **Row 34: the repository is public, and this list is in it.** A fault written into a report, a landing row or the list is published when it is pushed, before its fix lands. Row 1's account, with the address that opened a page in review, was public for about three hours before the landing.
  - Nothing in the list today is an open door (every row is fixed, a ruling with no exploit in its words, or noted).
  - The ruling is about the next High row: say less until it lands. Default below.
- **What else was read**: the repository has no fork, one collaborator (you, admin), no ruleset. The machine's token is a fine-grained one: it was refused the branch's protection, the Actions' defaults, the security settings, the webhooks and the deploy keys (403 each). That is as it should be for a token that pushes code; it also means those settings are only yours to look at.
- **Waits, polled at 20:37 UTC:** landing row 23 not landed; the scan of the git history still running (64 minutes at 20:41 UTC).

## What to review

1. Rows 33 and 34 of `docs/reviews/security-faults-2026-11-13.md`.
2. The list's count: 34 rows, none open; 1 closed, 10 fixed and waiting, 15 rulings, 8 noted.

## Checks, with exit codes

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 5175 (window P2)"` | 0 | on duty |
| `git merge origin/main` | 0 | merged |
| `gh api ...` | 1 | `gh` is not on this machine; the same reads made with Python and the machine's token |
| `runs/s5175/github.py` | 0 | as above |
| `pytest tests/test_session5163.py` (the list's count against its rows) | 0 | 6 passed |
| `git push origin wip/5166-security` (session 5174's), first try | 1 | "remote rejected (missing necessary objects)"; every object was present here (`git rev-list --objects --missing=print`: none missing); the second try, a minute later: exit 0 |

- **Not run:** the build, the whole suite.
- **Not verified:** whether secret scanning, push protection and the main branch's protection are on. The token is not shown them.

## Decisions made without you

- **GitHub's API asked with the machine's token**, GET only. The repository's own host; nothing of the token or of you was sent anywhere else.
- **Row 34 written into the public list.** It names nothing that is open, and the ruling it asks for is about how the list itself is written.

## For Samuel's ruling

1. Row 33. Default: you turn on Dependabot alerts, and look at secret scanning and push protection on the same page.
2. Row 34. Default: for a row of High severity, the landing row says "an urgent security fix" and no more; the account is pushed once the fix has landed. Lower rows as now.

## The prompt

`queue/done/247-day-15-november-portable-p2-security-continued.md`, "Sessions 5175 to 5178: a fresh pass".
