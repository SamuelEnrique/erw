# Slovenia's transmission network, production and take-over an hour from 2021 (ELES)

Energy Research Warehouse (ERW), method note written in session 2829 (chain 144) for a table first written on 26 October 2026 (session 2822).

Tables: `eles_slovenia_hourly`

## Publisher and address

ELES, d.o.o., Slovenia's transmission system operator. Its page "Prevzem in proizvodnja" (`https://www.eles.si/prevzem-in-proizvodnja`) shows the production and take-over on the transmission network, and its CSV export gives them an hour. The page is an ASP.NET form, so the connector makes two requests:
- a GET of the page, for its form fields;
- a POST of the form with `__EVENTTARGET` `dnn$ctr1215$View$ctl00$btn_exportCSV`, `pckDateFrom` 01.01.2021 and `pckDateTo` the last ended day. The answer is `Seznam.csv`.

Source id `eles:prevzem_in_proizvodnja`. Connector: `warehouse/connectors/eles_slovenia_hourly.py` (session 2822), whose raw store is `warehouse/raw/eles_slovenia/`. The raw capture saves both answers under the page's address, and offline the connector takes the newest saved answer that is the CSV. www.eles.si's robots file (read 1639) disallows `/admin/`, `/Portals/` and the site's code paths, not this page, and names no Claude agent.

## Vintage and revision

Written by run `20261026T064655Z` (offline), which read the export retrieved at 2026-10-26T06:45:06Z, from 1 January 2021 to 25 October 2026. Only days ended at the retrieval, in Ljubljana's time, are kept.

## Shape and variables

Series, 356,789 rows, 2,124 days:
- `entity` `eles:si`.
- `variable`: `forecast_generation`, `generation`, `forecast_takeover`, `takeover`, `nuclear_krsko` (NEK, the Krško plant's whole output), `thermal` and `hydro`.
- `unit` MW, the hour's mean, so also the hour's MWh. **The page states no unit;** the figures are MW by their size, and the cross-check confirms it.
- `ts_utc` the hour's start in UTC; `freq` PT1H; `geo` SI; `x_date` and `x_hour` the file's own.

**The page says** (in Slovene):
- since 1 January 2021 ELES publishes the production of producers connected directly to the transmission network, the pumped storage plant Avče included;
- producers on the distribution network (small hydro, solar and others) are not in it;
- Krško's whole output is shown, half of which belongs to Croatia by the two states' treaty.

## Reading the source

- **The time base:**
  - The labels H01 to H24 are local clock hours (Europe/Ljubljana): Hn is the hour from n−1 o'clock.
  - **On the spring change day H03 is skipped** (23 rows).
  - **On the autumn change day H01 to H24 appear once each,** so one of its 25 hours is not given. Its 02:00 hour is read as the first, in summer time. The six autumn days (2021 to 2026) are counted in the header and listed in the run log.
- One blank (25 October 2026's actual production at H24) has no row. Nothing is filled.
- The run stops on an export not the expected CSV (its header), a date or an hour label not readable, a value not a number, or a key given twice.

## License

**Internal.** ELES links no terms of reuse from its pages (read 1640). A web search shows a notice on dac.eles.si, ELES's diagnostic centre's site, allowing non-commercial use only and no copying or redistribution, but that host does not resolve (read 1644). The notice was not read, and no verdict is written. The table waits for ELES's terms or its written permission (session 2825's report).

## Cross-check

Krško's hourly output summed by month (Ljubljana's months) against `eurostat_electricity_monthly`'s Slovenian nuclear net production (`net_production:N9000`), over the 67 whole months both give:

| Measure | Value |
|---|---|
| Median ratio | 1.0000 |
| 10th to 90th percentile | 0.9999 to 1.0000 |
| July 2025 | 505,839 MWh here, 505,828 at Eurostat |

Slovenia's nuclear figure at Eurostat is the plant's whole output too.
