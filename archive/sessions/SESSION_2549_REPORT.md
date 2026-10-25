# Session 2549 report: Brunei's electricity, not taken (DEPS lists its electricity workbooks, but each address answers 404)

24 October 2026, about 23:02 to 23:06 UTC, on lab-desktop (the data machine), chain 125, unattended. Precheck passed (`runs/c125/pre2549.out`). Model spend USD 0. Pulls: 8 requests of 15 (4 by the probe, 4 by fetches, each answered 404).

## Read these first

- **The ERW holds no Bruneian source.**
- **The hosts:** deps.mofe.gov.bn redirects to www.deps.gov.bn, which has no robots file (read 1030); www.des.gov.bn has none (read 1031); www.me.gov.bn did not answer (a connection timeout, read 1032).
- **DEPS's eData Library** (read 1033) lists "Production and Consumption of Electricity" as yearly and quarterly Excel workbooks (and states "Copyright Government of Brunei Darussalam. All Right Reserved."). Both workbooks answer HTTP 404 at the page's addresses on www.deps.gov.bn, the yearly one again on deps.mofe.gov.bn, and the Statistical Yearbook's PDF (found by search) answers 404 too. The 404 pages were saved by the raw capture under `warehouse/raw/deps_bn/`; no connector reads them.
- **Not taken.** The figures exist (a search found DEPS's consumption by sector republished by a data vendor), but no address of DEPS's serves them today.

## Requests (8 of 15)

| n | What | Outcome |
|---|---|---|
| 1 to 3 | deps.mofe.gov.bn (by www.deps.gov.bn), www.des.gov.bn and www.me.gov.bn robots files | 404, 404, a timeout |
| 4 | DEPS's eData Library page | 200 |
| 5, 6 | the yearly and quarterly workbooks on www.deps.gov.bn | 404, 404 |
| 7 | the yearly workbook on deps.mofe.gov.bn | 404 |
| 8 | the Statistical Yearbook's PDF | 404 |

Reads recorded: 1030 to 1033. Two web searches found DEPS's library and yearbook; they reached no publisher's host.

## Decisions made without you

- **No table for Brunei;** a later chain may ask DEPS again, its files may be restored.

## For Samuel's ruling

- None.

## Files

- Changed: `warehouse/metadata/license_reads.csv` (reads 1030 to 1033), `docs/licenses.md`. New: this report.
- On the data machine only: `runs/c125/s2549/`, `warehouse/raw/deps_bn/` (the 404 pages).
