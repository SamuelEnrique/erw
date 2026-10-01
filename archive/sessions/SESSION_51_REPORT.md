# Session 51 report: cost of power v2, the seller's side

Energy Research Warehouse (ERW), session 51, run 2026-10-01 from 10:27 to about 11:25 UTC. **Wall time about 58 minutes.**

**API spend: USD 0.00, confirmed.** No model call, no data pull. The solar and wind shapes come from EIA-930 workbooks already on disk; Lazard's study was the PDF read in session 50. No force push. Nothing in Supabase; nothing released on Redivis.

## What was built

- **A second tab on `/cost-of-power`: "What a generator earns"** (`/cost-of-power/seller`). It is linked from the buyer's tab, which is otherwise unchanged; the only addition there is the tab bar.
  - **What it shows:** monthly merchant revenue for a solar, wind, battery or gas peaker asset of the reader's size at an ISO's main hub; the median and 10th-percentile month; the worst three months; the ERCOT stress days against a normal week; and debt service coverage, monthly and trailing twelve months, with months under 1.0x and 1.25x flagged.
  - **Labelling:** merchant only, with a note on why real assets are rarely fully merchant, and a "How a lender should read this" section.
- **The table:** `merchant_revenue_monthly` (tier derived, public), built by `warehouse/derived/merchant_revenue.py`.
  - **Rows:** 5,984. ERCOT 3,670 over 100 months; CAISO, ISO-NE, MISO and SPP 481 each over 13 months; NYISO 390, because EIA-930 reports no NYIS solar.
  - **Checks:** validator PASS, archived, in coverage (sector power;gas), uploaded to the public Redivis draft. Not in Supabase.
- **The page's snapshot:** `site/data/merchant_snapshot.json` (1.47 MB), read on the server only, as `/network` reads its own.
  - It holds the table's monthly figures, the hourly prices and Henry Hub (so the peaker can be recomputed at the reader's heat rate), and the ERCOT stress days.
- **The page's arithmetic:** `site/lib/merchant.ts`, shared by the page and `scripts/check-values.mjs` (keys `mr|<inputs>|<stat>`).
- **Docs:**
  - `docs/methods/cost_of_power.md`: a "The seller's side" section.
  - `docs/reviews/nabihan-questions.md`: the ten questions.
  - `docs/datastandard.md` and the validator: Decision 34 adds the units `USD/MW` and `MWh/MW`.

## Shapes, and their windows per ISO

**Solar and wind:**
- **Output:** EIA-930's hourly generation by fuel, the BA workbooks' `Adjusted SUN Gen` and `Adjusted WND Gen`.
  - The saved per-BA extracts hold demand, net generation and CO2 only, no fuel. So the builder reads the workbooks they were extracted from, already under `warehouse/raw/eia930_emissions/`.
- **Capacity:** the fuel's installed nameplate in that BA that month, from EIA-860M (operating plus retired generators, by month).
- **What it is:** a fleet average, not a site.

