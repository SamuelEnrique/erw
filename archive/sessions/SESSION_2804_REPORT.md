# Session 2804 report: European EV recharging infrastructure (Eurostat, road_if_rchev), the third own choice (run before 2801)

26 October 2026, from about 03:30 to 03:35 UTC, on lab-desktop (the data machine), chain 142, unattended. Precheck passed (`runs/c142/pre2804.out`). Model spend USD 0. Pulls: 3 of 20. Run before session 2801, as file 142 asks, so that 2801's notes and draft take this table.

## Read these first

- **`eurostat_ev_recharging_annual` is new:** Eurostat's electric vehicle recharging pools, stations and points and their power output (road_if_rchev), each European country's public recharging infrastructure a year, 2019 to 2025. 465 rows, 33 areas, 6 variables:
  - points, stations, pools and heavy-duty pools as counts;
  - the pools' and the heavy-duty pools' power output in MW (Eurostat's kW divided by 1,000).

  The table has been written, validated, archived and put in coverage. It is held from the live set and from Redivis storage until session 2801's draft.
- **Why this source:** EV charging is a load the ERW follows for the US by state (`afdc_ev_charging_state_annual`, session 2155) and holds for no other country. Session 2799's reading of Eurostat's dataflow list found it unheld; no connector, method note, source row or unlanded chain names it.
- **Coverage grows by year:** recharging points are given by 9 countries in 2019 and 31 in 2025. The other measures are given by fewer: pools' power by 27 countries, pools by 21, stations by 20 and the heavy-duty items by 9.
- **The largest numbers of points in 2025:**
  - the Netherlands 209,513;
  - France 185,501;
  - Belgium 106,500, down from 111,500 in 2024, as published;
  - Italy 66,501.

  Germany gives 2019 to 2024 only: 163,410 points in 2024.
- **Pools' power in 2024:** Germany 6,212 MW over 52,020 pools (119 kW a pool); Turkey 1,736 MW (168 kW a pool); Finland 1,100 MW (363 kW a pool).
- **Kept as published:**
  - 29 zeros, all of heavy-duty pools: Estonia before 2023, North Macedonia, Malta, and Greece's heavy-duty power in 2023;
  - 36 observations flagged `i` (see Eurostat's metadata), in `x_flag`;
  - 2 blanks, with no row;
  - the United Kingdom, left out.
- **No cross-check against a held table:** the ERW holds no European recharging count. The checks are the codelist's names, each type read only in its expected units, and no negative or doubled key.

## The requests

1. **ec.europa.eu's robots file (read 1599):** byte for byte session 2799's.
2. **road_if_rchev,** the whole dataset (36 KB).
3. **The TRA_INFR codelist:** the four recharging types' names, which the connector reads on each run.

## Decisions made without you

- **The year as `ts_utc`'s 1 January**, as the ERW's other annual Eurostat tables write it. Eurostat's figures are counts for the year it names; the note says the ERW does not read them as a 1 January stock.
- **kW written as MW,** the ERW's power unit.

## For Samuel's ruling

- None.

## Files

- New:
  - `warehouse/connectors/eurostat_ev_recharging.py`
  - `tests/test_session2804.py` (4 tests, passing)
  - this report
- Changed: the table's registration and holds, the license record, coverage, sources, the archive manifest and the release v1 records.
- On the data machine only: `runs/c142/s2804/`.
