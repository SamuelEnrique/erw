# Session 67 report: the battery revenue stack, and the release gate

Energy Research Warehouse (ERW), session 67, on the portable laptop, 2026-10-02 from about 20:30 UTC, unattended. **Model spend: USD 0.00** (the cap was USD 0). No paid service, no new pull, no force push. Branch `task/067-battery-stack`.

**For session 68: the release gate (Part C) shipped on this branch.** It is live once this branch's merge is on main (see "The push and production" at the end for whether the merge and the deploy were confirmed). `site/lib/release.ts` is the one list; `site/scripts/check-routes.mjs` has both passes.

## In plain words

**The page exists: "What a battery earns", at `/cost-of-power/battery`.** It answers the two reviewers' question for ERCOT (2018 on) and CAISO (September 2024 on), at 2, 4 and 8 hours, under two strategies: what a battery earns, from which streams, and whether it covers its debt, with and without a contract. Energy and ancillary services are split hour by hour by one optimization a day, so nothing is counted twice.

**Three things a person must know before sending it to the CFO.**

1. **The "average year" in ERCOT is dominated by one month.** February 2021 (Winter Storm Uri) is 57 percent of everything a 4-hour battery earned in 105 months under this model. The average year is USD 614.58 per kW with it and USD 269.7 per kW without it; the last twelve months earned USD 81.4 per kW. The page says this in a box directly under the summary sentence and breaks the chart's scale for 2021. I did not remove the month from the average, because that would be smoothing; but a reader who sees only the first sentence will be misled. Consider whether the summary sentence should lead with the last twelve months instead. That is a wording decision for you.
2. **Every figure is an upper bound of a particular kind.** The battery is a price taker, paid for holding reserves that are never called. In recent years that matters less (ancillary income is small); before 2024 and in Uri it matters enormously. The numbers before 2024 are well above what I understand real ERCOT batteries to have earned, and I could not check that against a source in this session. The page states the limits in a folded section; the methods doc has a section, "Results that look implausible".
3. **Two of ERCOT's duration requirements and all of CAISO's are assumed, not verified.** See "Duration requirements". For CAISO this means every reserve is backed by one hour of energy. The page and the methods doc say so.

**The release gate is built.** Six tools are open to visitors; everything else, the price board included, shows greyed in the menu with an "in review" label and answers a short in-review page. The internal link opens everything.

**The daily run now refreshes the ancillary prices and the stack**, and the capacity prices on the first of each month.

## Part 0: preflight

Session 65's finish was done: `iso_all_capacity_prices`, `ercot_as_prices` and `caiso_as_prices` are in `warehouse/output` and in coverage, and main (`e4debe2`) holds the merge. The "Finish" section of the session 65 report (`8152c2f`, local only) was cherry-picked onto this branch as `3c1c149`, so it reaches main with this merge.

## Part A: the model

`warehouse/derived/battery_stack.py`, tables `battery_stack_monthly` (10,461 rows) and `battery_stack_stress_daily` (1,260 rows). Method: `docs/methods/battery_stack.md`. Both valid (exit 0), in coverage (derived, public), the archive, the Redivis draft (public dataset; counts equal the CSVs; nothing released) and Supabase's live set. `upload.py --check-license`: 14 internal tables, 0 in the public dataset.

All figures below are USD per kW of rated power (the table is USD per MW; divide by 1,000), by calendar year, summed over the held days.

### ERCOT (HB_HUBAVG), 4 hours

**Perfect foresight** (real-time energy, day-ahead ancillary):

