# Session 2238 report: the next file, and France's grid every half hour (RTE's eco2mix)

24 October 2026, from 03:03 UTC, on lab-desktop (the data machine), the first session of `queue/done/101-day-4-november-data-france-spain-brazil-australia.md`, unattended. Model spend USD 0. Pulls: 14 requests of 15 (below).

## Read these first

- **Chain 101 taken** at 03:02 UTC by chain 059's agent when chain 098 landed (6a05c622). The owner's instruction for that run is to run the file the queue step prints. Chain 099, whose continuation this file is, still runs beside it under another agent; that agent was told, and its hosts closed to the reader were added to this chain's list (www.mbie.govt.nz, opendata.cbs.nl's OData paths, api.scb.se's v1, EirGrid's data). Chain 097 runs too.
- **The next file first,** pushed to main on its own before any other work (448a2c49, with snapshots): `queue/next/102-day-5-november-data-poland-belgium-new-zealand-columbia.md`, sessions 2252 to 2265, machine: data.
  - Its sources: Poland's grid (PSE), Belgium's (Elia), New Zealand's (the Electricity Authority's EMI), and the Columbia River's federal dams (the Corps' Northwestern Division).
  - Germany was dropped from it because chain 099 takes SMARD.
- **ODRE is closed to the ERW.** odre.opendatasoft.com's robots file disallows `/api/`, `/explore/download` and every dataset download for all readers but Googlebot (read 404). RTE's own download host serves the same national eco2mix data, so it is used instead.
  - eco2mix.rte-france.com has no robots file (read 405). www.rte-france.com's robots file disallows only admin, search, user and filter paths (read 406).
  - **RTE's legal notice** (read 410), a new verdict, may be public in both columns: "Les données publiées sur le portail « www.rte-france.com » sont publiques et leur réutilisation est permise sous réserve de mentionner la source. Toutefois la modification, la dénaturation totale ou partielle du site ou de son contenu, par quelque procédé que ce soit, et sur quelque support que ce soit est interdite." So the values are kept as published, reshaped only from wide to long.
- **One table written, validated, archived, in coverage (sector power), in the release package, both holds:** `rte_eco2mix_france_halfhourly`, 2020 to August 2026, 1,647,503 rows.
  - Fifteen measures in MW every half hour: consumption, oil, coal, gas, nuclear, wind, solar, hydro, pumping, bioenergy, net physical exchanges, battery charging and discharging, onshore and offshore wind.
  - Sources: the definitive years 2020 to 2025 and this year's consolidated file.
  - **French local time placed in UTC, nothing guessed.** RTE's files give 96 quarter hours every day.
    - On the spring change they print 02:00 to 02:45, which do not exist in French time; their values repeat their neighbours'. 14 half hours were left out.
    - On the autumn change they print the doubled hour once, so it cannot be placed. 12 half hours were left out.
  - **Wind's split:** in all of 2021, RTE prints 0 for both onshore and offshore beside a total wind that is not 0. That placeholder split is left out (17,520 half hours). Elsewhere the split stays as published; it differs from the total by more than 1 MW on 1,800 of 81,772 half hours, by at most 28 MW.
  - The forecasts, the CO2 rate (no unit stated), the commercial exchanges by border (hourly values repeated on every quarter hour) and the sub-sources are not taken.
- **The cross-check** (`runs/c101/s2238/cross.py`, `cross.out`, every table read past its header lines):
  - **Against Ember:** a year's consumption, each half hour's MW times half an hour, is a steady 0.926 to 0.933 of Ember's French demand from 2020 to 2025. For example, 2025 is 443.788 against 476.66 TWh.
    - The steadiness confirms the unit, which the files do not state.
    - eco2mix covers mainland France; why Ember's figure runs about 7% higher is not tested here.
  - **The file's own balance:** production plus net physical exchanges minus consumption is a median 65 MW (0.13% of consumption) over 116,853 half hours.
  - **Nuclear:** 335.1, 360.4, 278.8, 320.1, 361.6 and 373.0 TWh from 2020 to 2025. 2022's low year is there.

## The pulls

1. odre.opendatasoft.com/robots.txt (read 404): closed.
2. eco2mix.rte-france.com/robots.txt (read 405): HTTP 404.
3. www.rte-france.com/robots.txt (read 406).
4. The eco2mix download page (read 407).
5. Its list of downloadable years (read 408).
6. Its download script (read 409), for the files' addresses.
7. The legal notice (read 410).
8. to 14. The six definitive years 2020 to 2025 and the consolidated current year. They were seeded into the raw store, and the trial and the write read them offline.

## Errors

- **The first trial counted spring's nonexistent half hours as autumn's ambiguous ones.** A gap time also gives two UTC instants. Fixed: a round trip from UTC decides first. Nothing was written from it.
- **A trial folder kept an earlier trial's rows;** it was cleared and the trial run again.
- **Read 410's outcome** first carried words after "read"; the license test requires the bare word for a quoted sentence. Corrected.

## Decisions made without you

- **RTE's own host in place of ODRE,** whose robots file closes it.
- **The half hour kept** as RTE publishes it, not averaged to an hour; the queue file allowed either.
- **The two kinds of change-of-hour half hours left out,** rather than placed by a guess.
- **The zero wind split of 2021 left out** as a placeholder, not a measure.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/rte_eco2mix.py`, `tests/test_session2238.py`, this report; on main, `queue/next/102-day-5-november-data-poland-belgium-new-zealand-columbia.md`.
- Changed:
  - `tests/test_session205.py` (its bound, +20)
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`
  - `warehouse/metadata/license_reads.csv` (359 to 365), `warehouse/metadata/license_verdicts.csv` (RTE)
  - the coverage, sources, archive manifest and license files
  - `docs/redivis/release-v1/`
- On the data machine only: `runs/c101/`, `runs/license_reads/s2238/`, `runs/s2238_*`, `warehouse/raw/rte_eco2mix/`.
