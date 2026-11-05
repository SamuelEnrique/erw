# Session 2822 report: Slovenia's transmission network, production and take-over an hour from 2021 (ELES)

26 October 2026, from about 06:41 to 06:50 UTC, on lab-desktop (the data machine), chain 144, unattended. Precheck passed (`runs/c144/pre2822.out`). Model spend USD 0. Pulls: 6 requests of 15 (2 by the probe, 2 by a trial export, 2 by the connector's online trial); one web search.

## Read these first

- **`eles_slovenia_hourly` is new:** ELES's "Prevzem in proizvodnja", the production and take-over on Slovenia's transmission network, an hour, from 1 January 2021 to 25 October 2026. It comes from the page's CSV export.
  - Seven series: forecast and actual production, forecast and actual take-over, Krško nuclear (NEK, its whole output), thermal and hydro.
  - 356,789 rows, 2,124 days. The table has been written, validated, archived and put in coverage. It is held from the live set and from Redivis storage until session 2829's draft.
- **Its licence is internal:** ELES links no terms of use from its pages (read 1640), so session 2825's licenses round looks for them.
- **How the export is asked for:** the page is an ASP.NET form. The connector reads its fields (one GET), then posts them with the CSV button as the event target and the span from 01.01.2021 to the last ended day (one POST). The raw capture saves both under the page's address, and offline the connector takes the newest saved answer that is the CSV.
- **The page says** (in Slovene) that the figures cover producers connected to the transmission network, the pumped storage plant Avče included, not those on the distribution network (small hydro, solar). Krško's output is shown whole, half of it Croatia's by treaty.
- **The time base** (found here, from the export itself):
  - The labels H01 to H24 are local clock hours (Europe/Ljubljana): Hn is the hour from n−1 o'clock.
  - **On the spring change day H03 is skipped** (23 rows).
  - **On the autumn change day H01 to H24 appear once each,** so one of its 25 hours is not given. Its 02:00 hour is read as the first, in summer time. The six autumn days are counted in the header and listed in the run log.
- **The unit:** the page states none. The figures are MW, the hour's mean, so each is also the hour's MWh. The cross-check confirms it.
- **Cross-check:** Krško's hourly output summed by month against `eurostat_electricity_monthly`'s Slovenian nuclear net production (N9000), over 67 whole months. **The ratio's median is 1.0000** (10th to 90th percentile 0.9999 to 1.0000). July 2025, for one, gives 505,839 MWh here and 505,828 at Eurostat.
- Only days ended at the retrieval are kept; one blank (25 October 2026's actual production at H24) has no row.

## The requests

| n | What | Outcome |
|---|---|---|
| 1 | www.eles.si's robots file | 200, `/Portals/` and code paths closed, not the data pages |
| 2 | the Prevzem in proizvodnja page (probe) | 200, the export form |
| 3, 4 | a trial export, September 2026 (GET, POST) | 200, `Seznam.csv`, 720 hours |
| 5, 6 | the connector's online trial, 2021 to 25 October 2026 (GET, POST) | 200, 2.39 MB |

Reads recorded: 1639 and 1640.

## Decisions made without you

- **The autumn change day's one 02:00 hour read as summer time,** the day counted as 24 of 25 hours.
- **The unit written as MW,** from the figures' size and the Eurostat match, since the page states none.
- **Licence internal** until ELES's terms are read.

## For Samuel's ruling

- None new.

## Files

- New:
  - `warehouse/connectors/eles_slovenia_hourly.py`
  - `tests/test_session2822.py` (4 tests, passing)
  - this report
- Changed:
  - the table's registration and holds;
  - the license record (reads 1639 and 1640) and `docs/licenses.md`;
  - coverage, sources, the archive manifest and the release v1 records.
- On the data machine only:
  - `runs/c144/s2822/` (`try_export.py` and its answer), `runs/license_reads/s2822/`;
  - `warehouse/raw/eles_slovenia/`.
