# Session 253 report: the generator model for CAISO at ERCOT's depth

13 October 2026, from about 11:00 UTC, unattended, on lab-desktop (the data machine), the second of two sessions (252 and 253). Branch `task/253-caiso-generator`. Model spend USD 0: no model call (two web searches to find LBNL's reports). Pulls: nine requests to two hosts of Lawrence Berkeley National Laboratory, listed below; none to CAISO (its market monitor's report was on this machine from session 246). No warehouse table, no page file and no default changed. No write to the live set.

## Read these first

- **CAISO's generator tables equal a rebuild, and they are now written out as ERCOT's are.** `docs/methods/generator_earns_algorithm.md`, new section 12: capture price and rate at SP15, NP15 and ZP26 for solar and wind, in real time and day-ahead; revenue, energy and the gas peaker by the model; the inputs of the breakeven PPA price. The page's own files match a rebuild from today's tables to the cent in every whole month (26 months, three hubs, three assets).
- **Solar in California was paid under half the average price in the south: USD 14.51 per MWh against 31.19 at SP15 in 2025 (46.5 percent); 26.86 against 37.27 at NP15 (72.1 percent).** Wind was paid 95 to 97 percent of the average. A merchant solar plant covers its debt 0.24 times at SP15 and needs USD 72.58 per MWh for an NPV of zero (ERCOT: 58.36).
- **Wind agrees with LBNL to cents; the gas peaker does not agree with the market monitor at all.** Wind, 2025: our flat price and capture price, as the mean of SP15 and NP15, are 34.23 and 32.91; LBNL's are 34.21 and 32.97. The gas peaker at SP15 in 2025: the page's rule gives USD 30.05 per kW; CAISO's market monitor's combustion turbine earned 0.78.
- **Most of the peaker's gap is one missing cost: California's carbon allowance.** The page's rule charges fuel and variable O&M only. With the allowance on the fuel (USD 1.59 per MMBtu in 2025) the same rule gives 6.95 at SP15 and 10.11 at NP15 (theirs: 0.78 and 3.52). The rest is starts, minimum load and bids. It is a ruling, not a flip: it moves every CAISO peaker figure on the page.
- **Wind's last twelve months are not comparable with 2025.** EIA-860M lists SunZia (3,650 MW, New Mexico) in CAISO's balancing authority from May 2026, so the shape's denominator grows by 58 percent; energy per MW is 2,477 MWh against 3,125 in 2025, and the breakeven PPA price moves from USD 79.50 to 100.31 on that alone. LevelTen's CAISO wind index for 2025, in LBNL's file, is 78.2.

## What to review

- The method note on GitHub, section 12: https://github.com/SamuelEnrique/erw/blob/main/docs/methods/generator_earns_algorithm.md#caiso-depth
  1. 12.2: the capture table (12 rows). Compare a row with the page: https://erw-flame.vercel.app/cost-of-power/seller?iso=caiso&asset=solar#capture (the internal view is needed; the page is in review). The page shows the last twelve months: SP15 13.86 against 28.53.
  2. 12.5: the twelve comparisons, each with its gap and reason.
  3. 12.6: the list for the code machine, five rows.
- No page changed. On the site the method note's page, `/data/methods/generator_earns_algorithm`, gains section 12 (the page is in review).

## The tables, in short (2025, real time)

| Hub | Solar: capture price, rate | Wind: capture price, rate | Gas peaker, the page's rule, USD per kW | The same with the carbon allowance | The market monitor's turbine |
|---|---|---|---|---|---|
| SP15 | 14.51, 46.5 percent | 30.20, 96.8 percent | 30.05 | 6.95 | 0.78 |
| NP15 | 26.86, 72.1 percent | 35.40, 95.0 percent | 41.47 | 10.11 | 3.52 |
| ZP26 | 14.69, 46.3 percent | 30.89, 97.4 percent | 30.88 | 6.44 | none published |

- PPA inputs, page defaults: solar 2,075 MWh per MW, coverage price USD 48.68, breakeven 72.58; wind 3,125 MWh per MW, 55.09 and 79.50; a peaker's toll 8.34 and 12.28 per kW-month.

## Beside published figures: ours, theirs, gap, reason

