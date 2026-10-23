# Session 2033 report: the licenses' twelfth round

23 October 2026, from 19:24 UTC, on lab-desktop (the data machine), the sixth session of `queue/done/058-day-24-october-data-outages-fuels-mines-vehicles.md`, unattended. Model spend USD 0. Pulls: 2 requests of 20 (creativecommons.org's robots file and CC BY 4.0's legal code).

## Read these first

- **This chain's publishers first.** EIA (read 1) and EPA (read 55) have verdicts, and their tables (`eia_biofuel_plants`, `epa_rfs_rins_monthly`, `epa_rfs_fuel_annual`) read public. Two needed this session:
  - **`doe_oe417_events` read "not settled":** its source named DOE's office (the Office of Cybersecurity, Energy Security, and Emergency Response) as the publisher, which matches no verdict's key. The source is now "U.S. Department of Energy (DOE)" with the office in its report's name, in `sources.csv` and in `doe_oe417.py`, so the table takes DOE's verdict (read 54, may be public), as `doe_useer_employment` does. The DOE-417 site is built by Pacific Northwest National Laboratory for DOE and names no terms of its own.
  - **EAGLE-I's verdict: "Oak Ridge National Laboratory (ORNL), EAGLE-I", may be public** (read 187). The dataset's figshare record (read 180) names its license CC BY 4.0; read 187 is that license's legal code: "the Licensor hereby grants You a worldwide, royalty-free, non-sublicensable, non-exclusive, irrevocable license to ... reproduce and Share the Licensed Material, in whole or in part". Attribution is the condition. The table, `eaglei_county_outages_daily`, is not written yet (session 2029); the connector's source already names this key.
- **Recorded:** reads 186 and 187 (this session), after this chain's 175 to 185. Read 187's outcome is exactly "read", as `test_session205` requires of a verdict's read.
- **The other publishers without a verdict** (FERC, the Public Utility Commission of Texas, the Corps of Engineers, Bonneville, Grant PUD, the state commissions and tax departments, the news outlets, CME through EIA) were all read by earlier rounds and wait on rulings or on permissions already listed in chain 056's note. None was asked again.
- **`scripts/licenses.py check`: 389 tables, 83 publishers with a verdict, 185 requests in the record, 0 problems.** The release package's check: 0 differences. `test_session205`'s bound, raised by session 2030, holds.

## Decisions made without you

- **DOE's office moved from the publisher to the report's name** rather than a second DOE verdict for the office: the office's pages are DOE's, under DOE's notice.
- **EAGLE-I's verdict rests on the license its record names,** since figshare.com's own pages answer the ERW's reader with a challenge (read 178) and were not asked again.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv` (186, 187), `license_verdicts.csv` (EAGLE-I), `sources.csv` (DOE-417's publisher), `warehouse/connectors/doe_oe417.py` (the same), `license_tables.csv`, `docs/licenses.md`.
- On the data machine only: `runs/c058/s2033/`, `runs/license_reads/s2033/`.
