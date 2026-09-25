Session 2 of the Energy Research Warehouse (ERW). Read CLAUDE.md, ARCHITECTURE.md, docs/datastandard.md and SESSION_1_REPORT.md first. Same non-negotiables as session 1: real data only, fail loudly, no em dashes, never delete existing files, commit after each task, do not push.

Decisions from the human on the session 1 open questions: keep raw source files under warehouse/raw/ (gitignored) from now on; latest value only for v0 with vintage recorded; keep CSVs in git for now; include next-day DAM prices once published, marked by vintage; Python stays 3.14 tonight.

TASK 1. Generalize the connector.
Refactor warehouse/connectors/ercot_prices.py into a shared module warehouse/connectors/iso_prices.py with one function per ISO that returns day-ahead and real-time prices in the series standard, plus a thin CLI that takes an ISO name and a number of days. Keep ERCOT's behavior and output files identical (rerun and confirm the validator still passes and the row counts match session 1). Save every raw file each ISO returns under warehouse/raw/<iso>/ with its retrieval timestamp.

TASK 2. Add the ISOs that need no API key.
Using gridstatus, add CAISO, NYISO, MISO, SPP and ISO-NE. For each, pull the last 30 complete operating days of day-ahead and real-time prices for that ISO's trading hubs or load zones (CAISO: TH_NP15, TH_SP15, TH_ZP26; NYISO: the 11 load zones; MISO: its hubs; SPP: its hubs; ISO-NE: the 8 load zones plus the hub). Where an ISO offers 5-minute real-time, aggregate to 15-minute means and say so in the header. Apply the same strict completeness rule as ERCOT: write a file only if every node has every interval; otherwise write nothing for that market and log why. Output files follow the naming rule: caiso_dam_hub_prices.csv, nyiso_rtm_zone_prices.csv, and so on. Entities use the namespaced form iso:NODE. geo uses ISO 3166-2 where an ISO is one state and a comma-separated list otherwise. Skip PJM entirely; it needs an API key we do not have yet, and say so in the report.

TASK 3. Validate everything.
Run erw_validate on every file in warehouse/output. Extend the validator if a real ISO file exposes a gap in the standard, and record the change in docs/datastandard.md under Decisions in v0 with a one-line reason. Do not weaken any check to make a file pass.

TASK 4. One table of what we have.
Write docs/coverage.md: one row per output file with ISO, market, nodes, interval, date range, rows, source report, and validator result. This is the seed of the metadata table the IRW calls metadata.csv.

TASK 5. Report.
Write SESSION_2_REPORT.md in the same format as session 1: what was built, every decision, every error, rerun commands, open questions. Final commit.