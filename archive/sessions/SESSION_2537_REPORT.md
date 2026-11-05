# Session 2537 report: the licenses' forty-fifth round (five publishers need written permission; SingStat may be public, and its table is made public)

24 October 2026, about 21:24 to 21:33 UTC, on lab-desktop (the data machine), chain 124, unattended. Precheck passed (`runs/c124/pre2537.out`). Model spend USD 0. Pulls: 6 requests of 20.

## Read these first

- **`license_verdicts.csv` was read first:** none of this chain's publishers had a verdict; SingStat had none (session 2308 could not read its terms, drawn by script).
- **Six verdicts,** each sentence cut by code from the page as saved (`runs/c124/s2537/verdicts.py`):
  - **INSTAT (Madagascar)** (read 973, its home page): "Copyright INSTAT 2026. Tous les droits sont reserves". **Needs written permission** (a copyright line with no reuse statement, read as ZIMSTAT's in session 2495). `instat_madagascar_electricity_monthly` stays internal.
  - **ARSEL (Cameroon)** (read 978, its home page): "All rights reserved", after "Copyright 2025 ARSEL" and a dash the record does not quote. **Needs written permission.** `arsel_cameroon_electricity_annual` stays internal.
  - **INSEED (Togo)** (read 996, its home page): "Copyright 2024 INSEED - Tous droits reserves". **Needs written permission.** `inseed_togo_electricity_annual` stays internal.
  - **SBEE** and **ARE (Benin)** (reads 988 and 991, their home pages): "Tous droits reserves". **Needs written permission.** The ERW holds no table of theirs.
  - **SingStat (Singapore)** (read 1001, its terms of use, whose text the page holds in a script, not in its HTML): "Use of Datasets made available through the Services is subject to the terms of the Singapore Open Data Licence ... the terms of the ODL shall prevail." Clause 10 grants "a free, worldwide, revocable and non-exclusive right" to copy and distribute the Contents and to derive products, "for sale or otherwise", the source credited. **May be public,** sold or not.
- **`singstat_singapore_electricity` made public** under test 378's rule (no table flagged internal where its verdict reads may be public): the connector's docstring, header and registration say public and credit SingStat; the table was written again offline from its saved answers (run `20261024T212900Z`, 1,009 rows as before, validated, archived unchanged), its rows in `sources.csv`, `coverage.csv` and `docs/coverage.md` replaced, and its rows added to the release package (`docs/redivis/release-v1/`). **The question goes to you** (chain 114's rule).
- **The verdicts' reads now have the outcome exactly `read`** (test 205). Their earlier notes: read 973 "Copyright INSTAT 2026. Tous les droits sont reserves; no terms of reuse linked"; 978 "Copyright 2025 ARSEL"; 988 "2026 SBEE. Tous droits reserves"; 991 "2026 ARE Benin. Tous droits reserves"; 996 "Copyright 2024 INSEED - Tous droits reserves; the monthly bulletin and the national yearbook 2024 listed".
- **Not given a verdict:**
  - **CSP Latvia:** stat.gov.lv answered HTTP 403 at its robots file (read 997), so nothing more was asked; it joins the closed hosts.
  - **ASK (Kosovo):** no robots file (read 999), and its home page links no terms of reuse (read 1002). `ask_kosovo_electricity_monthly` stays internal.
  - **Statistics Greenland:** stat.gl's robots address redirects to a page of the site (read 1000); no terms page was found by search.
  - **The Danish Energy Agency:** a search found no terms page.
  - **JIRAMA, INStaD and the DGE (Benin), CEET:** no terms page read.
- **The record:** 552 tables, 178 publishers with a verdict, 1,000 requests, 0 problems. The license and release tests pass (119, `runs/c124/s2537/tests.out`), test 378 among them.

## Requests (6 of 20)

| n | What | Outcome |
|---|---|---|
| 1 to 4 | stat.gov.lv, www.singstat.gov.sg, ask.rks-gov.net and stat.gl robots files | 403, 200, 404, a redirect to a page |
| 5 | SingStat's terms of use | 200 |
| 6 | ASK's home page | 200 |

Reads recorded: 997 to 1002. Five web searches looked for terms pages; they reached no publisher's host.

## Decisions made without you

- **A copyright line with no reuse statement read as needing written permission,** as ZIMSTAT's was.
- **SingStat's table public now,** not held for a ruling: its terms grant reuse with the source credited, which test 378 requires to be flagged public.
- **ARSEL's sentence cut short** of its dash, by code, rather than quoted with it.

## For Samuel's ruling

- **`singstat_singapore_electricity` is public** under SingStat's terms of use and the Singapore Open Data Licence (chain 114's rule: the question goes to you). It is in the release package; nothing is released.

## Files

- Changed: `warehouse/metadata/license_verdicts.csv` (six rows), `warehouse/metadata/license_reads.csv` (reads 997 to 1002; five outcomes), `docs/licenses.md`; `warehouse/connectors/singstat_electricity.py`; the metadata files and `docs/redivis/release-v1/` (SingStat's table). New: this report.
- On the data machine only: `runs/c124/s2537/`, `warehouse/output/singstat_singapore_electricity.csv` (rewritten).
