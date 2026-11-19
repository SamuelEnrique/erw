# Progress of chain 505 (19 November 2026, lab-desktop, one window)

The chain: `queue/done/505-day-19-november-desktop-pages-authorities-prices.md`. One line a landing, request, page, file or table, its state and session. The resume file: `queue/next/550-resume-chain-505.md`.

| Part | Item | What | State | Session |
|---|---|---|---|---|
| start | the chain file | saved unchanged, committed alone (`queue/done/505-...`); chain 501's closing note written; resume file 550 replaces 510 | done | 8012 |
| start | the second window's resume file | `queue/next/520-resume-chain-502.md` removed (chain 502 stopped at 13:30 UTC; Samuel closed the window); its findings code, window 2's row 2, landed with chain 501's stack d | done | 8012 |
| A | landing desk | stack h (`fdb56c767`: data request 553 and the portable's row 42 at `ca7ba644e`), gated by chain 501, pushed to `task/c501-desk-h` at 19:16 UTC (snapshot `c501-deskh-before`) | landing | 8012 |
| A | stack h | failed on GitHub at the suite merged with main (19:27 UTC): test 7052, `site/data/map.json` with no proposed in-service date; not stack h's fault | relanding in `wip/c505-fix-map` | 8012 |
| F | the project map's proposed dates | cause: the data machine's daily copy of the map (`scheduled.py project_map`) restores `energy_projects` from the archive, whose newest copy (17 November 07:58 UTC) predates session 7052's `proposed_date` by minutes; the daily run of 19:04 UTC wrote 0 for all 3,684 positions. Fixed: `energy_projects` rebuilt with the current builder under the data lock (45,612 rows, 8,075 with a proposed date; validator 0), archived (run 20261119T193935Z-local), `map.json` rebuilt (3,252 positions with a date, as on 17 November); `project_map.py` now refuses a table without the column. On `wip/c505-fix-map` (`eee828ada`) with stack h, gating from about 19:41 UTC | gating | 8012 |
| B1 | Energy use by industry (`/industry`) | page, decisions (8), method note section, replication (535 and 586 figures reproduced), cross-checks (MER against SEDS 0.12 percent; EIA-861M against SEDS equal, not independent), test; seen at 1280 and 390 px (no sideways scroll); on `wip/c505-industry` (`ced21512f`) | built, to gate | 8012 |
