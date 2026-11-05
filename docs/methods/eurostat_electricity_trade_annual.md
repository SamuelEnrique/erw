# Eurostat's annual electricity imports and exports by partner country: 39 European countries and two aggregates, 167 partners, 2010 to 2024 (nrg_ti_eh and nrg_te_eh, electricity)

Energy Research Warehouse (ERW), method note written in session 2429 (chain 115) for a table first written on 24 October 2026 (session 2432 of chain 115, `archive/sessions/SESSION_2432_REPORT.md`). Eurostat's terms, the countries they allow and the shared country lists are described in `docs/methods/eurostat_renewable_capacity_annual.md` (session 2129). The same publisher's monthly electricity balance, whose imports and exports this table's partner totals are checked against, is the table `eurostat_electricity_monthly`; its hard coal and crude oil imports by partner are `docs/methods/eurostat_hard_coal_imports_annual.md` and `docs/methods/eurostat_crude_imports_monthly.md`.

Tables: `eurostat_electricity_trade_annual`

## Publisher and address

Eurostat (Statistical Office of the European Union), "Electricity and derived heat imports" (`nrg_ti_eh`) and "Electricity and derived heat exports" (`nrg_te_eh`), page `https://ec.europa.eu/eurostat/databrowser/view/nrg_ti_eh/default/table`, through the statistics API without a key, as JSON-stat 2.0, filtered to electricity (SIEC `E7000`):

- `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_ti_eh?format=JSON&lang=EN&siec=E7000&sinceTimePeriod=2010`
- `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_te_eh?format=JSON&lang=EN&siec=E7000&sinceTimePeriod=2010`

Eurostat publishes this trade by partner a year only: its table of contents (read in session 2426) lists `nrg_ti_eh` and `nrg_te_eh`, 1990 to 2024, and no monthly set. Both queries were answered at once (HTTP 200).

