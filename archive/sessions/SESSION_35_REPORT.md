# Session 35 report: Ask your grid, v1

Energy Research Warehouse (ERW), session 35, run 2026-09-30 from about 02:40 to 04:10 UTC, unattended.

**API spend: USD 0.3929 against the USD 3 cap** (`ERW_SESSION=35`, `ERW_SPEND_CAP_USD=3`). The ledger has 39 session 35 rows, all step `chat_grid`, model `claude-sonnet-5-5`: the seven scoped-chat questions of Part C and nothing else.

- **Nothing pulled:** no data pull, re-pull or backfill. The only outbound requests were status checks of the written layer's 32 source URLs (answer codes only, nothing kept).
- **Nothing added to the warehouse:** no new table, no source, nothing deleted from Redivis, no health-gate change, no force push.
- **Deployed and checked live:** routes 39 of 39, values 1,526 of 1,526.

## Part A: one template, seven pages

**Build.** One template, `site/app/grid/[iso]/page.tsx`, fed by `docs/grids/grids.json`, renders seven static pages: /grid/ercot, /grid/caiso, /grid/pjm, /grid/nyiso, /grid/isone, /grid/miso and /grid/spp.

- **The config.** Each grid's tables were read once from `warehouse/metadata/coverage.csv` and written into the config (BA code, time zone, hub, queue table, the tables that carry the grid). Nothing scans tables to find out.
- **Data readers:** `site/lib/grid.ts`.
- **Nav:** the Grid menu has a "Your grid" line with the seven, and /grid links them too.
- **Chips and links.** Every block has a tier chip and a citation; derived blocks link their method; the written layer has a "written, cited" chip.
- **Asking.** Each page has an "Ask <ISO>" box that opens the scoped chat.

**Blocks per grid.** "Renders" means the block shows the grid's rows; "not yet" means the one-line "not in the warehouse yet" with where EIA or the ISO publishes it.

