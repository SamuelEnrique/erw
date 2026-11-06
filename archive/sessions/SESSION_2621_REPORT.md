# Session 2621 report: the licenses' fifty-first round (GBoS, PURA, the Government of Palau and ARSE need written permission)

25 October 2026, about 06:45 to 06:50 UTC, on lab-desktop (the data machine), chain 130, unattended. Precheck passed (`runs/c130/pre2621.out`). Model spend USD 0. Pulls: 7 requests of 20.

## Read these first

- **`license_verdicts.csv` was read first.** This chain's publishers with a verdict already: LERC and LEC (session 2616) and NAWEC (session 2617). This round takes the others it met that could be read. Sessions 2622 and 2623 run after this one, so their publishers are left to their own sessions or the next round.
- **Three sites' page lists** hold no terms page: PURA's (read 1247), the Government of Palau's (read 1248) and ARSE's (read 1249). Their home pages were read instead (reads 1250 to 1252). ARSE's links its "Terme & conditions" (read 1253).
- **Four verdicts** (`runs/c130/s2621/verdicts.py`), each sentence cut by code; all **need written permission**:
  - **GBoS, the Gambia** (read 1233, session 2617's read of its home page): "Copyright © 2026", with no reuse statement. Read 1233's outcome was set to exactly `read`; it had been "read: its data portal's categories; a copyright line".
  - **PURA, the Gambia** (read 1250): "© The Gambia Public Utilities Regulatory Authority 2026", with no terms page.
  - **The Government of Palau** (read 1251): "© 2026 PalauGov.pw", with no terms or disclaimer page.
  - **ARSE, Chad** (read 1253): a general Terms and Conditions template that governs the site's use and grants no licence to reuse its content (RGGI's form).
  - The ERW holds no table of any of them.
- **Not given a verdict:**
  - LISGIS (Liberia) and INSEED (Chad): their sites are drawn by script, with no terms in their bytes.
  - PPUC (Palau): no terms page read, and the ERW holds nothing of it.
- **The record:** 573 tables, 221 publishers with a verdict, 1,251 requests, 0 problems. Tests 152, 205, 207 and 378 pass.

## Requests (7 of 20)

| n | What | Outcome |
|---|---|---|
| 1 to 3 | the page lists of pura.gm, www.palaugov.pw and www.arse.td (searches for terms pages) | 200 |
| 4 to 6 | their home pages (ARSE's redirected to arse.td) | 200 |
| 7 | ARSE's Terms & conditions | 200 |

Reads recorded: 1247 to 1253. No robots file asked again: each host's was read in sessions 2617 to 2619 (reads 1232, 1238 and 1246).

## Decisions made without you

- **GBoS's verdict from session 2617's read,** its outcome set to `read` (session 2593's form).

## For Samuel's ruling

- None new.

## Files

- Changed: `warehouse/metadata/license_reads.csv` (reads 1247 to 1253; read 1233's outcome), `warehouse/metadata/license_verdicts.csv` (four rows), `docs/licenses.md`. New: this report.
- On the data machine only: `runs/c130/s2621/`, `runs/license_reads/s2621/`.
