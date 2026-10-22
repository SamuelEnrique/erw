# Session 605 report: one more source; BOEM's lease production probed, EIA's heating fuel prices taken

22 October 2026, from 00:47 UTC, on lab-desktop (the data machine), a session of `queue/done/035-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **BOEM's offshore production by lease (OGOR-B): probed, not pulled.**
  - `www.data.boem.gov`'s robots file disallows only a list of named bad robots, not ours. BOEM's terms are record 86. The files are public: a delimited file a year from 1996, with 2024's last modified on 15 October 2026.
  - The files have no header. Each row is a lease's disposition under one of BOEM's disposition codes, and the field layout and codes are in yearly PDFs.
  - Deciding which codes make a lease's production would be my reading. It is left for a session that reads BOEM's PDF first (`runs/s605/` on the data machine holds the 2024 file and the pages).
- **Taken in its place: EIA's weekly heating oil and propane prices** (route `petroleum/pri/wfr`, the State Heating Oil and Propane Program), which the ERW did not hold (its regional retail prices are diesel and gasoline). `warehouse/connectors/eia_heating_fuel_prices.py` writes `eia_heating_fuel_prices_weekly`.
  - 48,534 rows: 140 series, January 2012 to 19 October 2026.
  - Residential and wholesale prices of No. 2 heating oil and propane, by state, PADD and the U.S., in `USD/gal`.
  - Weeks outside the heating season (October to March) have no rows, as EIA publishes none.
- **Cross-check, internal**: the residential price is above the wholesale price for the same fuel, area and week in 99.9% of 19,582 weeks, with a median margin of 1.058 USD/gal.
- **Written under the data lock** (00:51 UTC) with `--offline` (0 requests). The validator, coverage and archive exited 0. Its metadata met session 604's, and the union resolver kept both, with no duplicate rows. **Held** from `/data` and Redivis v1. Sector rule (`products`). Tests: `tests/test_session605.py`, 5.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.data.boem.gov | 5 | robots file, production page, OGOR-B page, the 2024 file, the field page |
| api.eia.gov | 12 | the route, a March 2026 page, the trial (10) |

In all, 17 of 20.

## For a later session

- BOEM's OGOR-B by lease, after reading BOEM's field and disposition code PDFs.

## Files

- New: `warehouse/connectors/eia_heating_fuel_prices.py`, `tests/test_session605.py`, this report. Changed: the shared metadata, holds and package.
