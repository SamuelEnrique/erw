# Session 251 report: the findings engine, from 7 patterns to 20

13 October 2026, 18:02 to 18:45 UTC, unattended, on lab-desktop (the data machine), the first of three sessions (251, 254, 255). Branch `task/251-findings-engine`. Model spend USD 0: no model call, and none in what was built. Pulls: none, no request to any publisher. Writes: 12 rows added to the review list `public.scanner_drafts` by the hunt, under the data lock; no warehouse table, no live-set table, no page.

## Read these first

- **The weekly hunt now holds 20 patterns: the 7 of session 233 and 13 new families,** each a measure by region and year computed straight from warehouse tables (`warehouse/analysis/findings/hunt_measures.py`), run on every public grid and region it applies to. The full hunt takes about three minutes.
- **The hunt ran once, at 18:18 UTC: 143 claims, 50 pass the three tests, 12 new drafts wait at `/internal/findings`** (the cap; the list now holds 28). All 12 are from the new families. 26 more passing claims wait beyond the cap: Saturday's hunt will raise up to 12 of them (ruling 2).
- **All 12 were verified as session 252 did, and only 3 of the 12 can be approved as drafted: 3 strong, 7 usable, 2 drop.** `docs/reviews/findings-verified-2026-10-13.md`, the new last section. Strong: the evening ramp in ERCOT (the median day's steepest hour, 1,123 to 6,871 MW per hour, 2019 to 2025) and in CAISO (4,473 to 7,122), and CAISO's curtailed share of wind and solar (0.67 to 4.53 percent, 2015 to 2025).
- **Drop:** California's demand growth after weather (a change of 2.5 points against the table's own uncertainty of 3.21, over four years) and wind's share of ERCOT's night (98.5 percent of the claim is the year 2019). The hunt ranked the first of them third of twelve: its strength is not safe on four years (rulings 3 and 4).
- **Session 252's two lessons are in the engine.** The two spike patterns are computed and never drafted (7 of their claims passed tonight, none drafted). Every draft's source line names only the tables its own region's rows come from; none of the 12 names a table in `license_status.csv`.

## What to review

- The verification on GitHub: https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/findings-verified-2026-10-13.md
  1. Scroll to "Session 251's twelve drafts, verified" (the last section). Read its "Read these first" (six bullets).
  2. Open https://erw-flame.vercel.app/internal/findings beside it (the internal view is needed: the form at `/internal/open`). The 12 new drafts are those raised on 13 October at 18:18 UTC; each block names its draft's pattern and region.
  3. For each block 17 to 28, read the last line (the verdict and its reason), then rule on the page. Nothing was ruled by this session.
