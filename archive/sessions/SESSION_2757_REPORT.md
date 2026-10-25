# Session 2757 report: European electricity consumption by sector a year (Eurostat's nrg_cb_e), a second own choice; Slovakia closed

25 October 2026, about 22:21 to 22:31 UTC, on lab-desktop (the data machine), chain 139, unattended. Precheck passed (`runs/c139/pre2757.out`). Model spend USD 0. Pulls: 10 requests of 20 (4 by the probe, 6 by the fetch, of which 4 were one refused query retried by `fetch_raw`).

## Read these first

- **A lapse of mine, reported first:** my first data query named a balance item, FC_E, that nrg_cb_e does not carry. Eurostat answered HTTP 400, and `iso_prices.fetch_raw` retried the 400 three times: **4 requests for one refused query**, all within the ceiling. I then asked once with a wildcard for every balance item, which cannot be refused for a code. The lesson is in the memory: ask an SDMX dataflow with a wildcard, or read its codes first.
- **Chosen after the record was read:** before any request, the record showed Statistics Lithuania (Cloudflare), Slovenia's SURS (its robots file names ClaudeBot), the BLS (both hosts refuse the reader) and energy.gov.au (reset) closed by earlier sessions.
- **Slovakia tried again and closed:** datacube.statistics.sk answered 503 (read 1504), and data.statistics.sk timed out as in session 2343 (read 1506). slovak.statistics.sk's robots file disallows `/` to `*`, the ERW's reader, and to Claude-Web (read 1505). It allows ClaudeBot and anthropic-ai by name, which are not this reader. Not asked again.
- **`eurostat_electricity_consumption_annual`, public, held from the live set and in the Stanford holds** (`warehouse/connectors/eurostat_electricity_consumption.py`, 15,667 rows, 40 areas, 1990 to 2025):
  - From nrg_cb_e, "Supply, transformation and consumption of electricity", every balance item of E7000 in GWh in one request (6.2 MB), with the NRG_BAL codelist for the items' names. Eurostat's last update: 22/10/26 23:00.
  - Twelve items, in MWh: available for final consumption (AFC), final consumption (FC), the energy sector's use (NRG_E), losses, statistical differences, and final consumption's energy use by seven sectors (industry, transport, commercial and public services, households, agriculture and forestry, fishing, not elsewhere specified). The file's other 51 items (production and trade, held already; the branches of industry, transport and the energy sector; the loss items' parts) are not written.
  - **Checked:** AFC equals FC plus the statistical difference within 1 GWh in all 1,326 country years; a miss stops the run. **In this dataset FC includes the energy sector's own use:** FC equals NRG_E plus the seven sectors within 1 GWh in 1,260 of 1,289 country years that give all eight. The other 29 (EU27_2020 14, France 14, Austria 2024 by 3,944 GWh) are kept as Eurostat publishes them and listed in the run log. 2025 gives totals without the sectors so far.
  - Countries as `eurostat_electricity_production_annual` keeps them; the United Kingdom, Kosovo and the euro area aggregate are left out. Zeros kept (2,972), no blanks.
- **Cross-check** against `ssb_norway_electricity_monthly` (Statistics Norway's monthly balance, summed over each year's twelve months): Norway's final consumption agrees with SSB's net consumption within 0.1 per cent in 2020 (125,545 against 125,410 GWh) and 0.8 per cent in 2024 (128,971 against 130,068). Households run 1.5 and 4.4 per cent below SSB's (39,884 against 40,483 GWh; 39,054 against 40,856), a difference of definition. SSB's "grid loss and statistical difference" is not Eurostat's losses.
- **Terms:** ec.europa.eu's robots file disallows the old SDMX path, the search pages and two language paths to `*`, and leaves `/eurostat/api/dissemination/` open. It names no Claude agent (read 1507). Eurostat's verdict on record (read 280, session 2123): reuse with the source acknowledged.
- **Written under the data lock:** validated, archived (15,667 rows), in coverage. The patch applied cleanly with no marker. Coverage has 602 tables and `sources.csv` 692 sources, none twice. `finish_table.sh`: the release and license checks pass (602 tables, 0 problems).

## Requests (10 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | datacube.statistics.sk's robots file (its own request) | 503 |
| 2 | slovak.statistics.sk's robots file (its own request) | 200, `Disallow: /` to `*` |
| 3 | data.statistics.sk's robots file (its own request) | timed out |
| 4 | ec.europa.eu's robots file (its own request) | 200 |
| 5 to 8 | nrg_cb_e with nine named items (the fetch, retried) | 400 four times: FC_E not in the dataflow |
| 9 | the NRG_BAL codelist | 200 |
| 10 | nrg_cb_e, every item of E7000 in GWh | 200, 6,179,930 bytes |

Reads recorded: 1504 to 1507.

## Decisions made without you

- **FC kept as Eurostat defines it here** (energy sector included), with the identity stated in the header, rather than recomputed without NRG_E.
- **Industry's and transport's branches not taken:** a later table may add them from the same saved file.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eurostat_electricity_consumption.py`, `tests/test_session2757.py`, this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `coverage.csv`, `docs/coverage.md`, `sources.csv`, `archive_manifest.csv`, the license record (reads 1504 to 1507), `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c139/s2757/`, `runs/license_reads/s2757/`, `warehouse/raw/eurostat_electricity_consumption/`.
