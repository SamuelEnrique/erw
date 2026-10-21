# Session 546 report: SEDS' other series

21 October 2026, from 21:52 UTC, on lab-desktop (the data machine), the fifth session of `queue/done/029-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`eia_seds_state_energy` now holds 27 series in every state** (it held 13 since session 507): 49,140 rows, 1990 to 2024. The 14 added:
  - electricity's consumption by sector: residential, commercial, industrial and transportation (ESRCB, ESCCB, ESICB, ESACB), in TBtu;
  - natural gas's consumption by sector: residential, commercial, industrial, electric power and transportation (NGRCB, NGCCB, NGICB, NGEIB, NGACB), in TBtu;
  - natural gas's price by sector and for all sectors (NGRCD, NGCCD, NGICD, NGEID, NGTCD), in USD/MMBtu.
- **`eia_seds.py` reuses a saved page**, as the newer connectors do, with `--offline` and `--fresh`. The write after the trial asked nothing.
- **Cross-checks** (`runs/s546/crosscheck.py` on the data machine):

  | Series | Against | State-years | Median |
  |---|---|---|---|
  | gas residential (NGRCB) | `eia_gas_consumption_state_monthly`, residential (session 518), at 1.036 TBtu per thousand MMcf | 1,223 | 0.995 |
  | gas commercial (NGCCB) | the same, commercial | 1,248 | 0.995 |
  | gas industrial (NGICB) | the same, industrial | 1,200 | 1.012; middle half 0.994 to 1.135 |
  | gas electric power (NGEIB) | the same, electric power | 1,143 | 0.994 |
  | electricity residential (ESRCB) | `eia_retail_sales_monthly`, at 3,412 Btu per kWh | 1,247 | 1.0000, all within 1% |
  | electricity commercial (ESCCB) | the same | 1,247 | 1.0000, 91.8% within 1% |
  | electricity industrial (ESICB) | the same | 1,248 | 1.0000, all within 1% |

  Industrial gas runs wider. SEDS counts some gas that EIA's monthly deliveries do not; which part was not established.
- **Written under the data lock** (21:54 UTC) with `--offline` (0 requests). The validator, coverage and archive exited 0 (49,140 rows archived as changed, since every row's address now names the longer list of series). The release row was replaced.
- Tests: `tests/test_session546.py`, 3.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 11 of 20 | the 14 candidates' 2024 page (the probe); the trial (10) |

## Files

- New: `tests/test_session546.py`, this report. Changed: `warehouse/connectors/eia_seds.py`, `docs/redivis/release-v1/`, `docs/coverage.md`, `docs/licenses.md`, `warehouse/metadata/{coverage,archive_manifest,sources,license_tables}.csv`.
