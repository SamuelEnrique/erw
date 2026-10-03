# Session 68 report: the network, finished as a tool

Energy Research Warehouse (ERW), session 68, on the portable laptop, 2026-10-02 from about 22:50 UTC, unattended, run straight after session 67 by its chain clause. **Model spend: USD 0.00** (the cap was USD 0). No paid service, no force push. Branch `task/068-network`. Session 67's report says the release gate shipped, so it was not rebuilt here.

## In plain words

**The network looks as it did, and now answers questions.** It opens filling its frame, with four Watch buttons above it (the live week, California's evening, Texas during Uri, the June 2025 heat), a Batteries switch, and a panel that opens beside the network when you click a grid. The explanation moved below the network into folded sections.

**California's imports, settled as far as the data allows.** Session 62 had two answers, 27 percent and 16.6 percent. The 16.6 percent is right on the evidence: EIA's own total interchange for CAISO equals the sum of its ties to the MWh on every day. The 27 percent comes from demand less net generation, and that measure broke in December 2025, when CAISO's published net generation dropped by about 80 GWh a day while demand and interchange did not move. Why EIA's figure dropped is not in the warehouse's data, and I say so rather than guess.

**Who supplies California** (October 2025 to September 2026, as a share of CAISO's demand): Nevada Power 4.03 percent, Arizona Public Service 3.62, Bonneville 3.07, Los Angeles (LDWP) 2.97, then six smaller ties; in all 16.84 percent net.

**Two things a person should know.**
1. **Production's unlock link answers 404** (session 67's report). Everything on the site except six tools is closed to everyone until Vercel's `INTERNAL_COSTS_TOKEN` matches a token you hold. This page is live, so it is not affected.
2. **The battery rings are drawn only where the warehouse holds battery data**: ERCOT, ISO-NE, MISO and SPP (EIA-930, from November 2024) and CAISO (CAISO's own data, from August 2025). That is a limit of the warehouse, not a finding about the other grids.

## The pulls, against their ceilings

| Pull | Table | Rows | Ceiling | Window |
|---|---|---|---|---|
| A: EIA-930's daily total interchange of every balancing authority (type TI) | `eia930_daily_total_interchange` | **210,911** | 300,000 | 2019-01-01 to 2026-10-01, 83 respondents (EIA's regional sums among them) |
| C: hourly interchange of every pair and hourly demand of every balancing authority, two windows | `eia930_event_hourly_interchange` | **266,833** | 400,000 | Uri, 2021-02-07 to 02-24 (432 hours; 151,184 interchange rows of 350 directed pairs, 29,185 demand rows); the June 2025 heat, 2025-06-20 to 06-28 (216 hours; 71,992 and 14,472) |

Both connectors count the rows the API reports before asking for a page and stop if the count passes the ceiling. Neither came near it. 24 hours of demand in the Uri window had no number at the source and were not written. Both tables are public domain (EIA), valid, in coverage, the archive and the Redivis draft (nothing released); neither is in the live set (history). No other pull was made.

## Part A: three measures, and the finding on CAISO

### The seven ISOs, September 2025 to August 2026, on the same days (percent of demand)

| Grid | Sum of its ties | EIA's total interchange | Demand less net generation | Agree? |
|---|---|---|---|---|
| CAISO | 16.49 | 16.49 | 26.87 | ties and EIA's total agree; the balance does not |
| ERCOT | 0.07 | 0.07 | 0.07 | yes |
| ISO-NE | 4.96 | 4.96 | 4.96 | yes |
| MISO | 2.54 | 2.54 | 0.17 | ties and EIA's total agree; the balance is lower |
| NYISO | 11.82 | 11.81 | 11.81 | yes |
| PJM | -2.72 | -1.25 | -3.18 | no: they spread about two points |
| SPP | -1.44 | -1.00 | -1.01 | the ties read about half a point lower |

PJM and SPP also leave out the most days (PJM 141 of 365, SPP 165): a regular neighbour missing or a pair-day screened.

### CAISO's gap: what the evidence supports

- **Missing or screened pair-days:** none in the year. CAISO reported all eleven ties on every held day; none was screened out.
- **Ties reported by one side only:** CEN (Mexico's operator) does not report its tie with CAISO back. Every neighbour that reports a tie with CAISO is one CAISO reports too.
- **The two sides disagree on four ties:** the Arizona ties (AZPS, SRP), TIDC and BANC report different flows from CAISO's on the same days (largest mean daily gap SRP, about 8,400 MWh). The two sides agree in sign on every tie's total for the year. The headline uses CAISO's own reports; the neighbour's report is in the table (`neighbor_report_mwh`).
- **Sign conventions:** consistent. EIA's total interchange equals the sum of CAISO's ties to within 1 MWh on all 307 common days of the year.
- **Dynamic or pseudo-tie schedules:** not separately identifiable in EIA-930's daily data. Nothing in the data points to them.
- **Where the gap is:** in the balance. CAISO's demand less net generation less its interchange was within about 2 percent of demand through 2024 and most of 2025, then jumped in December 2025 and has run at 70 to 93 GWh a day (10 to 15 percent of demand) from January 2026. The interchange did not change and demand did not jump; CAISO's published net generation fell (January 2026: 348 GWh a day, against 457 GWh in January 2025). The residual correlates only weakly with CAISO's battery discharge (0.51) and is about 1.7 times as large.
- **Not explained:** why EIA's net generation for CAISO fell. I state that and no more.

### The headline rule

The sum of the ties is the headline ("the sum of its reported ties"): complete on every held day, equal to EIA's total interchange on the same days for five of the seven ISOs, and the measure the neighbours' shares add up to. Where the three measures spread more than one point over the twelve months, the panel shows the range and says so: CAISO, MISO and PJM in this data.

## Part B: `ba_supply_monthly`

Derived, public, 158,503 rows, 473 entities, 2019-01 to 2026-09. For every balancing authority and month: each neighbour's net imports in MWh (positive: the neighbour supplied it), that as a share of demand (seven ISO grids, where demand is held), the neighbour's own report of the same flow, the three measures, days held and left out, and a thin-month mark. In the validator, coverage, the source registry, `llms.txt` (the chat spec regenerated, no model call), the Redivis draft, and Supabase (the last 430 days: 22,706 rows; Supabase stands at 398.9 MB of 7,500).

**Decision:** a month EIA reported nothing for is counted as left out, not skipped. My first build skipped such months, and CAISO's November and December 2025 (3 and 10 days held) would have looked absent rather than thin; I caught it in the totals and fixed it before loading. **Decision:** every share is taken over the "share days" (held days whose demand is held too), so a numerator and its denominator cover the same days.

**Tests** (`tests/test_session68.py`, 10, pass): the pair shares sum to the pair-sum total; a pair reported by both sides agrees in sign with the neighbour's own report; a thin month is marked and a month with no report is counted as left out; a day missing a regular neighbour is left out; the screening rule on made-up data and on the real table (SWPP-MISO, 2026-07-21, screened); the ceilings; the event rows are never filled; a story counts each pair once by the network's rule.

## Who supplies CAISO, the last twelve months

October 2025 to September 2026, the panel's figures, as CAISO reported each tie (311 days held, 54 left out, 2 thin months):

| Neighbour | Share of CAISO's demand | Net imports |
|---|---|---|
| Nevada Power (NEVP) | 4.03 percent | 8.156 TWh |
| Arizona Public Service (AZPS) | 3.62 | 7.333 |
| Bonneville Power Administration (BPAT) | 3.07 | 6.218 |
| Los Angeles Department of Water and Power (LDWP) | 2.97 | 6.014 |
| Balancing Authority of Northern California (BANC) | 1.62 | 3.264 |
| Salt River Project (SRP) | 1.49 | 3.088 |
| Imperial Irrigation District (IID) | 1.00 | 2.029 |
| Western Area Power, Desert Southwest (WALC) | 0.37 | 0.743 |
| PacifiCorp West (PACW) | 0.04 | 0.082 |
| CENACE, Mexico (CEN) | -0.37 | -0.744 (CAISO supplied it) |
| Turlock Irrigation District (TIDC) | -0.99 | -1.980 (CAISO supplied it) |
| **Total, the sum of its ties** | **16.84** | |

The same twelve months on the other two measures: EIA's total interchange 16.83 percent, demand less net generation 28.11 percent.

## Which grids report battery storage, and from when

As the warehouse holds it: ERCOT, ISO-NE, MISO and SPP in EIA-930's battery series (`eia930_all_storage`, from 2024-11), and CAISO in CAISO's own data (`caiso_battery_storage`, from 2025-08), because CAISO reports no battery series to EIA-930. NYISO and PJM report none. The warehouse does not hold EIA-930's battery series for the other balancing authorities, and pulling it was not approved, so no ring is drawn for them; the panel says "not reported for this period" where no data is held. In the Uri window no grid's batteries are held; in the June 2025 window, ERCOT's, ISO-NE's and MISO's (SPP's series is not held for those days).

The ring is one thin dark line, no glow, around the sphere, facing the camera, fuller as the grid's batteries discharge and emptier as they charge, against its largest hour in the range shown. It looked restrained in the screenshots, so it stayed.

## What each Watch story shows, and what is missing

- **Live now:** the live week as before, from its newest hour; plays the week.
- **California's evening:** the newest complete Pacific day in the live week (2026-09-29 at the time of the test), hour by hour, camera on CAISO, Batteries on, CAISO's panel open with its batteries line. Missing: CAISO's demand for hours older than the hourly refresh's 48 hours is now read from `eia930_all_demand`, so the share is shown.
- **Texas during Uri:** 2021-02-07 to 2021-02-24, camera on ERCOT. 144 pairs; no pair-hour missing on both sides, 3,898 read from the other side's report (the network's pair rule); 191 hours of demand not reported; no battery data; ERCOT's hub price only (the other hubs' history starts in 2024); carbon color for the seven ISO grids. Not drawn because they are not in today's network: AEC, GLHB, GRIF, HGMA, SPC, WACM. The story says all of this under the buttons.
- **The June 2025 heat:** 2025-06-20 to 2025-06-28, camera on PJM. 149 pairs; 239 pair-hours not reported by either side (blank), 2,805 from the other side; no demand missing; batteries for ERCOT, ISO-NE and MISO; hub prices for every ISO but PJM (licensed).

