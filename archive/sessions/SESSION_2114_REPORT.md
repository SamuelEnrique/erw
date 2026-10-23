# Session 2114 report: New York's distributed solar (not pulled: Open NY's terms bar automated access)

23 October 2026, from 22:42 UTC, on lab-desktop (the data machine), a session of `queue/done/069-day-27-october-data-public-lands-sunlight-spending-streams.md`. Model spend USD 0. Pulls: data.ny.gov, 2 requests of 15 (the robots file in a call of its own, and the OPEN-NY Terms of Use, the PDF of dataset 77gx-ii52 that session 2111 left to this session); no data.

## Read these first

- **No NYSERDA data was pulled.** The OPEN-NY Terms of Use (read 253, extracted with `pdftotext`) are open about reuse: "So long as you are not doing anything malicious with NYS data, you may use it as you wish, subject to no other requirements", with no attribution, share-alike or pre-approval. But they also say: "You must not create accounts with OPEN-NY or access the site through unauthorized means, including but not limited to, by using an automated device, script, bot, spider, crawler or scraper." The ERW read the IEF's like clause as a bar for JODI (session 2075), and MISO's for its pause, so the connector was not written.
- **A new verdict, Open NY (New York State): needs written permission** (read 253, the sentence cut by code). The note records that reuse itself is open and that the bar is on automated access. No ERW table comes from data.ny.gov (no connector names the host), so no table's license changes. **data.ny.gov joins the hosts not asked for data without a ruling.** Chain 079's agent was told.
- **Reads 252 and 253** follow session 2111's 251. The record has 419 tables, 93 publishers with a verdict and 251 requests; `licenses.py check` 0 problems. `tests/test_session205.py` passes (2 more reads, within the round's bound).
- **The distributed solar the question asked about is already held from other sources:** Berkeley Lab's Tracking the Sun (`lbnl_tracking_the_sun`, project by project, New York among its states) and EIA-861's distributed generation and net metering (`eia861_distributed_generation`, `eia861_net_metering`). So no replacement source was taken in this session's time.

## Errors

- None (the robots file allows `/api/views/` and `/resource/`; the bar is in the terms, not the robots file).

## Decisions made without you

- **No data, and no replacement source:** the clause read as JODI's was. Distributed solar is held from Berkeley Lab and EIA.

## For Samuel's ruling

- **Open NY's automated-access clause:** does data.ny.gov's published API (Socrata's `/resource/` and `/api/views/` exports, which its robots file allows) count as an authorized means, so that the ERW may read NYSERDA's Statewide Distributed Solar Projects automatically? Or should the State be asked first? The terms leave reuse of the data open.

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv` (252, 253), `license_verdicts.csv` (Open NY), `license_tables.csv`, `docs/licenses.md`.
- On the data machine only: `runs/c069/s2114/` (the terms' text among them), `runs/license_reads/s2114/`.
