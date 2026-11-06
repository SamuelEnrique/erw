# Session 2019 report: the licenses' eleventh round (ICE, and Tracking the Sun on OEDI)

23 October 2026, from 18:47 UTC, on lab-desktop (the data machine), a session of `queue/done/057-night-23-october-data-wholesale-solar-industry-buildings.md`. Model spend USD 0. Pulls: 2 requests of 20 (www.ice.com's robots file, asked in a call of its own; ICE's Terms of Use). `license_verdicts.csv` was read first.

## Read these first

- **This chain's publishers first:** EIA (record 1), ICE (session 2014) and Berkeley Lab's Tracking the Sun on the Open Energy Data Initiative (session 2015).
  - **ICE's own Terms of Use** (read 195) grant "a limited license to access and use this Website and to download and print copies of any content to which you have properly gained access, but only for your own personal, non-commercial use", and name as the site's content "all compilations of real time or other information, including all pricing and market data". Session 2014's verdict on EIA's page, "ICE, whose prices EIA republishes" (read 192), stands: **needs written permission**, and its note now quotes ICE's terms. `eia_ice_electricity_daily` stays internal; whether to ask ICE is Samuel's.
  - **Tracking the Sun on OEDI:** a verdict of its own, "Berkeley Lab, Tracking the Sun on OEDI" (read 193, the submission page session 2015 read: its record's `"license": "https://creativecommons.org/licenses/by/4.0/"` and the site's footer, "Content is available under Creative Commons Attribution 4.0 unless otherwise noted."): **may be public**. Session 2020 maps `lbnl_tracking_the_sun` to it when the table is written.
- **The other unsettled publishers were not asked again:** each was read before and is waiting on a ruling, as the record says. PUDL's 21 FERC Form 714 tables and FERC's 8 EQR tables wait on FERC's own page (403 to the ERW's reader, session 888); the Louisiana Department of Revenue's draft verdict and a second page for publishers whose one read gave no sentence are session 388's questions; the Corps of Engineers' edge server refuses the ERW's reader (session 983); CME's host reset the connection (session 859). A new read of the same pages would settle nothing.
- **The record:** 389 tables, 84 publishers with a verdict, 176 requests in the record; `licenses.py check` 0 problems; tests 205, 207, 324, 378 and 2014 pass (43). `tests/test_session205.py`'s bound did not need raising.
- **Reads numbered 193 to 195,** after session 2014's 192 (first numbered 176 to 178 after chain 056's last, 174, and session 2014's 175; renumbered at the merge with chain 059, whose reads 175 to 191 landed first on main, as the two chains' rule asks).

## Errors

- None.

## Decisions made without you

- **No request for publishers already read without a sentence;** the round's ceiling kept.
- **Tracking the Sun given its own verdict,** not Berkeley Lab's (read 14, which rests on its other files' CC BY statements), as the hybrid plants file has its own (session 991).
- **ICE's verdict kept on EIA's page** (read 192), with ICE's terms in its note, rather than a second ICE verdict: one publisher, one verdict.

## For Samuel's ruling

- **ICE's indices** (`eia_ice_electricity_daily`): ask ICE for permission, or keep internal.
- The standing ones above (FERC's terms, the Louisiana draft, a second page for the publishers whose read gave no sentence, the Corps of Engineers, CME).

## Files

- Changed: `warehouse/metadata/license_reads.csv` (193 to 195), `license_verdicts.csv` (a new verdict, ICE's note), `docs/licenses.md`, this report.
- On the data machine only: `runs/c057/s2019/`, `runs/license_reads/s2019/`.