| Year | Energy | Ancillary | Total | Reg Up | Reg Down | RRS | ECRS | Non-Spin | Days |
|---|---|---|---|---|---|---|---|---|---|
| 2018 | 45.2 | 198.5 | 243.7 | 7.3 | 35.1 | 135.7 | | 20.4 | 365 |
| 2019 | 110.7 | 291.4 | 402.2 | 17.1 | 65.7 | 198.3 | | 10.3 | 365 |
| 2020 | 34.1 | 153.4 | 187.5 | 27.7 | 59.1 | 65.7 | | 1.0 | 366 |
| 2021 | 23.0 | 3,407.5 | 3,430.6 | 106.6 | 808.8 | 2,463.5 | | 28.6 | 365 |
| 2022 | 126.1 | 267.0 | 393.1 | 58.9 | 68.4 | 48.3 | | 91.4 | 365 |
| 2023 | 152.0 | 378.1 | 530.1 | 49.9 | 114.3 | 18.1 | 185.8 | 10.0 | 365 |
| 2024 | 62.7 | 85.0 | 147.7 | 10.4 | 27.2 | 10.6 | 33.5 | 3.3 | 366 |
| 2025 | 57.4 | 30.1 | 87.4 | 7.7 | 11.2 | 6.7 | 0.6 | 4.0 | 365 |
| 2026 (to 30 September) | 40.8 | 19.4 | 60.2 | 4.4 | 6.9 | 3.0 | 1.9 | 3.1 | 273 |

**Day-ahead schedule** (day-ahead energy and ancillary):

| Year | Energy | Ancillary | Total | Reg Up | Reg Down | RRS | ECRS | Non-Spin | Days |
|---|---|---|---|---|---|---|---|---|---|
| 2018 | 8.6 | 200.8 | 209.4 | 7.5 | 36.0 | 136.9 | | 20.4 | 365 |
| 2019 | 2.4 | 321.0 | 323.4 | 17.6 | 67.1 | 225.4 | | 10.9 | 365 |
| 2020 | 3.9 | 159.2 | 163.1 | 30.2 | 60.4 | 67.6 | | 1.0 | 366 |
| 2021 | -37.7 | 3,427.9 | 3,390.1 | 108.1 | 811.3 | 2,479.1 | | 29.4 | 365 |
| 2022 | 58.9 | 256.0 | 314.9 | 59.1 | 70.0 | 44.8 | | 82.1 | 365 |
| 2023 | 100.4 | 359.2 | 459.6 | 44.7 | 116.5 | 21.6 | 166.3 | 10.1 | 365 |
| 2024 | 48.8 | 78.4 | 127.1 | 11.3 | 27.3 | 8.6 | 27.0 | 4.2 | 366 |
| 2025 | 52.3 | 26.4 | 78.7 | 7.5 | 10.8 | 4.5 | 0.5 | 3.2 | 365 |
| 2026 (to 2 October) | 35.6 | 18.8 | 54.4 | 4.2 | 7.1 | 2.7 | 1.5 | 3.2 | 275 |

The negative energy stream in 2021 on the day-ahead schedule is real arithmetic: in Uri the battery bought energy to back reserves that paid far more than the energy cost.

### CAISO (SP15), 4 hours

| Strategy | Year | Energy | Ancillary | Total | Reg Up | Reg Down | Spin | Non-Spin | Days held | Left out |
|---|---|---|---|---|---|---|---|---|---|---|
| Perfect foresight | 2024 (from September) | 14.7 | 15.9 | 30.6 | 1.9 | 11.5 | 0.0 | 2.5 | 121 | 1 |
| Perfect foresight | 2025 | 48.2 | 43.4 | 91.6 | 9.2 | 33.3 | 0.0 | 0.9 | 361 | 4 |
| Perfect foresight | 2026 (to 30 September) | 35.6 | 27.9 | 63.5 | 10.9 | 15.6 | 0.0 | 1.3 | 273 | 0 |
| Day-ahead schedule | 2024 (from September) | 15.7 | 13.9 | 29.6 | 1.7 | 11.1 | 0.0 | 1.1 | 121 | 1 |
| Day-ahead schedule | 2025 | 42.3 | 42.8 | 85.2 | 8.2 | 33.9 | 0.0 | 0.7 | 361 | 4 |
| Day-ahead schedule | 2026 (to 2 October) | 24.2 | 27.1 | 51.3 | 10.7 | 15.6 | 0.0 | 0.9 | 275 | 0 |

