# Session 138 report: What a datacenter pays

Run on 7 October 2026 (UTC), unattended, as the first session of the chain 138 to 139. The page is at `/cost-of-power`
on production, locked for visitors (`review`). One deploy, with the snapshot of the live pages before and after: 0
differences.

## Six things to know before anything else

1. **"Not published anywhere yet" is not true of New York, so the page does not say it there.** The research for
   session 139 found that NYISO publishes its load interconnection requests by zone (its queue workbook's sheets "Load
   Projects" and "Load Project Tracking": 74 requests, 14,473.1 MW), and Bonneville publishes a line and load queue.
   For NYISO the row "Large load in line, by region" reads "not held yet"; for the other four grids it reads "not
   published anywhere yet", and its hover says a search on 7 October found none, not that none exists. "How long a new
   large load waits" reads "not published anywhere yet" for every grid: no dataset of realized waits was found.
2. **Texas delivery charges: Oncor's are shown, the other three utilities' are held and blank. This is my reading of
   their terms and needs your ruling.** All four tariffs were read (73 figures, 73 kept with their line). The table,
   `texas_delivery_charges`, is internal. On the page: Oncor's nine charges for Transmission Service, each as the tariff
   prints it with its line on hover (its terms allow copying and display "for personal, noncommercial, and/or
   educational purposes"); CenterPoint "licensed source needed" (its terms forbid publishing its content without
   written consent); AEP Texas and Texas-New Mexico Power "held while terms are reviewed" (AEP authorizes "personal
   use only"; TNMP's site refused the request and its terms were not read). The repository is public, so what the
   page's file holds is published: that is why the three are not in it. Say "show them" or "hold Oncor too" and it is
   one line of `DELIVERY` in `warehouse/derived/datacenter_page.py`.
3. **The Commission's transmission cost filings were not obtained.** The docket for 2026 charges has no final order,
   and the document read for 2025 was a proposed order that names the charge matrix without holding it. No provider's
   transmission cost of service and no rate per kW is in the table. To get them: Docket 57491, Staff's final matrix of
   20 March 2025 and the signed order; Docket 59080 item 50, "Commission Staff's Final Transmission Charge Matrices".
   That is a new pull and I did not make it.
4. **ISO-NE's hourly demand is pulled, held internal and shown nowhere.** Its zonal workbooks answer a plain request
   (no cookie, no account), but its legal notice is the one session 136 quoted ("Any duplication of the Content or
   non-personal use may violate copyright, trademark, and other laws."). Two years were pulled (131,319 rows). The
   page's ISO-NE demand rows read "licensed source needed" and the site's files hold none of it.
5. **The first tab still reads "What power costs to buy" on the live battery page, and the menu still says "Cost of
   power".** Both are what a visitor sees on a live page, and the freeze runs through 7 October. On `/cost-of-power`
   and the seller tab the tab reads "What a datacenter pays". The two lines to change after the freeze are under "To
   finish".
6. **Every figure for a flexible load is the most it could have saved.** The hours it turns off, or moves energy out
   of, are chosen knowing the year's prices. The Method note says so; the page's face, by your rule, does not.

## Verdict: not ready to open. What is left, exactly

1. **Your ruling on the Texas tariffs' terms** (item 2), and on ISO-NE's demand (item 4, with session 136's row).
2. **ERCOT's regions are its six trading hubs.** A load in ERCOT settles at its load zone's price, and no load zone
   price is held. For the page's deepest grid that is the nearest thing held, not the right thing. A pull of ERCOT's
   load zone prices (the same report as the hubs, NP4-180-ER and NP6-905-CD) needs your approval.
3. **The zones of NYISO and ISO-NE, CAISO's ZP26 and SPP South have six weeks of prices**, so each reads "not held
   yet" for the last twelve months. A history pull for them needs your approval. NYISO's and ISO-NE's main hubs have
   twelve months day-ahead and not real time (their real-time files miss hours in several months): there the page
   shows day-ahead when the address names no market.
4. **The Commission's transmission cost matrix** (item 3).
5. **The two labels after the freeze** (item 5).
6. **A flexible load judged on a forecast, not on hindsight.** Not built. Until it is, the flexible rows are upper
   bounds and the page should not open without a visible word to that effect, which your rule keeps off the face. Your
   call: a short hover on the row, or a forecast rule.
7. **The reader's own hours against clean generation** ("not held yet" on the page), and **NYISO's load queue**
   (published, not read).
8. **The first Saturday run on the runner (10 October) is the first there**: the four load connectors and the page's
   builder. The builder merges into the kept files and never thins them; that rule is tested here and not yet seen on
   the runner.

## What was asked for, and what was built

| Asked | Built |
|---|---|
| Final address `/cost-of-power`, the existing tab; label "What a datacenter pays" | The page at that address, title and tab "What a datacenter pays", no version in any address. The label on the live battery page is unchanged (item 5) |
| Everything the tab shows today stays as a view | The view "Grid by grid" (`?view=grids`): the ranking by ISO, ERCOT since 2018, the hours of the day, cost against carbon, the calculator, every checked number (83 values match Supabase). Its paragraphs of method moved to the Method note; three became hovers on column heads |
| The mirror of the battery page: inputs left, answer right | `ToolPage`, `InputPanel`, the summary sentence written from the numbers, three headline numbers, one chart, one table for each question, folded detail, the source line: the battery page's components |
| Grid, and region within it (every hub and zone held) | ERCOT 6, CAISO 3, NYISO 11, ISO-NE 9, SPP 2: 31 regions. MISO shown and blank "paused while terms are reviewed"; PJM "licensed source needed" |
| Size; flat; flexible by hours a year or share of hours; shifting a share of each day's energy | All four, in the address. Off in the n dearest hours of each year, or the dearest share; or 24 x share hours of each day's energy moved from its dearest to its cheapest hours |
| Real time, day-ahead, or a contract at a typed price, in the browser, never sent | Two markets in the address. The contract panel is the battery page's: state of one component, no form, no field name; a real browser shows no request, no change of address, nothing in storage |
| Two stated defaults with their source on hover | 1.3 kW per GPU (NVIDIA DGX H100: 8 GPUs, 10.2 kW) and an overhead ratio of 1.56 (Uptime Institute 2024 survey); both checked against their sources today |
| (1) Cost: last twelve months per MWh and in dollars, by year, the bad month, per GPU-hour, what flexibility saves | All, from the site's own files of hourly prices (`site/data/datacenter`, 8.3 MB, 24 files by grid and year, built by `warehouse/derived/datacenter_page.py` from the public price tables; no request). By year since 2015 for ERCOT, since 2024 for the others |
| Texas delivery and transmission charges, read by the model, each with its sentence and address, its own row | Read: 4 tariffs, 73 figures, each with its line, page and address; 0 dropped. Shown: Oncor's (item 2). One figure computed: the transmission factor alone for a flat load, in its own row, never added to the market cost. Other grids: "not held yet" |
| (2) Hourly demand by region where published openly, each a connector in the daily or weekly run | Four connectors in the Saturday refresh (`warehouse/refresh_supply.sh`): ERCOT by weather zone from 2015, NYISO's eleven zones from 2019, CAISO's five areas from September 2021, ISO-NE's eight zones from 2025 (internal). Each passes the validator; in coverage, the archive and the Redivis drafts; held out of the live set |
| Demand growth, the peak against installed capacity by fuel, tight hours and when, the load's hours off | Demand growth and the peak with capacity by fuel from the demand and mix tools' own files, linked. Tight hours (demand at or above 95 percent of the year's highest hour) from the new tables, with their months and hours, and the count of them in which the reader's load is off. Demand by zone for ERCOT, NYISO and CAISO |
| (3) How clean, from the tables behind `/mix?view=clean`, with a link | The annual carbon-free share, what a flat load meets hour by hour, an annual-matched purchase hour by hour, carbon per MWh, linked. The reader's own hours: "not held yet" |
| (4) How soon | The queue's active megawatts, median years to operation and completion shares from the queue tool's file, linked; ERCOT's large load approved and observed; the two rows of item 1 |
| No methodology on the face; placeholders with a hover | A check and a test read the face for it. Every missing figure is a short placeholder with its reason on hover. Method: `docs/methods/datacenter_cost.md` |
| Nothing static | The chart answers the mouse with the year, both figures, the saving and the hours off (checked in a real browser) |
| Tests on saved real samples | 37 assertions in node on ERCOT's hub average, every hour of 2021 and 2025, both markets (`tests/fixtures/session138`): a flat load pays the mean of the hourly prices (year and each month); none of 14 flexible loads pays more than a flat one, in either year, in any month; the contract arithmetic equals the battery page's `contractResult` |

## Every pull against its ceiling

**Hourly demand by region: USD 0, ceiling 4,000,000 rows. Read: 2,083,495 rows, 52 percent.** Every row that crossed
the wire is counted, probes included.

| Operator | What was read | Rows read | Rows in the table |
|---|---|---|---|
| ERCOT | 12 yearly files, 2015 to 2026, nine series a line | 920,367 | 920,358 |
| NYISO | 94 monthly files from 2019, the newest two asked twice, one probe | 758,395 | 748,660 |
| CAISO | 62 windows of 30 days, six areas, the newest two asked twice, three probes | 273,414 | 265,824 |
| ISO-NE | two yearly workbooks, 2025 and 2026 | 131,319 | 131,319 |
| **Total** | | **2,083,495** | 2,066,161 |

**Texas tariffs and the Commission's filings: USD 0, no row ceiling stated; I allowed 14 documents and 14 were
used.** Four tariffs, two Commission documents (one a mail log, a wasted document), one docket list, two rates pages,
one Commission policies page, four terms pages. The Commission's charge matrix was not among them (item 3).

**No MISO request. No PJM request.** No other pull.

- **Terms.** ERCOT, NYISO and CAISO: the sentences session 136 quoted cover these reports and are in each connector
  and in `sources.csv`. ISO-NE and the four utilities: quoted in items 2 and 4 and in the Method note.
- **The hour.** Set against EIA-930's hourly demand over the days both hold, ERCOT, CAISO and NYISO agree at the same
  hour (correlation above 0.9999) and not one hour either side. ISO-NE's does not settle it (0.935 at the same hour,
  0.951 one hour later, on 148 hours).

## Model spend: USD 0.3013 of the USD 3.00 cap

Five calls, one step (`texas_delivery_read`, claude-sonnet-5-5), all in the ledger under session 138. Before each call
its worst case was estimated and the call was sent only if the ledger's total plus that estimate stayed under USD 2.70.
**No stage was refused.**

| Call | USD | Worst case checked before sending |
|---|---|---|
| The Commission's proposed order (the measured first call) | 0.0146 | 0.1753 |
| Oncor | 0.0807 | 0.1989 |
| CenterPoint | 0.0724 | 0.2261 |
| AEP Texas | 0.0866 | 0.2240 |
| Texas-New Mexico Power | 0.0471 | 0.1978 |

## The deploy

One deploy. Freeze: on (`python scripts/freeze.py status` exited 1), relaxed by the chain prompt for locked pages.
Every page this session changes is locked: `/cost-of-power` and the new Method note are `review`.

- **Snapshot before** (`138_before`, 02:23 UTC) **and after** (`138_after`, 02:31 UTC, and again at 02:32): **0
  differences** on the 25 live addresses; 3,357 checked number keys compared; no number moved. Nothing was reverted.
- Checks passed (run 37561745419); merged as `18ac72e`.
- **Vercel built it**: "Deployment has completed" for `18ac72e` at 02:31:39 UTC.
- On production, in the internal view, the page's check passes 30 of 30, including its reads of the price files on
  the server. The live battery page still reads "What power costs to buy".
- No table a live page reads was written and nothing was loaded into Supabase.

## Checks

| Check | Result |
|---|---|
| `site/scripts/test-datacenter.mjs`, no request | 37 of 37 on the saved real samples |
| `tests/test_session138.py` | 24 tests: the builder, the merge rule, the tight hours, the delivery rule, the page's rules, the node tests |
| `tests/test_session138_demand.py`, `tests/test_session138_delivery.py` | 29 and 9 tests: each parser on a real sample, 23-hour and 25-hour days, the ceiling, the pause check, the sentence rule, the spend check |
| `site/scripts/check-datacenter.mjs`, HTML and a real browser | 30 of 30, locally and on production |
| `check-routes` | 8 live pages and 121 in review asked as a visitor, 0 failed |
| The whole suite, locally | 1,517 tests; 2 failed and were dealt with: session 78's test read the moved view's old file (changed to the new file), and session 102's ran while a source was being registered (passes now) |
| The whole suite and the site's checks on GitHub | passed (run 37561745419) |
| `check-values`, locally | 83 values of `/cost-of-power?view=grids` match Supabase. 8 values elsewhere do not (the home page's catalogue counts, one figure on `/deals`, the current month on one battery page): none is on a page this session changed, and I did not find their cause |

## The five numbers a lab's energy lead would find most useful

1. **USD 32.20 per MWh, USD 0.065 per GPU-hour.** A flat load at ERCOT's hub average, real time, October 2025 to
   September 2026: USD 28.21 million a year for 100 MW. The same year day-ahead in New York City: USD 73.10; at New
   England's hub: USD 74.19. California's SP15: USD 28.58; SPP North: USD 30.80.
2. **Turning off in 100 hours a year was worth 10 percent last year and two thirds in 2021.** At ERCOT's hub average a
   load off in the year's 100 dearest hours paid USD 28.97 against 32.20 over the last twelve months. In 2021 it paid
   USD 47.93 against 148.19; in 2023, USD 28.97 against 48.36. The value of flexibility is in the bad years. (The
   hours are chosen with hindsight: an upper bound.)
3. **The dear hours are no longer the tight hours.** In 2023 ERCOT's demand was within 5 percent of its peak in 157
   hours, their mean real-time price was USD 525 per MWh, and a load off in the year's 100 dearest hours was off in 46
   of them. In 2025: 140 tight hours, a mean price of USD 42.82 against the year's 32.49, and such a load was off in 3.
   A load that sheds on price no longer sheds at the peak.
4. **Delivery adds about a quarter on top, and it just rose.** Oncor's transmission cost recovery factor for a
   transmission-voltage customer is USD 6.260839 per kW of four-coincident-peak demand a month from 4 October 2026:
   USD 8.58 per MWh for a flat load, against USD 32.20 of market energy. The same sheet prints USD 3.491759 from 1
   August 2026. It is charged on demand in four summer intervals, which a load that is off in them does not pay.
5. **Far West Texas's average demand: 2,070 MW in 2015, 7,478 MW in 2025, plus 261 percent.** ERCOT as a whole peaked
   at 91,134 MW on 22 July 2026 by its own file, against 83,679 MW in 2025. (EIA-930's daily total for that day,
   1,809,147 MWh, a mean of 75,381 MW, is consistent with it; I could not check the hour itself.)

Two more, for the record: shifting 20 percent of each day's energy to its cheapest hours cut the last twelve months'
cost by 29 percent in ERCOT and 46 percent at SPP North (USD 30.80 to 16.60); and ERCOT's six hubs differ by little
over a year (USD 30.66 at West to 32.90 at Houston).

## Things that look implausible, flagged and not changed

- ERCOT's system maximum of 91,133.73 MW (item 5 above).
- Oncor's transmission factor rising from 3.49 to 6.26 between two sheets two months apart. It is what the tariff
  prints; I read the page myself (page 98, the last column, "Transmission Service ($/4CP kW)").
- **Oncor's energy efficiency factor as the model read it is the wrong column** (0.000446 USD per kWh is the
  non-profit column; the for-profit column prints zero). It is in the table and is not shown on the page. A figure
  from a many-column row is shown only where its column was checked against the header by reading the page.
- Texas-New Mexico Power's tariff file is dated 29 December 2025 and may be superseded (its site refused its rates
  page).
- CAISO's small areas hold zeros and a few negative hours (VEA 33 negative hours, MWD 986 zeros). ERCOT's file has one
  blank hour (7 November 2016). CAISO's has one missing hour (31 August 2024).
- ISO-NE's hour convention is not confirmed (above).

## Decisions I made without you

1. **Hours are counted in each grid's standard time**, so every day has 24 hours. In summer an hour on the page is one
   hour behind the wall clock.
2. **A month counts when at least 95 percent of its hours are held**; the last twelve months are the newest twelve
   such months in a row. The comparison page uses the same rule.
3. **A flexible load turns off whole**, and its hours are chosen by calendar year, so months, years and the last
   twelve months add up. The last twelve months therefore hold the off hours of two calendar years (112 for n = 100).
4. **A bad month for a buyer is the top tenth by cost per MWh** of the last 36 months, the mirror of the battery
   page's 10th-percentile month.
5. **"Tight" is demand at or above 95 percent of the year's highest hour**, from the operator's own load. It is a
   count of high-demand hours, not of scarcity.
6. **The contract is a share of the energy at a price per MWh** (the battery's is per kW-month); the arithmetic is the
   same function of a share, a price and the last twelve months.
7. **The page computes on the server from files in the repository**, not from Supabase: 8.3 MB of hourly prices by
   grid and year. Past years' files do not change; the weekly refresh rewrites the current year's.
8. **The builder is in the Saturday refresh and the daily run's commit step adds its files.** It merges, so the
   runner, which holds no ERCOT price history, adds hours and never thins a file.
9. **Three agents worked beside me** (the demand connectors, the tariff read, and session 139's research). Each was
   told its ceiling. The demand agent ran about ten minutes over its time; none passed a ceiling or a cap.
10. **The data standard has a new decision (42) and the changelog a new entry**; the changelog had not been kept since
    session 31 and I did not fill the gap.

## Not done

- A full `build_coverage.py` fails on this machine: `census_metro_population` names a source that is only on the
  branch `wip/129-demand-weather-finished`. The new tables' rows were built with `--only`. Not this session's table.
- No load zone prices, no forecast-based flexibility, no Commission matrix (the verdict).
- The page's `/learn`, home and menu texts that name the old tab are unchanged (the menu is on live pages).

## To finish, after the freeze (from 8 October UTC)

```bash
# 1. the tab reads alike on all three pages: in site/app/cost-of-power/Tabs.tsx replace
#      {tab("/cost-of-power", active === "battery" ? FROZEN_LABEL : LABEL, active === "buy")}
#    with
#      {tab("/cost-of-power", LABEL, active === "buy")}
#    and delete FROZEN_LABEL; then in tests/test_session138.py change test_the_tab_is_named_and_the_live_battery_page_keeps_its_words
# 2. the menu: in site/lib/pages.ts, the line of "/cost-of-power": label "What a datacenter pays" and its one-line description
# 3. snapshot, push, snapshot, compare (both changes are words a visitor sees on live pages: expected differences)
node site/scripts/snapshot-live.mjs take label_before
git push origin HEAD:refs/heads/task/138-label
node site/scripts/snapshot-live.mjs take label_after && node site/scripts/snapshot-live.mjs compare label_before label_after
```

## For Samuel

1. Rule on the tariffs' terms: show Oncor's (as now), show all four, or hold all four.
2. Rule on ISO-NE's demand with session 136's ISO-NE row.
3. Approve or decline three pulls: ERCOT's load zone prices; a price history for the zones; the Commission's charge
   matrices (Dockets 57491 and 59080).
4. Say how a flexible load's upper bound should be said on a page whose face carries no method.
5. Open `/cost-of-power` in the internal view and try: ERCOT, 500 MW, off in 100 hours, day-ahead; then New York City.
