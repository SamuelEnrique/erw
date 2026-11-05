# Session 413 report: the competitors, read against coverage

21 October 2026, about 03:10 to 03:45 UTC, unattended, on samueloldlaptop (the code machine), in the worktree `C:\Users\lossa\Documents\erw-413` on `wip/413-s` (from `wip/381-382-land` at `61c4c309`). The chain of 20 October, afternoon (`queue/done/015-day-20-october-code-pm.md`, session 413). Model spend USD 0; no warehouse data written; no `site/` change, so no build. The one session of the chain allowed web requests: 35 made, to the four companies' public pages only.

## Read these first

- **The review is `docs/reviews/competitors/2026-10-20.md`**: Ask the Grid, Grid Status and Yes Energy, each against `coverage.csv` table by table in three tables (what it shows that the ERW holds; what it shows that the ERW does not, with a public source and that source's license as `docs/licenses.md` reads it; what the ERW holds that was not found on its pages), and one paragraph on where each overlaps. No recommendation.
- **Enverus was not read.** Its robots file answered HTTP 403 on both `www.enverus.com` and `enverus.com`; no other Enverus page was asked. Its section says so and nothing more.
- **No terms page of the four could be read.** Ask the Grid's `/terms` is in its own sitemap but answered 403 three times (once as `/terms.md`); Grid Status's `/terms` answered 403; Yes Energy's terms were not found at three addresses, nor linked from its home page, product list or privacy notice (which has no clause on automated access). No page read forbade automated reading; every robots file read allowed the pages asked.
- **Requests: 35 of 40.** Every one is in the review's section 7.2 and in `runs/chain_oct21/s413/requests.csv` (git ignores `runs/`): address, time, answer. 24 read, 8 refused with 403, 3 not found (404). Four were second readings of a file the fetch tool may have served from its cache; all are counted.
- **What the readings found, in one line each.** Ask the Grid: 25 grids, a catalog of about 600 datasets with PJM, Canada, Mexico, hydrology and gridded weather, an MCP server free with an account, and the stance "Values are never modelled or synthesised"; no oil, LNG, coal, uranium, deals, policy or economics models found. Grid Status: nine grid operators, nodes for eight, constraints and outages, the EIA's emissions and Henry Hub, API, Snowflake and bulk CSV. Yes Energy: 90,000+ nodes, FTRs, outages and constraints, 15+ years of history, a project database of 100,000+ entries, modeling and settlement software, all in packages; no source named for any dataset.

## What to review

- The review: `https://github.com/SamuelEnrique/erw/blob/wip/413-s/docs/reviews/competitors/2026-10-20.md`
- The test: `tests/test_session413.py` (commit `6ead3c28`).
- Beside it, the earlier reading of Grid Status and Electricity Maps (11 October): `docs/positioning.md`. It was not changed.

## Checks

Every gate redirected to a file under `runs/chain_oct21/s413/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `tests.test_session413` | 0 | 8 tests OK: no em or en dash; the request log numbered 1 to 35 and within 40; every address one of the four companies' hosts; no address robots disallows; no Enverus page beyond robots; every marker cited defined; every name in backticks a `coverage.csv` table or a listed other name; no recommendation words |
| `tests.test_session413` against a copy with a dash and an unknown table added | 1 | 2 failures, as it should |
| The whole suite (`ERW_LOCK_EXEMPT=1 ... unittest discover -s tests`) | 0 | 4,778 tests OK, 274 skipped, in 412 s (`test_session156` passed too). One line printed "FAILED request 1 of 30: https://www.ercot.com/x": a test's stubbed request, not a request made |
| Build, snapshot, browser checks | none | no `site/` change |

## Decisions made without you

1. **Sitemaps were read before the terms**, on Ask the Grid, Grid Status and Yes Energy: each robots file names its sitemaps, and the terms address was not known. Reading the sitemap was the way to find it; it found Ask the Grid's, and showed that Grid Status's static pages hold none.
2. **Where the terms could not be read or found, robots-allowed pages were read.** The rule stops a page that a robots file or a terms page forbids; no terms page read forbade anything, because none could be read. The review says, for every claim it makes, that the company's terms were not read, and claims nothing about what they allow.
3. **Enverus was left after two refused robots files.** A host that refuses its robots file to the fetch tool was not read further; a third try or another host of Enverus would have been guessing at what it permits.
4. **Yes Energy's home page was read once, for the terms link only**, after three guessed addresses answered 404. It held none.
5. **The licenses of the sources that could fill a gap come from `docs/licenses.md`**, the ERW's own record; no request went to any of those publishers. A publisher not in the record is written "not in the record".
6. **Quotations are as the fetch tool's summary gave them.** The tool returns a small model's reading of each page, not the page; the review says so, and calls the tool's own tallies approximate (the Ask the Grid catalog's 613 pages).
7. **The file keeps the chain's date, 2026-10-20**, though the requests were made at 03:13 to 03:20 UTC on 21 October; the review's first line gives both.
8. **Five requests were not spent.** Ask the Grid's `/about` and Grid Status's EIA Browser refused the tool; more pages of the same hosts would likely have done the same.

## For Samuel's ruling

- Enverus: read its public pages by hand, or leave it out of the review (its robots file refuses the fetch tool on both hosts).
- Ask the Grid's and Grid Status's terms refused the fetch tool: a person reads them before the review is quoted outside the project or any further automated read of either.
- Yes Energy's website terms were not found: a person finds them, or the review stands with "not found".
- Whether `docs/positioning.md` (11 October, Grid Status and Electricity Maps) takes this reading of Grid Status and adds Ask the Grid and Yes Energy, or the two stay separate documents.

## To finish

- Land `wip/413-s` with the next landing (docs and a test only; no build needed for it).

## Files

- `docs/reviews/competitors/2026-10-20.md` (new).
- `tests/test_session413.py` (new).
- This report.
- Not in git: `runs/chain_oct21/s413/requests.csv` (the request log), `test413.out`, `suite.out`.
