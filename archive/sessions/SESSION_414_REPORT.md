# Session 414 report: /internal/waits, each ruling once

21 October 2026, about 03:00 to 04:30 UTC, unattended, on samueloldlaptop (the code machine), in the worktree `C:\Users\lossa\Documents\erw-414` on `wip/414-s` (cut from `wip/381-382-land`, which holds the reports of sessions 367 to 383). The chain of 20 to 21 October (`queue/done/015-day-20-october-code-pm.md`, "Session 414"). Model spend USD 0. No pull, no warehouse data written.

## Read these first

- **`/internal/waits` opens with a ledger of sessions 351 to 413**: every item of the ruling sections of those reports, listed once, with a count at the top (48 items from 54 lines, 6 merged, 34 reports read), the three the notes rank highest first, then five groups by what each blocks: money (2), a data pull (18), a ruling on a figure (4), a public page (13), none of the four (11). The report-by-report list of session 188 stays below it, unchanged.
- **The first three, as the notes rank them**: `docs/state/morning_2026-10-21_day.md`, its list "highest value first", items 1 to 3: the Redivis storage (asked in 358, 363, 377 and 385, one item), the four permission letters (378), `nyiso_load_queue` public or internal (375). Only a note whose list says it is ranked by value ("highest value first", "in the order of their value") ranks; the night and day notes of the code machine number their lists without saying so, and the page shows their positions beside each item but takes no rank from them. Where no note ranks by value, the page says so and puts nothing first.
- **No model, fixed rules, each printed on the page**, with the words that matched: why two lines are one item, which rule placed an item in its group, and which note ranks it. The rules are in `site/scripts/build-waits.mjs` (`LEDGER`, `SUBJECTS`, `BLOCK_RULES`, `NAMED`, `SAME`, `NOTE_MATCH`, `BY_VALUE`).
- **This branch held the reports of sessions 351 to 383 and 385** (384 and 386 to 413 were not on it). The code reads whatever is in `archive/sessions/` at build time: each report of 401 to 413 joins the ledger at the first build after it lands, and the page names the sessions of the run it did not read.

## What to review

- After the landing, in the internal view (open `/internal/open`, then): `/internal/waits`. The ledger is the first section; "The rules, as the build applied them" folds out at its end; each merged item has "Why these are one item, and each report's own words".
- The shots (dev server, 21 October 03:34 UTC): `https://github.com/SamuelEnrique/erw/tree/wip/414-s/docs/brand/review-414` (`waits-desktop.png` at 1280 px, `waits-phone.png` at 390 px).
- The code: `site/scripts/build-waits.mjs` (the part headed "Session 414: the ledger"), `site/app/internal/waits/page.tsx` (`LedgerSection`), `site/lib/waits.ts`, `site/scripts/test-waits-ledger.mjs`, `site/scripts/check-internal-waits.mjs` (seven ledger checks added), `tests/test_session414.py`, `docs/machines.md` ("Each ruling once (session 414)").

## Checks

Every gate redirected to a file under `runs/chain_oct21/s414/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `node site/scripts/test-waits-ledger.mjs` | 0 | 212 of 212 held (written cases, and the repository's own reports: every line of the run in one item, each link on its line) |
| `node site/scripts/test-waits.mjs` (session 188's reader) | 0 | 3,285 of 3,285 held |
| `tests.test_session414`, `tests.test_session188_waits`, `tests.test_session160_waits` | 0 | 33 tests OK, 1 skipped (160's saved copies are not on this machine) |
| `npm ci` in the worktree's `site/` | 0 | |
| `duty.py beat` before the builds | 1, 0, 1 | the first and third timed out on Supabase |
| `npm run build`, first try (03:25) | 1 | TypeScript passed; the home page's required read met Supabase statement timeouts (57014, 9 in the log) |
| `npm run build`, second try (03:50) | 1 | the same, 17 timeouts in the log; the mutex was let go between tries |
| `npm run build`, third and last try (04:10) | 1 | the same, 9 timeouts; the built site's check is under "To finish" |
| `check-internal-waits.mjs http://localhost:3414` against `next dev` (no build) | 1 | 29 of 32: every ledger check and every visitor check passed (404 without the cookie, none of the ledger's words sent, a token in the address opens nothing, 390 px does not scroll sideways). The three failures are of the dev server: no-cache instead of no-store (the production server sends no-store), the browser counted 50 of 152 report sections while the dev server was still streaming the page (the server's HTML held all 152), and an exception from the home page's Supabase timeout |
| `curl` `/internal/waits` without the cookie, `/internal/open` | 404, 200 | the internal pages still answer 404 to a visitor; the door opens |
| The whole suite, `ERW_LOCK_EXEMPT=1` | 1 | 4,789 tests, 1 failure: `test_session156` (the ask fixtures), as the chain's rules expected; 252 skipped |

## Decisions made without you

