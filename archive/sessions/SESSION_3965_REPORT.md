# Session 3965 report: the BLS indexes' route read again (licenses requests 11 and 12)

Energy Research Warehouse (ERW). Chain 278, data machine (lab-desktop), 14 November 2026, 14:36 to 14:42 UTC. Opus 5.5. Model spend USD 0. Requests: 1 (api.bls.gov's robots file, in a call of its own), listed in `runs/c278/s3963/probe.csv`.

Taken early under the no-waiting rule (sessions 3968 to 3971's step): chain 272's other steps wait for the runs of 14 to 16 November; gate a runs its suite.

- **The question:** rows 11 and 12 stopped in session 3939 for want of a BLS key. The BLS Public Data API also has a version 1 that needs no registration, which session 3939 did not try.
- **Read first:** no BLS row in `license_verdicts.csv` or `sources.csv`; FRED's copies are retired (`warehouse/output/retired/fred_power_price_indexes_monthly.csv`).
- **api.bls.gov's robots file** (HTTP 200, 26 bytes): `User-agent: *`, `Disallow: /`. Every path of the API is refused to every automated reader, and www.bls.gov already answers this reader 403.
- **So neither route opens the series** under the ERW's robots rule (the Virginia SCC's pause is the precedent): not version 1, and not a key either. Nothing fetched past the robots file.
- **Rows 11 and 12** carry the finding beside session 3939's words; they stay stopped.
- **Gate a:** the suite running since 14:32 UTC.

## Decisions made without you

- **The robots file outranks the key:** the rows stay stopped whatever key the repository might hold.

## For Samuel's ruling

- **The BLS CPI and PPI series** (rows 11 and 12). api.bls.gov disallows every automated request, so a key would not open them under the robots rule. Default: not read; FRED's copies stay retired. A written permission from BLS, or a ruling that an API built for programs may be read despite its robots file, would open them.