Both stories are static snapshots, `site/public/network/story_*.json` (560 kB and 292 kB), and the same objects in the public Storage bucket `erw-public`. The page reads the site's own copy.

## What changed in the network's appearance, and what was left alone

**Changed:** the network fills its frame on opening and the frame is taller (up to 620 px); spheres a little smaller and lines a little more visible, so ties can be followed; the network and its controls come first and the explanation folds below; when a grid is selected, the other spheres turn translucent and the unrelated lines lighten, with no color changed; the page wears the shared header and grey source line.

**Left alone, deliberately:** the free-floating layout and its positions, the light background, rotating and zooming freely, the slow turn until touched, the particles running with the flow, names on hover only, carbon intensity as the sphere color at all times, no map, no dark stage, no color tabs.

**How:** the spheres are now drawn by the page (the same size rule 3d-force-graph uses) so each can have its own opacity; three.js comes from 3d-force-graph's own dependency.

## Tests and checks, local

| Check | Result |
|---|---|
| `python -m unittest discover -s tests` | 328 tests, pass, exit 0 (the first run failed 2 of session 54's source checks: one expected the "Newest hour:" text, one the old card's check key; the page keeps both again) |
| `tests.test_session68` | 10, pass |
| Package tests | 408 passed, 32 skipped, exit 0 (the first run failed 1: a filter test did not know the two new source tables name each BA) |
| `tsc`, the site build | exit 0 |
| `check-routes` (both passes) | 74 of 74; 14 live and 60 in review as a visitor, 0 failed |
| `check-values` | 6,622 of 6,622, including the 42 figures of the twelve months for the seven ISO grids (`bsup|`) |
| Browser test (`site/scripts/test-network.mjs`) | 30 assertions, pass: the four Watch buttons each set their view, play, and open their grid; the panel for CAISO, ERCOT and PJM, closed by Escape and by its button; the switch; the phone layout |

