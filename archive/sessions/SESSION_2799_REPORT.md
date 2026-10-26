# Session 2799 report: European data centres' electricity consumption (Eurostat, isoc_env_ict_nrg), the session's own choice

26 October 2026, from about 03:23 to 03:29 UTC, on lab-desktop (the data machine), chain 142, unattended. Precheck passed (`runs/c142/pre2799.out`). Model spend USD 0. Pulls: 4 of 20.

## Read these first

- **`eurostat_data_centre_electricity_annual` is new:** Eurostat's data centres' electricity consumption (isoc_env_ict_nrg: SIEC E7000, NACE "DATAC"), each European country's data centres' electricity a year, 2020 to 2024, in MWh (Eurostat's GWh times 1,000). 85 rows, 32 areas.
  - The table has been written, validated, archived and put in coverage.
  - It is held from the live set and from Redivis storage until session 2801's draft.
- **Why this source:** it is the ERW's first measured data-centre consumption. The ERW holds data centre projects, operators' sites and queue positions, but no metered or surveyed use; AI's demand for power is the ERW's sharpest lens. No connector, method note, source row or unlanded chain names it.
- **The countries a year:** 5 in 2020, 6 in 2021, 21 in 2022, 26 in 2023 and 27 in 2024. Eurostat's collection began with reference year 2020 and countries joined it year by year. 11 observations are confidential and have no row: Italy 2022 to 2024, Serbia 2020 to 2024, Malta 2023 and 2024, Bulgaria 2024.
- **Largest in 2024:**
  - Germany 20.0 TWh (4.2 per cent of its final electricity consumption in `eurostat_electricity_consumption_annual`);
  - **Ireland 6.97 TWh, 21.2 per cent;**
  - the Netherlands 5.09 TWh (4.7);
  - France 4.35 TWh (1.1);
  - Sweden 2.64 TWh (2.1);
  - Finland 2.35 TWh (3.1);
  - Norway 2.03 TWh (1.6).

- **28 zeros are kept as Eurostat prints them and counted in the header,** and the log names each. Some cannot be measured absences, among them Denmark 2020 to 2022 (it hosts large data centres) and Poland 2022 and 2023 (459 GWh in 2024). The header says to treat them with care; session 2801's note says so.

## The requests

1. **ec.europa.eu's robots file (read 1598):** byte for byte session 2798's.
2. **nrg_ind_331a,** taken for the electricity market indicators: HTTP 404, "not available for dissemination". It was a guessed code.
3. **Eurostat's dataflow list** (`dataflow/ESTAT/all?detail=allstubs`, 7 MB, 2,950 datasets): read for the codes, after the guess failed.
   - It lists TEN00119, the market share of the largest generator, which the earlier code meant.
   - It also lists NRG_IND_RE (the rate of electrification), NRG_INF_NUC (nuclear energy facilities), NRG_PC_205_V (non-household electricity volumes by band) and ROAD_IF_RCHEV (EV recharging points and power), none held. These are left for session 2804 or a later chain.
   - The file is kept under `warehouse/raw/eurostat_electricity_market/` (not in git).
4. **isoc_env_ict_nrg:** the whole dataset (8 KB), the table's one request.

## Decisions made without you

- **Zeros kept, not dropped**, unlike session 2798's all-zero household splits. A data-centre zero is one published figure, not a missing split, and nothing in the file marks it as unreported. The header names each country that gives one. Reversible.
- **No share of national consumption written into the table:** the shares above come from the held table, for this report and the note only.

## For Samuel's ruling

- None.

## Files

- New:
  - `warehouse/connectors/eurostat_data_centres.py`
  - `tests/test_session2799.py` (3 tests, passing)
  - this report
- Changed: the table's registration and holds, the license record, coverage, sources, the archive manifest and the release v1 records.
- On the data machine only: `runs/c142/s2799/`.
