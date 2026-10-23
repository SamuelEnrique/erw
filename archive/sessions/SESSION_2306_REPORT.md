# Session 2306 report: seven disclosure and consistency fixes, each its own commit

23 October 2026, about 21:15 to 21:50 UTC, on portable-laptop (the code machine), on the owner's instruction. Worktree `C:\Users\samen\Documents\erw-2306`, branch `wip/2306-audit-fixes` cut from `origin/main` at `c24a284b`, pushed after each commit. Model Fable 5.1. No site build, no landing, no model call, no warehouse write, no request but GitHub. No em dash in any file written. Eight commits: one a fix, and one more (4b) for the method note's heading that named the row fixed in 4.

## Read these first

- **Every fix is on the branch and tested where asked** (fixes 1, 3 and 7 on fixtures; the site's test file runs with `node --import ./scripts/alias-register.mjs scripts/test-session2306.mjs`, 16 of 16; the Python tests `tests.test_session2306` and `tests.test_session232`, 33 OK; the other daily-chart tests, `test_session238`, `267`, `315`, 60 OK).
- **Fix 7 changes what the Digest's chart may read.** Read from the license file, the held grids are ISO-NE, MISO and NYISO today, where the fixed line held NYISO and SPP: SPP's series become candidates for the chart of the day and ISO-NE's and MISO's stop being ones, from the first run after this lands. `hunt.py`'s blocked grids read the same (`blocked_grids()` gives the same three).
- **Fix 6 is a disclosure only:** the California solar case's shape stays EIA-930's; the size of the effect on the capture price is not measured, and the note says so.
- **Not landed:** no gate, no build (the instruction). The branch is ready for `land_check.py --ref wip/2306-audit-fixes`.

## The fixes, each with its file and commit

| Fix | What was wrong | What changed | Files | Commit |
|---|---|---|---|---|
| 1 | `AllGridsView.tsx` hard-coded "none of those held falls in these months" for ERCOT's four peak intervals while the model counted the intervals' hours in the window (`ProfileTwelve.peaks`) | the sentence is `peakWords(t.peaks, newest summer, note)` in `site/lib/siting.ts`: "none of those held falls in these months" at zero, "N of their hours held fall in these months and the load is off in them" otherwise | `site/lib/siting.ts`, `site/app/cost-of-power/AllGridsView.tsx`, `site/scripts/test-session2306.mjs` (new) | `d19a9b44` |
| 2 | the carbon column's head and tip did not say that the datacenter profile's figure is eGRID's generation-based annual rate and the flexible and electrolyzer profiles' is EIA-930's hourly consumption-based intensity, nor name the CAISO reporting break | the head reads "Carbon (eGRID 2023, generated)" or "Carbon (EIA-930 hourly, consumed, where held)" by profile (`columnHead`); the column's tip and each cell's tip state the measure, and name the 16 December 2025 break (`docs/methods/eia930_caiso_break.md`) for every CAISO row and in the head's tip | `site/lib/siting.ts` (`COLUMNS`, `columnHead`), `site/app/cost-of-power/AllGridsView.tsx` (`CarbonTd`, the two head renderings), the test file | `a00a1f1a` |
| 3 | the flexible profile's avoidance of ERCOT's four intervals (energy, and the own and curtailing four-peak charge) and the electrolyzer's strike at the row's own percentile are chosen knowing the year, and were not labelled so, where "Your load" labels its hindsight figure "If perfectly foreseen" | `foreseen(x)` (the flexible profile; the electrolyzer with no typed strike) and `foreseenWords(what)`; the energy head reads "Energy (if perfectly foreseen)" and the transmission head "Transmission and 4CP (own and off: if perfectly foreseen)" for those profiles; the profile cell's tip and the four-peak cell's own and curtailing tips carry the words | `site/lib/siting.ts`, `site/app/cost-of-power/AllGridsView.tsx`, the test file | `301da3f1` |
| 4 | the battery page's tail row was labelled "Merchant tail after the contract" while its arithmetic is the years after the debt's term (`c.r.tail.from = term + 1`) | "Merchant tail after the debt" | `site/app/cost-of-power/battery/Scenarios.tsx` | `fa0604a4` |
| 4b | the method note's heading for that row said "after the contract" | the heading follows the label and says the label changed in this session | `docs/methods/battery_earns_algorithm.md` | `b840ff4d` |
| 5 | CAISO's start was written as September 2024 where the code holds August 2023 (`GRIDS` in `site/lib/batterystack.ts`, session 273); the pack said "15 published figures" where the page prints 25 (`data-checked-against="25"`); NREL/TP-6A40-93281's authors were guessed as "Cole, Karmakar and Mann" in two places and absent in a third | August 2023 everywhere the start is stated (with "September 2024 until session 273" where the old figure explains an old table); 25 with the count's history (14, 15, 17, 25); one author list, "Cole, Ramasamy and Olmez Turan, Cost Projections for Utility-Scale Battery Storage: 2025 Update", as `warehouse/connectors/sourced_ranges.py` cites the report; the DMM cross-check row and the pack's row now say 2024 is held by both and not yet recomputed | `docs/methods/battery_earns_algorithm.md`, `docs/methods/battery_stack.md`, `docs/reviews/packs/battery.md` | `7b669c63` |
| 6 | section 12 of the generator note did not disclose that the California solar case prices on EIA-930's shape, which the repository records as reading below CAISO's own | a disclosure bullet after "Shape": EIA-930's solar 7,029 MW against CAISO's own 7,973 over the 888 hours both held (about 12 percent below CAISO's own, or CAISO's own about 13 percent above EIA-930's), wind and total likewise, from `eia930_caiso_break.md` (sessions 73, 78 and 82) and `docs/reviews/packs/grid.md`; a uniformly low level leaves a capture price unchanged, an hourly gap would move it, the effect is not measured; no figure moved | `docs/methods/generator_earns_algorithm.md` | `4f9f81d9` |
| 7 | `daily_chart.py` held `HELD = ("nyiso", "spp")` by the ruling of 12 October while `license_status.csv` marks ISO-NE's, MISO's and NYISO's tables "license needed" (21 October) and no SPP table | `held_grids(meta_dir)` reads the file (a grid is held when a table whose name begins with it is marked); `public_tables`, `held_series` and both callers read it; `HELD` is `held_grids()` of the repository's file; `hunt.py`'s and the scanner note's words follow | `warehouse/analysis/findings/daily_chart.py`, `warehouse/analysis/findings/hunt.py`, `docs/methods/automated_analysis_scanner.md`, `tests/test_session2306.py` (new), `tests/test_session232.py` (its fixture marks SPP's and NYISO's tables; its assertion on `HELD` reads the file) | `8cd56210` |

## Checks

| Check | Exit | Result |
|---|---|---|
| `node --import ./scripts/alias-register.mjs scripts/test-session2306.mjs` | 0 | 16 of 16 (peakWords at 0, 1 and 4 hours; the carbon heads and tip; foreseen by profile; the heads; the tab's use of the words) |
| `python -m unittest tests.test_session2306 tests.test_session232` | 0 | 33 OK |
| `python -m unittest tests.test_session238 tests.test_session267 tests.test_session315` | 0 | 60 OK |
| `eslint` on the changed site files | 1 | one error, pre-existing and not this session's: `AllGridsView.tsx` line 35, the tip counter reassigned outside a component (session 714); nothing new |
| `tsc --noEmit`, the changed files | 0 errors | (the 15 pre-existing errors of other files stand) |
| em dashes in every file written | 0 | |
| `daily_chart.HELD` and `hunt.blocked_grids()` on the repository's file | | `('isone', 'miso', 'nyiso')` both |

## Decisions made without you

1. Fix 3: a strike the reader types for the electrolyzer is not labelled hindsight (the hours it runs are then decided on the day-ahead price alone); the row's own percentile strike is. The flexible profile is labelled whatever its strike, for its four-interval hours.
2. Fix 2: the heads name "eGRID 2023" as the instruction says; the cell tips read the year from the file (`data_year`), so a later eGRID moves the tips and the head would need the word changed.
3. Fix 5: the date "June 2025" the pack gave the NREL report is dropped rather than kept beside an author list the connector does not date; the DMM cross-check row keeps its figures and says 2024 is now held by both and not recomputed.
4. Fix 6: both percentages are written (12 percent below CAISO's own; CAISO's own 13 percent above EIA-930's), since the instruction's "about 13 percent" is the second reading of the same two means.
5. Fix 7: the held grids are read by the table's name prefix, not the `publishers` column (which `hunt.py` reads separately and which `license_status.csv` does not fill for every row); a grid is held when any of its tables is marked, so MISO is held by its queue table alone. The ruling of 12 October (NYISO and SPP) is now expressed by the file: if SPP is to stay held, a person marks an SPP table in `license_status.csv`.
6. The lint error on `AllGridsView.tsx` line 35 is older than this session and left as it is.

## For Samuel's ruling

- Whether SPP's tables should stay held for the Digest's chart: the license file does not mark them, so after this lands they are candidates again (fix 7, decision 5).
- Whether the CAISO cross-check rows (the DMM fleet revenue) should be recomputed for 2024, now that both tables hold it (fix 5).
- Whether the California solar case should move from EIA-930's shape to CAISO's own supply by fuel, and the measured effect first (fix 6).
