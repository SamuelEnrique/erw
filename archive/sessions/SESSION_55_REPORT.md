# Session 55 report: leaner hourly pulls, the game's leaderboard by preset, problem set E

Energy Research Warehouse (ERW), session 55, run 2026-10-01 from 19:41 to about 20:08 UTC. **Wall time about 27 minutes,** against a 45-minute target.

**API spend: USD 0.00, confirmed.**
- No model call.
- No data pull: the hourly change was tested on fixtures, and no EIA request was made.
- No Supabase table was added.
- No force push. The daily job did not land during the session, so there was nothing to merge.

| Item | Done | Commit |
|---|---|---|
| 1. Leaner hourly pulls | yes | `382a3b1` |
| 2. The leaderboard by preset on the pick screen | yes | `ec91837` |
| 3. Problem set E, "Networks and money" | yes | `6eaf113`, wording `1b1b00d` |
| 4. check-routes, tests, deploy, live checks | yes | this report |

## 1. Leaner hourly pulls (session 54's open question 4)

`warehouse/derived/network_hourly.py`:

- **The new first request.** A run now starts by reading the interchange route's `endPeriod` from the route's metadata, which returns no data rows.
  - The prompt asked for "a length-0 request". EIA's `data/` endpoint with length 0 returns the row total, not the newest period, so the metadata request is the zero-row request that answers the question.
- **When nothing moved, the interchange pull is skipped.** If the `endPeriod` equals the one the Storage object was built from, and that object is the base (newer than the committed snapshot), the run:
  - skips the interchange pull;
  - carries the links over unchanged (hours, window, links and volumes identical);
  - pulls demand only, about 330 rows instead of about 15,900;
  - records `"interchange": "unchanged"` in the object, with `pull.interchange_pulled` saying when the links were last pulled.
- **Otherwise, the full pull.** A moved `endPeriod`, or a daily snapshot newer than the object, brings back the full pull, and the object records `"interchange": "pulled"`.
- **Objects from session 54** hold only `eia_interchange_end` (the newest period of the rows they pulled). `previous_end()` reads it as the recorded `endPeriod`.
- **Testable.** The run is now `build()`, which takes the two pulls as functions so the tests can pass fixtures.

**Tests** (`tests/test_session55.py`, `LeanerPulls`, 5 tests):
- **Fixtures:**
  - interchange rows written from the committed snapshot's own values (real EIA-930 flows, at their own hours);
  - demand from `tests/fixtures/network/eia_demand.json`: real EIA values for the seven ISO BAs at 15:00 UTC and ERCOT's at 16:00 UTC on 2026-10-01, recorded by session 54's runs.
- **Pulled path:** the interchange pull is called once and the links match the source.
- **Unchanged path:** the interchange pull raises if called, and is not called. Links, hours, window, positions and volumes are identical; ERCOT's demand moves from 15:00 (64,661 MW) to 16:00 (65,789 MW).
- **A moved `endPeriod`** pulls.
- **A newer daily snapshot** pulls.
- **Session 54's object form** is read correctly.

The runbook and the method page say what an "unchanged" run is.

## 2. The game's leaderboard by preset (session 50's open question 2)

- **The read route:** `GET /api/play/top?level=YYYY-MM-DD&preset=<preset>` (`site/app/api/play/top/route.ts`).
  - It returns `{level, preset, label, top}`: the best ten of `game_scores` for that level and preset, with the ERW's own checks left out (`lib/game.ts` `leaderboard`).
  - It is read only, with its own floor of 240 reads an hour per server instance, so changing settings does not use up the 30 plays an hour.
- **What it refuses, with HTTP 400:**
  - a preset that `presetOf` does not write: an unknown difficulty, a setting outside its range or off its step, a reserve and wear setting on a level other than Hard (or missing on Hard), or any other spelling of the same rules (`lib/battery.ts` `parsePreset`);
  - a level that is not a famous day or one of the last ten complete days.
- **The pick screen** (`Game.tsx`) reloads the board 400 ms after the day, the difficulty or a setting changes, and only while the settings are valid.
  - The heading names the preset: "Leaderboard, <date>: <preset label>".
  - While it loads, it says "Loading the board for <date>: <preset>...".
  - An error is shown in place of that line.
- **Tests:** presets round-trip through `parsePreset`, including the extreme settings; 19 malformed or non-canonical presets give null. Static checks confirm the route's refusals and that the route is read only.
- **Live** (2021-02-15 is a famous level):
  - `hard:13.5-5-90-r20-d0.11` answered 200, "Hard, the default battery", with no scores yet;
  - `turbo:1-1-1` answered 400.
  - Locally, `normal:13.50-5-90` (a non-canonical spelling) and level `1999-01-01` each answered 400.
