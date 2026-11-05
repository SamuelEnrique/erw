# Session 2635 report: the licenses' fifty-second round (REGIDESO, PUB and NSO Kiribati need written permission)

25 October 2026, about 07:56 to 08:00 UTC, on lab-desktop (the data machine), chain 131, unattended. Precheck passed (`runs/c131/pre2635.out`). Model spend USD 0. Pulls: 3 requests of 20.

## Read these first

- **`license_verdicts.csv` was read first.** This chain's one table so far (the Cayman Islands) has ESO's verdict (session 2633). This round takes the other publishers it met that could be read. Sessions 2636 and 2637 run after this one.
- **Three home pages read** (reads 1285 to 1287); www.regideso.bi and www.pub.com.ki redirected to their bare names, and nothing more was asked of either.
- **Three verdicts** (`runs/c131/s2635/verdicts.py`); all **need written permission**:
  - **REGIDESO, Burundi** (read 1285): "2026© REGIDESO. Tous droit reserves", a copyright line with no reuse statement.
  - **PUB, Kiribati** (read 1287): "© Copyright Public Utilities Board 2025. All Rights Reserved."
  - **NSO Kiribati** (read 1286): its home page carries no statement on reuse at all (RGGI's form, no sentence). The code checks that the page names no copyright, terms or reproduction.
  - The ERW holds no table of any of them.
- **Not given a verdict:**
  - INSEED (the Comoros): its certificate fails.
  - SONELEC: its name does not resolve.
  - INSBU (Burundi): its site is drawn by script.
- **The record:** 575 tables, 226 publishers with a verdict, 1,285 requests, 0 problems. Tests 152, 205, 207 and 378 pass.

## Requests (3 of 20)

| n | What | Outcome |
|---|---|---|
| 1 to 3 | the home pages of www.regideso.bi, nso.gov.ki and www.pub.com.ki | 200 |

Reads recorded: 1285 to 1287. No robots file asked again: each host's was read in sessions 2631 and 2632.

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- Changed: `warehouse/metadata/license_reads.csv` (reads 1285 to 1287), `warehouse/metadata/license_verdicts.csv` (three rows), `docs/licenses.md`. New: this report.
- On the data machine only: `runs/c131/s2635/`, `runs/license_reads/s2635/`.
