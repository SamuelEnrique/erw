# Session 2422 report: Mongolia's electricity, 2015 to 2020, from the Energy Regulatory Commission

24 October 2026, from 10:55 UTC, on lab-desktop (the data machine), a session of `queue/done/115-day-16-november-data-zambia-botswana-mongolia-cambodia.md`. Precheck passed (`runs/c115/precheck_2422.out`). Model spend USD 0.

Pulls: 7 requests of 15:
- **www.1212.mn's robots file:** its certificate fails verification.
- **erc.gov.mn:** its robots file, the home page, and `/mn/statistic`.
- **admin.erc.gov.mn:** its robots file, and the English "Statistics on Energy Performance" (2020).
- **opendata.1212.mn's robots file:** the name does not resolve.

The trial and the write ran offline.

## Read these first

- **Statistics Mongolia is closed to the reader:**
  - www.1212.mn answers with a certificate that fails verification, and the ERW does not work around that (as for Bangladesh in chain 110);
  - its open-data host, opendata.1212.mn, does not resolve.
- **The Energy Regulatory Commission's statistics for 2021 to 2025 are published only as pictures** (PNG infographics on `/mn/statistic`), which are not read: their numbers could only be guessed at.
  - The newest edition published as a document is the 2020 one, in Mongolian and English, on admin.erc.gov.mn.
  - Both hosts' robots files disallow nothing (every line is a comment).
- **The table:** `erc_mongolia_electricity_annual`, 210 figures, 2015 to 2020, internal (the site shows only a copyright sign, no terms).
  - **The country (`erc_mn:MN`):**
    - generation by type (CHP, diesel, solar, hydro, wind, total) and imports, MWh;
    - installed capacity (CHP, renewable, diesel, total), MW;
    - electricity sales by class (entity and industry, apartment, ger district, total), MWh.
  - **Sales by the same classes for each of the five grids:** central, western, eastern, Altai-Uliastai, and the southern distribution network.
  - Read with pdfplumber's table extraction, each table found by its header.
- **The checks:**
  - **Generation:** the types add to the total, except 2020: 7,144.9 GWh against a printed 7,145.6 (the report's own text says 7,145.7). The header names it, and the connector allows up to 1 GWh.
  - **Capacity:** the types add to the installed capacity. The table's unit label reads "GWh", but its figures are MW (1,485.3 MW in 2020), and they are written as MW.
  - **Sales:** each grid's classes add to its total, and the five grids to the sector's, within 0.6. CRIPG's 2017 and 2018 figures are printed as whole numbers.
  - One figure printed with a space ("5,033 .2") is read as 5,033.2.
- **Against `owid_ember_electricity_annual`'s Mongolia demand:** generation plus imports is 1.004 to 1.021 times Ember's demand for 2015 to 2019, and 1.069 for 2020. Sales are 0.63 to 0.69 of it.
- **Registered:**
  - the sector rule (`power`), the live-set hold;
  - the license tables (licenses check: 518 tables, 0 problems);
  - the test, `tests/test_session2422.py` (3 tests).

## Errors

- **The write's metadata patch conflicted** next to this chain's earlier rows (the main checkout lags this branch). The four files were put back from HEAD and the table's own rows added by `runs/c102/add_own_rows.py`. The first finish run, made before that, failed on the conflict markers and wrote nothing. Rerun clean.
- **The reader's first run stopped twice:**
  - at the 2020 generation gap;
  - at CRIPG's whole-number sales.
  
  Both are written into the connector as stated tolerances, not hidden.
- **Three tables on the report's pages are headed "Grid";** the sales table is now told apart by its second column.

## Decisions made without you

- **Data to 2020 taken rather than no table:** this is the newest document ERC publishes. The years 2021 to 2025 wait for a document or a working Statistics Mongolia host.
- **The capacity figures written as MW,** against the table's "GWh" label.

## For Samuel's ruling

- **Statistics Mongolia's certificate:** if a future session should read www.1212.mn despite its failing certificate, that is a ruling. Not done.

## Files

- New: `warehouse/connectors/erc_mongolia.py`, `tests/test_session2422.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`;
  - `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`.
- On the data machine only: `runs/c115/s2422/`, `runs/license_reads/s2422/`, `warehouse/raw/erc_mongolia/`.