Source id `eurostat:nrg_ti_eh_nrg_te_eh` (`sources.csv`: license public). The answers, saved in `warehouse/raw/eurostat_electricity_trade_annual/` (copied there from session 2432's probe, `runs/license_reads/s2432/02_...` and `03_...`, each with its fetch time as its modification time; not fetched by the connector):

| File | Bytes | sha256 | Dimension sizes | Values | Updated |
|---|---|---|---|---|---|
| `nrg_ti_eh_e7000.json` | 1,507,564 | `2f5bfb04...` | 1, 1, 167, 2, 43, 15 | 102,761 | 2026-10-22T23:00:00+0200 |
| `nrg_te_eh_e7000.json` | 1,507,392 | `79ae2a0f...` | 1, 1, 167, 2, 43, 15 | 102,743 | 2026-10-22T23:00:00+0200 |

The dimensions are `freq, siec, partner, unit, geo, time`, with freq `A`, siec `E7000` and two units, `GWH` and `TJ` (the same figures); neither answer has a status. ec.europa.eu's robots file, read in session 2432, disallows the old `/eurostat/SDMX/diss-web/rest/` path and the search pages, not `/eurostat/api/dissemination/`, and names no AI agent.

Connector: `warehouse/connectors/eurostat_electricity_trade.py` (session 2432), `[--offline] [--out-dir DIR]`. Ceiling: each address asked at most 10 times, a minute apart, until it answers with the data.
- **Kept:** the reporting areas in `eurostat_res_capacity.KEPT`; every partner; the GWh figures (the TJ ones passed over).
- **Values:** Eurostat's GWh times 1,000, written as MWh rounded to 0.001.
- **Stops:** dimensions other than the six named, a product other than `E7000`, units other than GWH and TJ, a frequency not annual, a period not a year, a value that is not a number, or a key given twice.
- **Offline:** on `--offline` the saved answers are read, and `retrieved_at` is each file's modification time.

## Schedule and records

Schedule: none. No shell script under `warehouse/`, no workflow in `.github/workflows/`, no file in `scripts/` and not `warehouse/scheduled.py` names it.

Records:
- `runs/status/eurostat_electricity_trade_annual.json`: run `20261024T115247Z` (session 2429's rewrite with the corrected header; the first write was session 2432's).
- `archive_manifest.csv`: 198,783 rows, run `20261024T115258Z-local`.
- `coverage.csv`: sector power (`build_coverage.py`'s rule of session 2432), 167 nodes, P1Y, 2010 to 2024, validator pass, public.
- License: `license_tables.csv`, Eurostat, "the source registry"; `docs/licenses.md`, verdict "may be public", flag public, "agrees".
- Release: listed as held in `docs/redivis/release-v1/tables.csv` (`STORAGE_HELD` in `warehouse/redivis/release_v1.py`).
- Live set: under `catalogue_hold` in `warehouse/supabase/live_set.yaml`, not loaded.
- Package: the row is added when the records are rebuilt at the chain's landing (session 2433).

Readers: none. `tests/test_session2432.py` (3 tests) tests the connector on JSON-stat built in the test.

## Vintage and revision

`retrieved_at` is 2026-10-24T11:43:38Z in every imports row and 11:43:45Z in every exports row, the probe's fetches. `vintage` is blank; Eurostat's update times are on header line 4. A revised year replaces the old figure on a later run; no earlier version is kept.

## Shape and variables

Series, 198,783 rows, 17 columns (`entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_geo_code, x_partner, x_partner_name, x_flag`), 10 header lines.
- **`entity`:** `eurostat_elec_trade:<Eurostat geo code>:<partner code>`, 6,845 values.
- **`variable`:** `imports` (99,391 rows) and `exports` (99,392); `unit` MWh; `freq` P1Y; `ts_utc` the year's 1 January, 2010 to 2024.
- **`geo`:** the reporting area's ISO alpha-2 code (Eurostat's EL written GR, 4,954 rows), blank for EU27_2020 and EA21 (10,020 rows).
- **`source_url`:** the imports or the exports address, by variable.
- **Values:** every value a whole number of MWh, none negative, no flag. 191,254 rows are zero; 3,756 imports and 3,773 exports are not. The largest value is the EU's exports to all partners in 2024, 452,548,956 MWh.
- **Areas, 41:** 39 countries (the 27 members, Iceland, Liechtenstein, Norway, Albania, Bosnia and Herzegovina, Georgia, Moldova, Montenegro, North Macedonia, Serbia, Turkiye and Ukraine) and EU27_2020 and EA21. Most have 5,010 rows (15 years); the fewest Georgia 3,964, Bosnia and Herzegovina and Liechtenstein 3,634, Ukraine 3,630. The United Kingdom and Kosovo are in the answers and left out by Eurostat's terms.
- **Partners, 167:** 159 countries and 8 aggregates, `TOTAL`, `NSP` (not specified), `AFR_OTH`, `AME_OTH`, `ASI_NME_OTH`, `ASI_OTH`, `EUR_OTH` and `EX_SU_OTH`. A sum over partners with `TOTAL` double counts.
- **Partner `NA` is Namibia** (1,200 rows): read with `keep_default_na=False`.

## Checks

Counted in session 2429 from `warehouse/output` in the main checkout, read past its 10 header lines with `keep_default_na=False` (`runs/c115/s2429/trade_facts.out`), and from session 2432 (`archive/sessions/SESSION_2432_REPORT.md`). No request was made.

- **Table:** no (entity, variable, ts_utc) twice; one `retrieved_at` for each variable.
- **The EU against its members:** the EU's imports and exports from and to all partners equal the sum of the 27 members' in every year (ratio 1.0000), so the EU's figures include the members' trade with one another.
- **Against the monthly balance** (`eurostat_electricity_monthly`, `flow:IMP` and `flow:EXP` summed over twelve months, MWh): the all-partner figures agree within 1 percent in 554 of 662 country-years with twelve months, and within 5 percent in 592. The EU's, TWh, annual against the monthly sum: imports 362.5 against 356.8 (2016) and 440.2 against 436.8 (2024); exports 361.9 against 357.2 (2016) and 452.5 against 449.6 (2024).
- **The EU's trade with all partners,** TWh: imports 291.5 (2010), 362.5 (2016), 381.0 (2020), 421.7 (2022), 440.2 (2024); exports 286.6, 361.9, 367.0, 408.7, 452.5.
- **Partner detail can be incomplete:** Germany's 2024 imports from all partners are 81.7 TWh, of which 37.9 TWh are "not specified"; France 20.5, Austria 9.4, the Netherlands 8.8 and Czechia 4.4 are named.

## What it cannot say

- **A year only,** from 2010: no months by partner; 1990 to 2009 not read.
- **Each country as it reports:** one country's imports from a partner need not equal that partner's exports to it, and some imports are "not specified".
- **Derived heat** (the data sets' other product) and the TJ figures are not taken.
- **Not the United Kingdom or Kosovo** (Eurostat's terms).
- **Prices and flows by hour or border point** are not in these data sets.

## Acted on in session 2429

- **The header's partner aggregates:** session 2432 first wrote "the EU, extra-EU" among them, which this table has neither of. The connector now names them from the answer, and the table was written again offline (run `20261024T115247Z`), the same 198,783 rows with only the header changed; its metadata rows were replaced by key.