- The method on GitHub: https://github.com/SamuelEnrique/erw/blob/main/docs/methods/automated_analysis_findings.md , the section "The hunt's own measures: from 7 patterns to 20": one row a family (the measure, the regions, the tables, the second number).
- No page changed. `/internal/findings` shows 12 more drafts (a row each in the review list; the page's code is as it was).

## The 13 families

| Family | The measure, by year | Regions computed | Passing claims | Drafted tonight |
|---|---|---|---|---|
| Solar cannibalization | solar's capture rate, percent of the average price; solar's share beside it | 5 hubs | 1 (ERCOT, 180.8 to 75.4 percent, 2019 to 2025) | 0 (beyond the cap) |
| The evening ramp's growth | the median day's largest one-hour rise of net load | 7 grids | 3 | 2 (ERCOT, CAISO) |
| Battery discharge against the evening price peak | percent of the year's discharge from 5 PM to 10 PM | CAISO, ERCOT | 1 | 1 (CAISO) |
| Gas pass-through | the median day's implied heat rate | 8 hubs | 5 | 0 |
| Negative-price hours by zone | percent of hours below zero | 4 ERCOT zones, 3 CAISO hubs | 4 | 2 (West, South) |
| Day-ahead against real-time by hour | the median hour's spread, five parts of the day | 40 (hub by part) | 9 | 1 (West hub, night) |
| Scarcity hours against demand | percent of hours with RTORPA above zero; mean demand beside it | ERCOT | 1 (24.2 to 2.4 percent, 2015 to 2025) | 0 |
| Curtailment against storage build-out | curtailed share of wind and solar; the battery fleet beside it | CAISO, SPP | 1 | 1 (CAISO) |
| Interchange dependence on stress days | net imports on the top 5 percent of days by demand | 7 grids | 2 | 1 (CAISO) |
| Weather-adjusted demand growth | energy above the base that temperature does not explain | 7 balancing authorities, datacenter markets named | 3 | 1 (CAISO) |
| The carbon of peak hours | the evening's intensity against the all-hours mean | 7 grids | 3 | 1 (CAISO) |
| Wind's night share and its price effect | wind's share of generation, midnight to 6 AM; the night's price beside it | 7 grids | 3 | 2 (ERCOT, PJM) |
| Record-setting days | days above every earlier year's highest day | 7 grids | 1 | 0 |

- Of the 143 claims: 12 drafted, 26 pass and wait beyond the cap, 5 pass and are not news, 7 pass and are one interval a year (never drafted), 20 fail a test, 29 are no claim (under two full years: every CAISO price region, held from September 2024), 44 are regions of a grid that needs a license or is held (ISO-NE, MISO, NYISO, SPP).
- Everything computed, with each claim's reason, is in `runs/hunt/2026-10-13/hunt.json` on this machine; session 233's file of the same name is kept in `runs/session251/hunt-before-251/`.

## Checks

| What | Exit | Notes |
|---|---|---|
| `python scripts/precheck.py --what "chain 13 Oct late morning: sessions 251, 254, 255"` | 0 | six of six; on duty |
| `python scripts/freeze.py status` | 0 | no freeze |
| `hunt_measures.py` (the 13 measures alone) | 0 | about 35 seconds; the price histories 25 of them |
| the hunt as a dry run into `runs/session251/dry/` | 0 | 143 claims, 50 pass, 12 drafts, 0 patterns not run |
| `lock.py run -- hunt.py --weekly` | 0 | 18:16 to 18:19 UTC; 12 added to the review list |
| `fetch_drafts.py` | 0 | 28 rows, all in state draft |
| `verify_251.py` (twice: before and after its folder moved) | 0, 0 | 12 of 12 exact from their own CSV, 12 of 12 rebuilt exactly from today's tables, 12 of 12 name their own tables |
| `build_251.py` | 0 | 12 blocks appended; session 252's text above is as it was |
| `python -m unittest tests.test_session251 tests.test_session233 tests.test_session252` | 0 | 55 tests (the first run: 1, see decision 7) |
| the same with five more modules that read the method note, `GITHUB_ACTIONS=true` | 0 | 195 tests, as the runner sees them |
| `python -m unittest discover -s tests` | 1 | 3,968 tests, 3 failures, 45 skipped, 496 s in the foreground: the three this machine always has (`test_session51`, `test_session125`, `test_session165`); none in what this session wrote |

## Decisions made without you

1. **A family is not a finding.** The 13 measures are in one module the hunt alone reads; none is added to `/analysis` (that would need a card, a do-file and page work, and `site/app` is closed to this chain). `run_finding.FINDINGS` is as it was.
2. **No measure is one interval of a year.** The ramp is the median day's, the heat rate the median day's, the spread the median hour's; the rest are shares of hours or days. The year's largest ramp, in the same table, was left as a check, not a pattern.
3. **The spike patterns stay in the library and are never drafted** (`one_interval`), so that their claims are still in the run's file. `hours_above_1000` is left as it was: session 252 dropped its draft for another reason (strength), which is ruling 2 of session 252, not ruled.
4. **A region of ISO-NE, MISO, NYISO or SPP is never drafted, EIA's rows about it included.** The hunt's rule names grids, and I kept it for EIA-930 rows (reversible; ruling 5). PJM's regions are drafted from EIA's rows.
5. **The EIA-930 families run on the seven grids' balancing authorities only.** With every respondent, the strongest "claim" was Arizona Public Service's 2019 interchange carrying the other sign. A day of demand under a third of, or over three times, its year's median is left out as a reporting fault.
6. **"Datacenter regions named" is words, not numbers:** each balancing authority's region carries its datacenter markets as places (PJM: northern Virginia, Ohio and Chicago's suburbs). No count of sites is read: `datacenter_facilities` needs a license from 21 October.
7. **The verification's scripts are in their own folder,** `docs/reviews/findings-verified-2026-10-13-session251/`. First put inside session 252's folder, they broke its test, which lists that folder; moved, and session 252's folder and test are as they were.
8. **The second number beside a claim is stated and never tested** (solar's share, the battery fleet, mean demand, the night's price). The footnote says so. Without it the family's "against" has no number; with a test it would claim a cause.
9. **The scarcity family has one grid.** "Scarcity hours (`ercot_rtm_price_adders`)" is ERCOT's table; the adder after 5 December 2025 (RTRDPA) is not joined to it, as the adder's method note says.
10. **The cap stayed at 12 drafts and 2 regions a pattern.** The 26 passing claims beyond it are in the run's file.
11. **The verdicts are mine,** by session 252's rule. I caught one sentence of mine with numbers I had not read from the file (the night price beside ERCOT's wind) before it was written to the document; it now holds the stored values (3.24, 6.74 and 1.14).
12. **Session 251's landing result is in session 254's report,** as sessions 252 and 253 did.

