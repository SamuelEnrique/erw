# Session 5169 report: the workflows and what the build offers; a flaw in this chain's own tests, corrected

13 November 2026, unattended, `portable-laptop` window P2. Branches `wip/5166-security` (this report, the tests) and `wip/5157-retire-link` (one test corrected). Model spend USD 0. No pull. Nothing built, nothing landed, no warehouse data written.

Clock: precheck 20:11 UTC, the tests by 20:14 UTC. Inside the long end of 1:00.

## Read these first

- **A flaw of mine in six tests of chain 237, found and corrected. Nothing was hidden behind it.**
  - The tests that scan the site's source drop comments first. The way they did it took out everything between any `/*` and the next `*/`, wherever they stood. An address inside a string (`"/:path*"` beside another) is a slash and a star: real code went out with the comments.
  - What was left unread: 4,680 characters in 3 of 503 files (`components/svgchart.tsx` 2,889, `site/next.config.ts` 1,513, `lib/thesis/server.ts` 278). So "the policy names no `'unsafe-eval'`" was asserted of only part of the configuration.
  - The stripper now works line by line. **Every scan passes with all the code read**: no script, no `eval`, no plain comparison of a token, no cookie, was in the unread parts.
  - The corrected tests are on `wip/5166-security` and `wip/5157-retire-link`. Landing row 23 (`wip/5150-security`) holds the first version: its tests pass and say slightly less than they claim, until this branch lands after it.
- **The fresh pass, continued where chain 237's stopped: nothing found.**
  - The nine workflows set their own permissions, run only GitHub's own actions, and pass every input to a command through the environment, never in the command's line. None runs on a pull request, an issue or a fork.
  - The site has no server action, publishes no source map, lets no SVG or other host's picture through the image optimizer, and has no error page of its own that could print an error.
- **Waits, polled at 20:11 UTC:** landing row 23 not landed; the scan of the git history still running (34 minutes).

## What to review

1. `tests/test_session5169.py`: 9 tests (the workflows, the build's offers).
2. `code()` in `tests/test_session5153.py`: the corrected stripper and what it says of the first one.

## What was done

- **The workflows** read one by one: triggers, `permissions:`, every `uses:`, every `${{ inputs... }}` and `${{ github.event... }}` and the line it stands on (all are named values of a step's `env:`).
- **The site's configuration and tree** read for what a build would publish or accept: no `"use server"` file; `site/next.config.ts` names no `productionBrowserSourceMaps`, `dangerouslyAllowSVG`, `remotePatterns`, `serverActions`; one file uses `next/image` (local pictures); no `error.tsx` or `global-error.tsx`; no `vercel.json`.
- **The test** of all that, so a later change is read: a third-party action, an input written into a command, a server action, a source map.
- **The stripper** corrected in `tests/test_session5153.py`, `5154`, `5162`, `5169` and, on its branch, `5157`; measured against the first one over the site's 503 files (`runs/s5169/stripper.py`).

## Checks, with exit codes

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 5169 (window P2)"` | 0 | on duty |
| `git merge origin/main` | 0 | merged |
| `pytest tests/test_session5169.py` with `5163`, `5161`, first run | 1 | two faults of the new test itself (a workflow's input named like a trigger; the first stripper on the configuration, which is how the flaw was found) |
| the same, corrected | 0 | 24 passed |
| `pytest` on `test_session5153`, `5154`, `5162`, `5169`, `5159`, `5102` with the corrected stripper | 0 | 67 passed |
| `runs/s5169/stripper.py` | 0 | 3 files, 4,680 characters |
| `pytest tests/test_session5157.py` on its branch | 0 | 10 passed |

- **Not run:** the build, the whole suite.

## Decisions made without you

- **Row 23's head not moved for this.** The tests on the row's branch pass; the stronger ones follow in this chain's own row (session 5179). A third push to `main` for a test's wording is not worth a deploy.
- **GitHub's own actions by their major version are left as they are** (`actions/checkout@v4`). Pinning each to a commit is stricter; for the publisher of the platform itself it buys little.

## For Samuel's ruling

Nothing new.

## The prompt

`queue/done/247-day-15-november-portable-p2-security-continued.md`, "Sessions 5175 to 5178: a fresh pass" (taken early: the steps before it wait).
