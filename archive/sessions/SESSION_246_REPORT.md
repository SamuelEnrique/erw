# Session 246 report: the CAISO battery at ERCOT's depth

13 October 2026, 07:12 to 07:45 UTC, unattended, on lab-desktop (the data machine), the fourth session of the chain of 12 to 13 October. Branch `task/246-caiso-battery`. Model spend USD 0: no model call. Pulls: three requests to caiso.com (its robots file and two of its market monitor's published reports). Writes under the data lock: the two battery tables rebuilt, their stores, their load into the live set. The page was not edited.

## Read these first

- **California's stress days are in the table now.** `battery_stack_stress_daily` held ERCOT's three events only; it holds 144 rows for CAISO at SP15 too. They are made by a rule from CAISO's own notices, not picked: two events fall inside the held prices, 4 to 9 September 2024 and 20 and 21 January 2025.
- **Run the market monitor's way, the model lands within 10 percent of the market monitor's own model for 2025:** USD 84.72 per kW against its 77.3, for a 4-hour battery selling energy and regulation day-ahead. Quarter by quarter: 29.2, 24.3, 17.5, 13.8 against 28.8, 22.8, 14.2, 11.5. Its 2025 annual report (June 2026) is the first with a year both hold.
- **The real fleet earned far less, and the whole gap is regulation.** Real batteries in CAISO's area: about USD 35 per kW for energy and 9 for regulation in 2025. The model: 42.31 and 42.25. On energy it is a fifth above; on regulation almost five times. The market monitor says the same of its own model.
- **CAISO's monthly history cannot reach ERCOT's with what is held:** CAISO's prices begin in September 2024 (25 months); ERCOT's in 2018. That needs a pull, for your ruling.
- **On the page, CAISO is not marked "in review" today:** `site/lib/batterystack.ts` has it `ready: true`. What the page shows for ERCOT and not for CAISO is two things, and both can be drawn from data that now exists. The list for the code machine is below and in the method.
- **Sessions 243, 244 and 245: each deployment finished before its after snapshot.** 243: deployed 06:42:02, snapshot 06:48:41. 244: 07:09:57, snapshot 07:10:38. 245: pushed 07:11:22 (`task/245-hourly-carbon-year`), check run 38361106197 passed, merged as `1ca3bd34` at 07:19:17, deployed 07:21:57; before snapshot `s244-after`, after snapshot `s245-after` (07:26:29, 25 pages, 0 failed); `compare`: 0 differences, as expected.

## California's stress days

- **The rule:** a stress day is a local day on which CAISO issued a system-wide notice (Flex Alert, Restricted Maintenance Operations, an Energy Emergency Alert, a Stage emergency, a Warning, an Alert, a load interruption), as `caiso_grid_emergencies` holds it. A Transmission Emergency is local and makes none. Days at most three days apart are one event, named for its first day.
- **Built on 13 October 2026, USD per MW of power over the window:**

| Event | Days | CAISO's notices | 2 hours, day-ahead | 4 hours, day-ahead | 8 hours, day-ahead | 4 hours, perfect foresight | Best day, 4 hours, day-ahead |
|---|---|---|---|---|---|---|---|
| `caiso_notices_20240904` | 4 to 9 September 2024 | Restricted Maintenance Operations on 4, 5, 6 and 9 September | 3,670 | 4,101 | 4,464 | 3,938 | 5 September: 1,726 |
| `caiso_notices_20250120` | 20 and 21 January 2025 | Restricted Maintenance Operations on both days | 475 | 638 | 854 | 731 | 20 January: 353 |

- The first is California's dearest stretch in the held prices: the three dearest day-ahead days at SP15 since September 2024 are 5, 6 and 4 September 2024.
- The second is an ordinary pair of days by price. The rule writes it because CAISO issued the notice.
- **CAISO's notices are held to 30 April 2025** (the report has no schedule). A notice after that makes no event until the report is read again; the next run then writes it.
- ERCOT's 1,260 stress rows did not change (0 values differ).

## Beside CAISO's market monitor

Source: CAISO, Department of Market Monitoring, *2025 Annual Report on Market Issues and Performance*, June 2026, section 1.3.3, Tables 1.7 and 1.8 (pages 118 to 121). A hypothetical 100 MW, 4-hour battery, round trip 0.85, energy and regulation day-ahead, at more than 280 nodes. Ours: SP15, the 361 days of 2025 held. USD per kW. Gap is ours less theirs.

| What | Ours | Theirs | Gap | Reason |
|---|---|---|---|---|
| 2025, energy and regulation, day-ahead, run their way (regulation only, round trip 0.85) | 84.72 | 77.3 (CAISO System) | +7.4 (10 percent) | One hub against every node; their regulation awards move energy and ours do not; their month-long horizon with no cycle limit against our day from empty with one cycle. Not separated |
| the same by quarter: Q1; Q2; Q3; Q4 | 29.23; 24.30; 17.45; 13.75 | 28.8; 22.8; 14.2; 11.5 | +0.4; +1.5; +3.3; +2.3 | The same shape: ours falls 53 percent from the first quarter to the fourth, theirs 60. The third quarter's gap is the largest and is not explained |
| the split: energy; regulation | 41.89; 42.83 | 39; 39 | +2.9; +3.8 | Both models earn about half from each |
| the page's model, day-ahead (all four reserves, round trip 0.86) | 85.34 | 77.3 | +8.0 | Spinning and Non-Spinning Reserve add USD 0.77 |
| the page's model, perfect foresight | 91.74 | 77.3 | +14.4 | Real-time with foresight against a day-ahead schedule |
| **the real fleet**: energy; regulation | 42.31; 42.25 | about 35; 9 | +7.3; +33.3 | The model sells regulation as if the market had no size. Their report: "there is a large amount of battery capacity competing to provide a relatively low amount of required regulation" |
| their southern areas: LA Basin; Big Creek/Ventura; San Diego/Imperial Valley | 84.72 | 62.6; 64.2; 66.3 | +22.1; +20.5; +18.4 | Not explained: our SP15 hub figure sits near their system figure, not near their southern local areas. How their nodes map to the hub was not checked |
| 2024, 2023, 2022 | no whole year held | the fleet: 53, 78, 103 (their 2024 battery report) | none to compute | Session 196's row stands |

- The full table with its sources is in `docs/methods/battery_stack.md`, "CAISO beside its market monitor". `python warehouse/analysis/battery_caiso_dmm.py` runs it again (about a minute; no request).

## For the code machine: what CAISO lacks on the page beside ERCOT

| On the page for ERCOT | For CAISO today | What makes it equal | Where |
|---|---|---|---|
| The stress days and the table's download | Nothing: `EVENTS` holds ERCOT's three ids, so `stress()` passes over CAISO's rows; the sentence is drawn only when `x.grid === "ercot"` | Read the events from the rows of the grid shown (an id beginning `caiso_notices_` is CAISO's; its label is its days), and draw the sentence for both grids. The rows are in Supabase now | `site/lib/batterystack.ts` (`EVENTS`, `stress`, the `stress` case of `stat`); `site/app/cost-of-power/battery/page.tsx` (the line beginning `{x.grid === "ercot" ? <> The stress days`) |
| One line beside the ancillary income: what ERCOT's storage was really awarded | Nothing: `awardsBeside` returns null unless the grid is ERCOT | The market monitor's real-fleet figures play the same part: USD 35 energy and 9 regulation per kW in 2025, against the model's 42.31 and 42.25, with the report cited | `site/lib/batterystack.ts` (`awardsBeside`); the page's "Income by stream" |
| History from 2018 | From September 2024 (the page already says so) | Not the page's to fix: a pull, for a ruling | |