| What | Ours | Theirs | Gap | Reason |
|---|---|---|---|---|
| Henry Hub, 2025 average | 3.54 | 3.54 (market monitor) | 0.00 | One series by two routes |
| Gas peaker, NP15, 2025, USD per kW | 41.47 | 3.52 | +37.95 | No carbon cost in the rule (with it: 10.11); then starts, minimum load, bids |
| Gas peaker, SP15 | 30.05 | 0.78 | +29.27 | The same (with the allowance: 6.95) |
| The same run their way (heat rate 9.3, USD 4.80, allowance) | 16.32 and 11.27 | 3.52 and 0.78 | +12.80 and +10.49 | Their costs are USD 65.7 and 71.0 per MWh run, ours 50.8 and 50.6: starts and the bid's adder |
| Wind, flat price, 2025 | 34.23 (mean of SP15, NP15) | 34.21 (LBNL) | +0.02 | Two hubs against every plant's node |
| Wind, capture price | 32.91 | 32.97 profile; 30.82 at the plants after curtailment | -0.06 | The page sees the profile, not the node or the curtailment |
| Wind, capture rate | 97.1 and 95.3 percent | 96.4 percent | -0.1 point | The same |
| Solar, capture price | 14.30 (SP15), 2025 | 8.62, 2024 | not computed | No year held by both |
| Solar, capture rate | 45.8 percent, 2025 | 25.1 percent, 2024 | not computed | The same |
| Solar, breakeven PPA | 72.58 | 47.06 (LevelTen, 2024) | +25.52 | No tax credit; 12 percent to equity; a fleet's output |
| Wind, breakeven PPA | 79.50 | 78.2 (LevelTen, 2025) | +1.30 | The same |

## For the code machine: exactly what to flip

1. **The count of published figures, 10 to 20, three edits** (no ruling needed): move the ten rows of 12.5 that hold a gap into the note's "Cross-checks" table; `site/app/cost-of-power/seller/page.tsx` line 299, `data-checked-against="10"` and "Checked against: 10 published figures (Lazard, the Annual Technology Baseline, EIA)" become 20 and add "CAISO's market monitor, Berkeley Lab"; `tests/test_session196.py`, `NOTES`, the generator's count.
2. **The peaker's carbon cost for CAISO** (after ruling 1): `site/lib/merchant.ts`, `peakerOver`, `const c = g * hr + vom;`; and the data machine's `warehouse/derived/merchant_revenue.py`, `cost = x["hh"] * HEAT_RATE + VOM`.
3. **CAISO's stress days** (after the data machine writes them into the snapshot): `site/lib/merchant.ts`, `EVENTS`, two ids, `caiso_notices_20240904` and `caiso_notices_20250120`.
4. **A sentence beside CAISO's wind** (after ruling 2).
5. **Nothing else.** The page has no "ready" flag by grid; CAISO is drawn by ERCOT's code from files that equal a rebuild.

## Pulls

