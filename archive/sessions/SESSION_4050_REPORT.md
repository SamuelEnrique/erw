# Session 4050 report: chain 230's ground, and the urgent row's first gate

Energy Research Warehouse (ERW). Chain 230 (`queue/done/230-day-13-november-desktop-window2-landings-continued.md`), the desktop's second window, 13 November 2026 from 22:07 UTC. Opus 5.5. Model spend: USD 0.

## Done

- **The next file first:** `queue/next/265-day-14-november-desktop-window2-landings-continued.md` (`672cb72cd`), committed alone and pushed with snapshots (0 differences). 231 to 264 were taken on origin's branches. Sessions 4050 to 4063 are this chain's; the next takes 4064 and on.
- **The ground:**
  - precheck passes (from the main checkout);
  - 5.8 GB free; 218 GB of disk;
  - this window's worktrees: `erw-w2-4000` (the reports' branch) and `erw-w2-landK`.
- **Portable row 28's gate** (`106fb873a`, session 4015's, 21:59 to 22:17 UTC) **failed its suite: tests 414 and 425** (`site/scripts/test-waits-ledger.mjs`), "session 5251's line 90 ... 98 holds its words".
  - The row's report `SESSION_5251_REPORT.md` holds a markdown table inside "For Samuel's ruling", and the waits ledger reads table rows there as ruling lines.
  - **The fix, small and plainly correct, on the requesting stack's landing branch:** the table moved out to its own section after the rulings, every word kept, and the first ruling's line says where it is.
  - The ledger test then held 2,955 of 2,955, and `test-waits.mjs` 9,193 of 9,193. Tests 414 and 425 and the 49 test files that read the waits pass.
  - Commit `32ee41fb1` on `wip/w2-land-k`.
- **The regate** was started at 22:22 UTC. It waits for the lock behind window A's `c227-gate5` (taken at 22:18).

## Decisions made without you

- **A report's table that a ledger misreads is moved, not the ledger changed.** That is the smallest correct fix for an urgent row. A ledger that also reads tables is a later item.

## For Samuel's ruling

- **The shared build lock has no priority.** An urgent row waited 25 and then 30 minutes behind window A's routine gates. Default: no change. A `--priority` for the lock is a code change for a later chain if wanted.