- No flag needs to flip: CAISO is `ready: true` at commit `1ca3bd34`, and no line of the page's code marks it "in review". If the rebuilt page marks it so, the two rows above are what it waits for.

## Checks

| What | Exit | Notes |
|---|---|---|
| `python scripts/precheck.py` | 0 | six of six |
| a trial build into a scratch folder, compared with the tables held | 0 | monthly: 10,542 rows in both, 101 values differ, all of October 2026 (two more days of prices than the copy held, which was of 10 October); stress: 1,260 rows identical, 144 new |
| `battery_stack.py`, under `lock.py run` | 0 | 10,542 and 1,404 rows |
| `table_stores.py` for both tables | 1, then 0 | the first run stopped at the coverage gate: see decision 6 |
| `load.py --only '^battery_stack_(monthly|stress_daily)$'` | 0 | match; written 101 and 144; deleted 0 |
| the 17 test modules that name the battery model | 0 | 341 tests, on the rebuilt tables |
| `python -m unittest tests.test_session246` | 0 | 14 tests |
| `python -m unittest discover -s tests` | 1 | 3,708 tests, 3 failures, the same three as before this chain |
| snapshots `s245-after` against `s246-after-load` | 0 | 0 differences: the load changed nothing a visitor sees |
| `python scripts/freeze.py status` | 0 | no freeze |

