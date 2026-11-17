# Research, Automated Analysis (`/research`), read as the reader it is for (session 7564, samueloldlaptop, 16 November 2026 Pacific, 17 November UTC)

Energy Research Warehouse (ERW). Asked by Samuel: the reader's read of chain 304's part B for the six tools of the first ten that had none. The tool reached the done line in the five tools' pack (`docs/reviews/five-tools-signature-pack-2026-11-14.md`; faults `docs/reviews/analysis-faults-2026-11-13.md`; replication `replication/analysis/`).

**The reader:** a fund analyst on Monday 16 November 2026 reading what changed in US power and whether each chart can go into a client note: today's chart, this week's chart, two library findings, and the files behind them.
**The five cases:** (1) today's chart, the Wyoming gas-generation record of 12 November 2026; (2) this week's chart; (3) the library's "The peak hour moved: five grids", for a note on evening prices in New York and New England; (4) "Gas sets the price less often?", ISO-NE beside ERCOT; (5) the files of case 3 (CSV, Python, Stata, the pictures). On the site's own files: `site/data/findings/` (14 cards, computed 12 and 16 November 2026), `docs/digest/charts/2026-11-12.json`, `docs/roundup/2026-W45.md`.
**How it was read:** the cards read as the site loads them (`lib/findings.ts`) and a card drawn to HTML by its own component (`site/scripts/test-research-read.mjs`, 17 of 17); the Wyoming series read in the warehouse's own table (`eia_state_generation_monthly`, retrieved 5 November 2026). Not seen: no click, no hover in a browser, not the charts (canvases), no layout at 390 px.

Part A's rows are cited by number and not written again.

## The cases, in one line each

| Case | What the page gives | Where it stops |
|---|---|---|
| 1. Today's chart | "Net generation from natural gas in Wyoming: 1,060,504 MWh in August 2026, the highest monthly value held since January 2001. The record until now was 765,381 MWh, in July 2024." | The table holds July 2026 at 1,034,451 MWh: the record until August was a month old, not two years (row 2) |
| 2. This week's chart | "This week's chart, 2026-W45" on 17 November, which is in 2026-W47 | The Roundup is paused; the heading called a chart of the week ending 8 November this week's (row 3, fixed) |
| 3. The peak hour, five grids | The callouts for NYISO read "license needed" (ruling 6a); the why paragraph printed them: "its evening share rose from 43.3 to 62.5 percent", "evening share ISO-NE 55.0 percent in 2025 and 41.2 in 2026"; the chart drew NYISO's and ISO-NE's panels | Both grids are held since 21 October 2026; the hold stopped at the callouts (row 1, fixed) |
| 4. Gas sets the price | ERCOT 38.8 to 40.9 percent; the why printed "ISO-NE's zones went from 18.6 to 5.5 percent" and the chart drew ISO-NE's and NYISO's bars | The same (row 1) |
| 5. The files | CSV `erw_2026_grids_peak_hour_solar.csv`: 192 NYISO lines and 192 ISO-NE lines of 965; `erw_2026_grids_spikes_batteries.csv` 102 and 30 of 314; `erw_2026_gas_share_hours.csv` 9 and 9 of 45; the pictures draw the same panels | Files the engine writes, served as they are (row 4) |

## The rows

Kind: `site` (fixed on this branch, with a test: `site/scripts/test-research-read.mjs`), `data machine`, `browser`, `ruling`.

