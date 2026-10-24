# Session 2371 report: the next file first; Sri Lanka's stations, capacity, generation and maximum demand (CEB's Statistical Digest)

24 October 2026, from 08:37 UTC, on lab-desktop (the data machine), the first session of `queue/done/112-day-13-november-data-sri-lanka-nigeria-ghana-jordan.md`, unattended. Precheck passed (`runs/c112/pre2371.out`). Model spend USD 0. Pulls: 13 of 15 (below).

## Read these first

- **Chain 112 taken** at 08:36 UTC by chain 059's agent when chain 108 landed (f24f579b), under the owner's instruction for that run: run the file the queue step prints. Chains 109 and 110 run beside it under other agents, who were told.
- **The next file first,** pushed to main on its own before any other work (be9bd4cb, with snapshots): `queue/next/113-day-14-november-data-uganda-tanzania-costa-rica-bolivia.md`, sessions 2385 to 2398, machine: data.
  - Its sources: Uganda (ERA), Tanzania (EWURA or TANESCO), Costa Rica (CENCE, ICE) and Bolivia (CNDC), none held and none planned by chains 057 to 112.
  - It carries 112's rules and chain 110's closed hosts.
- **PUCSL's dispatch dashboard was left.**
  - www.pucsl.gov.lk's robots file allows the reader (read 584). Its data portal links the dashboard at gendata.pucsl.gov.lk (read 586), which has no robots file (read 587).
  - Its figures load only in the browser, through its script chunks (21 on the generation profile page, session 2375; this line first said a dozen); the page's own script names no data address (read 590). Chain 109 closed eSett for the same pattern.
  - PUCSL's pages state no terms of reuse.
- **One internal table in its place:** `ceb_srilanka_electricity_annual`, from page 3 of the Ceylon Electricity Board's Statistical Digest 2025. It is written, validated, archived, in coverage (sector power), and held from the live set. 80 rows, 2024 and 2025:
  - power stations and installed capacity, by owner (CEB, the independent producers, all) and source (major hydro, oil, coal, wind, mini hydro, other NCRE, grid-connected solar);
  - net generation, likewise, with two rows of its own: small islands, and rooftop solar's energy exported to the network, which CEB prints under the IPPs (session 2375 corrected this line, which listed both among the station and capacity sources);
  - the day and night maximum demand.
  - Read with pdfplumber's table extraction. Each owner's sources add to its total, and CEB's and the producers' totals to the Total row, within 1.5.
- **Why only two years:** the 2023 digest's text is in CID-encoded fonts that do not extract, and the 2022 digest's generation table merges its rows into one cell. Both were fetched (2 requests) and are not used; a later session could read the 2022 digest's capacity table, which is clean.
- **License: internal.** Neither the digest nor CEB's pages read state terms of reuse (reads 591 to 593), so the table is internal until a ruling and no verdict is recorded.
  - CEB's robots file allows every path and asks a crawl delay of 30 seconds, which was kept (read 591).

## The cross-check (`runs/c112/s2371/cross.py`, `cross.out`; tables read past their header lines, never with `comment="#"`)

- CEB's net generation is 16.802 TWh (2024) and 17.812 TWh (2025).
- Ember's demand for Sri Lanka is 17.07 and 17.25 TWh. CEB's figure is 1.57 per cent below in 2024 and 3.26 per cent above in 2025; the 2025 rooftop solar (1,674 GWh, nearly double 2024's) is part of the difference.
- Installed capacity: 4,651 MW (2024, restated) and 4,814 MW (2025). Night maximum demand: 2,673.0 and 2,895.9 MW.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.pucsl.gov.lk | 3 | robots, the sitemap, the data portal |
| gendata.pucsl.gov.lk | 4 | robots (404), two pages, one script |
| www.ceb.lk | 6 | robots, two pages, three digests (2025, 2023, 2022); 30 s or more apart |

## Errors

- None.

## Decisions made without you

- **CEB's digest in place of PUCSL's dashboard;** two years only, for the reasons above.
- **The table internal** while CEB's terms are unstated.
- **Test 205's bound raised by 40,** for this chain's reads beside chains 109's and 110's.

## For Samuel's ruling

- **CEB's Statistical Digest:** public or internal? It states no terms.

## Files

- New:
  - `warehouse/connectors/ceb_srilanka.py`
  - `tests/test_session2371.py`
  - this report
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`
  - `warehouse/metadata/license_reads.csv` (584 to 593), `license_tables.csv`, `docs/licenses.md`
  - the coverage, sources and archive manifest files
  - `tests/test_session205.py`
- On the data machine only: `runs/c112/`, `runs/license_reads/s2371/`.