## Decisions made without you

1. **California's stress events are made by a rule, not chosen.** ERCOT's three are named events; nobody has named California's for this window. CAISO's own notices are the one record of when its system was under strain, so the rule reads them. The cost: the January 2025 pair is in the table though its prices were ordinary.
2. **A Transmission Emergency is not a stress day.** It is a local event (a line, a fire), not a shortage on the system. Counting it would add November 2024 and one day of April 2025.
3. **The monthly table was rebuilt on this machine,** from the prices held here. Only October 2026 moved, in both grids: this machine's copy was two days older than the prices. The page files built from it (the scenario steps, the dispatch export) were not touched; their 341 tests pass on the rebuilt table.
4. **The comparison uses the market monitor's annual report, not its battery report.** Its yearly battery report for 2025 was not found (a search of caiso.com on 13 October); the annual report has the model and the fleet's figures for 2025.
5. **Their figures are typed into the script from the PDF,** each with its table and page, and a test holds that their quarters add to their totals and that the method quotes the same numbers. The PDFs and their text by page are in `runs/session246/dmm/` on this machine, not in git.
6. **My first build wrote a note in brackets into the tables' "Derived from" line,** and the coverage builder, which reads that line as table names, refused both tables. Nothing reached the archive, the draft or the live set from that build. I corrected the line, rebuilt and ran the stores again (all exit 0). A test now holds the line to table names.
7. **Coverage names both grids for the stress table** (it said ERCOT).
8. **The existing cross-check row for CAISO in the algorithm note was left as written** (session 196: "no year is held by both"); a bullet under the table points to the new comparison.

## For Samuel's ruling

1. **Pull CAISO's price history before September 2024?** CAISO's system serves about 39 months back. That would give the battery page California from mid 2023 and put the 2023 and 2024 summers in the stress table. It is the one thing that keeps CAISO short of ERCOT's depth.
2. **Read CAISO's notices on a schedule?** They are held to 30 April 2025, so no stress event after that date can be written. One request for one PDF (session 218 listed the same connector).
3. **Keep the January 2025 event?** It is in the table by the rule. A floor (for example, a day-ahead hour above USD 200) would drop it and would be a judgment the rule now avoids.
4. **Should the page show California's ancillary income with the market monitor's caveat beside it?** The model takes USD 42 per kW of regulation where the real fleet was paid 9.
5. **The southern areas' gap** (our hub at 84.72, their LA Basin at 62.6) is not explained. Worth a session with CAISO's node list?

## Files

- New: `warehouse/analysis/battery_caiso_dmm.py`, `tests/test_session246.py`.
- Changed: `warehouse/derived/battery_stack.py` (CAISO's stress events by rule; the stress table's header), `warehouse/metadata/build_coverage.py` (both grids for the stress table), `docs/methods/battery_stack.md` (three new sections), `docs/methods/battery_earns_algorithm.md` (one bullet), and the metadata the stores wrote.
- On this machine, not in git: the two tables, `warehouse/output/analysis_internal/battery_caiso_dmm_2025.csv`, `runs/session246/` (the reports, the trial's comparison, the outputs).

## The landing

- Freeze: `python scripts/freeze.py status` exit 0, no freeze. Main pulled and merged before the push. Before snapshot `s246-after-load` (07:26:54 UTC, 25 pages, 0 failed; after the load), then the push of `task/246-caiso-battery`. The check run, the merge, the deployment's time, the after snapshot and the comparison are in session 247's report. Expected: 0 differences on the 25 pages.
