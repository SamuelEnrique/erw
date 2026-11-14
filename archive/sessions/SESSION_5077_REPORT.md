# Session 5077 report: chain 243, a fresh reader's read of the five tools at 1280 and 390

Energy Research Warehouse (ERW). Chain 243, portable laptop window P1, 13 November 2026, about 20:08 to 20:20 UTC. Opus 5.5. Model spend USD 0. Branch `wip/5072-read`.

- **Read** on production (main) in the internal view at 1280 and 390, as session 5076: the battery (ERCOT's default; CAISO, 4 hours, perfect foresight), the generator (ERCOT solar; CAISO wind), the datacenter (the default; bought day-ahead), Research (`/research`, `/research/2026-W45`), and the Grid (session 5076). Every page at both widths: no sideways scroll, no exception, no broken word. Each page's text read for its windows and figures; the battery's CAISO view looked at whole at 390.
- **One new fault, on two pages: the "Price years" choice is of 20 October.** `price_years_by_window` was built once (every row retrieved 2026-10-20T09:08:39Z) and no schedule builds it. Since then CAISO's October 2026 became whole and the datacenter's daily files reached October:
  - battery, CAISO: "The last twelve months (default): 79.31" and "2026, 9 months held" beside the headline's USD 79.80 for November 2025 to October 2026 and a year chart of 10 months (battery faults row 10);
  - datacenter: 33.73 beside the headline's 34.07 (datacenter faults row 4).
  - The generator and ERCOT's battery view agree only because their months have not moved.
- **The fix is a build of the table and its load, which are window A's** (`docs/state/data_requests_five_tools.md`, row 4). Proven here without writing anything: `python warehouse/derived/price_years.py --out-dir <scratch>` (the live set read with the anon key) gave 2,754 rows, its 33 proofs against the pages' keys equal, and CAISO's default 79.80 from November 2025, the datacenter's 34.07, ERCOT's 81.40 unchanged: the headlines' figures. The data machine's runner loads no table itself, so a schedule there would also need the load; whether to add it is window A's.
- **No code change for it, and no test:** the pages read the table as they should. A page-side override of the default row would break its check key in check-values, and a check comparing the default with the headline would fail every landing until the table is built.
- Generator, Research and the Grid: no new fault. Each faults file has a dated section of this read.

## Decisions made without you

- The fault filed as the data machine's with its proof, rather than patched on the page.

## For Samuel's ruling

- **Whether `price_years.py` joins the data machine's daily run** (a step and a load after the runner's). Default: window A builds and loads it by hand when asked (data request row 4).
