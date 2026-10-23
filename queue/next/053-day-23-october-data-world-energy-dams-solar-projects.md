# Chain of the day of 23 October 2026: sessions 937 to 950, data machine (lab-desktop), unattended: the world's coal, energy and emissions, the non-powered dams, solar projects' costs and output, hybrid PPAs and REC prices, producer prices, the licenses' seventh round

machine: data

Written by session 923, the first session of `queue/done/052-day-23-october-data-world-oil-reactors-stocks.md`, under chain 045's rule ("the next file is written and pushed to `queue/next` at the START of the chain"), at the owner's instruction for chain 045 ("at least twelve sessions, machine: data, ... the sources and gaps ... in chain 040's form"). The next free number in `queue/next` and `queue/done` was 053. Sessions 937 to 950 were free in every queue file and branch when this was written (the code machine holds 700 to 749, the laptop 800 to 849, the old laptop 1000 on). Session 936 of chain 052 updates it at chain 052's end. Model: Opus 5.5, high effort.

Each source session follows chain 040's form:

- the publisher's robots file asked alone and read before any other path of its host, and its terms (EIA's are record 1, public);
- a probe, and a trial with `--out-dir` from the main checkout, whose saved pages the write reuses (`--offline`);
- a cross-check, reading every ERW table past its header lines, never with pandas' `comment="#"` (session 917);
- `runs/c045/write_table.sh` (connectors), `runs/c051/write_derived.sh` (derived builders), `runs/c045/finish_table.sh`, `runs/c045/method_cells.sh`, and the resolvers `runs/union_resolve.py`, `runs/c046/take_theirs.py`, `runs/c048/ours_with_theirs_table.py` on the data machine, each given the chain's worktree (`WT=`, `WTN=`); stage the branch (`git add`) before a write, so its metadata patch applies; a metadata patch that meets the last session's rows is joined with `runs/union_resolve.py` (session 916);
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/052-day-23-october-data-world-oil-reactors-stocks.md` hold, word for word, among them:

- **ERCOT's robots file disallows `/misapp` and `/misdownload`**, and **EIA's disallows `/archive/`**: neither is asked.
- **Hosts that refused the ERW's reader are not asked again without a ruling:** api.census.gov, www.phmsa.dot.gov, FERC's policy page, EPA's bulk file API without a key, and apps.cer-rec.gc.ca (it reset the connection to its robots file, session 910).
- **Keys not held:** `EPA_CAMD_API_KEY`, `NREL_API_KEY` or `DATA_GOV_API_KEY`; a session that needs one stops and says so, without signing up.
- **HydroSource's download form is not filled**; ORNL's files are taken by their public links, pending the owner's word. HydroSource asks a crawl delay of 10 s.
- **A new read of a publisher already in `license_reads.csv` gets a label of its own**; a session checks `license_verdicts.csv` before reading a publisher's terms.
- **A table that a page reads is never rewritten to add rows from another file.**
- **A request cap on the Redivis uploader stops between tables, never inside one**, budgeted by session 892's measure (about 28 a run and 6 a table; session 919: 98 for fifteen tables); an empty `erw_headers` is rebuilt in full from disk, never merged.
- **Session 937 begins by writing `queue/next/<next free number>-<slug>.md`** for this machine (at least twelve sessions, machine: data, numbered from 951), commits it alone and pushes it to main before any other work; session 950 updates it.

Read first: chain 052's note (written by session 936), sessions 923 to 936's reports, `docs/state/note_2026-10-30_data.md`, `docs/reviews/siting-gaps.md`.

## Session 937: the world's coal, total energy and emissions (EIA's International Energy Statistics)

Long end 1:30. Pulls: none if the bulk file `warehouse/raw/eia_intl_bulk/` (`INTL.zip`) is the newest EIA serves; at most 4 requests to ask whether a newer one is out (EIA's robots file first). Sessions 909 and 923 took electricity, oil and gas from it; this takes every country's coal production, consumption, reserves and trade, total primary energy production and consumption, and energy-related CO2 emissions, annual, as tables of their own (`eia_intl_bulk.py`); cross-check: the U.S. rows against `eia_coal_production_annual` and `eia_co2_state_annual`, and the world against the countries summed.

## Session 938: hydropower potential at non-powered dams (ORNL)

Long end 1:30. Pulls: at most 10 requests, 11 seconds apart. HydroSource's "U.S. Hydropower Potential from Existing Non-Powered Dams (greater than 1 MW)" (its sitemap lists it), an entities table; cross-check: the dams against `ornl_hydropower_pipeline`'s non-powered dam projects by name and state.

## Session 939: utility-scale solar projects' costs and output (Berkeley Lab)

Long end 1:30. Pulls: none (the 2025 data update session 915 saved, `warehouse/raw/lbnl_ppa_prices/`). The workbook's "Individual_Project_Data" sheet (each project's capacity, technology, tracking, region, operation year, cost and capacity factor where given) as an entities table; cross-check: the projects against `uspvdb_solar_facilities` and `eia860m_operating_generators` by EIA plant id.

## Session 940: hybrid PPA prices and REC prices (Berkeley Lab)

Long end 1:30. Pulls: none (the files session 915 saved). The solar file's "PV+Battery Hybrid PPA Price" and the wind file's "REC Prices" sheets, as tables of their own (the PPAs as events, as `lbnl_ppa_prices`; the REC prices as series); cross-check: the hybrid PPAs' count and megawatts by year against the sheet's own summary, the REC prices against any the file sums.

## Session 941: producer prices for electricity and gas (the Bureau of Labor Statistics)

Long end 1:30. Pulls: at most 15 requests. BLS's Producer Price Index series for electric power generation, transmission and distribution, natural gas distribution and the industrial electric power and gas commodities, robots and terms first; BLS's public API v1 needs no key (and allows few requests a day); a series table of its own; cross-check: the index's movements against `eia_retail_electricity_prices` and `eia_gas_prices_state_monthly` (U.S.) over the same months.

## Session 942: the licenses' seventh round

Long end 1:30. Pulls: at most 20 requests, two a host. The publishers chains 046 to 052 did not reach, those of sessions 937 to 941 first; `license_verdicts.csv` read first.

## Sessions 943 and 944: two more sources

Long end 1:30 each. Pulls: at most 20 requests each. A public source the ERW does not hold, chosen by each session; say why.

## Session 945: a gap of the siting review

Long end 1:30. Pulls: at most 10 requests. One open row of `docs/reviews/siting-gaps.md` that a public table can close without a ruling (not substations and lines, not ERCOT's robots-held paths), as a derived table with its method note; read the code machine's latest state sections first, since it may have drawn the row on the tab (session 917 met chain 072's); else the session says why none can.

## Session 946: method notes for this chain's tables

Long end 1:00. Pulls: none. As session 918: each note's checks against the code and the table, every contradiction acted on.

## Session 947: the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 150 requests, in whole runs under the cap. First any table of chain 052 not yet in the draft or stale there (session 933's report names them); then this chain's public tables; `--reconcile`; the release note extended. Nothing released.

## Session 948: seven days of the data jobs

Long end 1:00. Pulls: GitHub's API, at most 30 requests (with this machine's token for reads). As session 920: each data job's last seven days, each failure with its step and first error line; a fault of this repository's code fixed with its test.

## Session 949: the package's and the site's records

Long end 1:00. Pulls: none. `python package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009 against this chain's tables and verdicts; rebuilt if stale.

## Session 950: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_2026-11-01_data.md`, in session 683's form.
2. The next file (written by session 937) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC. If the check run's merge step fails because main moved, merge origin/main again and push the branch again (session 922).
4. Then `python scripts/chain_queue.py next`.