| # | Case | The cell or click | What the reader meets | Kind | State |
|---:|---|---|---|---|---|
| 1 | 3, 4 | The why paragraph, the footnote and the chart of the three five-grid cards | NYISO's and ISO-NE's figures, from tables held since 21 October 2026, printed in words and drawn as panels and bars, while the same figures in the callouts read "license needed" (ruling 6a held the callouts alone; the page standard holds every held value) | site | fixed: a card is held where the cards are read (`site/lib/cardhold.ts`, applied in `lib/findings.ts`, so the library, a card's own page and the week's chart all draw it held). A held grid's panel or series leaves the chart and is named among its placeholders with "license needed", as MISO's and PJM's are; a sentence of the why or the footnote that names a held grid and carries a figure is taken out, and one line says how many and why. A sentence that names one with no figure stays ("New England's gas is dearer at Algonquin"). The card files are not changed; a card with no held grid is untouched |
| 2 | 1 | Today's chart, its fact line | The record until now is July 2024's 765,381 MWh; the table holds July 2026 at 1,034,450.83. Found before (`docs/reviews/periodicals-faults-2026-11-05.md`, row 87) and fixed in the scanner on 13 November (session 1982, `findings_scanner.py`), but the chart file of 12 November was written before the fix, and with the Digest paused it is still the newest | data machine | requested (row 309): write `docs/digest/charts/2026-11-12.json` and its picture again with the fixed rule (code, no model call): "The record until now was 1,034,451 MWh, in July 2026", the held record of July 2024 beside it |
| 3 | 2 | The heading "This week's chart, 2026-W45" | On 17 November (2026-W47) a chart of the week ending 8 November is called this week's | site | fixed: "This week's chart" while the newest is of this ISO week or the one before; older, "The newest weekly chart, 2026-W45: none since" (`weekChartTitle`, `site/lib/research.ts`); `check-analysis-flow.mjs` accepts both |
| 4 | 5 | The cards' files: CSV, the pictures (1600 by 900 and 1080 by 1350) | The held grids' rows and panels are in the public files (`site/public/findings/`); a reader downloads what the page now holds | data machine | requested (row 310): the engine writes the public CSVs and pictures without the rows and panels of a held grid (as the page now draws them), or the files are withdrawn until the license; the Python and Stata readers follow the CSV |
| 5 | 3 | The card's title line "The dearest hour moved later in ERCOT and NYISO and earlier in CAISO" | A finding about a held grid stated in words, with no figure | ruling | default: words with no figure stay, as the why's do. The other choice: a title or subtitle that names a held grid is written without it |
| 6 | 1, 3 | The Python and Stata files of a card | They read the CSV (row 4), so they reproduce the held figures | ruling | default: they follow the CSV once row 4 is done. The other choice: none |
| 7 | 3 | `/research#library`, the card "The peak hour moved: five grids" | No NYISO or ISO-NE panel; "NYISO: license needed", "ISO-NE: license needed" beside MISO and PJM; the why ends "2 sentences with figures of NYISO and ISO-NE are held" | browser | wanted (row 309) |
| 8 | 2 | `/research#week` | The heading "The newest weekly chart, 2026-W45: none since" (until a new Roundup) | browser | wanted (row 310) |

**Counts.** Site, fixed: 2 (rows 1, 3). Data machine: 2 (rows 2, 4). Ruling: 2 (rows 5, 6). Browser: 2 (rows 7, 8). Key: 0 (the request form is answered by a person and runs on the data machine; no model call is asked of this page).

**Words the reader would not know.** "the scanner" in today's chart's note (the code that flags records and jumps); the note says what it is.

## The figures this page shares with other pages

| Figure | Here | The other page | Agree? |
|---|---|---|---|
| A 1 GW datacenter's all-in cost, ERCOT HB_WEST and LZ_AEN | 41.83 and 47.63 USD per MWh (`siting_gigawatt`, computed 16 November) | `/cost-of-power?view=allgrids`, from which the card is computed | Not compared by hand here: the card runs the tab's own code |
| Wyoming's gas generation, August 2026 | 1,060,504 MWh | `eia_state_generation_monthly`, 1,060,503.7 | Yes; the record before it does not (row 2) |
| AEP and Google's 702 MW Bloom Energy fuel cells | Not on this page | The Roundup of W45, in the archive, and the datacenter tracker's 702 MW row (part A's datacenter row 19) | Not a figure of this page |

## What this reader still cannot get from the tool, and why

- **New York and New England.** Held whole (row 1); the findings that need them read "license needed".
- **A chart of this week.** The Digest and the Roundup are paused (row 3 says so now).
