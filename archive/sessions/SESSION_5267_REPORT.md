# Session 5267: a query says whether its window is whole

Energy Research Warehouse (ERW). portable-laptop, window P3, 14 November 2026 (09:06 to 09:16 UTC), Fable, unattended. Chain 256. Branch `wip/5200-ask-close` (worktree `erw-p3-5264`). Nothing built, nothing landed, no model call, no warehouse data written.

## Read these first

- **A query of a series with a start and an end now says whether its window is whole**, in both loops, under `window`: the steps held, the steps the window has at the table's step, the runs of steps missing.
- **It asks the database nothing more.** It is made from the rows the query already read and the table's step. No request is added and none is changed.
- **It never guesses.** Where the step cannot be told, `whole` is null and the note says so.
- **A whole window of a table of months or days is not a whole month.** Such a table says in a variable of its own whether a row covers its period; the note says that.
- No model was called: what it does to the chat's calls is measured from session 5269.

## What was done

- Precheck from the main checkout: exit 0.
- **The function, twice:** `warehouse/chat/window.py` `window_of` and `site/lib/chat/window.ts` `windowOf`, pure, with no imports on the site's side so that `node --test` runs it with no build.
- **35 made windows** (`tests/fixtures/session5267/window_cases.json`), answered alike by both: a whole day, a local day, runs missing, a day with nothing held, 15 and 5 minute steps, a table of two steps, days, months, years, weeks, two series, a row off the step's grid, a window shorter than a step, the day the clocks go back (25 hours).
- **The tools:** `site/lib/chat/tools.ts` `query` and `warehouse/chat/tools.py` `query` add `window` when the table is a series and both bounds are given. The rows counted are those in the window before a threshold keeps some.
- **The step.** The Python loop reads the table's `freq` values. The site's loop reads no `freq` with its rows, so it takes the steps the catalogue lists for the table; of several, the smallest gap between two neighbouring rows of a series when that gap is one of them.

## Why no request is added

- The stored tests of sessions 143, 148, 156 and 161 replay reads recorded from the live set and fail on any request that was not recorded. A `freq` added to the read's select, or one small read more, would have failed four scripts.
- So the site's step is the catalogue's, which the query has already read.

## What the stored tests needed

- Three scripts compare a whole tool result with a recorded one (`test-ask-161.mjs`, `test-ask-ready.mjs`, `test-ask-speed.mjs`). They failed on the new key and nothing else.
- They now set `window` apart, as session 168 set its local words apart in the same lines, and check it on the recorded rows: four Central days of hourly demand, 96 of 96; seven days of every fuel, each 168 of 168; September's thirty days; one month, 1 of 1.

## Checks run

- `tests/test_session5267_ask.py`: 13 passed (the function, the Python tool on session 1300's rows, the site's function through `node --test`, the sources).
- `node --test site/scripts/test-ask-window.test.mjs`: 6 of 6.
- Every Node script of the chat on the main checkout's packages (21 scripts): each exit 0.
- `tests/test_session1300.py`, both loops turn by turn: passed.
- Type check of `window.ts`, `tools.ts` and `panel.ts` with the main checkout's compiler: no error in the three. Two in `site/lib/supabase.ts`, which this stack does not touch (Next's own fetch types, which this narrow check lacks; session 5257 met the same two).
- The wide run is in session 5268's report.

## Model spend

- Estimate before: USD 0.00. Actual: USD 0.00. Chain 256: USD 0.00 of USD 20.

## Decisions made without you

- **Built in this chain.** Sessions 5251 and 5257 left it for a ruling with the default "not built in this chain", chain 238. It is on a `wip/` branch, measured before and after, and one block of each tool takes it out.
- **The stored replays set the key apart and were not recorded again.** Their recordings are of 8 October; a new recording would change every figure they pin.
- **Only with both bounds.** A window with one bound has no end to count to. The forms "newest day" and "this week" keep their own count.
- **Six runs of missing steps are shown**, with the count of all.

## For Samuel's ruling

- None new.
