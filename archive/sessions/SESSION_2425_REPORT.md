# Session 2425 report: the licenses' thirty-seventh round

24 October 2026, from 11:14 UTC, on lab-desktop (the data machine), a session of `queue/done/115-day-16-november-data-zambia-botswana-mongolia-cambodia.md`. Precheck passed (`runs/c115/precheck_2425.out`). Model spend USD 0. Pulls: none. Every page this round needed was read by sessions 2420 to 2423 and saved, and the round records those reads.

## Read these first

- **Main merged into the branch first** (chain 113 had landed, `39caf1b8`, reads to 702):
  - **The conflicts:** one in `docs/coverage.md`, `grid_stress_yearly`'s row, whose only difference was session 2424's Method cell. Joined, with main's new Iceland row kept.
  - **The licenses page** was rebuilt (523 tables, 0 problems).
  - **Duplicates:** none in sources, coverage, the archive manifest, the license files or the coverage page.
- **This chain's reads, 703 to 723 (21):** sessions 2420 to 2423's robots files, listings and terms pages; the data downloads are not counted, as in chains 102, 105 and 110. Chain 114 holds 703 to 762 on its branch: whichever chain lands second renumbers.
- **Three verdicts:**
  - **Statistics Botswana: may be public** (read 709, its terms of use): users "may utilise the information as they wish, provided that they acknowledge Statistics Botswana as the source of the basic data". They must also say an application or analysis is their own.
    - `statsbots_botswana_electricity_monthly` is now public: the connector's license lines changed, and the table was written again offline (the same 383 rows) with its metadata rows replaced by key.
    - It is added to the release package's held list and its rows (the release check passes); flag and verdict agree.
    - It is not yet in the Stanford draft; session 2429 uploads it.
  - **The Energy Regulation Board of Zambia: needs written permission** (read 705, the home page's footer: "Copyright 2026 All Rights Reserved", no terms linked). As KPX's (read 547) and chain 114's NamPower; `erb_zambia_electricity_annual` stays internal.
  - **ESCO, Georgia: needs written permission** (read 722, the footer: "© 2016 ESCO ALL RIGHTS RESERVED"). `esco_georgia_electricity_monthly` stays internal.
- **No verdict for ERC Mongolia:** its pages show only a copyright sign, with no terms and no "all rights reserved", as chain 110 left MakStat. `erc_mongolia_electricity_annual` stays internal ("not settled").
- **`tests/test_session205.py`'s bound raised by 40:** 682 later reads met the bound of 682 exactly; it is now 722. Tests 205 and 152 pass.
- **Licenses check:** 523 tables, 151 publishers with a verdict, 721 requests, 0 problems.

## Errors

- **The verdict's first quote for ESCO read "(c)"** where the page has "©". Corrected to the page's text before the commit.
- **Test 205 failed once** because `docs/licenses.md` had not been rebuilt after the reads were recorded. Rebuilt, and it passes.
- **The rewrite's metadata patch conflicted** (the main checkout lags). The rows were replaced by key with `runs/c066/s2066/replace_rows_many.py`, one row each.

## Decisions made without you

- **"All Rights Reserved" footers recorded as needing written permission,** as chain 114 did for NamPower. Session 2420's report called ERB's an "internal" reading. The two agree on the table, which stays internal, and differ only in whether a verdict is written.
- **The bound raised by 40 though not yet exceeded,** to leave room for chain 114's reads at the next merge.

## For Samuel's ruling

- None new. ERB's and ESCO's terms remain open questions (sessions 2420 and 2423).

## Files

- Changed:
  - `warehouse/metadata/license_reads.csv`, `license_verdicts.csv`, `license_tables.csv`, `docs/licenses.md`;
  - `tests/test_session205.py`, `warehouse/redivis/release_v1.py`, `docs/redivis/release-v1/`;
  - `warehouse/connectors/statsbots_botswana.py`;
  - `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`;
  - the merge's files.
- New: this report.
- On the data machine only: `runs/c115/s2425/`.
