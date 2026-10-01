# Session 48 report: the gate was not open when read, so the fallback ran (the shape premium draft)

Energy Research Warehouse (ERW), session 48, run 2026-10-01 from 00:15 to about 00:40 UTC. **Wall time about 25 minutes.**

**API spend: USD 0.00, confirmed.** No model call. No data pull, so no rows against any ceiling: NOAA weather 0 of 100,000, EIA-930 2018 files 0 of 100,000, RRC wells 0 of 500,000. No Supabase table, no force push.

## Part 0

### 1. GitHub issues

**Closed: none.** The repository token in `.env` cannot write issues: every comment and close request answered **HTTP 403**.

- **#3, #4, #5:** a comment, then a close, tried on each at 00:17 UTC.
- **#10:** one comment, tried at 00:32 UTC after run 14 had passed. Same answer.
- **Samuel:** close them by hand, or give the token issue write permission. The text for each:
  - **#3 (CARB), #4 (NYISO queue), #5 (ERCOT large-load queue):**
    - "Closing as a known gap: <reason>. It is listed in `warehouse/metadata/known_gaps.csv` with that reason, and since 8bf0c97 the three-day issue opener skips tables on that list."
    - The reasons: CARB's PDF and NYISO's workbook answer GitHub runners with HTTP 202 and no body, and both tables are refreshed from local runs. ERCOT publishes no request-level large-load list (Protocol 3.2.7 requires only an aggregate monthly report).
  - **#6 to #10 (daily run failures):** "Daily run 14 (374f8fd) passed on 2026-10-01 00:20 UTC. Fixes: 5c00e9d (package tests: tables carried over in coverage), cf660b0 (policy_reads header after a restore)."

**Known gaps:** all three tables were already in `warehouse/metadata/known_gaps.csv` with their reasons, which match the prompt's.

**The three-day issue opener now skips known gaps** (8bf0c97):
- `run_status.py streaks` prints a known gap as "known gap, no issue" and leaves it out of `runs/failure_streaks*.txt`, the file the workflow opens issues from.
- Run on the real history, it lists all three as known gaps and writes nothing.
- Tested in `tests/test_session48.py`.

### 2. The gate

- **When it was read** (00:17 UTC), the latest daily-prices run was **run 14** (workflow_dispatch, 374f8fd), still in "Pull, validate, rebuild coverage". It had not passed, so **the fallback ran.**
- **Run 14 then passed,** completing at 00:20:27 UTC. Its daily commit (1ee616b) is merged.
- **So the gate is open now, but it was not when either session read it:**
  - session 47's Part B: the interchange pull, the 3D network, the year of hub prices;
  - session 48's Parts A and B: NOAA weather, the 2018 EIA-930 files, the RRC wells.
  - None of their pulls was made. **The RRC's data terms were not read,** so no pilot county was chosen.
- **Next session:** these can run as soon as it starts, since a daily run has passed.

## The fallback: "What flat load pays: the shape premium across six ISOs"

**Where:** `/reports/draft/shape-premium` (fe139ea), a draft, internal:
- answers 404 unless `?token=` equals the server's `INTERNAL_COSTS_TOKEN`, the gate of `/internal/costs`;
- not indexed, not in the nav (checked by a test).

**Length and charts:** about 1,500 words (1,503 in the rendered text). Three charts, each with a table:
- the six hubs' premium as bars;
- ERCOT's monthly premium as diverging bars, cardinal above zero and green below, the axis cut at the second-largest month and Uri labeled;
- small multiples of each hub's hour-of-day price.

The chart labels were checked in the browser for overlap. One collision, the lowest y-label against the "00" hour label in each panel, was fixed.

**What it says** (numbers as read on 2026-10-01; the page reads them live):

- **Six ISOs, day-ahead, September 2026** (672 of 720 hours):
  - the premium runs from 0.92 USD/MWh at CAISO SP15 to 5.45 at MISO's Indiana Hub;
  - as a percent of the simple average, from 2.24 (CAISO) to 9.77 (SPP);
  - every hub's grid-shaped load paid more than a flat load.
  - **Why day-ahead:** SPP's real-time September holds only 96 hours.
- **What drives MISO's lead:** its September evening. Its dearest real-time hour, 18:00, averaged 509.85 USD/MWh, 16.25 times its cheapest.
- **ERCOT, 95 complete real-time months** (August 2018 to August 2026):
  - the premium was positive in 94 (the exception was June 2026) and averaged 5.65 USD/MWh;
  - Uri's February 2021 reached 246.77 (load-weighted 1,768.62 against simple 1,521.84), 7.88 times the next-largest month, August 2019's 31.33;
  - otherwise it is a summer story, and it has shrunk.
- **Grid-shaped against flat, per MW** (premium times hours, complete years only, 2019 to 2024):
  - 182,548.73 USD in 2021;
  - 13,600.31 in 2024, the latest complete year (2025 lacks December's real-time hours);
  - over the latest twelve months held (11 of them complete), 10,587.20, a mean premium of 1.31 USD/MWh.
- **Day-ahead against real-time** (ERCOT, September 2026): 1.07 against 1.18 USD/MWh.

**Every number is checked:**
- **Check keys:** each carries one. Table rows of `cost_of_power_monthly` and `cost_of_power_hourly_profile`; calc keys for percents and ratios; and a new `shape|<entity>|<market>|<stat>|<start>|<end>` key for the period statistics.
- **The period statistics** come from `site/lib/shapepremium.ts`, which the page and check-values share. `tests/test_session48.py` holds them equal to an independent pandas computation.
- **check-values visits the page with the token** where one is set (`.env.local`), and skips it, saying so, where the server answers 404.
- **Local:** check-values 2,373 of 2,373, including the report's 60 values. check-routes 58 of 58. `tests/` 105 OK.

**Live, after the deploy:** check-routes 58 of 58, check-values 2,313 of 2,313. check-values said the report was "not checked: answers 404". The page answers 404, because `INTERNAL_COSTS_TOKEN` is not set on Vercel (`/internal/costs` answers 404 with the token too). To read it on the live site, set the variable on Vercel and redeploy (`docs/runbook.md`, session 30).

## Decisions made without a human

1. **The gate as read, not as it later turned out:** both sessions read the gate while run 14 was running, and their fallbacks ran. I did not start the approved pulls after run 14 passed, mid-way through the fallback; the prompts route at Part 0.
2. **The report's six-ISO comparison uses day-ahead,** the one market every hub holds for nearly every hour of the month. ERCOT's long view uses real-time. It says why.
3. **The internal token:** the report reuses `INTERNAL_COSTS_TOKEN`, the one internal token the site has. The page is not in the nav.
4. **The browser render check used a throwaway local test token** in place of the real one, so the real token was never typed into a browser.
5. **Wording:** the report states no cause the warehouse does not hold. It mentions the battery fleet's growth only as a coincidence in time, and says the warehouse does not say why the premium shrank.

## Open questions

1. **The issues:** close #3 to #10 by hand (texts above), or give the repository token issue write permission?
2. **Next session:** run session 42 (the interchange pull and the 3D network), session 47's year of hub prices, and session 48's Parts A and B (weather, the 2018 baseline, the RRC wells), now that the gate is open?
3. **The draft report:** set `INTERNAL_COSTS_TOKEN` on Vercel to read it live? It should be redone once the year of hub prices is in, so all six ISOs have a long view.
4. **Still open from session 47:** the Supabase `VACUUM FULL` and the weekly vacuum workflow.
