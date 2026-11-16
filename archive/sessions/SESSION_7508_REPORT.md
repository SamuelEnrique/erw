# Session 7508 (chain 304, part A): the demand growth explorer at the done line

Energy Research Warehouse (ERW). samueloldlaptop (code role), unattended, 16 November 2026. Tool: `/explore/demand-growth`. Branch `wip/7508-demand-growth`, worktree `erw-7508`. Model spend USD 0. Nothing pushed, nothing landed, no table written, no shared explore file edited.

## At the top

- **Figures the page showed wrong (fixed here, with tests):** a whole percent lost its decimals ("+8 percent" in the headline of `?grid=us48&window=m07`, "+8.00" on the bar beside it; three rows of the table, 27 slots); "not held percent" and "2019: not held MW" on the Lower 48's peak view; the Lower 48's missing bar marked "shown below"; "january to october" in 2,205 chart hovers; "Stale since 6 November 2026" ten days after a monthly build.
- **No figure of the table is wrong as far as this machine can tell.** 24,060 of 24,062 rows recomputed from EIA's hourly workbooks equal the table's; the two are EIA's own revisions.
- **One figure to know before standing behind it:** CAISO's growth of +4.45 percent (2019 to 2025) stands beside -2.96 percent for EIA's California retail sales. Opposite signs; cause not established (faults row 12, a data request).
- **Not meant:** nothing. The shared scratchpad folder is shared with the sibling sessions (a sibling overwrote my scratch file `peek.py`; no file of the repository was touched by it).

## Faults in shared explore files

- `site/components/explore/HeldFreshness.tsx`, line 32 (and the same at `site/components/explore/Explore.tsx`, line 80): the freshness line's second sentence, an explanation, is drawn as grey text (`text-xs text-muted`). Smallest change: drop `text-muted` from that class list, or draw `detail` in a tip. Faults row 16.

## The five parts