1. **The ledger sits on `/internal/waits`, above the report-by-report list**, which stays as session 188 built it (its test holds). `/internal/open` is unchanged: it says nothing of what the internal view opens, and it opens this page as before.
2. **What is read**: the items of a section headed for you, as session 188's rule finds them (in this run every one is the usual ruling heading); items elsewhere in a report that ask for a ruling in their own words are on the report-by-report list, not in the ledger. "Nothing new" items are not listed, nor one that only points to a note's list (session 372's "The items of the note's ..."); the page names those sessions and why. A long "Nothing new. ..." line that goes on to name what stands (365, 366, 367, 370) is listed, as session 188's rule lists it.
3. **Merging**: one subject is written down, the Redivis storage, because four reports name it in four ways ("Redivis's free 10 GB", "Redivis storage, 10 GB free", "Redivis's storage", "The storage: the four choices"); every other merge comes from a session named with shared words (359 and 379; 357 and 362) or from near-same words. Session 355's line restates both of session 361's questions: it is kept beside each, and the two stay two items.
4. **The words shown are the newest report's**, with every report's own words folded under the item.
5. **The groups**: "a public page, a data pull, a ruling on a figure, money", as the chain asked, and a fifth, "None of the four", for what no rule matched (the CLAUDE.md patch, the security items, the reaper, the alert policy, the five signatures). A fifth group is more honest than forcing those into one of the four.
6. **The rank**: only a note that says its list is by value ranks; the newest such note first, in its own order, each item once. Today the three come from `morning_2026-10-21_day.md` alone. Notes older than the run's first report are not read.
7. **The run's bounds are a constant** (`LEDGER = { from: 351, to: 413 }`); reports marked answered in `LAST_ANSWERED` leave the ledger as they leave the list.

## For Samuel's ruling

- Whether the five groups are the right ones, and whether "None of the four" should be split (security, the machines, the method notes).
- Whether a numbered list in a chain's note (not said to be by value) should count as a rank when no morning note ranks; today it does not, and the page says so.

## To finish

The built site's check, once Supabase answers the home page's reads (in the worktree, under the build mutex, port 3414):

```bash
cd C:/Users/lossa/Documents/erw-414/site
npm run build > ../../erw/runs/chain_oct21/s414/build3.out 2>&1; echo "exit=$?"
npx next start -p 3414     # in the background
node scripts/check-internal-waits.mjs http://localhost:3414 ../docs/brand/review-414 > ../../erw/runs/chain_oct21/s414/check-waits2.out 2>&1; echo "exit=$?"
# stop the process listening on 3414; release the mutex
```

## Files

- `site/scripts/build-waits.mjs` (the ledger), `site/app/internal/waits/page.tsx`, `site/lib/waits.ts`, `site/scripts/check-internal-waits.mjs`, `site/scripts/test-waits-ledger.mjs` (new), `tests/test_session414.py` (new), `docs/machines.md`, `docs/brand/review-414/` (two shots).

## Finished on the combined branch (21 October)

On `wip/015-finish` (the worktree `C:\Users\lossa\Documents\erw-finish`, cut from `wip/015-land`: sessions 401 to 410, 413 and 414 merged on main), 21 October 2026, 09:17 to 09:42 UTC under the build mutex: `duty.py beat` exit 0, `npm ci` exit 0, **one build, `npm run build` exit 0** (no statement timeout in its log), `npx next start -p 3415`. Every output is under `runs/chain_oct21/finish/` (outside git). Common to every section below: the **full `check-values.mjs`** (no restriction) exit 1: **6,359 of 6,359 values match Supabase**; 10 pages below their floors, exactly session 408's list with its counts (`/deals` 0 of 10, `/map` 0 of 1, `/events` 2 of 9, `/events/uri-2021` 9 of 10, `/events/covid-2020` 7 of 10, `/events/caiso-heat-2020`, `/events/caiso-heat-2022` and `/events/east-heat-2025` 0 of 10, `/learn/bill` 5 of 10, `/research/card/gas_sets_price` 4 of 6), every one license-held, expected; no other failure. **`check-routes.mjs`** exit 0 (1 live page and 223 in review asked as a visitor, 0 failed). The **whole suite** (`ERW_LOCK_EXEMPT=1 python -m unittest discover -s tests`, 09:43 to 09:49 UTC, the server stopped) exit 1: 4,911 tests, 1 failure, `test_session156` (the ask fixtures, the chain's known failure tonight), 254 skipped; the ten sessions' own modules (402 to 410, 414) exit 0, 107 tests. The server was stopped and the mutex released at 09:42 UTC.

- **The built site's check:** `node scripts/check-internal-waits.mjs http://localhost:3415 ../docs/brand/review-414` exit 0, 32 of 32 checks. The two shots were written again (commit `a351ac8d`); looked at both: "Waits for Samuel (internal)", built 2026-10-21 09:18 UTC, 124 items waiting, 133 lines, 50 reports read of 63 sessions, the first three items under it; at 390 the counts stack in three columns and nothing scrolls sideways.
- `tests.test_session414`: exit 0 within the ten sessions' modules.
