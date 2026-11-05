# Session 2547 report: Bosnia and Herzegovina's electricity by utility, 2021 to 2025 (DERK's report on activities, Annex C), internal

24 October 2026, about 22:55 to 23:00 UTC, on lab-desktop (the data machine), chain 125, unattended. Precheck passed (`runs/c125/pre2547.out`). Model spend USD 0. Pulls: 5 requests of 15 (4 by the probe, 1 by the fetch the connector reads offline).

## Read these first

- **The ERW held no source for Bosnia and Herzegovina** (`sources.csv`, the connectors and the queue searched): only Eurostat's and EIA's international tables name it.
- **The hosts:** bhas.gov.ba has no robots file (read 1019); www.nosbih.ba's closes `/wp-admin/` only (read 1020); www.derk.ba's closes Joomla's own folders only (read 1021), so `/DocumentsPDFs/` is open. None names an AI agent.
- **DERK's terms:** its English home page states "DERK (c) 2004-2026. All Rights Reserved." and gives no terms of reuse (read 1022). The table is **internal** until a ruling.
- **The source:** DERK's (in English SERC's) "Osnovni EES pokazatelji BiH" in English, Annex C of its report on activities for 2025, "Balance Values of the Electric Power Sector of Bosnia and Herzegovina" (one page, last modified 10 July 2026), fetched once: five blocks, 2025 to 2021, each by utility (EP BiH, ERS, EP HZHB, Komunalno Brcko, other entities, and BiH in total): generation by plant type and in total, consumption by category and in total, and transmission losses.
- **Read by the words' places:** a utility's cell may be empty (EP HZHB has no thermal plant), so the page's text cannot tell the columns apart. Each block's heading words give the columns' right edges; each figure goes to the nearest. A row between two blocks would stop the run, not be passed over (the test holds this).
- **A new table, `derk_bih_electricity_annual`** (series, 214 rows, 6 entities, `power`), in MWh: generation 14.540 TWh and consumption 12.330 TWh in 2025 (17.055 and 12.170 in 2021). Each BIH figure equals the sum of the utilities (its consumption with the transmission losses, 350.02 GWh in 2025, given in its column only), and each utility's generation and consumption equal their parts. Written by run `20261024T225844Z` under the data lock, validated (exit 0), in coverage, archived (`20261024T225848Z-local`), held from the live set and from Redivis (internal).

## Cross-checks

- Against `eia_world_electricity_annual`'s Bosnia and Herzegovina for 2024: DERK's consumption 12.131 TWh against EIA's 12.052 (99.3%); DERK's generation 14.554 TWh against EIA's 15.716 (EIA's figure includes what DERK's balance does not; 2023: 15.822 against 16.185).

## Requests (5 of 15)

| n | What | Outcome |
|---|---|---|
| 1 to 3 | bhas.gov.ba, www.nosbih.ba and www.derk.ba robots files | 404, 200, 200 |
| 4 | Annex C (the fetch) | 200, 0.35 MB |
| 5 | DERK's English home page | 200 |

Reads recorded: 1019 to 1022. One web search found the annex; it reached no publisher's host.

## Decisions made without you

- **DERK's annex rather than BHAS's releases or NOS BiH's reports:** one table, five years, by utility.
- **Internal** under DERK's "All Rights Reserved", until a ruling.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/derk_bih_electricity.py`, `tests/test_session2547.py`, this report.
- Changed: the registration; the metadata files; the license record (reads 1019 to 1022) and `docs/licenses.md`.
- On the data machine only: `runs/c125/s2547/`, `warehouse/raw/derk_ba/`, `warehouse/output/derk_bih_electricity_annual.csv`.