- **Method note:** `docs/methods/demand_growth.md` completed with "The tool as a reader meets it" (what the page reads; the 8 grids by 39 windows; every figure in the page's order; how a figure is written; the rule in full with the four things the notes did not say; the replication; the cross-check; what is not held; the 16 decisions; five rulings). Nothing above it was rewritten. The page reads `eia930_demand_growth` only: not the subregion or the FERC Form 714 tables, not `site/data/demand_growth.json`.
- **Replication** (`replication/demand_growth/`), as printed:
  - `replicate.py`: "/explore/demand-growth: 35936 of 35936 slots of text on 315 views equal the replication's (3275 distinct checked figures; 770 of 770 growth figures recomputed from the MW rows)". Before the fixes 2,237 slots differed.
  - `from_hourly.py` (all eight areas, every year, about one minute after `extract_hours.py`): "From EIA's hourly demand (workbooks of 3 October 2026): 24060 of 24062 rows of 24116 equal the table's; 51 rows need hours after the workbooks' last (39 equal from EIA's hourly route); 3 not recomputed; 0 recomputed and not in the table".
  - `replicate.do`: five headline figures, expected values at its top. Not run (no Stata here); `replicate.py --headline` prints the same lines.
  - `table_rows.csv` (the 3,380 rows the page reads, public), `page_figures.json` and `.csv` (the page as it opens and each view's three headlines; the run compares all), `from_hourly.json`.
  - The page's own figures: `site/scripts/demand-growth-figures.mjs` draws `page.tsx` with the site's code, its reads answered from the table file.
- **Cross-check:** ten rows in the note; the table under "For the pack". Hosts read after their robots files and terms: eia.gov, pjm.com, caiso.com, nerc.com, gridstrategiesllc.com. Not asked: ercot.com.
- **Decisions block:** `site/app/explore/demand-growth/Decisions.tsx`, 16 choices, default and source on hover, no grey text, at the foot of every view. None editable: the page computes nothing.
- **Faults:** `docs/reviews/demand-growth-faults-2026-11-16.md`, 19 rows: 8 fixed (6 site, 2 note), 2 data machine, 1 shared explore file, 6 ruling (one shared with a data row), 2 not a fault.

## Tests

Each file in its own process, one at a time: `ERW_SPEND_CAP_USD=0 C:\Users\lossa\Documents\erw\.venv\Scripts\python.exe -m unittest tests.<file>`, output in `runs/s7508/tests/`, exit code read.

- `tests/test_session7508_demand_growth.py`: 13, pass (the page drawn on 81 views and replicated; each fix; the decisions against the note; the hourly rule on made hours; the do-file's lines; no dash).
- `test_session404` 12 (1 skipped), `test_session152` 17, `test_session2201` 6, `test_session2203` 6, `test_session2204` 5, `test_session1496` 6, `test_session281` 6, `test_session2877` 6, `test_session331` 8, `test_session472` 4, `test_session538` 14, `test_session97` 12 (4 skipped): all pass.
- Type check of the two changed page files alone (`tsc`, a scratch config, removed): exit 0.
- Not run: `site/scripts/check-values.mjs` and `check-routes.mjs` (they need a running site). "8.00" for a raw 8 passes the checker's rule (the text begins with the raw as shown).

## What to review

1. `https://erw-flame.vercel.app/explore/demand-growth` (in review). At the foot, click "Decisions on this page": 16 lines; rest the mouse on an "i": "Default:" and "Source:". The freshness line no longer begins "Stale since" within 35 days of a build.
2. `https://erw-flame.vercel.app/explore/demand-growth?grid=us48&window=m07`: first headline "+8.00 percent" (was "+8").
3. `https://erw-flame.vercel.app/explore/demand-growth?grid=us48&window=peak`: the first two headlines read "not held" with no unit; the Lower 48 in the first chart is marked "not held".
4. Any view, second chart, a year's bars: the hover reads "the year so far (January to October)".

## For the pack

- **What Samuel signs:** that every figure of the explorer is one row of `eia930_demand_growth`; that the table follows from EIA's hourly demand by the note's rule (24,060 of 24,062 rows from this machine's workbooks; 54 rows wait for the data machine's); and that the growth of the Lower 48 agrees with EIA's own retail sales to 0.02 points.
- **The five choices that matter most:**
  1. Base year 2019 (session 97). ERCOT: +27.22 percent on 2019, +5.57 on 2024.
  2. Weather is not removed (as metered; the adjustment is a second table).
  3. An hour is used when held, above zero and within 25 percent of its neighbours' median (docs/methods/impossible_hours.md); 60 hours left out since 2019.
  4. Peak is an hour's average, not an instant (CAISO 2025: 43,860 MW here, 44,506 MW in CAISO's Peak Load History).
  5. Demand is EIA-930's balancing authority demand, not a state's sales (EIA Form EIA-930).
- **The cross-check:**

| Ours | Theirs | Publisher, document, date | Difference, why |
|---|---|---|---|
| Lower 48, 2019 to 2025: +7.03 percent | +7.05 (sales, computed) | EIA, Electric Power Monthly, data for August 2026, table 5.1 | 0.02 points; sales, not demand |
| Lower 48, 2024 to 2025: +2.73 | +2.63 sales; +2.7 generation | The same; EIA, STEO, November 2026, table 7a | 0.10; 0.0 |
| ERCOT, 2019 to 2025: +27.22; on 2024: +5.57 | Texas sales +24.20; +5.51 | EIA, Form EIA-861M by state (warehouse, 5 November 2026) | 3.0; 0.06. ERCOT is not all of Texas |
| CAISO +4.45; NYISO -2.73; ISO-NE -2.54 | California -2.96; New York -1.26; New England +0.14 | The same | 7.4; 1.5; 2.7. California: opposite signs, not established |
| 14 highest hours (six records, seven 2026 peaks) | The same to 0.1 GW, the same days | EIA, Today in Energy, 15 October 2026 | none |
| PJM peak 152,315 and 160,560 MW: +5.41 | 151,302 and 160,709 MW: +6.22 | PJM, 2026 Load Forecast Report, 14 January 2026, table F-1 | +0.7 and -0.1 percent; unrestricted load |
| PJM average, 2019 to 2024: +1.57 | Net energy +1.54 | The same, table F-2 | 0.03 |
| CAISO peak 43,849 and 43,860 MW | 44,301 and 44,506 MW | CAISO, Peak Load History, January 2026 | -1.0 and -1.5 percent; hour against instant |
| No forecast held (Lower 48: 1.14 percent a year since 2019) | PJM peak +3.6 percent a year; North America +224 GW in ten years; US +166 GW in five | PJM (above); NERC, 2025 LTRA, January 2026, page 25; Grid Strategies, November 2025, page 3 | nothing of ours stands against a forecast |

- **Stata:** `do replication/demand_growth/replicate.do` should print: 1. ERCOT average demand growth 2019 to 2025, 27.22; 2. ERCOT peak growth, 12.16; 3. ERCOT year so far of 2026 on 2019, 33.34; 4. Lower 48 growth, 7.03; 5. ERCOT 2024 to 2025, 5.57.
- **Rulings:** under "For Samuel's ruling" below.

## Data request rows

| Requested (UTC) | Session | Table or file | What, exactly | Source | State |
|---|---|---|---|---|---|
| 2026-11-16 12:00 | 7508 | `eia930_demand_growth`; `replication/demand_growth/from_hourly.json` | On the data machine, with the eight EIA workbooks the table was built from (`warehouse/raw/eia930_emissions/20261105T230347Z/`): `python replication/demand_growth/extract_hours.py warehouse/raw/eia930_emissions/20261105T230347Z runs/hours` then `python replication/demand_growth/from_hourly.py runs/hours warehouse/output/eia930_demand_growth.csv --out=replication/demand_growth/from_hourly.json`. Expected: all 24,116 rows equal, the 54 rows of October and the year so far of 2026 among them, and the Lower 48's August and September 2026. Commit the JSON; a row that differs is a fault of the builder | EIA Form EIA-930 workbooks | requested |
| 2026-11-16 12:00 | 7508 | `eia930_demand_growth`, `eia930:CISO` | Set EIA-930's California demand (the workbook's Adjusted demand, yearly means of 2019, 2024, 2025 and January to October 2026) beside CAISO's own published load for the same periods, and say whether EIA's series changed scope: here CAISO grew 4.45 percent from 2019 to 2025 and 10.98 percent in 2026 so far, while EIA's California retail sales fell 2.96 percent | CAISO's own load (OASIS or its annual reports); EIA Form EIA-861M | requested |

## Browser read rows

| Asked (UTC) | Session | Branch | Address | What to look at | What should be seen | State |
|---|---|---|---|---|---|---|
| 2026-11-16 12:00 | 7508 | wip/7508-demand-growth | /explore/demand-growth | The foot: "Decisions on this page", opened; an "i" under the mouse and under the keyboard; the same at 390 px | 16 lines; each tip shows "Default:" and "Source:", is not cut off at 390 px, and the page does not scroll sideways | wanted |
| 2026-11-16 12:00 | 7508 | wip/7508-demand-growth | /explore/demand-growth?grid=us48&window=m07 | The first headline and the Lower 48's bar | "+8.00 percent" in both | wanted |
| 2026-11-16 12:00 | 7508 | wip/7508-demand-growth | /explore/demand-growth?grid=us48&window=peak | The three headlines and the first chart, at 1280 and 390 px | "not held" with no unit, twice; the Lower 48 marked "not held" with no bar; no third chart; no sideways scroll | wanted |
| 2026-11-16 12:00 | 7508 | wip/7508-demand-growth | /explore/demand-growth?grid=ercot&window=ytd | The second chart's hover card on 2026; the freshness line | "The year so far (January to October)" with +33.34 percent; no "Stale since" | wanted |

## Landing request

- Head: the commit that holds this report on `wip/7508-demand-growth` (the reply names it).
- Tests: `tests/test_session7508_demand_growth.py` (13) and the twelve older files above (112 tests, 5 skipped), all pass.
- Changes: `/explore/demand-growth` (in review): the decisions block, a percent to two decimals, no unit beside "not held", the hover's month names, stale after 35 days. New: `replication/demand_growth/`, `site/scripts/demand-growth-figures.mjs`, the faults file, the note's section, the test.
- Does not change: any table, any shared explore file, `release.ts`, any other page. A snapshot of the live pages differs on none (the page is in review). `check-values` reads the same keys; three texts gain ".00".

## Needs the key

None.

## Decisions made without you

- The rows are the table as this machine holds it (restored from the archive, the build of 6 November 2026), not the live set, which this worktree cannot read.
- The decisions block is imported by the site's alias (`@/app/explore/demand-growth/Decisions`), not `./Decisions`: session 404's test forbids a relative import on this page, and it was left as it is.
- Stale after 35 days for this monthly table (the monthly job starts on the first daily run on or after the third).
- `table_rows.csv` is committed: the table is public (EIA, public domain) and held only for review.
- The published documents were fetched by a background agent of this session under the brief's rules (curl, the ruled User-Agent, robots and terms first, at most six requests a host); I read one more EIA article myself. Documents are in `runs/s7508/web/` (not committed).
- California's moved hour: the table keeps EIA's own hour at 2023-10-31T22:00Z; found by trial and written into the note.
- `page_figures.json` and `.csv` hold the page as it opens and each view's three headlines, not all 35,936 slots (3 MB); the command regenerates all.

## For Samuel's ruling

1. A month the newest year already holds (March 2026) shows no growth, only its MW. Default: left; the table writes a month's growth for the last whole year only.
2. California's growth here (+4.45 percent) against EIA's retail sales for the state (-2.96 percent). Default: both stated in the decisions block, nothing changed, the data machine asked.
3. Demand at the grid ran about one point ahead of EIA's retail sales in 2026. Default: stated in the note, no cause claimed.
4. Grey explanatory lines drawn by shared frames (`ToolPage.tsx`, `HeldFreshness.tsx`). Default: not changed here.
5. No second window beside the first (A and B). Default: not built.
6. "ERCOT's 2023 record is 85,508 MW" in the note has no document, and ERCOT's site may not be asked. Default: left in the note, marked; not on the page.
7. PJM's report is printed "For Public Use" and linked from its public page, but the file's properties carry the label "Confidential - PJM Personnel Only". Default: its figures are cited.
8. Words: "the year so far" twice in one label; a hover that says "from 2019 to 2026" without the months. Default: left.

## A fault seen in another tool

- None. `docs/methods/eia930_demand_growth.md` describes the build of 21 October (24,108 rows); the table is now 24,116 rows and its item 5 (the site's copy differs) no longer holds: `/demand`'s copy was rebuilt with the table on 6 November.