- **Not checked in a browser:** the reload on the pick screen was checked by its code and its tests only. Memory was short on this machine in session 54, so I did not drive a browser.

## 3. Problem set E, "Networks and money"

`/learn/problems/networks-and-money`, on the session 44 pattern. Every answer is computed on the server (`lib/problems.ts` `setE`) and carries a check key; none is typed.

- **The network questions** read the snapshot `/network` draws: the hourly one in Storage, else the committed one. The Storage fetch moved into `lib/network.ts` (`fetchHourly`), so the page and the problem set share it. New helpers there: `tiesAt`, `netExports`, `topExporter` and `netValue`.
- **The money questions** read the seller's tab, `lib/merchant.ts` on `data/merchant_snapshot.json` (built from `merchant_revenue_monthly`), at its defaults. `stat` gains `flat:<month>`.
- **Where it is linked:**
  - a teacher note;
  - the Learn menu, now 7 entries;
  - the problem sets index, which lists sets automatically;
  - `docs/tools.md`.
- **Checks:**
  - check-values covers the new page. It recomputes `net|` keys on the Storage snapshot when that holds the hour, else on the committed snapshot. `mr|` and `calc|` keys work as before.
  - check-routes lists the page.

### The five computed answers (live, 2026-10-01 about 20:00 UTC)

1. **ERCOT's neighbors and largest flow,** in the newest hour of the network, 2026-09-30 03:00 UTC (Sep 29, 23:00 Eastern): ERCOT exchanged power with **2 neighbors** (Southwest Power Pool and CENACE, Centro Nacional de Control de Energia). The largest flow was **220 MW, in from Southwest Power Pool**.
   - The first draft said "ties". A neighboring balancing authority may be several physical DC ties, so the answer now counts neighbors.
2. **The largest net exporter in that hour:** **Salt River Project (SRP), 6,283 MW net.**
   - Checked against its ties: 5,450 MW to Arizona Public Service and 1,862 MW to CAISO, less its imports. SRP's net export over the week ran from 2,452 to 6,932 MW, median 4,440 MW.
3. **Merchant solar's capture rate,** ERCOT HB_HUBAVG, 2026-09 (the latest held month): it **captured 33.66 USD/MWh against a flat 38.98 USD/MWh, a capture rate of 86.36 percent**.
4. **Months a default ERCOT battery covered its debt** (100 MW / 400 MWh; 6,783,357 USD a year of debt service): **26 of 99 months.** It fell short in 73.
5. **Solar revenue on Uri's days against a normal week** (100 MW, the 18 days from 2021-02-07 to 2021-02-24): **12,382,219.96 USD, against 61,312.70 USD for a normal week, 201.95 times as much.**

**Tests** (`SetE`): the network answers are recomputed by hand in Python on the committed snapshot; the money answers come from `lib/merchant.ts`, with the capture rate checked as capture over flat; the wiring is checked; and a check confirms no typed number in `setE`.

## 4. Checks

- **Local build:**
  - check-values: 3,817 of 3,817, all of set E included (`net|ties` 2, `net|maxflow` 220, `net|topexport` 6,283, and the `mr|` and `calc|` keys);
  - check-routes: 63 of 63.
- **Live, after the Vercel deploy:** check-values 3,732 of 3,732; check-routes 63 of 63.
- **Tests:** sessions 53, 54 and 55 together, 30 tests, OK.
  - `tests/test_session54.py` was changed: it now looks for the Storage fetch in `lib/network.ts`, where it moved.
- **Lint and types:** eslint and tsc are clean on every changed file.

## The hourly workflow, three hours on

The workflow has still not run on its schedule. Its only run is the failed dispatch of 17:14 UTC. The Storage object is still the one uploaded at 18:17 UTC.

This confirms session 54's open question 1: GitHub's scheduler runs this repository's frequent crons rarely. Item 1 makes each run cheaper, but it does not make runs happen.

## Open questions

1. **A trigger outside GitHub:** as in session 54. Until one exists, "hourly" means whenever GitHub's scheduler runs the cron.
2. **The network answers move with the snapshot.** A full pull may revise the newest hours, so a problem page cached for up to an hour could, for that hour, show a value the new object no longer holds. check-values would then report a mismatch. It has not happened yet. Should set E use the committed daily snapshot instead, which is stable but older?
3. **The battery's debt cover (26 of 99 months)** comes from a perfect-foresight upper bound on its revenue. Should the question say "at best", as the seller's tab does in its notes?
