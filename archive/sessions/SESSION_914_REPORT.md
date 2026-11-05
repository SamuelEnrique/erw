# Session 914 report: the licenses' fifth round

23 October 2026, from 08:20 UTC, on lab-desktop (the data machine), a session of `queue/done/051-day-23-october-data-world-gas-hydro.md`. Model spend USD 0. Pulls: 14 requests of 20, at most two a host, each robots file first (reads 118 to 131); session 911's three reads of HydroSource recorded with them (reads 115 to 117).

## Read these first

- **Three new verdicts** (75 publishers with one; 41 tables still unsettled, from 42):
  - **Oak Ridge National Laboratory (ORNL), HydroSource: may be public** (read 116, by session 911): "Data hosted on HydroSource is openly shared, without restriction, in accordance with Department of Energy's Public Access Plan." Settles `ornl_eha_hydropower_plants`.
  - **California Public Advocates Office (.gov): may be public.** The Office is part of the CPUC, and its home page's footer (read 127) links the CPUC's conditions of use, read 50, on which the CPUC's verdict rests.
  - **T&D World: needs written permission** (read 131): Endeavor Business Media's terms, linked from T&D World's footer: "Copying or storing of any Content for other than User's legitimate non-commercial business end-use is expressly prohibited without the prior written permission of Endeavor". The same terms forbid, without Endeavor's prior written consent, robots, spiders or scripts that "collect the Content, data or information from the Services using automated means".
- **The sessions of this chain first:** EIA (record 1) and the CER (read 96) already have verdicts; ORNL's is the one new publisher of sessions 909 to 913.
- **Found, not yet read (for the sixth round):** the Texas Comptroller's site policies (`/about/policies/`, linked from its home page; its robots file allows `/about/`). The Georgia Public Service Commission's, the New Mexico Taxation and Revenue Department's and CTVC's home pages link no terms page.
- `test_session205`'s bound on the record raised for this chain's 17 reads, each session under its own ceiling.

## Decisions made without you

- **No address guessed:** each terms page read was linked from the publisher's own page, read in this round.
- **The Public Advocates Office given the CPUC's verdict,** since its site links the CPUC's conditions of use and no page of its own.

## For Samuel's ruling

- **T&D World's RSS feed** (`warehouse/news/feeds.yaml`, line 52) is read by the news ingest every day; Endeavor's terms forbid automated collection of its content without its prior written consent, as MISO's did before its pause. Whether to pause T&D World (`paused_sources.csv`) or ask Endeavor is a ruling; the feed is left as it is.

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv` (115 to 131), `license_verdicts.csv` (three rows), `docs/licenses.md`, `tests/test_session205.py` (its bound).
- On the data machine only: `runs/c051/s914/`, `runs/license_reads/s914/`.