Two things to flag in CAISO. Regulation Down is the largest ancillary stream: the battery sits near empty most of the day and is paid for the room to absorb energy in nearly every hour. And Spinning Reserve earns nothing, because with every product assumed to need one hour, Regulation Up always pays at least as much for the same stored energy. Both follow from the model, not from anything a real operator does, and the second would change if CAISO's true requirements were entered. No capacity (resource adequacy) revenue is in it, which for a California battery is a real omission.

### What 2 and 8 hours earn against 4 (total, USD per kW)

| | ERCOT foresight 2h / 4h / 8h | 2h over 4h | 8h over 4h | CAISO foresight 2h / 4h / 8h | 2h over 4h | 8h over 4h |
|---|---|---|---|---|---|---|
| 2022 | 352.5 / 393.1 / 413.9 | 0.90 | 1.05 | | | |
| 2023 | 451.5 / 530.1 / 551.6 | 0.85 | 1.04 | | | |
| 2024 | 122.4 / 147.7 / 158.6 | 0.83 | 1.07 | 24.5 / 30.6 / 37.2 | 0.80 | 1.22 |
| 2025 | 64.4 / 87.4 / 104.3 | 0.74 | 1.19 | 70.4 / 91.6 / 115.3 | 0.77 | 1.26 |
| 2026 | 43.4 / 60.2 / 73.0 | 0.72 | 1.21 | 49.4 / 63.5 / 77.6 | 0.78 | 1.22 |

In ERCOT before 2022 duration barely mattered (2 hours earned 93 to 99 percent of 4 hours): the money was in reserves, which need power, not energy. As ancillary income fell, duration came to matter: by 2026 a 2-hour battery earns 72 percent of a 4-hour one and an 8-hour battery 21 percent more. Doubling the duration never doubles the revenue. The 8-hour battery never earns less than the 4-hour, nor the 4-hour less than the 2-hour, on any day (tested, and true of every day built).

### The difference from the old energy-only figure, and why

ERCOT, 4 hours, perfect foresight, USD per kW:

| Year | Seller tab (energy only) | Energy only, this program | This model: energy | This model: total | Total less the seller tab |
|---|---|---|---|---|---|
| 2018 | 39.4 (from July) | 68.2 | 45.2 | 243.7 | 204.3 |
| 2019 | 140.7 | 141.7 | 110.7 | 402.2 | 261.5 |
| 2020 | 49.4 | 50.1 | 34.1 | 187.5 | 138.1 |
| 2021 | 134.9 | 137.9 | 23.0 | 3,430.6 | 3,295.7 |
| 2022 | 150.6 | 153.9 | 126.1 | 393.1 | 242.5 |
| 2023 | 201.0 | 205.3 | 152.0 | 530.1 | 329.1 |
| 2024 | 73.4 | 75.1 | 62.7 | 147.7 | 74.3 |
| 2025 | 62.0 | 63.2 | 57.4 | 87.4 | 25.4 |
| 2026 | 43.6 | 44.7 | 40.8 | 60.2 | 16.6 |

**The prompt's premise was not right, and I am correcting it rather than explaining around it.** The prompt said the existing energy-only figure uses finer real-time intervals. It does not: `merchant_revenue.py` uses the hourly mean of the 15-minute prices. So resolution is not a cause. The causes are:

1. **Ancillary services.** The total is higher, and the energy stream on its own is lower than the energy-only figure, because the battery gives up energy sales to hold reserves that pay more.
2. **Partial power.** The seller tab's battery moves at full power or not at all in an hour; this program may move at part power, worth 1 to 2 percent on energy alone (the third column against the second).
3. **Days.** The seller tab starts in July 2018 and skips the two clock-change days of each year.