**The panel's hour figures and check-values.** The panel is drawn in the browser, so its hourly figures are not in the page's HTML and check-values cannot read them. Its twelve-month figures for the seven ISO grids are also in a folded table on the page, server-rendered with check keys, and those are what check-values compares.

## Errors and decisions

- **Supabase statement timeouts.** The page's first read of `ba_supply_monthly` (all rows at once, then one grid at a time with a LIKE) passed the anon role's time limit under load, and the page showed "could not be read". A range on the key (`entity >= eia930:CISO and < eia930:CISP`) uses the index; each read now takes about 0.15 s. check-values reads the same way.
- **The twelve months shown** are October 2025 to September 2026 (the newest whole month in the table), one month later than Part A's comparison window.
- **ISO-NE on the page's three-measures table** shows EIA's total interchange at 5.36 percent against 4.67 for its ties, because each measure is taken over its own months and EIA's total is missing on some days. On the same days they agree exactly (Part A).
- **Shares only for the seven ISO grids.** Demand is held for them only. Elsewhere the panel says why there is no share.
- **Local time** is shown for the seven ISO grids; for the others the panel shows UTC and says the local time is not held.
- **This laptop's `eia930_all_interchange` is older than the cloud's** (session 67's report). This session never read it: the live network comes from the hourly snapshot in Storage, and Part A and B read `eia930_daily_interchange`, which matches the cloud (945,130 rows here and in the last upload).
- **The data lock** was held from 22:52 to about 23:30 UTC for the pulls, the builds, the archive, the uploads and the load, and released.
- **`SESSION_69_PROMPT.md`** is in the repository root and a `wip/069-storage-buildout` branch exists on the remote; another session appears to be working. I did not touch either.

## The push and production

- **The push:** `git push origin task/068-network`, once, after every local check passed. The workflow's checks passed (run 37080999300) and merged it: main is at `595ae59`, "Merge task/068-network: checks passed". Production served the new page within a minute.
- **The live URL:** `https://erw-flame.vercel.app/network`.
- **On production,** the browser test passes, 30 of 30: the network draws and fills its frame; each Watch button sets its view, plays, and opens its grid (Uri on ERCOT, the June 2025 heat on PJM, California's evening on CAISO with the Batteries switch on); the panel opens for CAISO, ERCOT and PJM beside the network, PJM's without a price, CAISO's and ERCOT's with the link to what a battery earns there; Escape and the close button close it; the switch turns on and off; on a phone the panel stacks under the network and nothing is wider than the screen.
- **The panel's numbers match Supabase:** all 42 twelve-month figures on the production page equal this script's own recomputation from Supabase (`runs/session68/prod_supply.mjs`, not committed: `runs/` is not in git). CAISO 16.84 percent, largest supplier Nevada Power at 4.03; ERCOT 0.08, Southwest Power Pool 0.11; PJM -2.66 (a net exporter), Tennessee Valley Authority 0.84. The panel's hourly figures (the MW of each tie in the hour) come from the network's own snapshot, which the page already drew before this session.

**This section is committed on the local branch only.** Pushing it would merge and deploy a second time, which the run's rules forbid. It reaches main with the next session's merge, or when you push `task/068-network` yourself.

## For Samuel

1. **The unlock link answers 404 on production** (session 67). Set `INTERNAL_COSTS_TOKEN` on Vercel to the value in `.env`, or tell me which token Vercel holds.
2. **CAISO's net generation from December 2025.** Worth asking EIA, or checking CAISO's own data, why it fell about 80 GWh a day. Until then the network says the balance overstates California's imports.
3. **EIA-930's battery series for every balancing authority** would let the ring cover more than five grids. It needs an approved pull.
4. **Redivis:** three new tables in the draft only. Releasing is yours.
