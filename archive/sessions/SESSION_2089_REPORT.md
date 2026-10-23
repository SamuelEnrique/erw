# Session 2089 report: the licenses' sixteenth round

23 October 2026, from 21:35 UTC, on lab-desktop (the data machine), the sixth session of `queue/done/068-day-26-october-data-mexico-renewables-loans-credits-pipelines.md`, run after sessions 2090 to 2092 so that their publishers came first. Model spend USD 0. Pulls: 6 requests of 20, two pages a host beside its robots file.

## Read these first

- **This chain's publishers first:**
  - **The IRS (`irs_soi_energy_credits_annual`, session 2087): "Internal Revenue Service (IRS), Statistics of Income", may be public** (read 232). The IRS's own pages say nothing on reuse (its privacy policy, read 229); SOI's tables are the IRS's own statistics, and USA.gov's Copyrighted government works page (reads 230 to 232: its robots file, the old address that redirects, the page) defines them: "Government work is something created by a U.S. government officer or employee as part of their official duties." The table now reads public.
  - **EIA** (`eia_state_to_state_capacity`) and the **National Weather Service** (`noaa_cpc_oni_monthly`) have verdicts (reads 1 and 8), and their tables read public.
  - **IRENA** (`irena_capacity_annual`, internal): its terms live on www.irena.org, which refused the reader (session 2085); not asked again.
  - **CENACE, USDA Rural Development and the IAEA:** no table was written (sessions 2084, 2086, 2091); USDA's host and the IAEA's refused the reader and are not asked again.
- **The U.S. Drought Monitor's Permission page,** which chain 066's `usdm_drought_state_weekly` waits on (reads 233 and 234: its robots file, which disallows `/data/` and the archive but not `/About/`, and the page): "If you reproduce the U.S. Drought Monitor map, please use this wording: The U.S. Drought Monitor is jointly produced by the National Drought Mitigation Center at the University of Nebraska-Lincoln, ... Map courtesy of NDMC." **Verdict: "U.S. Drought Monitor (National Drought Mitigation Center, USDA, NOAA)", may be public,** the key chain 066's source names, so the table takes it when that chain lands; the credit wording is the condition.
- **`scripts/licenses.py check`: 409 tables, 90 publishers with a verdict, 232 requests in the record, 0 problems.** `test_session205`'s bound raised by 40, with room for chains 066 and 067's reads at their merges.

## Decisions made without you

- **The IRS's verdict rests on the federal rule,** read on USA.gov, since the IRS's own pages state none; a ruling can hold the table internal by its line in `sources.csv`.
- **The Drought Monitor's page read for its data,** though it names the map: the weekly statistics are the same product's, and the page sets no other condition.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv` (229 to 234), `license_verdicts.csv` (the IRS, the Drought Monitor), `license_tables.csv`, `docs/licenses.md`, `tests/test_session205.py` (the bound).
- On the data machine only: `runs/c068/s2089/`, `runs/license_reads/s2089/`.