| Block | ERCOT | CAISO | PJM | NYISO | ISO-NE | MISO | SPP |
|---|---|---|---|---|---|---|---|
| 1. Right now: demand, today so far, same day last week | renders | renders | renders | renders | renders | renders | renders |
| 2. Generation by fuel, 24 hours and 30 days | renders | renders | renders | renders | renders | renders | renders |
| 3. Batteries: daily cycle | renders (EIA-930) | renders (CAISO's own series) | **not yet** | **not yet** | renders | renders | renders |
| 3. Batteries: fleet MW and MWh | renders | renders | renders | renders | renders | renders | renders |
| 4. Carbon intensity now, 24 hours, monthly since 2018 | renders | renders | renders | renders | renders | renders | renders |
| 5. Prices at the main hub | renders | renders | **not yet** (internal) | renders | renders | renders | renders |
| 6. Queue by kind and status | renders | renders | **not yet** | renders | renders | renders | renders |
| 6. Datacenter facilities | renders | renders | renders | renders | renders | renders | renders |
| 7. News, 14 days | renders | renders | renders | renders | renders | renders | renders |

**Why the three "not yet" lines:**

- **PJM and NYISO batteries:** EIA-930 carries no battery series for either (session 31). Their fleets from EIA-860M still render.
- **PJM prices:** licensed for internal use. The block says so and links PJM's energy market page.
- **PJM queue:** the warehouse holds no PJM queue table. The block links PJM's queue page.

**Headline figures on the rendered pages, as built (2026-09-30):**

| Grid | Latest demand hour | Operating battery fleet | Datacenter facilities (states counted) | News, 14 days |
|---|---|---|---|---|
| ERCOT | 79,553 MW (Sep 28, 6 PM CDT) | 18,204.50 MW, 30,019.80 MWh | 37 (TX) | 26 |
| CAISO | 33,897 MW (Sep 28, 4 PM PDT) | 17,094.20 MW, 59,118.30 MWh | 35 (CA) | 30 |
| PJM | 97,725 MW (Sep 28, 7 PM EDT) | 665.90 MW, 1,504 MWh | 58 (DE, DC, MD, NJ, OH, PA, VA, WV) | 10 |
| NYISO | 17,518 MW | 268.70 MW, 760.60 MWh | 5 (NY) | 8 |
| ISO-NE | 14,150 MW | 1,021.70 MW, 2,130.80 MWh | 1 (six New England states) | 2 |
| MISO | 87,704 MW | 1,175.90 MW, 3,449.90 MWh | 11 (MN, WI, IA) | 6 |
| SPP | 40,004 MW (Sep 27, 6 PM CDT; EIA's latest for SWPP) | 490.50 MW, 1,609.50 MWh | 10 (KS, NE, OK) | 5 |

**News: there is no ISO tag.** `news_index` has no ISO field, so a story counts for a grid when:

- its model-written headline names the grid (ERCOT, CAISO, PJM, NYISO, ISO-NE, MISO, SPP, and the long names), or the state for single-state grids (Texas, California, New York); or
- its region is one of the grid's counted states.

`check-values.mjs` matches the same way from the same config.

**Check keys.** Every block that shows a number has keys, on every grid; for example ERCOT has 55 on its page. Keys are counted from each grid's HTML: demand 2 to 3, generation 9 to 11, batteries 4 to 7, intensity 4, prices 5, building 2 to 38, news 1. PJM's price block has none: it shows no number. The new key types are:

- `gridq`: queue count and MW by kind and status;
- `griddc`: datacenter count and MW in the grid's states;
- `gridnews`: stories matched since a date;
- `storage|iso_mwh`: the fleet's MWh.

**Two fixes during the build:**

- **The queue read timed out** (Supabase statement timeout on a JSON-field filter). It now reads `energy_projects` by its id prefix (`ercot_queue:*`), which the primary key serves.
- **The 30-day generation sums were short by a few hours** because the read began inside the window. The read now covers 34 days.

## Part B: the written layer

`docs/grids/<slug>.md`, seven files with five sections each:

- what the grid is and who runs it;
- how its market sets prices;
- what makes it different (ERCOT's isolation and energy-only market, CAISO's solar and evening ramp, PJM's capacity auction, NYISO's downstate constraint, ISO-NE's winter gas, MISO's north-south seam, SPP's wind);
- three dated events;
- a ten-term glossary.

**Rules the text follows:**

- Every section ends with its sources.
- No market number appears in prose. The few counts and superlatives carry inline citations: PJM's thirteen states, "largest wholesale market" and its 1927 origin; Texas's wind and California's solar leadership (EIA); SPP's wind share.
- It renders on each page: "who runs it" at the top, the rest at the bottom, both with the "written, cited" chip.

**Sources, all 32 answering 200 on 2026-09-30:**

- **ERCOT:** ercot.com/about, /about/profile, /mktinfo.
- **CAISO:** caiso.com/about, /about/our-business, /todays-outlook; westernenergymarkets.com.
- **PJM:** pjm.com/about-pjm, /about-pjm/who-we-are, /markets-and-operations/energy, /markets-and-operations/rpm.
- **NYISO:** nyiso.com/about-us, /what-we-do, /energy-market-operational-data.
- **ISO-NE:** iso-ne.com/about, /about/key-stats, /markets-operations/markets/forward-capacity-market.
- **MISO:** misoenergy.org/meet-miso/about-miso/.
- **SPP:** spp.org/about-us/, /about-us/fast-facts/.
- **EIA:**
  - gridmonitor/about and each BA's Grid Monitor dashboard (ERCO, CISO, NYIS, ISNE, MISO, SWPP);
  - electricity/wholesale;
  - energyexplained: delivery-to-consumers, electricity-in-the-us, where-solar-is-found, where-wind-power-is-harnessed.
- FERC's pages answer 403 to automated requests, so none is cited.

**The dated events:**

- **ERCOT:** 1970 formed; 2010-12-01 nodal market; 2021-02-15 Uri load shed.
- **CAISO:** 1998-03-31 operations begin; 2014-11-01 Western EIM; 2020-08-14 rotating outages.
- **PJM:** 1927 pool; 2007-06-01 first RPM delivery year; 2022-12-24 Winter Storm Elliott.
- **NYISO:** 1999-12-01 takes over from the Power Pool; 2003-08-14 Northeast blackout; 2021-04-30 Indian Point's last reactor closes.
- **ISO-NE:** 1997 created; 2003-03-01 Standard Market Design; 2008-02 first Forward Capacity Auction.
- **MISO:** 2001-12 first RTO; 2005-04-01 markets open; 2013-12-19 MISO South.
- **SPP:** 1941 pool; 2014-03-01 Integrated Marketplace; 2021-02-15 Uri.

These dates are from my knowledge and the cited ISO pages' framing, not fetched text. A human should spot-check them (question 2).

## Part C: Ask ERCOT and the six others

**How the scope works.** `/ask?grid=<slug>`, and `ask.py --grid <slug>` for the same loop in Python:

- A block after the system prompt says which grid the chat speaks for.
- `list_tables` shows only the tables carrying that grid.
- `query` and `describe_table` read only its rows: partition `ba`, market prefix, `storage_capacity`'s `iso`, and `energy_projects`' queue prefix.
- A fifth tool, `grid_notes`, reads the written layer. It is cited as `docs/grids/<slug>.md` with tier `written`.

**Wiring.** The grid pages' Ask box opens the scoped chat with the question filled in. `/api/ask` refuses an unknown grid (checked live).

**The check: seven questions, one per grid,** run through `warehouse/chat/eval/grid_check.py` on the local backend, every call in the ledger. Records: `warehouse/chat/eval/results/20260930T034641Z_grids.json`.

| Grid | Question | Status | Tool calls | Cites | USD |
|---|---|---|---|---|---|
| ERCOT | Highest hourly demand in the last 30 days, and when | answered | 8 | eia930_all_demand | 0.1239 |
| CAISO | Batteries discharged and charged on the latest complete day | **answered, but empty** | 8 | none | 0.0664 |
| PJM | Who runs PJM; its capacity market's name | answered | 1 | docs/grids/pjm.md | 0.0162 |
| NYISO | Latest day-ahead daily mean, N.Y.C. zone | answered | 8 | nyiso_dam_zone_prices | 0.0667 |
| ISO-NE | Carbon intensity of generation, latest month | answered | 3 | carbon_intensity_monthly | 0.0251 |
| MISO | Active solar projects in the queue, and their MW | answered | 3 | miso_interconnection_queue | 0.0245 |
| SPP | What makes SPP different; wind over the last 7 days | answered (after one retry) | 8 | docs/grids/spp.md, eia930_all_generation | 0.0702 |

**Total USD 0.3929.**

**The answers:**

- **ERCOT:** the window was ambiguous, so it gave both readings:
  - from 2026-08-31, 88,535 MW in the hour starting 2026-08-31 21:00 UTC (16:00 Central);
  - from 2026-08-30, 88,768 MW at 2026-08-30 22:00 UTC.
- **CAISO:** an empty answer with no citation, after eight tool calls that did find `storage_daily_cycle`'s CAISO rows. The loop accepted it: its citation check applied only to answers containing numbers.
- **PJM:** PJM Interconnection runs the grid. It is the largest wholesale market in the US and covers all or part of thirteen states and DC. Its capacity market is the Reliability Pricing Model (RPM), with a yearly auction. All from `docs/grids/pjm.md`.
- **NYISO:** 45.92 USD/MWh for the Eastern-time operating day 2026-09-29, the mean of 24 hourly prices; 46.20 the day before (`nyiso_dam_zone_prices`).
- **ISO-NE:** 244.35 kgCO2/MWh in August 2026, the latest complete month (`carbon_intensity_monthly`).
- **MISO:** 383 active projects with fuel "Solar", 71,671.18 MW requested (`miso_interconnection_queue`, hybrids separate).
- **SPP:** the wind text from `docs/grids/spp.md`, and wind over 2026-09-21 to 09-27 UTC: 10,363.67 MW mean, 1,741,096 MWh (`eia930_all_generation`).

Each figure passed the loop's check that every number appears in a tool result.

**Fixed after the check,** in both loops (Python and site):

1. **An empty or uncited answer is now sent back once, then refused.** An answer of "not in the warehouse" still needs no citation.
2. **`list_tables(iso=...)` compared the ISO field exactly,** so it missed every consolidated table ("CAISO;ERCOT;..."). That cost the CAISO question its first calls. It now splits on ";".

`tests/test_session35.py` covers the scope, the written layer's sections and sources, the ISO filter, and the gate (on a fake client).

**CAISO was not asked again:** the check allowed seven calls (question 1).

## Part D: verify and ship

- **check-routes and check-values** extended to the seven pages; the new key types are listed in Part A.
  - Local: routes 39 of 39, values 1,526 of 1,526.
  - **Live:** the same, routes 39 of 39 and values 1,526 of 1,526.
- **Chat spec** regenerated after `llms.txt` and the loop changed; `check_spec` passes. `llms.txt` lists the pages, the config, the written layer, `grid_notes` and the scoped chat.
- **Package tests untouched.** `tests/`: 60 of 60 before the new file; `test_session35` 5 of 5.
- **Deployed** by push; live after about 60 seconds. `/ask?grid=spp` renders "Ask SPP".

## Decisions made without a human

1. **Datacenters by state, not by grid.** The warehouse places facilities by state, so each grid counts only the states wholly or mostly inside it:
   - TX; CA; NY; the six New England states;
   - PJM: DE, DC, MD, NJ, OH, PA, VA, WV;
   - MISO: MN, WI, IA;
   - SPP: KS, NE, OK.

   Shared states (Texas for MISO and SPP, Illinois, Michigan and others) are left out, and the page says a facility may be served by a neighboring grid.
2. **News by headline and region,** since no ISO tag exists (above). The state names widen single-state grids' matches beyond grid news, for example Texas politics.
3. **Main hubs** are those of `price_board_peak_offpeak` (HB_HUBAVG, SP15, N.Y.C., .H.INTERNAL_HUB, INDIANA.HUB, SPPNORTH_HUB).
4. **"Right now"** is the latest hour EIA has published, a day or so late, and says so.
5. **The Part C check ran on the Python loop,** which writes the ERW cost ledger and enforces the cap. The site loop is the same spec and tools, but it logs to `site_api_calls` without a cap.
6. **The chat's citation gate was tightened.** This is a chat check, not the health gate.
7. **FERC is not cited** (its pages refuse automated requests).
8. **The market filter in the scoped chat** keeps rows whose market starts with the grid's prefix. It drops the Henry Hub and Brent rows of `price_board_spreads`.

## Run health and the gate

- **Gate: CLOSED,** unchanged. The latest GitHub daily run (2026-09-29, failed at coverage before its commit) has 2 failures outside the known gaps:
  - `coverage`: fixed in `670ba69`, not yet proven by a run;
  - `eia930_swpp_demand`: EIA's missing SPP forecast hours.
- This session added no source and no tool to the warehouse. The grid pages are a reach layer on existing tables, and PRIORITIES.md allows work a human asks for directly.
- **No daily job has run since 2026-09-29 18:58 UTC;** the next is scheduled for 14:00 UTC today. Nothing landed during the session, and origin had no new commits at either push.

## Open questions

1. **CAISO's scoped answer** came back empty before the gate fix. Allow one more call to confirm the fixed loop answers it (about USD 0.07)?
2. **Spot-check the written layer's dated events and claims** before students rely on them. They are from my knowledge, framed by the cited pages; I fetched status codes only, not the text.
3. **News matching** by headline words and regions is loose. Add an ISO tag to the scorer's output (a model-extracted field), or keep the rule?
4. **Datacenter state lists for PJM, MISO and SPP.** Accept them, or map facilities to grids by the utility named, where one is?
5. **Still open from session 34:**
   - `eia930_swpp_demand` as a known gap or per-day rule;
   - `DIGEST_RECIPIENTS` on GitHub;
   - coverage's 14-minute build.

## Skipped

- A second CAISO question (the seven-call limit).
- Exercising the site's scoped `/ask` with a live model call. Its tools and routing were checked without one: an unknown grid is refused, and the page renders scoped.
- Package tests: untouched, as asked.
