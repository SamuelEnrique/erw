# Session 1450 report: the tracers

Energy Research Warehouse (ERW), session 1450 (chain 149's "1447"), `queue/done/149-day-5-november-code-periodicals-excellent.md`, samueloldlaptop, 6 November 2026, about 03:00 to 03:04 UTC. Model Fable 5.1, high effort. Model spend USD 0. No warehouse data written; nothing sent or posted; web requests to the ERW's own database (the tracer's reads). Branch `wip/1450-periodicals` over `wip/1449-periodicals`.

## What it did, with commits

- **`7f89b3917`**:
  - **The block's story rows are traced** (fault 6): `site/lib/digest.ts` keys a story row of the v2 block ("Datacenter load, Australia: 1,000 MW (...) [3]") as `digest_story|news_stories|<cluster id>|mw` or `|price`, reading the Tables line's "story news:... (mw)" notes; `scripts/check_digest.py` traces the key to the story's scored row in `news_stories.csv` (its `mw`, or the digits of its `price_mentioned`), "not here" when the row is not held. The two rows of the 26 October dry run trace.
  - **A revision stays a revision** (session 1434's note): `check_digest.compare` reads the publisher's window as the issue's (an issue written within the window of the figure's period printed a figure the publisher could still revise), not the retrieval's: the WTI close of 14 October in the issues of 20 and 21 October, re-read on 5 November, is "revised", not FAIL; an issue written after the window that differs is still a fault (the test's fourth case).
  - Tests: `Session1450TheTracers` (a story row traced, not held, wrong; the re-read revision; the settled-figure fault), the node case "a story row of the v2 block is keyed to its story" (14 pass), `test_session2206`'s wording re-pinned.
- The faults file: row 6 fixed.
- Not changed here: the Roundup's five numbers keep their ids and the chart's template and path in the row as `check_roundup.py`'s keys (faults 28, 29 in part); moving them to a Tables line with the regexes is for chain 150 (the chain's session 1444 ran first and left them).

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 1450"` | 0 | |
| `tests.test_session2206`, `2207`, `test_periodicals`, `402` | 0 | 137 passed, 1 skipped |
| `node scripts/test-digest-numbers.mjs` | 0 | 14 passed |
| `scripts/check_digest.py --supabase --then-csv` on this branch's code (`runs/s1450/check_digest.out`) | 0 | 155 ok, 0 FAILED, 2 revised (the WTI close of 14 October in the issues of 20 and 21 October, as session 2207 proved it), 6 not held, 5 from charts, 10 fun facts |

## Decisions made without you

- The story row's price is compared by its digits (the row's `price_mentioned` is the model's verbatim text, "$1.6 Trillion"; the issue prints "USD 1.6 trillion").
- The window rule change makes the tracer gentler on one case only: a differing row retrieved after the window for an issue written inside it. A row retrieved before the issue, or an issue written outside the window, still fails.

## For Samuel's ruling

- None new.
