# The grid network's links: each pair of balancing authorities once an hour, the latest week (ERW derived, from Form EIA-930)

Energy Research Warehouse (ERW), method note written in session 2228 (chain 099) for a table first written on 1 October 2026 (session 49).

Tables: `grid_network_links`

The page that draws it, the sign check of the source and the published cross-checks are in `docs/methods/grid_network.md` (session 49 on); this note describes the code and the rows as they stand.

## Publisher and address

No publisher is asked by the builder. The one input of the links is `eia930_all_interchange`: U.S. Energy Information Administration (EIA), Form EIA-930, Hourly Electric Grid Monitor (`https://www.eia.gov/electricity/gridmonitor/`), API v2 route `electricity/rto/interchange-data` (`https://api.eia.gov/v2/electricity/rto/interchange-data/`), source id `eia:electricity/rto/interchange-data`, pulled by `warehouse/connectors/eia930_interchange.py`. Builder: `warehouse/derived/grid_network.py` (session 49), which writes `grid_network_nodes` and `site/data/grid_network.json` in the same run. Source id `erw:grid_network`; `source_url` on every row is `https://github.com/SamuelEnrique/erw/blob/main/docs/methods/grid_network.md`. The header's "Derived from" line names `eia930_all_interchange`, `eia930_all_demand` and `carbon_intensity_hourly`; the last two feed the nodes only.

## Vintage and revision

A rolling snapshot: the daily run (`warehouse/run_daily.sh`, step `grid_network`) deletes the file and writes it whole. The hourly network workflow (`network_hourly.py`) writes only the Storage object, never this table (`grid_network.md`, "What refreshes hourly, and what daily").

The file on the data machine was rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261023T152740Z-github` (its first header line); the builder's header that follows names run `20261023T143657Z`. Its window line reads "168 hours, 2026-10-15T00:00:00Z to 2026-10-22T00:00:00Z"; the rows hold 144 of those hours, 2026-10-16T00:00:00Z to 2026-10-21T23:00:00Z, as its "File holds" line says. The 24 hours of 15 October have no report: `eia930_all_interchange` on the data machine holds no hour of 14 or 15 October 2026 (48 hours missing between 13 September and 21 October), and the code writes a row only for a pair and hour with a report.

The builder gives every row the run's own time; in the restored file 3,773 rows carry 2026-10-23T14:36:57Z and the rest five earlier times:

| `retrieved_at` | Rows |
|---|---|
| 2026-10-19T14:49:30Z | 4,218 |
| 2026-10-19T20:17:14Z | 3,293 |
| 2026-10-20T05:50:23Z | 25 |
| 2026-10-21T14:34:56Z | 7,462 |
| 2026-10-22T14:33:54Z | 3,837 |
| 2026-10-23T14:36:57Z | 3,773 |

`vintage` is empty. EIA revises EIA-930 after first publication; the links follow whatever `eia930_all_interchange` holds at the build.

## Shape and variables

Series, 22,608 rows: 157 pairs of 70 balancing authorities, each pair in all 144 hours and all 157 pairs in every hour. `entity` `eia930:<A>-<B>`, A the code that sorts first; `variable` flow_mw; `unit` MW; `freq` PT1H; `ts_utc` the hour's start, UTC; `geo`, `market` and `node` empty. Extra columns: `ba` (A, lowercase; the partition column) and `x_to_ba` (B, lowercase). The value is positive when A exported to B. 1,659 rows are 0.

The six pairs with the largest mean absolute flow over the 144 hours:

| Pair | Mean flow, MW | Lowest | Highest |
|---|---|---|---|
| AZPS-SRP | -3,306.3 | -4,255 | -2,529 |
| MISO-TVA | 2,061.7 | 144 | 3,261 |
| NYIS-PJM | -1,703.8 | -2,737 | -291 |
| BPAT-PSEI | 1,633.6 | 983 | 2,233 |
| CISO-NEVP | -1,429.7 | -1,832 | -1,008 |
| BCHA-BPAT | 1,355.3 | 51 | 2,265 |

A negative mean is a flow from B to A: from SRP to AZPS, PJM to NYIS, NEVP to CISO.

## Reading the source

- The builder reads `eia930_all_interchange` in `warehouse/output` (entity, ts_utc, value, ba, x_to_ba), past its `#` lines. The window ends one hour after the newest hour it holds and starts `HOURS` (168) hours before.
- Every report whose reporter or neighbour is one of EIA's regions or country totals (`REGIONS`: CAL, CAN, CAR, CENT, FLA, MEX, MIDA, MIDW, NE, NW, NY, SE, SW, TEN, TEX, US48) is left out and counted in the log.
- The pair rule: the reports are sorted by pair, hour and whether the reporter is A, and the last kept, so A's report is read when it exists (as reported) and B's otherwise (sign flipped).
- A row is written for each pair and hour with a report; nothing is filled.
- Any error stops the build: the log holds the traceback, `run_status` gets one failed row (it names `grid_network_nodes`), and the exit is 1.
- No request is made to any publisher, so neither `iso_prices.paused()` nor `paused_host()` is asked. The option `--nodes-from-supabase` reads the live set, for the nodes only.
- The code counts no row ceiling.

## License

Public. The header: "License: public. A derived table inherits the most restrictive license of its inputs (Decision 23)." `sources.csv` flags `erw:grid_network` public (tables `grid_network_links`, `grid_network_nodes`) and `eia:electricity/rto/interchange-data` public. `license_tables.csv` lists the table under EIA, "the source registry and the tables its header derives it from: carbon_intensity_hourly, eia930_all_demand, eia930_all_interchange". `license_verdicts.csv` records EIA, read 1: "may be public", for public and for commercial use. The sentence: "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service." EIA asks for the acknowledgment "Source: U.S. Energy Information Administration" with the date. `docs/licenses.md` (line 802): may be public, and the flag agrees.

## Cross-checks (session 2228)

- Every row's A sorts before its B, `ba` is A and `x_to_ba` is B in lowercase, no code is one of the 16 regions, and no key (entity, variable, ts_utc) appears twice.
- Against `eia930_all_interchange` on the data machine, the pair rule recomputed for the 144 hours: the same 22,608 pairs and hours, none on one side only. 20,976 are read from A's report and 1,632 from B's, sign flipped. 22,598 values agree within 0.05 MW. The other 10 are DUK-SEPA on 17 October 2026, 1 or 2 MW apart, all among the rows that carry 2026-10-19T20:17:14Z: the input now holds other values for those hours than the build read.
- The two reports of one pair against each other, where both reported (19,824 pairs and hours): 13,929 agree within 1 MW; the median gap is 0 and the 90th percentile 143.7 MW. The table carries one side only, by the pair rule.
- Scripts: `links_check.py`, `links_check2.py` and `gaps.py` in the session's scratchpad.

## What it does not hold

- Hours before the window: the table holds one week at most (`HOURS`, 168).
- EIA's regions and country totals, whose interchange repeats their balancing authorities'.
- Hours neither side of a pair reported, 14 and 15 October 2026 among them.