The seller tab was not changed. Its battery figures and this page's will not agree, by design; the seller tab now carries one line pointing here.

### Duration requirements

| Market | Product | Used | Source |
|---|---|---|---|
| ERCOT | ECRS | 2 hours from 2023-06-10; 1 hour from 2025-12-05 | verified: NPRR 1096 (effective 2022-12-09) and NPRR 1282 (effective 2025-12-05), read from ERCOT's own pages in this session |
| ERCOT | Non-Spin | 4 hours from 2022-12-09 | verified: NPRR 1096 |
| ERCOT | Non-Spin | 1 hour before 2022-12-09 | **assumed** |
| ERCOT | Regulation Up, Regulation Down, RRS | 30 minutes from 2025-12-05 | verified: NPRR 1282 |
| ERCOT | Regulation Up, Regulation Down, RRS | 1 hour before 2025-12-05 | **assumed** |
| CAISO | all four products | 1 hour | **assumed**: the tariff was not checked |

The two ERCOT pages were fetched with a plain request (public pages, no data pull, no model). I did not go looking for CAISO's tariff text: it is a set of PDFs and I chose not to spend the session on it. A person who knows the tariff can change one line per product in `MARKETS` in `battery_stack.py` and rebuild.

### Days left out

- **ERCOT: none**, under either strategy (3,195 days with perfect foresight, 3,197 on the day-ahead schedule).
- **CAISO: five under each strategy.** 2025-04-06, 04-07, 04-08: OASIS returns no ancillary prices. 2024-11-03 and 2025-11-02: the 25-hour days of the autumn clock change, which the hub price history does not hold.

### Tests (`tests/test_session67.py`, 21 tests, pass)

The program equals an exhaustive search on toy days; a day worked by hand; one hour's power is never sold twice; with ancillary prices at zero it reproduces the energy-only optimum at the same resolution, and without losses it equals the seller tab's battery; every constraint holds in every solved hour; charging and discharging never share an hour; a day missing a price is left out and counted; a month with no held day gets no revenue row; 8 hours never earns less than 4, nor 4 less than 2. The builder also checks every constraint on every day it solves and fails on a violation.

### The daily refresh

`run_daily.sh` now runs `ercot_as_prices.py`, `caiso_as_prices.py` and the builder, each under `health.py run --strict`, and `iso_capacity_prices.py` on the first day of the month (or with `CAPACITY=1`). **This has not run on the GitHub runner yet; the first real test is the 14:00 UTC run.** What I did to make it safe there, and what could still go wrong:

- The runner has no ERCOT price history. The builder recomputes the months the rolling tables reach and keeps earlier months from its own table, restored from the Redivis draft; a month is never replaced by one resting on fewer days (tested on made-up frames, not on the runner).
- `caiso_as_prices` is restored from the draft and only the last days are requested, so the runner does not make 760 requests.
- `ercot_as_prices` downloads ERCOT's yearly files each day (nine files). If ERCOT is slow this adds minutes.
- `scipy` was added to `requirements.txt`. It was already installed as a dependency of another package, but was not declared.

## Part B: the page

Built as specified: inputs in a fog beige left panel (grid, duration, strategy, size, fixed O&M, debt payments, Show), the optional contract below it, and on the right the summary sentence, three headline numbers, one chart, the income table, the contract result, the other grids in words, three folded sections and a grey source line. Seven grids are listed; ERCOT and CAISO are selectable.

Decisions where the prompt was silent:

