# Northern Ireland's electricity a month (DfE's Electricity Consumption and Renewable Generation, figures 6 to 9)

Energy Research Warehouse (ERW), method note written in session 2544 (chain 124) for a table first written on 24 October 2026 (session 2544).

Tables: `dfe_ni_electricity_monthly`

## Publisher and address

The Department for the Economy (DfE), Northern Ireland, its report "Electricity Consumption and Renewable Generation in Northern Ireland", April 2025 to March 2026 (published 4 June 2026), hosted by NISRA: `https://datavis.nisra.gov.uk/Economy/electricity-consumption-and-renewable-generation-report.html`, the document of DfE's publication page. One GET, no key. Source id `dfe_ni:electricity_consumption_renewable_generation_2026`. Connector: `warehouse/connectors/dfe_ni_electricity.py` (session 2544). datavis.nisra.gov.uk serves an "Unavailable" page at its robots address (read 1011); www.economy-ni.gov.uk's robots file asks ClaudeBot for a crawl delay of 5 seconds, which is kept (read 1009).

## Vintage and revision

January 2018 to June 2026, written by run `20261024T215950Z` (the write under the lock, offline), which read the page saved at 2026-10-24T21:58:24Z (5.2 MB). `vintage` is its last-modified time, 2026-09-03T08:30:10Z. Each release replaces the report at the same address, so a run with `--fresh` takes the newest months.

## Shape and variables

Series, 1,326 rows, 9 entities, 102 months. `entity` `dfe_ni:gb-nir:<item>`; `unit` MWh (DfE's whole GWh times 1,000); `ts_utc` the month's first day; `freq` P1M; `geo` GB-NIR; `node` DfE's column header; `x_figure` the figure's link text.

| `variable` | Items | April 2025 to March 2026, GWh |
|---|---|---|
| `renewable_generation` | total; wind, hydro_tidal, bioenergy, landfill_gas, solar | 4,264 |
| `non_renewable_generation` | total; coal, gas, distillate_other | 3,938 |
| `imports`, `exports`, `net_imports` | total (exports written positive) | 2,500, 1,882, 615 |

The totals hold their parts: a sum over entities takes one level.

## Reading the source

- The run stops at once, asking nothing, while `dfe_ni_electricity` or datavis.nisra.gov.uk is paused.
- One request a run (timeout 180 seconds, a pause of 5 seconds); `--offline` reads the saved page.
- **The figures' data:** each figure's CSV is written into the page as a link to a `data:text/csv;base64,` address, the link's text naming it ("Figure 6.CSV"). Each is decoded: UTF-16 characters with one-byte line ends, so the zero bytes are dropped (the text is ASCII), then read as CSV.
- **Taken by header, not number:** the four monthly figures, whose headers after "Date" are the map's (renewables by type; the two generation totals; fossil fuels; imports, exports, net imports). Figures 1 to 5 (shares and rolling twelve-month sums) and 10 (one month's flows) are passed over.
- **Sums:** each month's types to the renewable total and its fuels to the non-renewable total within 2 GWh; imports less exports to net imports within 1 GWh.
- The run stops, and no file is written, for: no CSV in the page, a figure not found, two figures of one header, a row of another form, a gap between months, a figure that is not a whole number, a key given twice, a sum missed.

Nothing is filled.

## License

Public. DfE's Crown copyright page (read 1013): "You may use and re-use the information featured on this website (not including logos) free of charge in any format or medium, under the terms of the Open Government Licence", the source acknowledged and no official endorsement suggested. Verdict (session 2544): may be public. The header acknowledges DfE and the licence and states the scaling and the sign of exports. Held from the live set; in the release package and the next Stanford draft.

## Cross-checks (session 2544)

- The twelve months April 2025 to March 2026 against DfE's own headline for the year: renewable generation 4,264 GWh in both; non-renewable 3,938 GWh, the report's rolling figure; net imports 615 GWh against the headline's 616 (each month rounded).

## What it does not hold

- Gross final consumption and the renewable share (the rolling figures); the monthly flows by interconnector (Ireland, Great Britain), given for one month only; prices (GBP).