**Batteries:** the perfect-foresight daily optimum (exact-state DP) at 2 and 4 hours.
- Round trip 86 percent (Lazard's low end), from empty each day, at most one cycle a day.
- An upper bound, labelled.

**Peaker:** runs when the hub price exceeds Henry Hub x heat rate + variable O&M.

| ISO (hub) | Window held | Solar | Wind | Shape flags |
|---|---|---|---|---|
| ERCOT (HB_HUBAVG) | 2018-07 to 2026-09 (99 months held) | yes | yes | 1,428 solar hours above installed nameplate (EIA-860M lists new plants late) |
| CAISO (SP15) | 2025-09 to 2026-09 (13) | yes | yes | 4,197 negative solar hours (station use, as EIA reports) |
| ISO-NE (.H.INTERNAL_HUB) | 2025-09 to 2026-09 (13) | yes | yes | 6 wind hours above nameplate |
| MISO (INDIANA.HUB) | 2025-09 to 2026-09 (13) | yes | yes | none |
| NYISO (N.Y.C.) | 2025-09 to 2026-09 (13) | **no**: EIA-930 reports no NYIS solar | yes | none |
| SPP (SPPNORTH_HUB) | 2025-09 to 2026-09 (13) | yes | yes | 121 solar hours above nameplate |

- **The stress days** are ERCOT's only: the other hubs' prices start in September 2025, after the events.
- **PJM is excluded** (internal prices).

## The default tab's numbers, with their checks

**Defaults:** each is the midpoint of Lazard LCOE+ (June 2025). Debt service = capital x 60 percent debt at 8 percent, levelized over the life (Lazard's own financing). This reproduces Lazard's wind illustration: $342M of debt, $30.4M a year.

**All at ERCOT HB_HUBAVG, over 99 held months, 2018-07 to 2026-09:**

| | Solar 100 MW | Battery 100 MW / 400 MWh | Peaker 100 MW |
|---|---|---|---|
| Annual debt service (default) | $7,078,769 | $6,783,357 | $6,928,540 |
| Fixed O&M | $12.5/kW-yr | $22/kW-yr | $13.5/kW-yr |
| Median month | $550,485 (2018-09) | $492,260 (2025-07) | $382,267 (2024-06) |
| 10th-percentile month | $240,213 (2020-12) | $263,722 (2023-02) | $155,550 (2021-12) |
| Worst three months | 2024-02 $139,299; 2026-02 $148,707; 2023-02 $175,324 | 2019-12 $102,127; 2020-06 $137,675; 2020-01 $162,309 | 2020-06 $27,484; 2019-12 $29,366; 2018-12 $64,802 |
| Months under 1.0x / 1.25x | 62 / 71 | 73 / 79 | 74 / 79 |
| Trailing twelve months: latest, lowest | 0.66x (2026-09), 0.65x | 0.54x, 0.38x | 0.50x, 0.38x |
| Twelve-month windows under 1.0x (of 88) | 33 | 36 | 38 |
| Uri: per day; the window | $687,901/day; $12.38M | $361,449/day; $6.51M | $5.52M/day; $99.4M |
| Elliott: per day | $12,343 | $79,731 | $107,086 |
| 2023 heat: per day | $257,502 | $304,785 | $392,732 |
| A normal week (Uri's baseline) | $61,313 | $88,465 | $77,484 |

**What the numbers show:**
- Under Lazard's midpoint costs and merchant revenue alone, coverage at ERCOT's hub is below 1.0x in most months and in a third or more of the trailing-twelve-month windows, for all three assets.
- Uri carried most of the peaker's best years: one window earned $99.4M for 100 MW.

**The checks:**
- **check-values** covers every number on the tab.
  - It recomputes each `mr|` key from the snapshot with `lib/merchant.ts`: 1,334 keys on five tab pages (the default, battery, peaker, and MISO wind).
  - Locally 3,800 of 3,800 values; live 3,715 of 3,715.
- **The hand-computed checks** (`tests/test_session51.py`) recompute from the source files, not through the builder:

| Check | Inputs | Result |
|---|---|---|
| ERCOT solar, 2025-07 | 744 hours; 26,000.2 MW of solar installed in ERCO | 277.9898 MWh/MW; $7,941.5254/MW; capture $28.5677/MWh. Equal to the table |
| ERCOT peaker, 2025-07 | 142 run hours | sales $9,901.2650, fuel and variable O&M $5,401.1143, margin $4,500.1507/MW. Equal to the table |
| Battery 2 h, 2023-08-10 | the day's 12 evening hours, every action sequence (3^12) | the DP equals brute force, $5,195.4751 |

- **More on the battery day:**
  - **Rounding:** the two differ by $0.0000016. The DP keys states to 1e-9 MWh, and at that day's prices the rounding shows in the sixth decimal; the test checks to $0.0001.
  - **The full day's plan:** charge 04:00, 08:00, 09:00; discharge 15:00, 16:00. Replayed by hand, it nets $5,676.3210/MW within one cycle.
- **The snapshot equals the table** for every asset, month and metric (more than 3,000 values).

## The questions file

`docs/reviews/nabihan-questions.md` holds ten questions for a private credit investor. Each is tied to one part of the tab and ends with the design decision it settles:
1. which downside statistic leads;
2. which coverage tests and thresholds;
3. what else comes out of cash flow before coverage;
4. the debt service default (levelized vs sculpted, the tenor);
5. which contract to layer in first;
6. a basis haircut;
7. fleet vs site shapes;
8. a haircut on the battery's perfect foresight;
9. availability on stress days;
10. a minimum history before coverage shows.

## Verify and ship

| Check | Result |
|---|---|
| Builder and validator | PASS, 5,984 rows |
| Coverage | `merchant_revenue_monthly` in, sector power;gas |
| Archive | 5,984 rows (private bucket) |
| Redivis | public draft, `count(*)` equal; nothing released |
| check-routes | covers `/cost-of-power/seller`: local 61 of 61 |
| check-values | local 3,800 of 3,800 |
| Tests | `tests/test_session51.py`, 8 tests, OK (the hand-computed three, the snapshot against the table, never in Supabase, the units, the Lazard trace, the questions file) |
| Deploy | pushed 9fabb32..ed2055a; live: check-values 3,715 of 3,715 (the seller's keys included), check-routes 61 of 61 |

## Decisions made without a human

1. **A separate route, `/cost-of-power/seller`, for the second tab,** with a tab bar on both. The buyer's page stays static and unchanged; the seller's tab takes its inputs as query parameters and is computed on the server.
2. **The shapes come from the raw BA workbooks.** The saved extracts hold no fuel columns, and the workbooks are already on disk, so this is no pull.
3. **Output above installed nameplate is kept as EIA reports it, not capped,** and counted on the page and in the log. Capping would alter the data.
4. **Batteries at 2 and 4 hours only,** the durations Lazard prices. The page uses the nearer of the two from MWh / MW and says so.
5. **Defaults are Lazard's midpoints.** The battery's round trip is Lazard's low end (86 percent), the downside a lender would take.
6. **Cash flow available for debt service is revenue less fixed O&M** (Lazard's), nothing else. The page names what is left out.
7. **A month counts at 90 percent of its hours held,** the rule session 49 set for the buyer's ranked month. Months below it are shown grey and not counted.
8. **Peaker gas is Henry Hub,** the last trading day's on non-trading days, with no basis. The page warns that it understates delivered gas in New England and New York.
9. **Stress days are ERCOT's only.** The other hubs have no prices for those dates.

## Open questions

1. **Nabihan's answers** decide the next version's downside statistic, its coverage tests, its CFADS and its contract layer (see the questions file).
2. **The fleet shape's early-year inflation in ERCOT,** where EIA-860M lists plants late. Should the shape be normalized by a later vintage of 860M, or by the month's highest output?
3. **Delivered gas** (Algonquin, Transco Zone 6) for the eastern peakers would need a data pull. Not done.
4. **NYISO solar** is not in EIA-930. A state source would be needed.
5. **The snapshot is 1.47 MB, read on the server.** If more ISOs gain years of history it should be split per ISO.
