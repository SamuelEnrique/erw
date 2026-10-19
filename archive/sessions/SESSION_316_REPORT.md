# Session 316 report: the hunt and the daily chart (the Research pack's rulings 2a and 4b)

19 October 2026, from 21:58 UTC, unattended, on samueloldlaptop (the code machine), the third session of the chain of 19 October, daytime (`CHAIN_OCT19B_PROMPT.md`). Branch `wip/316-hunt` in the worktree `erw-316` (new: `erw-296` was building session 315), from session 315's commit; lands on main as `task/316-hunt` after session 315. Model spend USD 0: no model call. No pull (the read of EIA's figures is the data machine's: the script is written, not run), no warehouse data written.

## Read these first

- **The hunt tests five things, not three** (`hunt.py`, `test_claim`): the fourth, half of the change must remain when the first year is left out (session 252 asked for it); the fifth, a floor on the strength, the change must be at least one typical yearly move (`STRENGTH_FLOOR = 1.0`). `tests/test_session316.py` runs the stored yearly series of the verified drafts through the rule: the four spike drafts of 13 October (strength 0.43 to 0.51) fail the floor; ERCOT's night wind of 14 October (26.97 to 31.45 percent, 1.5 percent of the change left without 2019) fails the fourth test; the four hunt drafts of 13 October that were not spikes keep 77 to 107 percent of their change and still pass. Every claim's row carries `remains_without_first`. The data machine runs the next hunt (`run_data_machine_tables.sh`, unchanged).
- **A record of EIA's newest month carries the publisher's figure before approval** (ruling 4b). `warehouse/analysis/findings/publisher_figure.py` (new) reads the open record drafts on `eia_*` tables from the review list, asks EIA's API once per draft and month (the route and facets as the connector `eia_series.py` reads them: a retail price by state and sector, generation by location and energy source, the series id for the petroleum routes), records EIA's value as written and in the ERW's unit by the connector's conversion, the address without the key and the time of the read, and writes them into the draft's card (`card.publisher`). `/internal/findings` shows "EIA's own figure for 2026-07: ... as EIA writes it; ours ...: the same" beside the draft, or "not read yet: approval waits for it"; the approval route refuses "approved" for such a draft without the figure (409, the reason named). A read that fails leaves the draft without a figure and the script exits 1: nothing is made up. **The script has not run** (a pull is the data machine's): the two record drafts of EIA tables on the list (the District of Columbia's industrial price, Wyoming's gas generation) wait for it before they can be approved.
- **The 25 percent guard stays** (ruling 3a, session 315's test); nothing else of the scanner moved.

## What to review

1. `warehouse/analysis/findings/hunt.py` (`test_claim`, `STRENGTH_FLOOR`), `tests/test_session316.py` (the fixtures are the verification files of 13 and 14 October).
2. `warehouse/analysis/findings/publisher_figure.py`; `site/app/internal/findings/state/route.ts` (the refusal); `site/app/internal/findings/page.tsx` (`PublisherLine`); `site/lib/scanner.ts` (`needsPublisher`).
3. https://erw-flame.vercel.app/internal/findings : the two EIA record drafts read "EIA's own figure for this month is not read yet: approval waits for it"; pressing Approve on one answers the refusal.
4. The notes: `docs/methods/automated_analysis_findings.md` ("The hunt's fourth test and its floor"), `docs/methods/automated_analysis_scanner.md` ("The publisher's figure beside a record").

## What was done

- `warehouse/analysis/findings/hunt.py`: `STRENGTH_FLOOR`; `test_claim` with the fourth and fifth tests and `remains_without_first`.
- `warehouse/analysis/findings/publisher_figure.py` (new): `is_eia_record`, `period_of`, `request_of`, `figure_of`, `convert`, `compare`, `read`, `main` (`--dry-run`, `--only`, `--out`).
- `site/lib/scanner.ts` (`needsPublisher`, `PublisherFigure`), `site/lib/findings.ts` (`publisher` on a card), `site/app/internal/findings/state/route.ts` (the refusal before any state change), `site/app/internal/findings/page.tsx` (`PublisherLine`).
- `tests/test_session316.py` (9 tests), `tests/test_session233.py` (the test names, marked); the two methods notes.

## Checks

| Check | Exit | Result |
|---|---|---|
| `tests.test_session316`, `233`, `251`, `252`, `258`, `286` (worktree) | 0 | OK after two pins of this session's own were set to the measured values (the strong drafts keep 77 to 107 percent, not 90; a float product compared almost-equal) |
| `publisher_figure.py` pure parts by hand | 0 | the DC retail price and Wyoming's gas generation requests built as the connector reads them; the conversion 32.15 cents to USD 321.5 |
| `tsc --noEmit` (the worktree, with session 296's packages by junction) | 2 | 13 errors, every one a fresh worktree's generated types (`PageProps`, `LayoutProps`); none in the files changed |
| `eslint` on the four site files | 0 | |
| `npm run build`, `check-routes`, `check-internal-findings` (in `erw-296` after session 315 lands) | BUILD | |
| Suite, clean copy, the commit pushed | SUITE | |
| `scripts/freeze.py status` | FREEZE | |

## Landing of session 315 (recorded here: session 315's report is in that landing's own commit)

LANDING315

## Landing

LANDING

## Decisions made without you

- **The floor is a fifth test, not a silent filter**: a claim under one typical move is listed in the hunt's results with the test that stopped it, as the other failures are.
- **Fewer than three full years fail the fourth test** (the first year cannot be left out); session 233's rule that fewer than four cannot move the window stands beside it.
- **The publisher's figure is read from EIA's API**, the publisher's own data service for a series (the address recorded is the API's, without the key), not scraped from a web page: EIA's pages draw from the same service, and the API answers for the exact series and month.
- **The refusal is on the approval route**, so a click on Approve answers with the reason; the page's line says the same before the click.
- **A record on a table that is not EIA's is approved as before** (the ruling names EIA's newest month).
- **The script's read is left to the data machine**; this session ran its pure parts only.
- Questions skipped (Impeccable's playbooks ask them; the review page's one line took the page's own classes).

## For Samuel's ruling

- The data machine's next daily run should call `publisher_figure.py` after the scan (one line in `run_data_machine_tables.sh`, not added here: the step is a pull, and its place in the run is yours); until then the two EIA record drafts cannot be approved.
- Whether the floor should be higher than one typical move (the verification of 13 October suggested one; the strong drafts sit at 2.6 to 3.4).

## Files

- New: `warehouse/analysis/findings/publisher_figure.py`, `tests/test_session316.py`, this report.
- Changed: `warehouse/analysis/findings/hunt.py`, `site/lib/scanner.ts`, `site/lib/findings.ts`, `site/app/internal/findings/state/route.ts`, `site/app/internal/findings/page.tsx`, `tests/test_session233.py`, `docs/methods/automated_analysis_findings.md`, `docs/methods/automated_analysis_scanner.md`.
