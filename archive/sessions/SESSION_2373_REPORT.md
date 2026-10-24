# Session 2373 report: Ghana's electricity, 2000 to 2025 (the Energy Commission's National Energy Statistical Bulletin)

24 October 2026, from 08:53 UTC, on lab-desktop (the data machine), the third session of `queue/done/112-day-13-november-data-sri-lanka-nigeria-ghana-jordan.md`, unattended. Precheck passed (`runs/c112/pre2373.out`). Model spend USD 0. Pulls: 5 of 15 (below).

## Read these first

- **One internal table:** `energycom_ghana_electricity_annual`, from the Energy Commission's National Energy Statistical Bulletin 2026. It is written, validated, archived, in coverage (sector power), and held from the live set. 221 rows, 2000 to 2025:
  - generation by hydro, thermal and other renewables, and the total (table 3.7);
  - imports, exports and net exports (table 3.8);
  - Ghana's peak load and the system peak (Ghana's plus export load; the body's table 3.9, listed as 3.6 in the contents).
  - In MWh (the bulletin's GWh times 1,000) and MW.
- **Read with pdfplumber's table extraction.** Its rows come with their cells shifted on alternate lines, so each row's non-empty cells are read in order and the shares left out.
  - The sources add to the total, and exports less imports to net exports, within 1.5 GWh, in every year.
  - The bulletin's footnote 8 says total generation "includes embedded generation and import". Session 2375's note found that table 3.7's total holds no imports (it is hydro plus thermal plus other renewables, and the bulletin's energy transmitted is that total plus imports in 2000 to 2006); the header now says so.
  - Ghana's peak is above the system peak in 2001 (1,213 against 1,190 MW) and 2007. The bulletin defines the system peak as Ghana's peak plus export load (footnote 11) and as Ghana's load at peak plus export load (its text); both years are kept as published and named in the header.
- **License: internal.** The bulletin states no terms of reuse, and the site's "Terms & Condition" link leads to its home page (read 608). So the table is internal until a ruling and no verdict is recorded.
  - www.energycom.gov.gh's robots file allows every path, asks a crawl delay of 3 seconds (kept), and names no AI agent (read 606).
- **GRIDCo was not needed:** the bulletin carries GRIDCo's and ECG's figures, as its tables' source lines say.

## The cross-check (`runs/c112/s2373/cross.py`, `cross.out`; tables read past their header lines)

- **Generation less exports plus imports, against `owid_ember_electricity_annual`'s Ghana demand:**
  - Within 0.3 per cent in 2021 to 2023 (2022: 20.99 against 21.05 TWh).
  - 2.1 per cent above in 2020, 5.6 per cent above in 2019, and 7.8 per cent above in 2024 (23.52 against 21.83 TWh).
  - Generation less exports plus imports counts imports once, since table 3.7's total holds none (session 2375; this line first said they were counted twice).
- Generation rose from 7.224 TWh (2000) to 27.945 TWh (2025); the system peak from 1,161 to 4,283 MW.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.energycom.gov.gh | 5 of 15 | robots, the flyer page, the index, the statistics page, the bulletin (2.2 MB); 4 s or more apart |

## Errors

- **The first trial stopped at the contents page,** which names the tables too. A page with a table's title but no table of years is now skipped.

## Decisions made without you

- **The 2026 bulletin only,** since it carries 2000 to 2025 in each table.
- **The table internal** while the Commission's terms are unstated.

## For Samuel's ruling

- **Ghana's Energy Commission bulletin:** public or internal? It states no terms.

## Files

- New:
  - `warehouse/connectors/energycom_ghana.py`
  - `tests/test_session2373.py`
  - this report
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`
  - `warehouse/metadata/license_reads.csv` (606 to 609), `license_tables.csv`, `docs/licenses.md`
  - the coverage, sources and archive manifest files
- On the data machine only: `runs/c112/s2373/`, `runs/license_reads/s2373/`.
