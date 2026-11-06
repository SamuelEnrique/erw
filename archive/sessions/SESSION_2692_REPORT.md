# Session 2692 report: installed renewable capacity at year end by UK region and technology, 2003 to 2025 (DESNZ's Regional Renewable Statistics), public, a source of the session's own choosing

25 October 2026, about 12:56 to 13:02 UTC, on lab-desktop (the data machine), chain 135, unattended. Precheck passed (`runs/c135/pre2692.out`). Model spend USD 0. Pulls: 2 requests of 20 (1 by the probe, 1 fetch of the workbook under a run name of its own, read offline by the trials and the write).

## Why this source

- **This chain's four sources gave no table** (the Dominican Republic, Ukraine, Libya, Haiti).
- **The companion of session 2684's table:** DESNZ's Regional Renewable Statistics give installed capacity by region beside generation, from the same page, host and licence. The ERW held the generation and not the capacity.

## Read these first

- **The host:** www.gov.uk's robots file closes only print and search paths (read 1418). The assets host has no robots file (read 1393). The page was read in session 2684 (read 1400).
- **The terms:** the Open Government Licence v3.0 (DESNZ's verdict, read 315). The table is **public**.
- **A new table, `desnz_regional_renewable_capacity_annual`** (series, 3,157 rows, 197 entities, `power`), at 31 December of each year from 2003 to 2025:
  - `desnz_rc:<region>:<technology>` for England's nine regions, the nations, England, the other sites and the UK, and `co_firing` (the non-fossil capacity used in co-firing, which the UK total leaves out).
  - Variable `capacity`, MW.
- **Figures:**
  - The UK's renewable capacity was 3.5 GW in 2003, 9.3 in 2010, 48.0 in 2020 and 65.3 in 2025.
  - In 2025: onshore wind 16.4 GW, offshore 16.6, solar 21.9. Scotland's onshore wind went from 5.4 GW in 2015 to 10.5 in 2025.
- **The sheets differ from the generation workbook's,** each difference read, not forced:
  - The sheet names have no space ("MW2025").
  - Yorkshire's region is "Yorkshire and Humber" from 2015.
  - The 2022 sheet calls three regions "Eastern", "Other" and "Total".
  - The 2003 to 2006 sheets head a column "Other bioenergy (incl Sewage gas" without its closing parenthesis.
  - A co-firing row follows the UK total, and footnote rows follow it.
  - "[y]" marks data not available, outside the total, beside "[x]" (too few sites to show, inside it). Neither has a row.
- **Checks, all passing:**
  - a region's technologies add to its total within 1 MW (no more than it where a cell is "[x]");
  - England's nine regions add to England;
  - the nations and the other sites add to the UK.
- **Its record:** written by run `20261025T130035Z` under the data lock and validated (exit 0). It is in coverage, archived (`20261025T130040Z-local`), held from the live set, and in the release package (public). The write's and the finish's results were read before the commit; the patch applied cleanly.

## Cross-checks

Against the ERW's `desnz_uk_renewables_quarterly` (Energy Trends 6.1, the fourth quarter of 2025):
- onshore wind 16,430.69 MW and solar 21,914.97 MW in both;
- the total 65,306.7 MW against 65,271.2 (0.05 per cent apart).

## Requests (2 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www.gov.uk's robots file | 200 |
| 2 | the capacity workbook (the fetch) | 200 |

Read recorded: 1418.

## Decisions made without you

- **DESNZ's regional capacity as the own choice; public** under the verdict on record.
- **Co-firing kept as its own row,** outside the UK total, as DESNZ gives it.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/desnz_regional_renewable_capacity.py` (made from session 2684's by `runs/c135/s2692/make_connector.py`), `tests/test_session2692.py`, this report.
- Changed: the registration; the metadata files; the release package; the license record (read 1418) and `docs/licenses.md`.
- On the data machine only: `runs/c135/s2692/`, `runs/license_reads/s2692/`, `warehouse/raw/desnz_regional/s2692probe1/`, `warehouse/output/desnz_regional_renewable_capacity_annual.csv`.
