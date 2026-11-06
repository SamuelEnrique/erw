# ERCOT's seasonal load, capacity and reserve margin (Capacity, Demand and Reserves report)

Energy Research Warehouse (ERW), method note written in session 862 (chain 046) for a table first written on 23 October 2026.

Tables: `ercot_cdr_reserve_margins`

## Publisher and address

Electric Reliability Council of Texas (ERCOT), Capacity, Demand and Reserves Report (CDR). The connector reads ERCOT's
resource adequacy page, `https://www.ercot.com/gridinfo/resource`, and takes the newest CDR workbook it links, by the
date in its address. When written:
`https://www.ercot.com/files/docs/2025/12/19/CapacityDemandandReservesReport_December2025.xlsx`. The sheet read is
"Seasonal Summary". Connector: `warehouse/connectors/ercot_cdr.py` (session 851).

ERCOT's robots file (read by session 850) disallows `/misapp` and `/misdownload`. This report comes from `/gridinfo/` (the
page) and `/files/docs/` (the workbook), which it allows.

## Vintage and revision

The December 2025 report, posted 19 December 2025 (`vintage` 2025-12-19, the date in the file's address). Retrieved
2026-10-23T01:40:30Z. A snapshot: each run replaces the table whole with the newest report the page links, so an earlier
edition is not kept. Ceiling two requests a run (the page and the workbook; a workbook saved in `warehouse/raw/ercot_cdr/`
is reused). Session 851 made 4 of its 6 requests (the probe's page and workbook, then the trial's, which the write reused).

## Shape and variables

Series. `entity` `ercot_cdr:<season>:<peak_load | peak_net_load>`: each season at ERCOT's peak load hour and at its peak
net load hour. `freq` `P3M`; `geo` `US-TX`; `market` `ercot`; `node` ERCOT's season and hour as printed (for example
"Summer 2026, peak load hour 17"); `x_hour` the hour ending ERCOT names; `x_report` the file name.

How seasons are dated: each season's row is dated at its first day, 00:00:00Z. Spring is 1 March, summer 1 June, fall
1 September, and winter 1 December of its first year (winter 2026/2027 is 2026-12-01). The hours ERCOT names (hour ending):
summer 17 and 21, fall 17 and 20, winter 8 and 19, spring 17 and 21 (peak load hour first, peak net load hour second).

Units: every variable is MW as ERCOT prints it, except `reserve_margin`, which is pct (ERCOT's fraction times 100). ERCOT
defines it as total capacity less firm peak load, over firm peak load. The `less_` variables are the adjustments the sheet
marks "less:". A row label the connector's map does not know stops the run, so a changed report is never misread. A cell
ERCOT leaves empty has no row.

The 40 variables, by the sheet's section:

Load forecast and adjustments (11, MW): `total_seasonal_load`, `less_rooftop_pv`, `less_load_resources_rrs`,
`less_load_resources_nonspin`, `less_load_resources_ecrs`, `less_controllable_load`, `less_emergency_response_service`,
`less_tdsp_load_management`, `less_voltage_reduction`, `firm_peak_load`, `energy_efficiency_savings`.

Operational generation capacity (17, MW): `operational_thermal`, `operational_hydro`, `operational_switchable`,
`operational_less_switchable_unavailable`, `operational_mothballed`, `operational_private_use_networks`,
`operational_coastal_wind`, `operational_panhandle_wind`, `operational_other_wind`, `operational_far_west_solar`,
`operational_west_solar`, `operational_other_solar`, `operational_storage`, `operational_rmr`,
`operational_pending_retirement`, `operational_total`, `dc_ties` (ERCOT's non-synchronous ties).

Planned resource additions (10, MW): `planned_thermal`, `planned_coastal_wind`, `planned_panhandle_wind`,
`planned_other_wind`, `planned_far_west_solar`, `planned_west_solar`, `planned_other_solar`, `planned_storage`,
`planned_unconfirmed_retirements`, `planned_total`.

Totals (2): `total_capacity` (MW), `reserve_margin` (pct).

Wind, solar and storage are counted at ERCOT's ELCCs, not at nameplate.

When written: 1,600 rows; 8 entities (4 seasons, 2 hours each); 20 seasons, summer, fall, winter and spring of 2026 to
2030 (`ts_utc` 2026-03-01 to 2030-12-01); 40 variables in every season and hour (8 x 5 x 40).

## License

Public: ERCOT's terms (record 2 of the license reads, `docs/licenses.md`) let raw data from public portions of the site be
used, reproduced and redistributed in compilations, charts and analyses. Verdict in `docs/licenses.md`: public. Cite
"ERCOT, Capacity, Demand and Reserves Report".

## Cross-check (session 851)

- In every one of the 40 columns, ERCOT's own arithmetic holds in the table to the rounding of the sheet: the reserve
  margin recomputed from total capacity and firm peak load; the firm peak load from the forecast and its adjustments;
  each total from its parts.
- The summer 2026 normal-weather load (95,419 MW) is 1.14 times EIA-930's 2025 ERCOT peak (83,597 MW,
  `grid_peak_vs_capacity`).
- The capacity the CDR counts in summer 2026 (104,850 MW) is 0.64 of the nameplate `grid_peak_vs_capacity` lists
  (164,685 MW). The difference is the ELCC derating of wind, solar and storage.
- What it says: the summer reserve margin at the peak load hour is 18.3 percent in 2026, 11.4 in 2027, then -1.3 in
  2028, -5.8 in 2029 and -12.7 in 2030.

## What it does not hold

- ERCOT's "Difference" columns (the two hours' difference), left out.
- Only the "Seasonal Summary" sheet is read; the workbook's other sheets are not taken.
- Only the newest edition: earlier CDR reports are not kept, so a forecast's change between editions is not in the table.
- Nameplate capacity (see `grid_peak_vs_capacity`) and NERC's reserve margins.
