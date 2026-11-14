# Session 5162 report: the fresh pass, part 4: the usage counts' method note against the code

13 November 2026, unattended, `portable-laptop` window P2. Branch `wip/5150-security`, worktree `erw-p2-5150`. Model spend USD 0. No pull. Nothing built, nothing landed, no warehouse data written.

Clock: the read from 19:40 UTC while session 5161's scan of the history ran; the tests by 19:42 UTC. Inside the long end of 1:00.

## Read these first

- **The method stands.** Every number and every list in `docs/methods/usage_counts.md` is the code's: the four events, the path's form and its 120 characters, the daily code's two steps, the limits (600 counts an hour, 400 lines a code a day, 200,000 lines a day), the quiet pages, what is never read.
- **The note was wrong or silent in three places, now corrected in the note** (the code is unchanged):
  - "Scenario compared" was described as an event a tool sends. No tool sends it.
  - Four cases in which nothing is counted were not said: a body over 600 characters or of the wrong kind; more than 600 counts an hour from one address; a server without its secret or a visitor whose address is not known; an address under `/api/`, `/internal/` or `/_next/`.
  - The site's own checks can add page views (row 32, below).
- **Row 32, noted.** A site built on a machine that holds the secrets writes its page views into the same counts. Of the checks that drive a browser, only `check-links.mjs` asks not to be counted. So a landing's checks can appear in a day's counts as readers. Not measured: a day's codes cannot be told apart by where they came from.
- **A test now holds the note to the code line by line** (`tests/test_session5162.py`, 9 tests). The note is the promise `/privacy` points a reader to.

## What to review

1. `docs/methods/usage_counts.md`: the three corrections ("The four events", "What this cannot promise", "When nothing is counted").
2. `tests/test_session5162.py`.
3. Row 32 of `docs/reviews/security-faults-2026-11-13.md`.

## What was done

- **The read**: the note's 14 statements, each against `site/lib/usage.ts`, `site/components/Usage.tsx`, `site/app/api/usage/route.ts`, `site/lib/usagepath.ts`, `site/lib/guard.ts` and migration 028's three functions (each closes the day before: `usage_rollover` is called by all three, as the note says).
- **`/privacy` read** (`site/app/privacy/page.tsx`): its account of the count matches the code as it runs by default. Its sentence on limits names four things the site limits per address; this stack adds limits on the map's cards and the email's links, which the sentence does not name. Ruling 1.
- **The checks read**: `check-links.mjs` sends `DNT` and `Sec-GPC` and blocks `/api/usage`; `check-security.mjs` posts to the route on purpose (five requests that must be answered 204); the other browser checks send nothing of the kind.

## Checks, with exit codes

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 5162 (window P2)"` | 0 | on duty. **Run at 19:42 UTC, after the read had begun** (a fault of order, below) |
| `pytest` on `test_session5162`, `5155`, `5154`, `177` | 0 | 55 passed |

## A fault of mine

- This session's read began while session 5161 waited on its scan of the history, before this session's own precheck. The precheck ran at 19:42 UTC and passed; nothing had been pushed or written outside the worktree before it. The chain's rule is precheck first.

- **Not run:** the build, the route against a database.
- **Not verified:** how many of a day's page views are a check's (row 32).

## Decisions made without you

- **The note corrected, the code left.** In each of the three places the code was right and the note behind it.
- **Row 32 not fixed here**: the checks' scripts are the landing desk's, and a check that stops counting must still prove the count works (`check-security.mjs` and `check-battery-scenarios.mjs` read the count's request on purpose).

## For Samuel's ruling

1. `/privacy`, the sentence on limits. Default: when this stack lands, a session adds "the map's cards and the email's links" to it. Until then the page says less than the site does, and nothing false.
2. Row 32. Default: the browser checks send Do Not Track, except the two that read the count itself.

## The prompt

`queue/done/237-day-14-november-portable-p2-security-continued.md`, "Sessions 5159 to 5162: a fresh pass".
