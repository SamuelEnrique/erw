# Session 550 report: interstate natural gas movements

21 October 2026, from 22:03 UTC, on lab-desktop (the data machine), a session of `queue/done/030-night-22-october-sources.md`, run while chain 029's landing waited for its checks. Model spend USD 0.

## Read these first

- **`warehouse/connectors/eia_gas_interstate.py`: interstate and international natural gas movements by state, a year**, from EIA's API v2 (route `natural-gas/move/ist`, the Natural Gas Annual), as `eia_gas_interstate_annual`.
  - 29,470 rows: 1,903 series, 1997 to 2024, in `MMcf`.
  - Nine processes: net receipts, deliveries, receipts, net across borders, exports and imports in transit, and their combined forms.
  - EIA codes each movement as a pair of areas (`SAL-SFL`, Alabama to Florida; `Z0R` a state's own total). The pair is kept in the entity, the first area gives the geo, and the node is EIA's name, which names both areas.
- **A repeat in EIA's data, handled**: Louisiana's 2016 net receipts from the United Arab Emirates appear under two series ids (NA1290_SLA-NTC_2 and NGM_EPG0_IMB_SLA-NTC_MMCF) with one value.
  - The first trial stopped on the repeated key, with nothing written.
  - The connector now keeps a row repeated with the same value once (3 such rows in all), and still stops if the same key comes with two values.
- **Cross-check, an order of magnitude** (`runs/s550/crosscheck.py` on the data machine): each state's net receipts (interstate and across borders) against its consumption (SEDS NGTCB, at 1.036 TBtu per thousand MMcf) less its marketed production (session 528), 2010 to 2022.
  - 653 state-years, 51 states: correlation 0.991, the same sign in 98.2%.
  - Storage, fuel and losses lie between the two, so the check reads the relation only.
- **Held** from `/data` and Redivis v1. Sector rule (`gas`). Tests: `tests/test_session550.py`, 5.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 7 of 20 | a 2024 page (the probe); the first trial (4, stopped on the repeat); the second (2 more) |

## Files

- New: `warehouse/connectors/eia_gas_interstate.py`, `tests/test_session550.py`, this report. Changed: the shared metadata, holds and package.
