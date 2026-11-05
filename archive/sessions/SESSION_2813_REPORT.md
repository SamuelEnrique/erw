# Session 2813 report: European EV recharging points by power category (Eurostat, road_if_rchevpow), the second own choice

26 October 2026, from about 05:20 to 05:26 UTC, on lab-desktop (the data machine), chain 143, unattended. Precheck passed (`runs/c143/pre2813.out`). Model spend USD 0. Pulls: 4 of 20 (3 by the probe, 1 by the fetch).

## Read these first

- **`eurostat_ev_recharging_power_annual` is new:** Eurostat's recharging points for electric vehicles by power category (road_if_rchevpow), each European country's public recharging points a year, 2019 to 2025.
  - The breakdown is the total, AC and DC, and seven power bands:
    - AC below 7.4 kW, 7.4 to 22 kW, and above 22 kW;
    - DC below 50 kW, 50 to 150 kW, 150 to 350 kW, and 350 kW and above.
  - 1,171 rows, 33 areas, in counts.
  - The table has been written, validated, archived and put in coverage. It is held from the live set and from Redivis storage until session 2815's draft.
- **Why this source:** session 2804's table (`eurostat_ev_recharging_annual`) holds the points' total. This one says how fast they charge, which is what sizes their load on the grid. Session 2799's reading of Eurostat's dataflow list named it beside road_if_rchev; no connector or chain holds it.
- **Cross-check:** this table's total equals session 2804's recharging points **exactly in all 157 country years** both give.
- **Figures, 2025:**
  - The Netherlands' 209,513 points are 202,611 AC, nearly all 7.4 to 22 kW (200,189), and 6,902 DC, of which 684 are 350 kW and above.
  - The most points at 350 kW and above: France 4,278, Sweden 1,855, Norway 1,673, Austria 1,062, Finland 1,031.
- **The parts against their whole,** exact, in every country year that gives them:
  - the total against AC plus DC: 118 of 138;
  - AC against its bands: 87 of 91;
  - DC against its bands: 85 of 89.

  The others are kept as published and listed in the run log, among them France's total 986 to 1,246 under its parts a year (2021 to 2025) and Germany's total 54 to 159 above its parts (2019 to 2023). Also kept:
  - 98 zeros;
  - the flag `i` in `x_flag`.
- **The bands' names** are the POWER codelist's (read 1624), written in the connector in ASCII.

## The requests

| n | What | Outcome |
|---|---|---|
| 1 | ec.europa.eu's robots file | 200, byte for byte session 2812's |
| 2 | road_if_rchevpow's data (probe, one request, no retry) | 200 |
| 3 | the same, into the connector's raw folder | 200, byte for byte |
| 4 | the POWER codelist (probe) | 200 |

Reads recorded: 1622 to 1624.

## Decisions made without you

- **A table of its own** beside session 2804's, rather than its rows added there: a different dataset and key.

## For Samuel's ruling

- None new.

## Files

- New:
  - `warehouse/connectors/eurostat_ev_recharging_power.py`
  - `tests/test_session2813.py` (4 tests, passing)
  - this report
- Changed:
  - the table's registration and holds;
  - the license record (reads 1622 to 1624) and `docs/licenses.md`;
  - coverage, sources, the archive manifest and the release v1 records.
- On the data machine only:
  - `runs/c143/s2813/`, `runs/license_reads/s2813/`;
  - `warehouse/raw/eurostat_ev_recharging_power/`.