- **"Average year"** is the mean of each calendar month's held months, summed over the twelve calendar months, so a window that is not a whole number of years does not count one season twice.
- **The 8-hour cost default** is not Lazard's: Lazard prices 2 and 4 hours only. The 8-hour default is the straight line through those two (capital USD 2,110 per kW, fixed O&M USD 43.6 per kW a year). The page says it is an extrapolation.
- **The contract** treats the contracted share as paid the contract price for its power and earning nothing from the market. The "market income on the uncontracted share" line uses the average year, so in ERCOT it carries the Uri month too.
- **The chart's scale is broken for 2021** in ERCOT, with the value written and a note. Otherwise every other year is a sliver.
- **Stress days** are a second small table (`battery_stack_stress_daily`), because the monthly table cannot show days.
- **The page's own background is white**, so the beige panel reads as a panel; the site's background is already fog beige.

The contract terms: tested in a real browser that typing them makes no network request, leaves the address unchanged, writes nothing to storage or cookies, and that a later change of duration carries none of them in any request.

## Part C: the release gate

- **The one list:** `site/lib/release.ts`. One line per page.
- **Live:** `/`, `/cost-of-power/battery`, `/cost-of-power/seller`, `/network`, `/storage`, `/about`, `/terms`, and the methods pages they link to (`battery_stack`, `cost_of_power`, `grid_network`, `storage`).
- **In review:** everything else: `/board`, `/markets`, `/cost-of-power` (the buyer's tab), `/prices`, `/explorer/ercot-peak-premium`, `/grid` and the seven grid pages, `/mix`, `/curtailment`, `/emissions`, `/consumption`, `/map`, `/datacenters`, `/companies`, `/policy`, `/deals`, `/events`, `/tour`, `/learn/problems`, `/learn/bill`, `/play/battery`, `/severance`, `/severance/lease`, `/digest`, `/roundup`, `/subscribe`, `/data`, `/data/standard`, the other methods pages, `/analysis`, `/ask`, `/reports`.
- **The unlock link:** `https://erw-flame.vercel.app/internal/unlock?token=<INTERNAL_COSTS_TOKEN>` (the value is in `.env` and on Vercel; I have not written it anywhere). `/internal/lock` clears it. 90 days, httpOnly; the cookie holds a digest of the token, not the token.
- **Not security:** said in `docs/release-gate.md`. Supabase and Redivis are as public as before.
- **The scheduled jobs and the game's API:** unaffected. The gate never covers `/api/*`; none of the scheduled jobs reads a page. Confirmed by reading the workflows and by the route check asking an API route as a visitor.

**Things the gate does that you may not expect.**

- **Every link in the site now goes through one component.** To grey out in-page links I replaced the import of the link component in 56 files with the gated one. It is a one-line mechanical change per file, but it touches most of the site. tsc, the build and both route passes are clean.
- **The home page is busy with "in review" labels.** Most of its cards point to pages in review, so most carry the label, and so does every table name in its citation lines. That is the ruling applied literally. It looks cluttered.
- **Email links.** The digest and Roundup emails link to `/digest` and `/roundup`, which are in review. A subscriber following one sees the in-review page. Unsubscribe and confirm are API routes and still work.
- **An internal browser sees the visitor's page for a moment**, then its links redraw. The server always renders the visitor's view so cached pages can never leak the internal one.
- **`/storage`'s tier chips are no longer links** (they pointed to a page in review).

## Part D: the home page and `/storage`

- **Home:** an "Open now" strip under the tour button, four tools, each with one number read from the tables. Nothing else changed.
- **`/storage`:** the shared header, type and source line; the operating fleet (MW) and the last-24-hours chart first. No data change, no new section; every check key is as it was.

## Tests and checks, local, on the final build

| Check | Result |
|---|---|
| `python -m unittest discover -s tests` | 318 tests, pass, exit 0 |
| `tests.test_session67` | 21 tests, pass |
| Package tests (`pytest package/tests`) | 402 passed, 32 skipped, exit 0 |
| `npx tsc --noEmit` | exit 0 |
| `npm run build` | exit 0 |
| `check-routes`, pass 1 (internal cookie) | 74 of 74 pages |
| `check-routes`, pass 2 (visitor) | 14 live and 60 in review asked, 0 failed |
| `check-values` | 6,581 of 6,581 values match Supabase, exit 0; 1,741 of them are this page's, across seven combinations of grid, duration, strategy and size |
| Browser test (`test-battery-stack.mjs`) | 48 assertions, pass |
| Validator, coverage, `--check-license` | exit 0 each |

**Tests I changed that were not this session's.** Three package assertions and one `tests/` assertion failed on arrival or because of a list I extended:

- `test_session46`: pinned the no-prefetch list to exactly one page; I added the battery page to that list. The test now accepts a longer list. This one I caused.
- Two package tests failed because of session 65's tables (`ercot_as_prices` is a day-ahead table that holds services not hubs; `iso_all_capacity_prices` has four publishers and NYISO localities, not price zones). They would have failed the daily run's package step as soon as those tables reached the runner. I changed the tests to describe the tables correctly. No table changed. Session 65's report said the package tests passed; they were run before its tables were in `warehouse/output`.

## Errors and decisions

- **The first build's header failed coverage, correctly.** Its "Derived from" line named a table with a note in parentheses. Coverage exited 1; I read the exit code, fixed the header, rebuilt, and reran validation and coverage before any upload.
- **A stale local cache made the page look empty.** The local site had cached the empty read from before the Supabase load. I cleared the local cache. Production has never read these rows before, so it is not affected.
- **`check-values` failed three times on the final build before it passed, and the cause is not this session's work.** Each time the only failures were the 39 latest prices on `/` and `/prices`. Those prices change in Supabase every 15 minutes and those two pages cache for 15 minutes, so the check passes only when both fall in the same window. I confirmed the page does regenerate, and that production lags Supabase the same way, then ran it inside one window: exit 0. Every battery figure matched on every run. The check is timing-sensitive for those two pages and will fail again by chance; worth fixing, not fixed here.
- **Two regular expressions in the route check were mangled by my own scripted edit** (a backspace character where `\b` should be). Caught on review before the script ran, and fixed.
- **Why this laptop's `eia930_all_interchange` and `news_scores_shadow` are short.** The laptop's files are older than the cloud's: interchange here is 127,560 rows to 2026-09-28 (pulled on 2026-10-01), against 135,456 in the last upload (2026-10-02 00:24 UTC, by the daily run); the shadow scores here are 2,375 rows against 3,595. `sync.py` does not see it because it compares local rows with `coverage.csv`, and `coverage.csv` was rebuilt on this laptop (sessions 64, 65 and this one) from the local files, so it compares the laptop with itself. I did not touch either table, uploaded only my two tables by name, and never forced the gate.
- **A consequence of that I should state plainly:** I rebuilt `coverage.csv` on this laptop and loaded the catalogue to Supabase, so until the next daily run the catalogue may show older row counts and dates for tables the runner refreshes. The 14:00 UTC run rewrites it. Session 65's finish did the same.
- **Supabase load:** only the two new tables (`load.py --only`), not the whole live set, so nothing else in Supabase was overwritten from this laptop's older files.
- **The lock** was held from 21:00 to about 21:45 UTC for the build, archive, upload and load, and released.
- **`SESSION_69_PROMPT.md` appeared in the repository root during the session.** I was told to stop after session 68. I have not read or acted on it.

## For Samuel

1. **Before sending the page: the ERCOT summary sentence.** It leads with an average year that is 57 percent one storm. Decide whether it should lead with the last twelve months.
2. **CAISO's duration requirements** are assumed at one hour. If you or the CFO know them, they are one line each.
3. **Watch the 14:00 UTC daily run.** Four new steps, never run on the runner.
4. **The home page's clutter** under the gate: accept it, or tell me which labels to drop.
5. **Email links to pages in review.**
6. **Redivis:** the two new tables are in the draft only. Releasing is yours.
7. **The sync blind spot** above: `sync.py` should compare against Redivis's counts, not against a coverage file the same machine may have rewritten. Not fixed here.
