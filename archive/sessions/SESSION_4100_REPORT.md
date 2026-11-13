# Session 4100 report: the chain file, the next file, the ground of the licensing sweep

Energy Research Warehouse (ERW). Chain 229 (`queue/done/229-day-13-november-desktop-window3-licenses.md`), session 1 of 50, lab-desktop third window, 13 November 2026 09:27 to 09:40 UTC. Opus 5.5. Model spend USD 0.

## The queue

- **Chain file** written as 228; window B's `228-...-window2-landings.md` reached main first (09:31), so it was pushed as **229** (`4bd2deef5`).
- **Taken by hand** (`2c031305c`): `chain_queue.py next --file 229-...` refuses the mark `machine: lab-desktop-window3` on a data machine (exit 2, dry run). The same move and message were made in a queue worktree (`erw-w3-queue`), so the main checkout was not touched.
- **Next file** pushed as 230 at `6afa79427`. Window B renumbered its own next file to 230 a moment before, so mine was renumbered **231** (`ed0634ecc`): `queue/next/231-day-14-november-desktop-window3-licenses-continued.md`, sessions 4150 to 4165.
- **Sessions 4100 to 4199** are free: no `SESSION_41xx` file, and no commit on any branch names one.

## The precheck

- **From the worktree** (`erw-w3-4100`): failed on `daily_cap`. A worktree holds no cost ledger, and Supabase's copy did not answer in that run. The run recorded idle.
- **From the main checkout**: passed, 6 of 6. The machine is back on duty for "session 4100" until 14 November 01:33 UTC, so the idle email is not sent (`alert.py ready` skips a machine back on duty). Only an ignored report under `runs/precheck/` was written.

## The ground (on `origin/main` at `ed0634ecc`)

- **`docs/licenses.md` is current:** `licenses.py write` regenerates it with no change, and `licenses.py check` exits 0 (648 tables, 259 publishers with a verdict, 1,649 requests in the record).
- **The document's own counts:**
  - 528 tables agree;
  - 47 are settled by a ruling: 45 "license needed" (flag public, sentence asks permission, owner's ruling of 12 October) and 2 kept internal;
  - 0 disagree;
  - 71 are not settled;
  - 1 is internal by the ERW's own choice.
  - ERW verdict: 476 public, 115 internal, 57 unsettled.
- **This chain's counts** (`erw-w3-work/ground.py`):
  - **No verdict: 85 tables** with at least one publisher never read (19 of them flagged public). The document counts 71 because it lists a table only when the read publishers would allow it.
  - **Stale verdict: 362 tables** rest on a publisher read before 14 October (more than 30 days ago). All 259 verdicts are from October 2026.
  - **Flag disagrees with the verdict: 45 tables**, all settled by the "license needed" ruling (flag public, verdict "needs written permission"). No open disagreement.
- **Flag and registry:** 5 coverage flags differ from their `sources.csv` rows, each by design:
  - `energy_deals`, `news_index` and `nyiso_load_queue` declare `License: public` in their headers;
  - `policy_reads_evidence` declares internal;
  - `price_board_carbon` is derived from an internal input.
  - These three public headers can be changed only by window A (it holds the data lock).
- **The unread publishers, by table count:**
  - Catalyst Cooperative (PUDL, FERC Form 714) 23; Public Utility Commission of Texas 12; FERC 11; Energy-Storage.news 10; Electrek 7;
  - "each row's own document" 3;
  - the four state commissions of the large-load rules, 2 each; Grant PUD, CTVC, OPEC, PJM's news releases, Texas.gov, 2 each;
  - about 30 others, 1 each.
- **The publishers with the most tables:** EIA 206, ERCOT 71, CAISO 56, NYISO 38, SPP 38, ISO-NE 37, MISO 30, Eurostat 27, PUDL 23, DESNZ 17, NOAA NCEI 16, DOE 15, NRC 14, Berkeley Lab 13.
- **Holds:** `docs/licenses_holds.csv` holds 14 held figures (ISO-NE and NYISO prices on `/digest` and `/research`, ISO-NE's queue on `/grid`), all from 21 October.
- **Unsettled file:** `docs/state/unsettled_licenses_2026-10-19.md` lists 19 tables, 10 publishers, each with the sentence an email would need.
- **Letters:** `docs/reviews/licenses/` holds four, for MISO, NYISO, PJM and SPP (brought up to date in later sessions).

## How later sessions confirm a verdict

- **Never asked twice:** `scripts/license_read.py` asks once per publisher label. A re-read uses a new label ("<publisher>, current terms (session 41xx)"), as sessions 2827 and 2832 did for Eurostat.
- **Robots first:** the host's robots file is read as its own recorded row and checked for the ERW's agent and for ClaudeBot and anthropic-ai by name, in a separate command before the terms page.
- **Matched by code:** whether the verdict's quoted sentence is still on the current page is checked by code, never by eye.

## Decisions made without you

- **Chain file 229 taken by hand** with `chain_queue.py`'s own message: the owner asked for the window-3 mark, and the script refuses it on a data machine. The mark also keeps window A's bare `next` off this file.
- **Numbers kept unique:** this chain's files took 229 and 231. Window B's took 228 and 230. Window B's queue files were not touched.
- **The 45 "license needed" tables keep their public flag.** The owner ruled on 12 October that they stay flagged public and show "license needed" on the site. A tightening is allowed on new evidence, and this is not new evidence.
- **"Stale" means a read more than 30 days old** (before 14 October). The prompt names no age.

## For Samuel's ruling

- None new in this session.
