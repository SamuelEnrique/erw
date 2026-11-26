# Battery storage (`/storage`): its figures audited as a hostile expert would

Session 10212, chain 710 part D, 26 November 2026, the old laptop. Read as a storage developer's analyst and an ISO market monitor who want to find it wrong. The page `/storage` (its three tabs: the fleet, the build-out, the owners) and its view `/storage/places`. The battery earnings model at `/cost-of-power/battery` was audited on 20 November (`docs/reviews/battery-model-audit-2026-11-20.md`) and is not repeated; nor are the lender's read and the replication of 16 November (`docs/reviews/storage-read-2026-11-16.md`, `storage-faults-2026-11-16.md`).

- Nothing changed on main but this file and its evidence folder (`docs/reviews/storage-model-audit-2026-11-26/`). No table written, no lock taken, no default moved, no model called, no live service asked.
- Each finding has its own branch, `wip/audit-storage-<n>`. Words-only fixes (1, 2, 3, 4, 6, 7) are for landing, also merged together as `wip/audit-storage-words`; 5 would move figures and waits for the owner.

## In short

- **The arithmetic is right.** Every figure the default view prints (the fleet tab) follows from its files as the note says: 97 of 97 marked figures, the 6 thirty-day sparklines (180 daily values with their days not held), the inventory month, the 24-hour window and the grids named under the table came out to the digit in an independent restatement from EIA-860M and the hourly series. The build-out tab, never restated before: 629 of 629 figures on three views.
- **"US Lower 48" leaves out a third of the fleet (finding 1).** EIA-930's national battery total holds no CAISO, NYISO or PJM: 18,200 of 56,121 operating MW (32.4 percent). Over the 30 days to 4 November CAISO's own output was 88 percent of the "Lower 48" figure and above it in 267 of 683 hours. The page never said so. Words, for landing.
- **"Latest complete local day" is two days old (finding 2).** The EIA-930 rows wait 48 hours for EIA's revisions (session 7050); drawn on 5 November they showed 1 November while 2 and 3 November were complete, and CAISO's row, with no wait, showed 4 November. The two hourly charts draw the unsettled hours. Words, for landing.
- **ISO-NE's and SPP's series carry no charging (finding 3).** Never below zero in a year (8,832 and 6,528 hours), SPP's zero in 2,949; ERCOT's had none before 15 December 2025. The page's sign decision, its "net output" hover and both charts read them as net. Words, for landing.
- **Smaller.** The build-out's early years are "slightly understated": 2015 lacks 31 percent of what operated, 2019 10 percent (finding 4, words; putting them back is finding 5, for the owner). "Operating" holds 508 MW on standby or out of service, and "Retired" is two years only, 338.5 of 524.3 MW (finding 6, words). "Storage against solar" said the batteries "could carry" the solar fleet; their power is 3 to 66 percent of solar's (finding 7, words).
- **What an expert would add:** the fleet's equivalent full cycles a day (ERCOT 0.62, CAISO 0.79 on the days shown), out over in over 30 days (ERCOT 0.81 against the day's 0.54), a national figure with CAISO's own output in it, usable rather than nameplate energy, and accredited capacity; the last two are not held.
- **Held grids reach nothing.** Every ISO-NE, MISO and NYISO figure on the page is EIA's (public); no drawn view prints "license needed" or reads a held table. No "share of the evening peak" or growth rate is printed.

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/storage/page.tsx` | The page and its fleet tab (the default view): headline of operating MW and units with the inventory month; "The last 24 hours, by grid" (EIA-930 BAT for ERCOT, ISO-NE, MISO, SPP, and CAISO's own line); the fleet by status (MW, units, MWh where given); by ISO; the 15 states; planned additions by year; the daily cycle (newest day per grid, discharged, charged, out over in, peak hours, a 30-day sparkline); the 30-day hourly charts (the four, CAISO, and the Lower 48 alone); the decisions block; downloads |
| `site/app/storage/buildout/view.tsx`, `parts.tsx`, `read.ts` | The build-out tab: summary, operating power and energy, twelve months' additions, bars by duration at each year end, MWh of batteries per MW of solar, the table by grid with planned MW by year, three folds |
| `site/app/storage/owners/view.tsx` | The owners tab, from the committed snapshot `site/data/storage_owners.json` (EIA-860M September 2026, built 2026-11-17) |
| `site/app/storage/places/page.tsx`, `Decisions.tsx` | `/storage/places`: any two balancing authorities or states side by side, every authority and state ranked, from `site/data/storage/places.json` (September 2026, built 2026-11-20) |
| `site/lib/storagefleet.ts` | The inventory month, the days a sparkline does not hold, the "Discharged MWh" hover |
| `site/lib/buildout.ts` | The build-out's months, view and number formats (no arithmetic: every value is a row) |
| `site/lib/decisions.ts` `STORAGE_DECISIONS` | The nine decisions, word for word the note's |
| `site/lib/data.ts` `storageUnits`, `series` | The live reads: `storage_capacity` (entities), `storage_daily_cycle` (45 days), `eia930_all_storage` and `caiso_battery_storage` (31 days), `storage_buildout_monthly` |
| Builders | `warehouse/connectors/eia930_storage.py` (EIA-930 BAT, complete UTC days), `caiso_outlook.py` (CAISO's 5-minute Total batteries); `warehouse/derived/storage_capacity.py` (every BA unit of the three EIA-860M tables), `storage_daily_cycle.py` (complete local days, settled 48 hours; CAISO's hours as means of twelve 5-minute values), `storage_buildout.py` (every month from 2015 rebuilt from the one inventory), `storage_owners.py`, `storage_places.py` |
| Notes | `docs/methods/storage.md` (the method, decisions, cross-checks, replication), `eia930_all_storage.md`, `caiso_battery_storage.md`, `storage_buildout.md`, `storage_owners.md`, `storage_places.md`; `replication/storage/` (63,075 of 63,075 on 16 November) |

## The default view re-done, to the digit

The page reads the live set; this machine reads none. The main copy holds the inputs newer than its derived tables (EIA-860M September 2026; EIA-930 to 4 November 23:00 UTC; CAISO to 5 November 07:55 UTC), so:

- **The page's own pipeline.** `trim.py` copied the inputs (EIA-860M whole; the hourly and 5-minute tables from 1 November 2025, a year) into a trial folder under `runs/`; `trial_build.py` ran the page's three builders unchanged there (`iso_prices.set_out_dir`, nothing under `warehouse/output`, no lock). `fixture.py` answered the page's reads from those tables, and `draw.mjs` drew `/storage` (fleet, build-out for the US, ERCOT and CAISO in MWh, owners) and `/storage/places` with the site's own components, "now" set to 5 November 2026 12:00 UTC, every other request refused (`main_asked.txt`).
- **The restatement.** `restate.py` (standard library, none of the site's or the builders' code), written from the method note and the page's words: the fleet from the EIA-860M tables themselves (not `storage_capacity`), the cycle from the hourly series and CAISO's 5-minute values (not `storage_daily_cycle`).
- **Result: 97 of 97 marked figures agree, raw value and shown text, and so do the 9 words-level figures** (`restate.out`): the inventory month, the 24-hour window's end, the grids named under the table and each sparkline's 30 values, span and days not held.
- **The build-out:** `restate_buildout.py`, from EIA-860M with its own month rule, **629 of 629** figures of the US, ERCOT and CAISO-in-MWh views (`restate_buildout.out`).

| Figure (drawn 5 November 2026) | Page | Restated |
|---|---|---|
| Batteries operating in the US | 56,120.70 MW, 1,156 units, September 2026 | the same |
| The fleet: under construction, planned, retired | 23,298.60 MW (240); 40,936.20 (244); 338.50 (8) | the same; MWh 154,272.40 over 1,155 operating units, 1,236.10 over 8 retired |
| By ISO, operating | CAISO 17,265.50, ERCOT 19,194.60, ISO-NE 1,021.70, MISO 1,175.90, NYISO 268.70, PJM 665.90, SPP 490.50, outside 16,037.90 | the same, and every under-construction and planned cell |
| The 15 states | TX 19,394.60 down to OK 432 | the same, in the same order |
| Planned by year | 2026 9,650 to 2031 1,218.60 (64,234.80 in all) | the same |
| Daily cycle, ERCOT, 1 November (Central) | 19,559 out, 36,582 in, 0.54, 17:00, 11:00 | the same |
| Daily cycle, CAISO, 4 November (Pacific) | 46,989.67 out, 52,946.58 in, 0.89, 17:00, 13:00 | the same |
| Daily cycle, US Lower 48, ISO-NE, MISO, SPP | 36,538 / 39,141 / no ratio; 569 / 0; 1,680 / 2,708 / 0.62; 12 / 0 | the same (US48's ratio, 0.93, is computed and not shown, as the page says) |
| Build-out, the United States | 56,120 MW, 154,272 MWh, 2.75 hours, up from 37,790 a year ago; 18,330 MW added | the same |

### One rule changed at a time

`measures.py` (`measures.json`, `measures.out`), from the trial folder's tables and, read only, the main copy's `eia860m_retired_generators_all`.

| Rule | The page | Changed to | Measured worth |
|---|---|---|---|
| What "operating" holds | EIA's operating sheet (OP, SB, OS, OA) | OP only | 56,120.7 MW becomes 55,612.7 (-508.0, 0.9 percent): OA 362.0, OS 144.0, SB 2.0 |
| Nameplate against net summer | nameplate | net summer capacity | 56,120.7 becomes 55,746.0 MW (-0.7 percent) |
| The national line | EIA-930 US48 | US48 plus CAISO's own | over the 683 common hours to 4 November: 1,467,480 MWh discharged becomes 2,754,157 (+88 percent); still without NYISO and PJM (934.6 MW) |
| The newest day | settled: ended 48 hours before EIA's newest hour | complete | every EIA-930 row moves from 1 November to 3 November; CAISO's stays at 4 November |
| Out over in | the newest day | the 30 days held | ERCOT 0.54 becomes 0.81 (daily 0.49 to 1.63); MISO 0.62 becomes 0.82 (0.41 to 1.99); CAISO 0.89 becomes 0.87 (0.65 to 1.11) |
| The fall-back day | 25 hours (1 November) | 24 | ERCOT's charged 36,582 becomes 35,702 (the second 01:00 hour, 880 MWh, 2.4 percent); discharged unchanged; ISO-NE 569 becomes 568 |
| Retired batteries in the build-out's history | the retired table's two years | EIA's full list | the US year end 2015 250.2 MW becomes 362.9 (+45.0 percent), 2016 +27.2, 2017 +19.7, 2018 +13.9, 2019 +11.1, 2020 +6.7, 2021 +1.9, 2022 +0.4, 2023 +0.2; 2024 on unchanged |
| The fleet's "Retired" cell | the retired table (2025 and 2026) | EIA's full list (August 2026) | 8 units, 338.5 MW becomes 50 units, 524.3 MW |
| Average hours | MWh over the MW of units that give MWh | over all MW | 2.7498 becomes 2.7489 (one unit, 17.5 MW, gives none) |

## Each claim against the code

- **MW against MWh and duration.** The fleet sums nameplate MW by status, and MWh only where EIA gives it (operating and retired; 1,155 of 1,156 operating units), said in the section's note and in decision 8. The build-out's average hours are MWh over the MW of the units that report energy, said in its header; the one unit without energy is drawn grey in MW and left out in MWh, and the chart says so. Right.
- **Nameplate against operable.** "Operating" is EIA's operating sheet, which counts 22 units (508.0 MW) on standby or out of service; "nameplate power" is said, the statuses are not (**finding 6**). Net summer capacity is 0.7 percent lower; not on the page, not wrong.
- **Charging against discharging, the sign.** Positive discharging, negative charging, as EIA-930 and CAISO publish. True for ERCOT from 15 December 2025, MISO, the Lower 48 and CAISO; ISO-NE's and SPP's series are never negative, and the page reads them as net in its decision, its hover and its charts (**finding 3**). The Lower 48's missing ratio is explained under the table and names ISO-NE and SPP. Right there.
- **Net output in peak hours.** "Peak discharge hour" is the hour of the largest net output of the grid's fleet; the hover says the count is netted and that the awards page's per-resource count stands above it. Right, but for ISO-NE and SPP it is the output above zero as reported (finding 3).
- **"Share of the evening peak".** No such figure is on the page, any tab or the places view.
- **Interval against hourly.** EIA-930 is hourly; CAISO's hour is the mean of twelve 5-minute values, an hour short of twelve is not drawn (`caisoHourly`, `n === 12`), and a Pacific day needs every interval (288, 276, 300). Said in the notes and decision 2. The method note's cross-check sets CAISO's 5-minute peak (13,441 MW) beside the others' hourly peaks and says so; the 30 days' highest CAISO hourly mean was 10,841 MW. Right.
- **Daylight saving days.** Local days of 23 or 25 hours, said in decision 3. The newest EIA-930 day drawn, 1 November, was a 25-hour day: one extra hour (ERCOT's charged +2.4 percent), not marked on the row. CAISO's autumn day is never whole (CAISO prints 288 rows) and the sparkline names it as not held. Acceptable.
- **The clock.** Each grid's local time (ERCOT and SPP Central, ISO-NE and the Lower 48 Eastern, MISO fixed EST, CAISO Pacific), named on each row; the charts are UTC, said. The rows can be of different days, each named (finding 2).
- **Growth from few points.** No growth rate is printed. "Up from 37,790 MW a year ago" and the year-end bars are rebuilt from one inventory (said in a fold); the fold's "slightly understated" is not (**finding 4**, and **finding 5** for the figures). Planned MW by year are developers' dates, said as intentions; no planned unit in the September inventory is dated before it.
- **Held grids.** ISO-NE, MISO and NYISO appear with EIA-860M's units and EIA-930's series, both EIA's, public (`site/data/license_status.json`); no held table is read (`main_asked.txt`), no drawn view prints "license needed".
- **Staleness and the window.** The fleet names its inventory (September 2026); each cycle row names its day and time zone; the 24-hour chart names its last hour; the sparklines name the days not held; the owners and places snapshots name their inventory and build date, the same September inventory as the fleet. "Latest complete local day" was false by up to two days (**finding 2**).
- **"Batteries operating in the US" beside "US Lower 48".** The headline counts every unit (Alaska 131.7 MW, Hawaii 516.9, Puerto Rico 38.2 included); the Lower 48 output leaves out CAISO, NYISO and PJM (**finding 1**).
- **Storage against solar.** MWh of batteries per MW of solar, "the hours the grid's batteries could carry its whole solar fleet at nameplate output": an energy ratio worded as a power claim (**finding 7**).

## What an expert's own number would hold that this does not

- **Cycles, not only MWh.** A developer's analyst reads discharge against energy capacity: on the days shown ERCOT's fleet gave 19,559 MWh against 31,720 MWh of nameplate energy (0.62 equivalent full cycles), CAISO's 46,990 against 59,726 (0.79). Sized from the page's own figures; not on the page.
- **Out over in over a month.** The day's ratio swings with charge carried across midnight (ERCOT 0.49 to 1.63 in 30 days); over the 30 days it is 0.81 for ERCOT, 0.82 for MISO, 0.87 for CAISO. The page labels the day's ratio "not a measured efficiency", right; the steadier figure is not shown.
- **A national output with California in it.** EIA-930's Lower 48 plus CAISO's own data would add 88 percent to the 30 days' discharge (finding 1); NYISO and PJM (934.6 MW) would still be missing.
- **Usable energy and degradation.** EIA's nameplate MWh is the energy at installation; a lender sizes on usable, degraded energy. Not held.
- **Accredited capacity.** A market monitor reads a battery's capacity value (ELCC, the ISO's accreditation by duration), not nameplate. Not held for most grids.
- **Batteries under other fuel types.** EIA-930 reports solar and wind with integrated storage apart from BAT (`eia930_all_generation`); how much battery output sits there for the four grids is not measured here (data request b).
- **What EIA revises.** The size of EIA's revisions to its newest hours (session 7050's example: ERCOT 853 MW posted, 8,438 the day before) is not measured here: one copy of each hour is held (data request a).

## Findings

| # | Severity | Finding | Measured | Branch | Kind |
|---|---|---|---|---|---|
| 1 | Major | "US Lower 48" (a row and a chart line) leaves out CAISO, NYISO and PJM, and the page never says so | 18,200.1 of 56,120.7 operating MW (32.4 percent); CAISO's own discharge 88 percent of the Lower 48's over 683 hours, above it in 267 | `wip/audit-storage-1` (`db93006e1`) | words, for landing |
| 2 | Moderate | "Latest complete local day" is the newest day settled 48 hours; CAISO's row has no wait; the hourly charts draw the unsettled hours | drawn 5 November: EIA-930 rows on 1 November, 2 and 3 November complete; CAISO on 4 November | `wip/audit-storage-2` (`2c6ea7ad6`) | words, for landing |
| 3 | Moderate | ISO-NE's and SPP's series carry no charging (ERCOT's had none before 15 December 2025); the decision, the hover and the charts read them as net | ISO-NE 0 of 8,832 hours below zero, SPP 0 of 6,528 (zero in 2,949); ERCOT November 2025 542,549 MWh out, 0 in | `wip/audit-storage-3` (`aabbcbaba`) | words, for landing |
| 4 | Minor | The build-out's fold says the early years are "slightly understated" | the US year end lacks 31 percent in 2015, 21 in 2016, 10 in 2019, 6 in 2020 | `wip/audit-storage-4` (`3db505ba8`) | words, for landing |
| 5 | Minor | The build-out's history leaves out batteries retired before 2025 though the full list is held | 2015 +45.0 percent, 2019 +11.1, 2020 +6.7, from 2024 none | `wip/audit-storage-5` (`10a105cff`) | figure, the owner's ruling |
| 6 | Minor | "Operating" counts standby and out-of-service units; "Retired" is two years only | 22 units, 508.0 MW; 8 units, 338.5 MW against 50 and 524.3 | `wip/audit-storage-6` (`de9938cee`) | words, for landing |
| 7 | Minor | "Storage against solar" says the batteries could carry the solar fleet at nameplate | battery MW over solar MW 0.034 (PJM) to 0.663 (CAISO), 0.326 in the US | `wip/audit-storage-7` (`132daefed`) | words, for landing |

### 1. The Lower 48 without California

- **Where.** `page.tsx`: `BAS` entity `eia930:US48`, label "US Lower 48", in the daily cycle's first row and the third chart. `eia930_storage.py`: `NO_BAT = ["ciso", "nyis", "pjm"]` are never asked, because EIA-930 has no BAT series for them. The page said "NYISO and PJM report no battery series" and that CAISO reports none to EIA-930, but never that the national row and line therefore leave them out, beside a headline of every battery in the US.
- **The fix on the branch.** Words only: under the table, "The Lower 48 row is EIA-930's national total, which leaves out CAISO, NYISO and PJM: their batteries report no series to EIA-930, so it is not the whole country's battery output, and CAISO's own row in this table is not in it."; the line's label "US Lower 48 (EIA-930, without CAISO, NYISO and PJM)"; the section's note one sentence. Drawn and read: pass (`words_default.txt`); the 97 figures unchanged. Test `tests/test_audit_storage_1.py`; the fourteen other test files that read the page and the site's read script (25 of 25) pass, but for `test_session148.py`'s node test (the Ask speed tests), which fails the same way on a clean origin/main.

### 2. The newest day, and the hours not yet settled

- **Where.** `storage_daily_cycle.py`: `SETTLE_HOURS = 48`, an EIA-930 day only once it ended 48 hours before the area's newest hour (session 7050: EIA posts early and fills in later); `caiso_rows` has no such rule. `page.tsx`: the header "Balancing authority, latest complete local day"; the 24-hour chart and the 30-day chart draw every hour held, including the 48 the cycle waits for.
- **The fix on the branch.** Words only: the header "Balancing authority, newest local day shown"; under the table, "The EIA-930 rows show a day only once it ended at least 48 hours before EIA's newest hour, because EIA posts its newest hours early and fills them in later: the newest one or two complete days wait. CAISO's row has no such wait, so its day can be newer."; in the 24-hour chart's note, "These are EIA's newest hours, which it may still revise; the daily cycle below waits 48 hours for them." Drawn and read: pass. Test `tests/test_audit_storage_2.py`; the page's test files and `test_session7050_storage_settle.py` pass (but for the same `test_session148.py` node test, failing on clean origin/main).

### 3. No charging in two series

- **Where.** Decision 1 (`decisions.ts`, word for word `storage.md`); `DISCHARGED_TITLE` ("It is the fleet's net output, so a battery charging while another discharges cancels within the hour"); both charts' notes. `docs/methods/eia930_all_storage.md` already records "Charging is not in every series"; the page did not. ISO-NE's series was above zero in 8,795 of 8,832 hours: it never shows the fleet charging.
- **The fix on the branch.** Words only: decision 1 adds "ISO-NE's and SPP's series never go below zero, nor did ERCOT's before 15 December 2025: for them charging is not in the series, and a zero hour is not an idle battery." (in both places); the hover "... cancels within the hour, where the grid reports charging: ISO-NE and SPP report none (their series never go below zero), so theirs is the output above zero as reported, and their charged MWh is 0 because nothing below zero is reported."; both charts "ISO-NE's and SPP's lines never go below zero: they report no charging to EIA-930, so a zero hour there is not an idle battery." Drawn and read: pass (every tab's decisions). Test `tests/test_audit_storage_3.py`; the 20 test files that read the decisions list or the methods notes, the page's test files and the read script pass.

### 4 and 5. The build-out's early years

- **Where.** `storage_buildout.py` reads `eia860m_retired_generators`, the inventory's year and the year before; a battery retired earlier is in no month. The fold: "so early years are slightly understated". The warehouse holds `eia860m_retired_generators_all` (every retired generator EIA lists, public): 50 batteries, 524.3 MW, 42 and 185.8 MW retired before 2025.
- **Finding 4, the fix on the branch.** Words only: "... so early years are understated: by EIA's full list of retired batteries, the United States' end of 2019 lacks about a tenth of the MW then operating and the end of 2015 nearly a third." Drawn and read: pass; the 629 figures unchanged. Test `tests/test_audit_storage_4.py`; the build-out's test files and `test-buildout.mjs` (935 checks) pass.
- **Finding 5, for the owner.** Reading the full list would move the bars: 2015 250.2 MW becomes 362.9, 2019 1,004.0 becomes 1,115.4, 2020 1,589.0 becomes 1,695.0, from 2024 nothing. Test `tests/test_audit_storage_5.py` (passes on main: it shows the rule). Default: left as it is.

### 6. Two of the fleet's cells

- **Where.** `page.tsx`, "The fleet": "Nameplate MW of every battery unit (prime mover BA) in EIA-860M, by EIA's status". Operating is the operating sheet (OP, SB, OS, OA; the build-out's header says so, the fleet tab did not): 2 units on standby (2 MW), 10 out of service and not expected back next year (144 MW), 10 out of service and expected back (362 MW). Retired is the two-year table.
- **The fix on the branch.** Words only, in the note: "Operating is EIA's operating inventory, which also counts units on standby and units out of service (EIA's codes SB, OS and OA). Retired holds only the units retired in the inventory's year and the year before, not every battery ever retired." Drawn and read: pass. Test `tests/test_audit_storage_6.py`; the page's test files pass.

### 7. Storage against solar

- **Where.** `buildout/view.tsx`, the chart's note; `storage_buildout.md`, the variable's row ("the hours the batteries could carry the solar fleet's nameplate").
- **The fix on the branch.** Words only: "The ratio is the batteries' energy counted in hours of the solar fleet's nameplate output: at 1.0, they hold as much energy as the solar fleet makes in one hour at nameplate. It compares energy only: in EIA's newest inventory the batteries' power is below the solar fleet's on every grid, so they could neither take in nor give back that output at its rate." and the note's row to match. Drawn and read: pass. Test `tests/test_audit_storage_7.py`; the build-out's test files pass.

**Together.** Branches 1, 2, 3 and 6 each add a constant beside `ISOS` in `page.tsx` and 1, 2 and 3 touch the same two chart notes, so they conflict when merged one after another. `wip/audit-storage-words` (`2931844e2`) is origin/main with 1, 2, 3, 4, 6 and 7 merged and the conflicts resolved (each branch's words kept whole): its six audit tests, 412 tests of the 42 files that read the touched files, the read script (25 of 25) and the build-out's checks (935) pass; drawn, every figure of the six views unchanged, the words read: pass.

## What was checked and found right

- The fleet's sums by status, ISO, state and planned year; the inventory month from the newest vintage; the 15 states' order (MW, then name).
- The daily cycle: complete local days with 23 and 25 hours, the 48-hour rule, CAISO's hourly means and complete Pacific days, the peak hours (earliest on a tie), the ratio to three places half up, the Lower 48's ratio withheld, the grids with no charging named.
- The sparklines' last 30 days held and the days not held between them; the 24-hour chart's window; the charts' breaks (`gap`) where hours are not held.
- The build-out: operating at a month's end by first month and retirement month, the duration buckets, the twelve months' change, MWh per MW of reporting units, MWh per MW of solar, planned MW by year, all three views to the digit.
- The owners and places snapshots are the same September 2026 inventory as the fleet (US 56,120.7 MW, 1,156 units).

## Not covered, or left open

- The owners tab's and the places view's figures were drawn (their text is under `runs/`, not kept) but not restated one by one; their US totals agree with the fleet.
- The hourly charts' plotted points (SVG) were not compared point by point; their inputs are the restated hours.
- `/grid`'s batteries block and the home page's tile read the same tables; not drawn here.
- The Ask panel on ERCOT's views was not run (it calls a model).

## Rows for the desk

- **Landing (words, requested):** `wip/audit-storage-words` `2931844e2` (1, 2, 3, 4, 6, 7 merged, conflicts resolved), or each alone: `wip/audit-storage-1` `db93006e1`; `wip/audit-storage-2` `2c6ea7ad6`; `wip/audit-storage-3` `aabbcbaba`; `wip/audit-storage-4` `3db505ba8`; `wip/audit-storage-6` `de9938cee`; `wip/audit-storage-7` `132daefed`.
- **For the owner (not for landing):** `wip/audit-storage-5` `10a105cff`.
- **Data requests:** (a) the size of EIA's revisions to its newest BAT hours: for ERCO, ISNE, MISO, SWPP and US48, each hour's first-posted value (the raw pages under `warehouse/raw/eia930_storage/<run_id>/` of three consecutive daily runs) against the value held 72 hours later, over the last 30 days; it sizes finding 2. (b) From `eia930_all_generation`, the MWh of EIA-930's other storage fuel types (solar and wind with integrated storage, other storage) for ERCO, ISNE, MISO and SWPP over the last 30 days held, beside each one's BAT discharge; it sizes how much battery output the page's four series do not see.
