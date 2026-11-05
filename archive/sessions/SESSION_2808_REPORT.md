# Session 2808 report: Switzerland's electricity balance on each Wednesday (the SFOE's weekly statistics, ogd51), in place of the FSO; one request reached a path a robots file disallows

26 October 2026, from about 04:50 to 05:00 UTC, on lab-desktop (the data machine), chain 143, unattended. Precheck passed (`runs/c143/pre2808.out`). Model spend USD 0. Pulls: 8 requests of 15 (6 by the probe, 2 by the fetch).

## Read these first

- **A request reached a path a robots file disallows.** The session's catalogue search went to `https://opendata.swiss/api/3/action/package_search?...`. opendata.swiss has no robots file (read 1607), but it redirected the request to `ckan.opendata.swiss/api/...`, and the reader followed the redirect. **ckan.opendata.swiss's robots file disallows `/api/` to every reader** (read 1608, asked straight after).
  - The memory's rule (a redirect to a new host needs its robots file first) was broken because `fetch_raw` follows redirects itself.
  - That one answer (36 KB, the list of datasets) was read. Nothing more was asked of `/api/`, and every later request to ckan.opendata.swiss kept its `Crawl-Delay: 10`.
  - **The lesson goes into file 144:** ask opendata.swiss's dataset pages and ckan.opendata.swiss's `/dataset/<name>.xml` records, never `/api/`.
- **The FSO publishes no electricity dataset on opendata.swiss.** Its two datasets matching the search are votes' results. 34 of the SFOE's match it, one of them held (`bfe_switzerland_electricity_monthly`, ogd35, chain 080). The session's title names the SFOE's statistics as the other choice.
  - The first choice, the SFOE's physical imports and exports by country, has no data file: its DCAT record points only at the SFOE's publication search (read 1610).
- **`bfe_ch_electricity_wednesdays` is new:** the SFOE's ENSTAT weekly electricity balance (ogd51), "based on Wednesday data". Each row is one Wednesday's energy, 1 January 2003 to 24 June 2026: generation by type, storage pumps, imports, exports and national consumption, in MWh.
  - 11,154 rows, 1,222 days. Written, validated, archived, in coverage; held from the live set and from Redivis storage until session 2815's draft.
  - Each Wednesday is written at its date's 00:00Z, as a Swiss local day.
- **Thermal, wind and solar split out in 2025, and a column changed meaning with them** (found here):
  - The file's `Erzeugung_netto` is the generation less the storage pumps on all 1,144 days through 2024, within 0.05 GWh.
  - It is the generation before the pumps on all 78 days from 2025. On 1 January 2025 it is 132.778 GWh, with the pumps 26.509 GWh above the columns' net.
  - **Each day is written under the measure it is:** `generation_less_storage_pumps` (through 2024) and `net_generation` (from 2025), with `x_definition`. Neither series mixes the two.
  - National consumption equals the generation less the pumps plus imports less exports on all 1,222 days.
- **Kept as published, counted:**
  - one date not a Wednesday (27 October 2009, a Tuesday, after a six-day step);
  - steps of 14 and 35 days (after 20 October 2004 and 28 November 2007);
  - 3,510 blanks with no row (thermal, wind and solar before 2025, other from 2025).
- **Cross-check** against `energy_charts_central_europe`, Switzerland's hourly public net generation, summed over each Wednesday in Swiss time (182 Wednesdays from 2023):
  - **nuclear agrees within 0.09 per cent at the median** (90th percentile 0.74), e.g. 46,358 MWh against 46,350 on 10 June 2026;
  - run-of-river differs by 3 per cent at the median;
  - Energy-Charts' load is about 7 per cent above the SFOE's national consumption, by its own definition.
- **Terms:** opendata.swiss's licence `terms_by` ("Open use. Must provide the source."), the SFOE's verdict on record (read 594, session 2343). www.bfe-ogd.ch has no robots file (read 1612, HTTP 404, as session 2343 found).

## The requests

| n | What | Outcome |
|---|---|---|
| 1 | opendata.swiss's robots file | 200, its 404 page: no rule |
| 2 | the catalogue search (fetch), redirected to ckan.opendata.swiss/api/ | 200; **a path that host's robots file disallows** |
| 3 | ckan.opendata.swiss's robots file | 200, disallows /api/, Crawl-Delay 10 |
| 4 | the trade by country dataset's page (opendata.swiss) | 200, resources drawn by script |
| 5 | its DCAT record (ckan.opendata.swiss/dataset/...xml) | 200, a publication search only |
| 6 | the weekly balance's DCAT record | 200, ogd51's CSV |
| 7 | www.bfe-ogd.ch's robots file | 404, none |
| 8 | ogd51's CSV (fetch) | 200, 97 KB, last modified 18 September 2026 |

Reads recorded: 1607 to 1612.

## Decisions made without you

- **The SFOE's weekly balance taken for the FSO,** as the session's title allows.
- **`Erzeugung_netto` written under two variables,** split by what each day's figure is.
- **Each Wednesday written as a daily figure** (P1D), not spread over its week.

## For Samuel's ruling

- **The `/api/` request:** told here, not repeated. No ruling is asked unless you want the answer deleted from the data machine: it is `warehouse/raw/swiss_catalog/`, not in git and not in any table.

## Files

- New:
  - `warehouse/connectors/bfe_weekly_balance.py`
  - `tests/test_session2808.py` (4 tests, passing)
  - this report
- Changed:
  - the table's registration and holds;
  - the license record (reads 1607 to 1612) and `docs/licenses.md`;
  - coverage, sources, the archive manifest and the release v1 records.
- On the data machine only:
  - `runs/c143/s2808/`, `runs/license_reads/s2808/`;
  - `warehouse/raw/swiss_catalog/`, `warehouse/raw/bfe_weekly/`.
