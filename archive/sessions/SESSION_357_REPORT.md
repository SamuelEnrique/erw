# Session 357 report: the price years

20 October 2026, from 08:41 UTC, unattended, on lab-desktop (the data machine), the first session of the chain of 20 October, night (sessions 357 to 364). Model spend USD 0. Pulls: none (one request was made to ERCOT's list of DAM Settlement Point Prices for session 358's design; it is counted against session 358's ceiling).

## Read these first

- **`price_years_by_window` is built, validated, in coverage, loaded and in the Redivis draft: 2,754 rows** (battery 234, generator 108, datacenter 2,412), every figure computed by the pages' own modules. The chain's prompt names the table `price_years`; the validator's rule for a series table needs three parts in the name, so it is `price_years_by_window` (`docs/methods/price_years.md`, first section). The code machine's chain (session 352) reads that note.
- **The shapes of all three new tables of this chain were landed first, before any table, at 09:02 UTC** (`cfe05c6d`, "Merge task/357a-shapes: checks passed", run 39396754585): `docs/methods/price_years.md`, `docs/methods/node_basis.md`, `docs/methods/ercot_4cp.md`. Snapshots `s357a-before` and `s357a-after`: 0 differences on 25 pages, expected (documents only).
- **Every default figure equals the page's to half a cent, 45 proofs**: the battery's twelve configurations at ERCOT and CAISO and six at SPP against the page's check-key stat, the twelve at ERCOT and CAISO again against a second read of the live set, the generator's twelve against `spans().twelve`, the datacenter's main region at each grid. The packs' numbers come out of the table: 81.40, 255.08, 614.58 (battery); 59.85, 102.24, 130.80, 59.46, 217.53 (generator solar); 33.73, 21.68, 150.61 (datacenter `LZ_NORTH`).
- **The battery is read from the live set, not from this machine's copy of `battery_stack_monthly`, because the two differ.** The runner rebuilt the battery stack at 01:04 UTC and loaded it; this machine's copy is older and leaves out CAISO's 2 November 2025 (the autumn clock change: "25 of 25 hours not held"). CAISO's 2-hour battery reads USD 61.29 per kW over the last twelve months on the page and 61.11 from this machine's copy (November 2025: 3,754.05 against 3,576.83 per MW). The page reads the live set, so the table does too; session 362 (the archive proven) will meet this difference.

## What to review

1. `docs/methods/price_years.md`: the shape (written first), the windows, how each tool's figure is computed, the first build.
2. `site/scripts/price-years.mjs` (the pages' modules run over the pages' inputs) and `warehouse/derived/price_years.py` (the inputs, the frame, the proofs).
3. `tests/test_session357.py` (5 tests; the pages' code on the committed files alone, no key).

## What was done

- The table, one row per tool, grid, price point, configuration and window: each calendar year with a month held (`x_complete` false for a part year), the page's last twelve months, the last three and seven full calendar years (only where all are full), the whole span by the page's own rule, and the whole span without each stress event of the grid and without all of them. Units USD/kW-year (battery, generator) and USD/MWh (datacenter).
- Grids ERCOT, CAISO and SPP. The battery's six configurations (two strategies, three durations); the generator's four assets at the main hub; the datacenter's four ways of running in two markets at every region the page offers (ERCOT's fourteen, CAISO's three, SPP's two), at the page's defaults, the flexible load's figure being the page's rule decided from day-ahead prices.
- The stress events are the battery page's leave-out boxes: ERCOT's Uri, Elliott and the 2023 heat; CAISO's ten events made from its own notices. The generator's leave-outs are ERCOT's three, from its snapshot's own daily figures (it holds none for CAISO or SPP). A left-out event takes the event's days out of the months they fall in, as the battery page's boxes do; nothing is re-optimized.
- `warehouse/supabase/live_set.yaml`: the table loaded whole, and held under `review_hold` (a new table of pages in review: its catalogue row says review).
- `warehouse/metadata/build_coverage.py`: the sector rules of this chain's new tables (`price_years_by_window`, `node_basis_daily`, `node_basis_summary`, `ercot_node_prices_hourly`, `ercot_4cp_intervals`) and the ISO column of the price years.

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py --what "session 357"` | 0 | on duty until 2026-10-21 00:42 UTC |
| `warehouse/derived/price_years.py --live` (data lock) | 0 | 2,754 rows; 45 proofs equal |
| `erw_validate.py warehouse/output/price_years_by_window.csv` | 0 | PASS, 0 errors, 0 warnings |
| `build_coverage.py` (data lock) | 0 | 205 tables; the first run failed (exit 1) on my "Derived from" line, which named files beside tables; fixed and rerun |
| `load.py --only '^price_years_by_window$'` (data lock) | 1 | the table matched: 2,754 in the CSV, 2,754 in Supabase, 2,754 written. Exit 1 is the sources check: Supabase holds 11 sources this machine's `sources.csv` does not (`erw:impact_tax_rules`, `la_ldr:la_rib_26_013`, `la_ldr:la_rib_26_014`, `la_legislature:la_rs_47_633`, `nlr:jedi` and six more), registered by another machine's load; not this table's. Nothing was pruned |
| `redivis/upload.py price_years_by_window` (data lock) | 0 | count(*) 2,754; coverage and sources too; the headers table skipped by the export cap, as before; nothing released |
| `tests.test_session357` | 0 | 5 tests |
| tests 142, 147, 158, 160 (the methods notes) | 0 | 205 tests |
| `scripts/freeze.py status` | 0 | no freeze |

No snapshot was taken around the load: no page reads `price_years_by_window` yet and no page is live.

## Pulls against their ceilings

| Pull | Ceiling | Used |
|---|---|---|
| none named for this session | 0 | 0 (the live set and the Redivis draft were read and written; ERCOT's NP4-190-CD list once, for session 358, counted there) |

## Landing

The shapes: above (`cfe05c6d`, 0 differences). This session: see the commit that carries this report; its before and after snapshots are recorded in session 358's report.

## Decisions made without you

1. **The table is `price_years_by_window`**, not `price_years`: the validator's three-part rule for series tables. The note says so first.
2. **ERCOT, CAISO and SPP only.** NYISO, ISO-NE and MISO are "license needed" from 21 October 2026 (MISO is also paused); PJM is licensed. A grid joins when its license allows.
3. **Each tool's inputs are what its page reads**: the battery's ready grids from the live set (which is newer than this machine's copy), SPP from the committed review snapshot, the generator from its committed snapshot (built 4 October), the datacenter from its committed year files (built 19 October). The table then equals the pages by construction, and the proofs say so.
4. **"The whole span" is each page's own rule**, which differs by tool: the battery's reader window at its default (every held month, the twelve-calendar-month mean), the generator's "every full year held", the datacenter's every complete month. The note says which.
5. **The seven-year average is written only where seven full years are held** (ERCOT, and the datacenter's day-ahead load at SPP's South hub); elsewhere there is no row, never a shorter average under the same name.
6. **A left-out event takes out the event's days and nothing else**: the battery as its page does; the generator from its snapshot's daily figures; the datacenter by each hour's price and weight as the page's run set them, without re-running the rule (a flexible load's budget of hours off stays as the page spent it).
7. **The table is under `review_hold`**: loaded for the pages, its catalogue row "review", like every new table of a page in review.

## For Samuel's ruling

- Whether the generator's leave-outs should cover CAISO's events too: its snapshot holds daily figures for ERCOT's three only, and adding CAISO's means rebuilding the snapshot (`warehouse/derived/merchant_revenue.py`), which changes the page's input.
- This machine's `battery_stack_monthly` is older than the live set (CAISO's 2 November 2025): whether the data machine should restore the runner's copy (`warehouse/archive/restore.py`) before its own builds read it. Session 362 lists it with the archive's comparison.

## Files

- New: `docs/methods/price_years.md`, `docs/methods/node_basis.md`, `docs/methods/ercot_4cp.md` (the shapes), `warehouse/derived/price_years.py`, `site/scripts/price-years.mjs`, `site/scripts/price-years-live.mjs`, `tests/test_session357.py`, this report.
- Changed: `warehouse/supabase/live_set.yaml`, `warehouse/metadata/build_coverage.py`, `warehouse/metadata/coverage.csv`, `docs/coverage.md`, `warehouse/metadata/sources.csv`.
- Outside git: `warehouse/output/price_years_by_window.csv` (in the live set and the Redivis draft), `runs/s357/`.
