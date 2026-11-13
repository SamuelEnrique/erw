# Session 3894 report, with 3895 to 3898 and 3902: the siting gaps, the tab, the drafts and the records

Energy Research Warehouse (ERW). Chain 227, data machine (lab-desktop), 13 November 2026 11:50 to 12:00 UTC. Opus 5.5. Model spend USD 0. Requests: Redivis's API, one `--tables` run of one table; no publisher asked (session 3888's 14 requests are its own: caiso.com's robots file was its fourteenth, read for the Board's decision, whose page was then not guessed).

## 3894 to 3897, the siting gaps a public US source can close

- **Done early, in session 3888:** Utah's R746-318 (5 steps under PACE) and the CAISO's draft final proposal (4 steps). They were the two rows a public document could fill without a ruling.
- **Looked for again and still closed:**
  - ERCOT: the Planning Guide's current Section 9 is the 11 July 2026 version held (the current-guide page, read by session 3888).
  - NYISO and ISO-NE: both operators' terms ask written permission. New York's Case 26-E-0045 was read at 05:49 UTC (session 3848) and states no clock.
  - SPP's Kansas row (Evergy's LLPS): the KCC holds no tariff library, and its docket search names no document address (session 3862). Evergy's own site blocked the research pass.
  - Reserve margins outside the CAISO and ERCOT: NERC's robots file names ClaudeBot; PJM's data terms need a paid license; SPP's and the other ISOs' terms bar commercial reuse or ask permission.
  - The CAISO Board's decision of 28 October: caiso.com's robots file allows all but `/resources/`, but no page the ERW has read names the Board's documents, so no address was guessed.
- So sessions 3895 to 3897 had no row of their own, and none was a session.

## 3898, the tab and the siting gaps file

- **On the gate's build of `b0d16d2e2`** (chain 226's landing, which carried session 3888's work), internal view, 1280 and 390 px: the CAISO rows' "filed steps" hover reads as before, because the draft final proposal's steps print no single duration. No tab row is in Utah. No visible cell moved, and the snapshots before and after the landing showed 0 differences.
- **A new dated state section** in `docs/reviews/siting-gaps.md` ("13 November 2026, late morning (chain 227)"), on `wip/c227-data`.

## 3902, the drafts and the records (done early)

- **`large_load_connection_rules` on the warehouse's own Redivis draft:** 84 rows, Redivis count 84; `erw_headers` 2,796 lines (8 for the table). Nothing released.
- **The Stanford draft:** not asked. The table's ERW verdict is unsettled, which the uploader refuses (sessions 3853 and 3869).
- **The records:** `redivis_uploads.csv` moved onto the branch from the main checkout, which was put back after `lock.py status` read the lock free. Tests 410, 275, 1008, 1009 and 1001: 38 passed. `build_llms.py` ran after the table's last coverage row (session 3888).

## Decisions made without you

- **No address guessed for the CAISO Board's decision.** A guessed address costs a request on the publisher's server for a likely miss.

## For Samuel's ruling

- None new.
