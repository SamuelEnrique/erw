# Session 2427 report: the EU's crude oil imports by field of production (Eurostat), a second source of the session's own choosing

24 October 2026, from 11:28 UTC, on lab-desktop (the data machine), a session of `queue/done/115-day-16-november-data-zambia-botswana-mongolia-cambodia.md`. Precheck passed (`runs/c115/precheck_2427.out`). Model spend USD 0.

Pulls: 4 requests of 20:
- ec.europa.eu's robots file, alone;
- `nrg_ti_coifpm` for August and September 2026, every area, to read its dimensions (1,786,391 bytes);
- the EU's query from January 2016 (HTTP 413, asked to try again later);
- the same query two minutes later (`runs/c115/s2427/retry.py`): 2,015,581 bytes.

The trial and the write ran offline.

## Read these first

- **Why:** Eurostat's crude oil imports by field of production name the crude streams Europe buys, with each stream's volume, value, price in USD, API gravity and sulphur. U.S. streams are among them: WTI, Bakken, Eagle Ford, Mars and others. It complements session 2369's imports by country of origin, is not held, and no chain has taken it. Eurostat's table of contents (read in session 2426) lists it.
- **One series table, `eurostat_crude_imports_by_field_monthly`:** 51,718 figures, January 2016 to September 2026, the EU as a whole (Eurostat's `EU_V`, the members of the month), public.
  - **Streams:** 818, plus `TOTAL` (corrected by session 2429: this line first said 819 plus `TOTAL`). The streams begin in January 2020; 2016 to 2019 hold only the total's volume, value and price, and five months have no row.
  - **Variables:** `volume` (kbbl), `value` (USD), `price` (USD/bbl), `api_gravity` (degAPI), `sulphur` (pct).
  - **Not taken:** the reporting companies count, which has no value for the EU.
  - **USD:** Eurostat publishes these values and prices in USD, so the currency rule raises no question.
- **The zeros:** Eurostat writes 0 for a price, API gravity or sulphur where a stream had no import or a confidential volume, which is no measurement. Those are not taken (price 15,260, API gravity 18,278, sulphur 18,279), and the header counts them. A volume or value of 0 is kept. Confidential cells (29,409) carry no value and have no row. Three values carry Eurostat's flag "b" (a break in series).
- **The checks:**
  - **Value against volume times price:** equal within 1 percent in 2,395 of 2,402 stream-months with all three.
  - **The total volume against session 2369's EU crude imports in tonnes:** 7.4 to 8.2 barrels a tonne by year, the median of the months, as for a light crude slate (annual sums: 7.33 for 2021, 8.12 for 2025).
    - 2016 to 2019 run higher (7.7 to 7.9), perhaps because `EU_V` then held 28 members, the United Kingdom among them, against the EU27's tonnes; Eurostat's label says only "aggregate changing according to the context", and this was not tested.
    - 2020 to 2022 run lower (7.4 to 7.5); 2023 to 2025 higher (7.9 to 8.15).
    - (Corrected by session 2429: this said the 2016 to 2019 figures were "because" of the United Kingdom, and gave medians without saying so.)
- **What it shows:** the EU's imports of West Texas Intermediate, million barrels a year (price, USD/bbl, the mean of the monthly prices; weighted by volume it is 104.2 for 2022 and 96.4 for 2026, the others within 0.1 but 2021's 76.3 against 70.2; corrected by session 2429):

  | Year | Volume | Price |
  |---|---|---|
  | 2020 | 91 | 43.8 |
  | 2022 | 159 | 103.9 |
  | 2023 | 423 | 85.4 |
  | 2024 | 451 | 83.2 |
  | 2025 | 386 | 71.4 |
  | 2026 (to August) | 253 | 95.5 |

  In August 2026 it was 36.5 million barrels at 94.36. Every stream's total was about 4.0 billion barrels a year in 2016 to 2019 (with the United Kingdom) and 3.7 billion in 2023 to 2025.
- **Registered:**
  - the sector rule (`oil`), the live-set hold;
  - the release package's held list and its rows (the release check passes);
  - the license tables (licenses check: 525 tables, 0 problems);
  - the test, `tests/test_session2427.py` (3 tests).
- **Not yet in the Stanford draft:** session 2429 uploads it.
- **An overlap checked:** chain 114's agent reported that its shell was stopped for low memory and that its branch copies of the metadata files and the validator may have stood in the main checkout from about 11:33 to 11:36 UTC. This session's write ran 11:36:39 to 11:36:47.
  - Neither its metadata patch nor session 2426's holds a row of chain 114's tables.
  - The table's own rows were taken by key (`runs/c102/add_own_rows.py`), and the branch's coverage row carries this branch's sector rule.
  - The trial was validated by this branch's validator (pass).

## Errors

- **The write's metadata patch conflicted again;** one row each was put in by key.

## Decisions made without you

- **The EU aggregate only,** not each member: every member's streams would be several million values a request. The EU's totals answer the question of what Europe buys.
- **Zero prices and grades left out** as placeholders, counted in the header; zero volumes kept.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eurostat_crude_by_field.py`, `tests/test_session2427.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`;
  - `docs/redivis/release-v1/`;
  - `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`.
- On the data machine only: `runs/c115/s2427/`, `runs/license_reads/s2427/`, `warehouse/raw/eurostat_crude_imports_by_field_monthly/`.
