# Session 2299 report: the licenses' twenty-ninth round

24 October 2026, from 06:23 UTC, on lab-desktop (the data machine), a session of `queue/done/105-day-8-november-data-mexico-india-peru-korea.md`. Model spend USD 0.

Pulls: 4 requests of 20, two pages a host:
- cea.nic.in: its Website Policies page, and the Copyright Policy PDF it lists;
- www.kpx.or.kr: its English home page, and its Korean home page.

## Read these first

- **The Central Electricity Authority (India): needs written permission.** Its Copyright Policy (read 500) says the content "may be reproduced free of charge, subject to the following conditions", the first being "Users must obtain prior permission by sending an email request to the designated CEA contact". It also requires:
  - no modification that alters the meaning;
  - CEA acknowledged as the source;
  - no misleading use;
  - third-party material excepted.

  `cea_india_psp_annual` stays internal.
- **The Korea Power Exchange: needs written permission by default.**
  - Neither home page links a copyright policy or shows a KOGL (Korea Open Government License) mark.
  - Both carry "COPYRIGHT(C) ... KOREA POWER EXCHANGE(KPX) ALL RIGHTS RESERVED" (2022 on the English page, 2021 on the Korean page, read 501).
  - EPSIS's pages carry the same notice (read 497).
  - KPX's sets on data.go.kr may carry a licence there, but they need a key the ERW does not hold.

  `kpx_korea_generation_annual` and `kpx_korea_demand_monthly` stay internal.
- **This chain's reads, 483 to 501 (19):**
  - **Sessions 2294 to 2297's own requests:** robots files, home pages, listings and the pages that carried a figure. The data downloads (CEA's six PDFs, EPSIS's demand pages) are not counted as reads.
  - **This round's four.**
  - **Numbering:** they follow main's 482, after chain 103's landing, merged into this branch first. Chain 104's 17 reads (462 to 478 on its branch) will be renumbered by whichever of the two chains lands second.
- **Mexico's and Peru's publishers** (SENER's information system, COES) got reads but no verdict: no terms were found, and neither gave a table.
- **Grid-India and www.datos.gob.mx** refused the reader (reads 483, 487, 488).
- **`tests/test_session205.py`'s bound raised by 20.** The record now holds 460 reads after the first 41; with chain 104's 17 it will hold 477, against 482 now allowed.
- **The record:** 482 tables, 129 publishers with a verdict, licenses check 0 problems; the license tests (39 files, 383 tests) OK.
- **The merge of origin/main** (chain 103's landing and the queue files 106 and 108) came first. Its one conflict was `docs/licenses.md`, which `licenses.py write` generates and was rebuilt. There are no duplicated rows in `sources.csv`, `coverage.csv`, `archive_manifest.csv` or `license_tables.csv` (482 tables).

## Errors

- None.

## Decisions made without you

- **The data downloads are not counted as license reads,** as chain 102 counted its own.
- **KPX's "all rights reserved", with no licence stated, is read as needing written permission,** as for other publishers with no terms.

## For Samuel's ruling

- **Ask CEA for permission?** Its policy asks for an email to "the designated CEA contact" (no address is given on the policy). No letter was sent.
- **Ask KPX, or read its data.go.kr licence** (which needs a key the ERW does not hold)?

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv` (483 to 501), `license_verdicts.csv` (two verdicts), `docs/licenses.md`, `tests/test_session205.py`.
- On the data machine only:
  - `runs/c105/s2299/` (the probe, `record.py`, the license outputs, the tests' output);
  - `runs/license_reads/s2299/`;
  - `runs/c105/merge1*.out`.
