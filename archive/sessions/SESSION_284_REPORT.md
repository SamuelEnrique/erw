# Session 284 report: the tables behind the price board and Supply and trade

14 October 2026, 18:21 to about 19:10 UTC, unattended, on lab-desktop (the data machine), the first session of the daytime chain of 14 October (started after the 13:45 to 16:15 window had passed). Branch `task/284-board-supply`. Model spend USD 0: no model call. Pulls: EIA's API, two requests of three rows each (Henry Hub and WTI, to read EIA's newest day). Nothing from NYISO, ISO-NE, MISO, SPP, PJM or a paused publisher.

## Read these first

- **The board's 36 ERCOT rows stood at 7 and 8 October and no schedule could move them. Fixed at the cause and refreshed.** The runner builds the board every day, but holds only ERCOT's rolling window (from 26 August); `page_keep.py` takes a new row only where it is no shorter than the held one, so the runner's ERCOT rows were never taken. The board is now a page file of this machine's daily run (`dm_board_page`, gated by the board's Python tests as the group `dm_test_board`), and was built here tonight: ERCOT's day-ahead now reaches 14 October, its real time 13 October, its spark spread 10 October (the newest Henry Hub day, below).
- **Every other board and Supply table is at its publisher's date, or not this chain's to ask.** EIA's spot prices end 6 October at EIA itself (read tonight from EIA's API); EIA's weekly petroleum and gas storage reports for the week of 9 October are due 15 October (Columbus Day moved them); CARB's LCFS report lags at source (session 271's rule).
- **No "not held" cell can be filled from a public source under terms the ERW can use.** The 54 blank board rows (and 4 blank futures curves) are PJM (licensed), MISO (paused), ISO-NE's reserves and the two carbon auctions (held while terms are reviewed), and vendor-licensed series (Platts, ICE, CME, UxC, Fastmarkets). The table below names each with its source and terms.
- **NYISO's and SPP's reserve prices on the board (30 rows, to 3 and 4 October) have no schedule anywhere.** Not this chain's to ask: a ruling (1).
- **The board's own node test (`site/scripts/test-board.mjs`) fails on main as it stands**, not because of this session: it holds the top twelve rows to a week from the build, and Henry Hub's newest EIA day is 8 days old. The branch checks do not run it. A ruling (2).

## The tables, newest row against cadence

Read from `warehouse/output` on this machine at 18:22 UTC (the script is `runs/session284/fresh.py`, not in git).

| Table | Page | Newest row | Cadence | Verdict | Schedule |
|---|---|---|---|---|---|
| ERCOT hub rows of `ercot_all_hub_prices_history`, `iso_dam_hub_prices`, `iso_rtm_hub_prices` | /board | here 15 Oct 04:00 UTC; **on the board 8 Oct** | daily | **stuck: fixed and refreshed** | `dm_board_page` (new), after the runner's `board` |
| `caiso_as_prices`, `ercot_as_prices` | /board | 15 Oct | daily | fresh | runner, daily |
| `iso_hub_prices_history` (CAISO, ISO-NE, NYISO, SPP hubs) | /board | 13 to 15 Oct | daily | fresh | runner, daily |
| `nyiso_as_prices` | /board | 5 Oct | daily | stale, no schedule | none: NYISO, a ruling (1) |
| `spp_as_prices` | /board | 4 Oct | daily | stale, no schedule | none: SPP, a ruling (1) |
| `eia_fuel_spot_prices`, `eia_product_spot_prices` | /board | 6 Oct | weekly post | at source (EIA's API's newest day, read tonight) | runner, daily |
| `frb_treasury_yields` | /board | 9 Oct | daily | at source: 12 Oct a holiday; 13 Oct posts in the evening | runner, daily (`refresh_board.sh`) |
| `eia_regional_retail_fuel_prices` | /board | 12 Oct | weekly | fresh | runner, daily |
| `carb_lcfs_credit_prices` | /board | 14 Sep | weekly report | at source (CARB lags; skip by session 271's rule) | this machine, daily |
| `eia_crude_stream_prices`, `eia_power_plant_fuel_costs`, `eia_retail_electricity_prices`, `imf_commodity_prices` | /board | Jul to Sep | monthly | at source (EIA's and the IMF's monthly releases) | runner, daily |
| `eia_gas_storage_weekly`, `eia_petroleum_supply_weekly` | /supply | 2 Oct | weekly | at source: the week of 9 Oct is due 15 Oct | runner, Saturdays |
| `cftc_cot_positions` | /supply | 6 Oct | weekly | at source: next report 16 Oct | runner, Saturdays |
| `eia_basin_production_monthly`, `eia_gas_trade_monthly` | /supply | Jul | monthly | at source | runner, Saturdays |

- **Older last dates inside the monthly tables** (crude streams to 2020 to 2025, plant fuel costs by state to 2020 to 2026) are series EIA stopped or withholds; by design.
- **Supply's trade and production rows are all held** in `site/data/supply.json` (built 10 October): every one has its latest, its year-ago and its five-year figures, except five LNG terminals that are too new for five years (Plaquemines and four more) and the cleared energy of NYISO and SPP (the open ruling 51 of the morning note). Its burn rows that are blank are EIA-930's own blanks.

## Not held on /board, each with its source and terms

| Rows | Why blank | The source that would fill it | Terms |
|---|---|---|---|
| PJM: 5 hubs by 2 markets, the spark row, reserves (12) | licensed | PJM Data Miner | PJM's data license and an account |
| MISO: 8 hubs by 2 markets, the spark row, reserves (18) | paused | MISO | its terms forbid automated access (`docs/methods/miso_pause.md`) |
| ISO-NE reserves (1) | held internal | ISO-NE | terms under review |
| California and RGGI carbon auctions (2) | held internal | CARB, RGGI | terms under review |
| Henry Hub, WTI, RBOB, heating oil futures 1 to 4 (4 rows, 4 curves) | licensed after 5 Apr 2024 | CME Group | CME's market data license |
| Waha, SoCal, Algonquin, Chicago gas hubs (4) | licensed | Platts or NGI daily indices | vendor license |
| TTF, JKM (2) | licensed | ICE Endex or LSEG; Platts | vendor license (the IMF's monthly averages are held) |
| Coal spot, five basins (5) | licensed | S&P Global | EIA says the history is proprietary |
| Uranium, lithium daily (2) | licensed | UxC or TradeTech; Fastmarkets or Benchmark | vendor license (the IMF's monthly uranium is held) |
| EUA, RECs (2) | licensed | ICE Endex; S&P Global or ICE | vendor license. EEX posts its EUA primary auction results; its terms are unread: a ruling (3) |
| Capacity prices (1) | held internal | each operator | terms under review |
| Energy equities (1) | licensed | an exchange data vendor | vendor license |

## The refresh

- `page_keep.py board` under the data lock, 18:27 UTC: 794 rows, 740 with values, all 794 from this build, none kept; 71 files changed. ERCOT: 36 rows moved from 7 and 8 October to 13 and 14 October (the spark spreads to 10 October). No other row's date moved.
- Tests: `tests.test_session132`, `test_session240`, `test_session248` (the board's): 58, OK. `test-board.mjs`: fails at its top-twelve freshness check, identically on main (Henry Hub 6 October).

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py --what "session 284"` | 0 | six of six |
| `scripts/freeze.py status` | 0 | no freeze |
| `page_keep.py board` (under `lock.py run`) | 0 | above |
| `bash -n` and `run_data_machine.sh --check` | 0 | the step is listed |
| `tests.test_session284` | 0 | 5 tests |
| the tests of the data machine's run (149, 181, 185, 190, 204, 206, 244, 247, 271, 277) | 1, then 0 | one error in `test_session244` run in that order (an import of `build_coverage`); alone it passes, 16 tests |
| the whole suite | see the landing | |

## Decisions made without you

1. **The board is gated on this machine by its Python tests, not its node test.** The node test's newest-week check of the top twelve fails whenever EIA posts its spot prices late (as today), and would put back an ERCOT refresh that has nothing to do with EIA.
2. **The board files built tonight go in with the landing**, on the task branch, rather than by a direct commit to main: one deploy, with its snapshots.
3. **No NYISO or SPP schedule was added**, though their reserve prices have none: the chain's rule forbids asking them, and a schedule is a standing request.
4. **Supply was not rebuilt:** every table it reads is at its publisher's date; the runner's Saturday build is the next.

## For Samuel's ruling

1. NYISO's and SPP's day-ahead reserve prices (`nyiso_as_prices`, `spp_as_prices`): no run refreshes them. A daily step on this machine, once their publishers' terms are read?
2. `site/scripts/test-board.mjs`, the top twelve "within a week of the build": allow EIA's weekly posting (8 to 10 days), or leave it failing when EIA is late?
3. EUA: read EEX's terms for its primary auction results, which would fill one board row by the auction day?

## Files

- Changed: `warehouse/run_data_machine.sh` (the step, the group, the paths), `docs/machines.md`, `docs/methods/price_board.md`, `site/data/board.json` and 70 files under `site/public/board/` (the build).
- New: `tests/test_session284.py`, this report.
- On this machine, not in git: `runs/session284/`.