## For Samuel's ruling

1. The 12 new drafts, with a verdict each: approve the three strong ones, dismiss the two to drop?
2. Saturday's hunt will raise up to 12 of the 26 passing claims beyond tonight's cap, 12 of them under one typical yearly move. Apply session 252's floor on strength first?
3. A fourth test for the hunt, as session 252 asked: half of the change must remain without the first year. It stops ERCOT's night wind and none of the three strong drafts.
4. A floor of years for the hunt's strength: on four full years it ranked a change inside the table's own uncertainty third of twelve.
5. EIA's rows about ISO-NE, MISO, NYISO and SPP (EIA-930: demand, interchange, generation, carbon): may the hunt draft them? They are EIA's publication, and 44 claims were set aside for the grid's name.
6. A card that says "up from" for a step: print the count of yearly steps in the claim's direction on the card? Five of the seven usable drafts are one step or a hump.
7. CAISO's carbon rows for 2026 read 118 kg per MWh in all hours against 190 in 2025: a fault of the table or a real year? It is outside every claim, and it would be inside next year's.
8. CAISO's daily interchange in EIA-930 falls by half in 2023, and 2025 holds 315 days: read EIA's known issues before the stress-day draft is approved?

## Files

- New: `warehouse/analysis/findings/hunt_measures.py`; `tests/test_session251.py`; `docs/reviews/findings-verified-2026-10-13-session251/` (three scripts, what two of them printed, the result file); this report.
- Changed: `warehouse/analysis/findings/hunt.py` (the 13 patterns, `one_interval`, `OWN_TABLES`, the second number, version 1.1.0); `docs/reviews/findings-verified-2026-10-13.md` (a section appended; nothing above it changed); `docs/methods/automated_analysis_findings.md` (a section, and four words of one line); `tests/test_session233.py` (one test skips the measure families, which `tests/test_session251.py` holds).
- On this machine, not in git: `runs/session251/` (the 28 drafts as downloaded, every output); `runs/hunt/2026-10-13/` (tonight's hunt); `runs/hunt/state.json` (the memory, 12 keys more).

## The landing

- Freeze: `python scripts/freeze.py status` exit 0, no freeze.
- The before snapshot, the push, the check run, the merge, the deployment and the after snapshot with its comparison are in session 254's report, under "The landing of session 251". Expected: 0 differences on the 25 pages (a module, a document's section, a method section, scripts and tests; no page, no table a live page reads, no load into the live set).
