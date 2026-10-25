# Bosnia and Herzegovina's electricity by utility, a year (DERK's report on activities 2025, Annex C)

Energy Research Warehouse (ERW), method note written in session 2555 (chain 125) for a table first written on 24 October 2026 (session 2547).

Tables: `derk_bih_electricity_annual`

## Publisher and address

The State Electricity Regulatory Commission of Bosnia and Herzegovina (DERK; in English SERC), Annex C of its report on activities for 2025, "Balance Values of the Electric Power Sector of Bosnia and Herzegovina" (one page, in English): `https://www.derk.ba/DocumentsPDFs/Osnovni_EES_pokazatelji_BiH_en.pdf`. One GET, no key. Source id `derk:annex_c_balance_2025`. Connector: `warehouse/connectors/derk_bih_electricity.py` (session 2547). www.derk.ba's robots file closes Joomla's own folders only (read 1021).

## Vintage and revision

2021 to 2025, written by run `20261024T225844Z` (the write under the lock, offline), which read the annex saved at 2026-10-24T22:55:05Z. `vintage` is its last-modified time, 2026-07-10T12:52:11Z. Each year's report has its own annex at its own address; this address holds the 2025 report's.

## Shape and variables

Series, 214 rows, 6 entities. `entity` `derk:ba:<utility>`: `ep_bih` (Elektroprivreda BiH), `ers` (Elektroprivreda Republike Srpske), `ep_hzhb` (Elektroprivreda HZ HB), `komunalno_brcko`, `other_entities`, `total` (the BIH column); `unit` MWh (DERK's GWh, to two decimals, times 1,000); `ts_utc` the year's first day; `freq` P1Y; `geo` BA; `node` and `x_label` DERK's row label.

| `variable` | What | 2025, TWh (BIH) |
|---|---|---|
| `generation_hydro`, `generation_thermal`, `generation_solar_wind`, `generation_small_industrial` | generation by plant type (larger solar and wind plants; small and industrial plants) | 4.433, 7.934, 1.123, 1.051 |
| `generation` | the four together | 14.540 |
| `consumption_distribution` | customers connected to the distribution network | 11.252 |
| `transmission_losses` | in the BIH column only | 0.350 |
| `consumption_large_customers` | large customers | 0.650 |
| `self_consumption_pumping` | plants' self-consumption and pumping | 0.078 |
| `consumption` | the four together | 12.330 |

A utility with no figure in a cell (EP HZHB has no thermal plant, Komunalno Brcko generates nothing) has no row. The BIH column equals the sum of the utilities, and BIH's consumption holds the transmission losses as well: a sum over entities takes `total` or the utilities, never both.

## Reading the source

- The run stops at once, asking nothing, while `derk_ba` or www.derk.ba is paused.
- One request a run (timeout 180 seconds); `--offline` reads the saved annex.
- **The page:** the one whose text holds "Balance Values of the Electric Power Sector". Its five blocks are each headed "Year YYYY" and the six columns.
- **By place, not by text:** a cell may be empty, so the page's text cannot tell the columns apart. Each block's heading words ("BIH" of EP BIH, "ERS", "HZHB", "Brcko" of Komunalno Brcko, "entities" of Other entities, and the last "BIH") give the columns' right edges; a figure (right-aligned) goes to the nearest; the words left of the first column make the label. A block runs to 8 points above the next block's "Year" line, so a row between two blocks stops the run rather than being passed over; a line with no figure-shaped word (a heading's second line, the page's footer) is passed over.
- **Sums:** each BIH figure within 0.05 GWh of the utilities' sum (its consumption with the transmission losses); each utility's generation and consumption within 0.05 GWh of their parts.
- The run stops, and no file is written, for: no year block, a heading not found or out of order, a row not in the map, a row missing, two figures under one column, a figure of another form, a key given twice, a sum missed.

Nothing is filled.

## License

Internal. DERK's English home page states "DERK (c) 2004-2026. All Rights Reserved." and gives no terms of reuse (read 1022). Verdict (session 2551): needs written permission. Held from the live set and from Redivis.

## Cross-checks (session 2547)

- `eia_world_electricity_annual`, Bosnia and Herzegovina, 2024: DERK's consumption 12.131 TWh against EIA's 12.052 (99.3%); DERK's generation 14.554 TWh against EIA's 15.716.

## What it does not hold

- Years before 2021 (earlier annexes); months; trade with neighbours (not in the annex); prices (BAM).
