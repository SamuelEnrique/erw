# Session 670 report: large-load tariffs: the connector, nothing pulled

22 October 2026, on lab-desktop (the data machine), a session of `queue/done/043-night-23-october-data-redivis-gaps.md`. Model spend USD 0.

## Read these first

- **No `OPENEI_API_KEY` on this machine, so nothing was pulled** and `utility_large_load_tariffs` is not written, as the chain foresaw. OpenEI's data is public (CC0, session 666).
- **The connector is written and tested:** `warehouse/connectors/openei_large_load_tariffs.py` asks URDB's API by sector (Industrial and Commercial, 500 rates a page, within a ceiling of 400), keeps approved rates with a minimum demand of 1 MW or more of a utility that `utility_service_territories` lists in the seven grids' states, and writes the energy charge (USD/MWh, the hour-weighted mean over URDB's weekday and weekend schedules), the demand charge (USD/kW-month), the fixed charge, the minimum demand and `all_in_300mw` (USD/MWh) = energy + demand * 1000 / 730 + fixed / (300 * 730). Never the bulk CSV, which OpenEI's robots file refuses.
- **It has not met the API.** "A saved sample of ten rates" could not be saved without a key; the tests (`tests/test_session670.py`, 6) use rates built in the API's documented form. Its first run with a key is a trial (`--out-dir`) read against three utilities' rate pages.
- The cross-check against the large-load rules' saved rate pages waits for the table.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.openei.org | 0 of 400 | no key |

## Decisions made without you

- The pull pages by sector rather than asking utility by utility, so the requests do not grow with the utilities (thousands in the seven grids' states).
- A rate whose energy tiers are not in kWh, or whose schedule names a period with no rate, gets no energy figure and no all-in figure; nothing is estimated.

## For Samuel's ruling

- An OpenEI (NREL developer network) API key in this machine's `.env` as `OPENEI_API_KEY`.

## Files

- New: `warehouse/connectors/openei_large_load_tariffs.py`, `tests/test_session670.py`, this report.
