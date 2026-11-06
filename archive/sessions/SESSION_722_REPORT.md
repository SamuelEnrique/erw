# Session 722 report: chain 050's end, checked

22 October 2026, from 14:48 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-722` on `wip/722-allgrids` (cut from `wip/721-records`, which is origin/main plus 721's landing record). Chain `queue/done/062-day-23-october-code-allgrids-2.md`, session 722, the first. Model spend USD 0. No warehouse data written by this session; no request to a publisher. The reads: the live set with the anon key (the replication) and the site's own pages.

## Read these first

- **Chain 050 is on main**: 700 to 705 (`b25a5c66`), 706 to 712 (`8a54e3b4`), 713 to 718 (`e39de81a`), 719 to 721 (`0787ad72`).
- **Production serves all of it since 14:56 UTC.** Vercel had refused 719 to 721's merge ("rate limited", 13:44 UTC). The queue's next push to main (below) deployed at 14:53 and brought them out: the card's title showed on `/research/card/siting_gigawatt` at 14:56:05.
- **The queue's taking of 062 was pushed to main at 14:52 UTC** (`9cb5e71f`, the one file moved from `queue/next/` to `queue/done/`). `chain_queue.py next` commits the move without pushing it. The personal laptop is a code machine too and could have taken the same file, so the push did not wait for the landing window.
  - Snapshots: `s722q-before` at 14:51, `s722q-after` at 14:56.
  - `compare s722q-before s722q-after`: **0 differences**.
  - `compare s721-before s722q-after` (721's landing as a whole): **0 differences** on 25 pages, expected, since every page is in review.
  - 721's "To finish" item 1 is done here.
- **The replication against production**, in its clean environment (`runs/chain_050/venv712`): 81 figures computed, 69 beside the page, **0 differ**.
- **The open items, one table**: `docs/reviews/siting-open-2026-10-23.md`, 25 lines (item, session, kind, the session of this chain that closes it). Line 23 (production serves 719 to 721) is closed by this session.
- **`scripts/sync.py`** was run at 14:30 by 721's queue step. It pulled main, then restored local tables from the archive into `warehouse/output/` until its 10-minute limit stopped it (a local copy, as every session's sync makes; no upload, no publish).

## What to review

1. `docs/reviews/siting-open-2026-10-23.md` on the branch (on main after the landing): the 25 lines.
2. `https://erw-flame.vercel.app/research/card/siting_gigawatt` (internal view): session 720's card, served since 14:56 UTC.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | on duty for "session 722" |
| the replication against production (`runrepl.py`, venv712) | 0 | 81, 69, 0 differ |
| Vercel's status on `9cb5e71f` | | "Deployment has completed", 14:53:23 UTC |
| probe for the card's title on production | 0 | served at 14:56:05 |
| snapshots and compares (above) | 0 | 0 differences |

## The landing

Sessions 722 to 730 landed in one push at 16:15 UTC: see `SESSION_730_REPORT.md`, "The landing".

## Decisions made without you

1. **The queue's move was pushed to main at once**, with its snapshots, rather than waiting for the window after 16:15. It is a file move, and leaving it local let a second code machine take 062.
2. **This session cut its branch from `wip/721-records`**, so 721's landing record lands with it.

## For Samuel's ruling

- Nothing new.

## Files

- New: `docs/reviews/siting-open-2026-10-23.md`, this report.
