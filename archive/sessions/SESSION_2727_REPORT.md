# Session 2727 report: the licenses' fifty-eighth round (Qulliq Energy and Yukon Energy need written permission)

25 October 2026, about 19:26 to 19:29 UTC, on lab-desktop (the data machine), chain 137, unattended. Precheck passed (`runs/c137/pre2727.out`). Model spend USD 0. Pulls: 2 requests of 20 (Qulliq Energy's robots file and legal page).

## Read these first

- **`license_verdicts.csv` was read first.** None of this chain's publishers had a verdict.
- **Two verdicts** (`runs/c137/s2727/verdicts.py`), each line cut by code with session 2495's `cut`:

  | Publisher | Read | The line | Verdict |
  |---|---|---|---|
  | Qulliq Energy Corporation | 1463 (its legal page, read here; www.qec.nu.ca's robots file again, read 1462) | "The website and its contents are intended solely for personal non-commercial use. Downloading of any of the website's contents or of any materials shall be limited to one copy on a single computer for your personal, non-commercial use only." | needs written permission |
  | Yukon Energy Corporation | 1454 (session 2723's read of its page Electricity Generation; its outcome set to exactly `read` first) | "This material is provided 'as is' for informational purposes only." A disclaimer with no statement of reuse, as the workbook's own Disclaimer sheet says, read as the IHSI's (session 2691). | needs written permission |

- **Not given a verdict:**
  - the Government of Prince Edward Island, whose site served a bot challenge (session 2722);
  - NTPC and the NWT Bureau of Statistics, whose terms were not read because there was no file to take (session 2724).
- **The record:** 593 tables, 247 publishers with a verdict, 0 problems. Tests 378, 205 and 152 pass.

## Decisions made without you

- **Yukon Energy's disclaimer read as needing permission:** it grants no reuse, as the IHSI's copyright line did not.

## For Samuel's ruling

- **Yukon Energy:** a permission request, or the ruling on its hourly workbook (session 2723), would open Yukon's grid hour by hour.

## Files

- New: this report. Changed: `warehouse/metadata/license_verdicts.csv` (two rows), `warehouse/metadata/license_reads.csv` (reads 1462 and 1463, and one outcome), `docs/licenses.md`.
- On the data machine only: `runs/c137/s2727/`, `runs/license_reads/s2727/`.