| Host | Requests | Result |
|---|---|---|
| `emp.lbl.gov` | 3: its robots file (HTTP 200, allows), two publication pages | HTTP 403 on both pages. Not asked again, and not worked around |
| `eta-publications.lbl.gov` (LBNL's publications server) | 5: its robots file (allows), two publication pages, two public data workbooks (33.8 and 56.9 MB) | HTTP 200. Each file once, 5 seconds apart; kept in `runs/session253/lbnl/`, not in git |
| CAISO | 0 | The market monitor's report and its text by page were on this machine (`runs/session246/dmm/`) |

- Two web searches found the reports' addresses. No paused publisher was asked (`iso_prices.paused_host` consulted for each host).

## Checks

| What | Exit | Notes |
|---|---|---|
| `python warehouse/analysis/generator_caiso_check.py --cache-dir runs/session253/cache`, three times | 0, 0, 0 | 36 rows; the last run 11:09 UTC |
| `python runs/session253/build_section.py`, run twice in a row | 0, 0 | the note is the same after the second run |
| `python -m unittest tests.test_session253` | 0 | 12 tests; ERCOT's default case comes out of this script's finance at the note's own 39.14, 58.36 and -741.60 |
| the six test modules that read the note or the folder (`183`, `186`, `195`, `196`, `235`, `249`), with `252` and `253` | 0 | 110 tests |
| `tests.test_session252` and `tests.test_session253` with `GITHUB_ACTIONS=true` | 0 | 19 tests, as the runner sees them |
| `python -m unittest discover -s tests` | 1 | 3,889 tests, 3 failures, 45 skipped, 471 s in the foreground: the three this machine always has (`test_session51`, `test_session125`, `test_session165`); none in what this session wrote |
| `python scripts/freeze.py status` | 0 | no freeze |

## Decisions made without you

1. **The section is in the generator's method note, before "Checks", not in its "Cross-checks" table.** That table is counted by the page ("10 published figures") and pinned by `tests/test_session196.py`; adding rows would have needed an edit to the page, which this session may not make.
2. **2025 is the year compared.** It is the one whole calendar year of CAISO prices held, and it is the year of the market monitor's and LBNL's wind figures.
3. **LBNL's files came from `eta-publications.lbl.gov`.** `emp.lbl.gov` refused the ERW's reader with HTTP 403 though its robots file allows the pages. I did not change the reader's name to get past it; LBNL's own publications server links the same public data files and answered.
4. **I read each host's robots file and not a terms page.** The workbooks are LBNL's "public data file" of each report; figures are quoted with their source and no file is copied into the repository. Ruling 5.
5. **LBNL's solar figures are for 2024, and no gap is computed against them.** Its newest solar update found is October 2025's (the year 2024); the ERW's CAISO prices begin in September 2024.
6. **Their figures are typed into the script from the documents,** each with its table or sheet, and a test holds that their tables add up and that the note quotes the same numbers (as session 246 did).
7. **The peaker was also run "their way"** (heat rate 9.3, variable O&M USD 4.80, the allowance) to size the gap. California's delivered gas is not held, so gas stayed Henry Hub; on the year's average the two differ by cents (3.54 against 3.40 and 3.60).
8. **The results are kept in git** under `docs/howitworks/computed/` (the folder that holds session 249's computed text), because `warehouse/output/analysis_internal/` is not.
9. **The mean of SP15 and NP15, equally weighted, is my choice** for setting two hub figures beside LBNL's one CAISO figure. The note says so in the row.

## For Samuel's ruling

1. The CAISO gas peaker has no carbon cost: USD 30.05 per kW at SP15 in 2025 by the page's rule, 6.95 with California's allowance on the fuel, 0.78 by the market monitor. Add the allowance for CAISO? It needs `carb_auction_allowance_prices`, which is license internal.
2. SunZia (3,650 MW, New Mexico) is in CAISO's wind denominator from May 2026 and lowers the last twelve months' energy per MW by a fifth. Say it on the page, hold it out, or check first that EIA-930's CAISO wind counts its output?
3. CAISO at ERCOT's depth in years and hubs needs a pull: prices before September 2024 and the load aggregation points. The battery page waits on the same pull (session 246).
4. CAISO's stress days for the generator: write session 246's notice days into the generator's snapshot?
5. LBNL's public data files: is quoting their figures with the source enough, or should a terms page be read and recorded as for the other publishers in `docs/licenses.md`?
6. Count the ten new comparisons on the page (10 to 20)?
7. Not this session's: the code machine's landing of sessions 237 and 238 (`01161064`) put 35 files under `warehouse/output/raw/madeup_as_prices/` into git. Each is a manifest with a header line and no row, written by a test. `warehouse/output/` is not meant to be in git except the news tables. Remove them and ignore the folder?
8. The live-page snapshots of today hold 0 checked numbers on all 25 pages (`s250`, `s252`): the comparison rests on each page's text and HTML. Meant, since the pages were rebuilt on the brand?

## Files

- New: `warehouse/analysis/generator_caiso_check.py`; `docs/howitworks/computed/generator_caiso_check_2026-10-13.json` and `.csv`; `tests/test_session253.py`; this report.
- Changed: `docs/methods/generator_earns_algorithm.md` (section 12 added before "Checks"; no other line).
- On this machine, not in git: `runs/session253/` (LBNL's two workbooks and robots files, the cache of EIA's workbook, the section's builder, every output); `warehouse/output/analysis_internal/generator_caiso_check.csv` and `.json`.

## The landing of session 252

- Freeze: exit 0, no freeze. Main had moved (the code machine's `01161064`); merged into the branch before the push.
- Before snapshot `s252-before`: 10:59:16 UTC, 25 pages, 0 failed. Pushed 10:59:37 UTC (`task/252-findings-verified`, `cc370a72`).
- Check run 38387137812: success (its last update 11:09:30 UTC); it merged the branch as `460f704a` at 11:09:24 UTC. Deployment of `460f704a`: success at 11:10:44 UTC.
- After snapshot `s252-after`: 11:11:54 UTC, 25 pages, 0 failed. `compare s252-before s252-after`: exit 0, **0 differences in all**, on each of the 25 pages. Expected: session 252 added a document, scripts and a test.

## The landing

- The before snapshot, the push, the check run, the merge, the deployment and the after snapshot with its comparison are in no committed file: this is the last session, and a commit to record them would be one more landing. They are in the closing message and in `runs/session253/landing.out`. Expected: 0 differences on the 25 pages (a method note's section, a script, two result files and a test; the three live pages read none of them).
