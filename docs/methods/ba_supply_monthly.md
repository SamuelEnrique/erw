# Who supplies a grid: each balancing authority's net imports by neighbour and month

Energy Research Warehouse (ERW), method note written in session 2578 (chain 127) for a derived table first written in session 68. The method itself is the section "Who supplies a grid (session 68)" of [`grid_network.md`](grid_network.md); this note names the table, gives its shape as held, and points there.

Tables: `ba_supply_monthly`

## Builder and inputs

`warehouse/derived/ba_supply.py` (session 68), run by hand: no workflow, `run_daily.sh` or other builder runs it (searched on 25 October 2026; `network_daily.py` imports only its screening rule), and its last run was on 2 October 2026. Inputs: the ERW's EIA-930 daily interchange (`eia930_daily_interchange`), EIA's own total interchange (`eia930_daily_total_interchange`), and demand and net generation for the seven ISO balancing authorities. No request is made. Source id `erw:ba_supply`.

## What a row is

Series, partitioned by `ba`. A month's days are EIA's Eastern days. Positive always means the neighbour supplied the balancing authority (a net import); EIA's own sign is flipped once, in the builder.

- **Pair rows** (entity `eia930:<BA>-<NEIGHBOUR>`, `x_to_ba` the neighbour): `net_import_mwh`, `net_import_share_pct`, `neighbor_report_mwh`, `neighbor_report_days`.
- **Balancing-authority rows** (entity `eia930:<BA>`): the three measures of total net imports side by side (`net_import_pairs_mwh`, `net_import_total_interchange_mwh`, `net_import_balance_mwh`) and their shares of demand; EIA's total interchange and the balance over every day they cover; `demand_mwh`; `days_held`, `days_left_out`, `days_in_month` and `thin_month` (1 when fewer than two thirds of the month's days are held).
- Units: MWh, `pct`, or `count` (days); `freq` P1M; `ts_utc` the month's first day at 00:00:00Z.

## Held days

A day counts for a balancing authority when every regular neighbour reported it (one that reports on at least half of the month's days with any report) and none of its pair-days was screened out; a pair-day is screened out when it lies further than 10 median absolute deviations (at least 500 MWh) from the pair's own median over its history. Nothing is filled: a day left out is counted, and a month with no held day has no flow row. Demand and net generation, and so the shares, exist for the seven ISO balancing authorities only.

## As held on 25 October 2026

Run `20261002T230348Z`, counted by code from the table read past its header lines: 158,503 rows, January 2019 to September 2026; 473 entities (83 balancing authorities, 390 pairs); 31,620 pair-months of `net_import_mwh` and 4,293 of its share; 7,455 balancing-authority months, 630 of them thin. Units: 84,537 rows in MWh, 67,769 counts, 6,197 percentages.

## License

Public, as its inputs (EIA's public domain data). Read by the site's Gravity tab (`site/lib/basupply.ts`), as `grid_network.md` describes.
