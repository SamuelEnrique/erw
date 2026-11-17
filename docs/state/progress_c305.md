# Progress of chain 305: the browser reads, seven tools to the done line, each tool read as its reader (sessions 7600 to 7699, portable-laptop)

Energy Research Warehouse (ERW). The chain file: `queue/done/305-night-16-november-portable-done-line-and-browser-reads.md`. One line a tool and part, with its state and the session. This file, the resume pointer, the claims, the requests and the landing rows are on main; the work is on `wip/` branches named in each line.

States: `done` with the commit, `needs the key` with the cost, `ruling` with the default taken, `waiting` with what for, `open`.

## The ground

| Step | State | Session |
|---|---|---|
| Precheck, fetch, memory and disk, freeze | done (precheck passed 10:30 UTC; no freeze; 2.2 GB of memory free of 15.6 at the start; 307 GB of disk) | 7600 |
| Session numbers 7600 to 7699, queue numbers 350 to 359 | done (free on origin/main, every branch and every queue file) | 7600 |
| The resume pointer `queue/next/350-resume-chain-305.md` | done (`60435cc99`, committed alone) | 7600 |
| `docs/state/done_line_claims.md` | done (`e5ba04eb4`: it was on no branch; written from the chains' table, 24 rows) | 7600 |
| `docs/state/data_requests_done_line.md`, row 1 | done (`df15207e5`) | 7600 |
| The before snapshot of the live pages | done (`runs/snapshots/c305-before`, 25 pages, 0 failed, 10:30 UTC) | 7600 |

## Part A: the browser reads

| Step | State | Session |
|---|---|---|
| The large-load pages of chain 302, built here from `wip/7200-large-load` (not landed), read at 1280 and 390 px | done (`wip/7600-large-load-read`: 15 numbered rows in `docs/reviews/large-load-on-site/browser-read-2026-11-16.md`; 12 site faults fixed with tests, 2 requests of the data machine (rows 8 and 9), 1 ruling with its default; 17 of 17 figures in their table rows; axe, no rule broken; landing row 34 of `docs/state/landing_request_portable.md`) | 7600 |
| `docs/state/browser_reads_wanted.md`, rows 1 to 14 (the old laptop's `/severance`, `/contracts`, `/shoulder`, `/cost-of-power/battery/awards`) | done (`b137693bb`: 8 seen, 6 with a fault. The shared "i" mark's box past a phone's screen, fixed for every page on `wip/7600-large-load-read`; one sentence of `/shoulder`, fixed on `wip/7600-shoulder-read`, landing row 35; index and 24 screenshots in `docs/reviews/browser-reads-2026-11-16/`) | 7600 |
| `docs/state/browser_reads_wanted.md`, rows 15 to 31 (the old laptop's `/impact` and its three explorers) | done (`ce9be9911`: 13 seen, 4 with a fault: three the shared mark's; one of its own and on production too, the demand growth chart's hover card drew no figure, fixed on `wip/7601-demand-growth-read`, landing row 36) | 7601 |
| `docs/state/browser_reads_wanted.md`, rows 32 on (added by the old laptop from 12:35 UTC) | done (`wip/7602-landed-reads` at `eef5b5861`, landing row 38; the rows marked on main): 130 rows read on a build of the old laptop's 27 branches, 119 seen, 4 seen in part, 7 with a fault. Six fixed with tests and read again on a second build: the placer widens a tall box (rows 52, 62), a one-point chart's axis (row 63), the event-day table's frame (rows 80, 82, on production too), `/supply`'s links line (row 179, on production too). One for the data machine: the battery page's awards snapshot of 10 October (row 55, request 261). Section "Rows 32 to 278" of `docs/reviews/browser-reads-2026-11-16/README.md`, 175 pictures | 7602 |
| The snapshots of the live pages around session 7600's pushes to main (`c305-before`, `c305-after-7600`) | done (25 pages, 0 differences; every push held state and queue files only) | 7600 |

## Part B: the done line for this machine's seven tools

| Tool | State | Session |
|---|---|---|
| `/map` | done line (`wip/7601-map` at `884c94071`: the note, the replication (the units 3,790 of 3,790 against EIA's own workbook; 301 queue figures named), the cross-check (18 of 27 technologies the same as EIA's table), 11 decisions on the page, the browser read, 8 faults: 3 fixed, 3 requests (rows 32 to 34), 2 rulings; landing row 37) | 7601 |
| `/events` and its nine event pages | skipped: moved to samueloldlaptop by Samuel's instruction of 16 November 2026, about 22:00 UTC (`docs/state/note_2026-11-17_oldlaptop_c304.md`, "The second run"); done line there on `wip/7531-events-b` (landing row 29 of `docs/state/landing_request_oldlaptop.md`, landed by chain 370) | 7602 |
| `/grid/caiso/alerts` | skipped: moved to samueloldlaptop, as above; done line on `wip/7532-caiso-alerts` (landing row 30, landed) | 7602 |
| `/learn/bill` | skipped: moved to samueloldlaptop, as above; done line on `wip/7533-learn-bill` (landing row 31, landed) | 7602 |
| `/learn/problems` | skipped: moved to samueloldlaptop, as above; done line on `wip/7534-learn-problems-b` (landing row 32, landed) | 7602 |
| `/play/battery` | skipped: moved to samueloldlaptop, as above; done line on `wip/7535-play-battery` (landing row 33) | 7602 |
| `/play/ev` | skipped: moved to samueloldlaptop, as above; done line on `wip/7536-play-ev` (landing row 34, landed) | 7602 |

## Part C: each tool read as the reader it is for

| Tool | State | Session |
|---|---|---|
| This machine's seven tools | skipped: all seven read by samueloldlaptop (`/map` in session 7537 on `wip/7537-map-read`; the six in sessions 7546 to 7551 on their own branches), each marked `read: samueloldlaptop` in `docs/state/done_line_claims.md` | 7602 |
| The datacenter tracker (`/datacenters`) | open: no `datacenters-read-2026-11-16.md` on any branch (searched every remote branch, session 7602) | |
| The deal tracker (`/deals`) | open: no read on any branch | |
| Automated Analysis (`/research`) | open: no read on any branch | |
| Grid (`/grid`) | open: no read on any branch | |

## Needs the key

- Nothing so far. No model was called by any session of this chain; no other key or route was tried.

## For Samuel's ruling (each with the default taken)

- **A box opened in a table's frame on a phone** has the frame's scroll indicator drawn across one of its lines for about a second after the frame is scrolled (row 13 of the large-load read). Default: left as it is.
- **"(session 83)" in grey beside each line of the decisions blocks** of `/contracts` and the five tools, against the page rule of no grey text. Default: nothing changed; it is the five tools' signed form.
- **The hub table's two rule lines are 24 px high** (they were 18), which axe's target size asks. Default: 24 px.

## Not as the chain file expected

- The first build of session 7600 started at 1,760 MB free, under the chain's 2 GB (the measure before it read 2,268 MB and was not taken again). Every later build is gated on a fresh measure.
- Two of Samuel's windows were closed by their own window to free memory, as the chain's rule says: the Snipping Tool and the Edge window (a Google Doc and one more page).
- Session 7602's second build (the fixes merged) started with 1,175 MB free, under the chain's 2 GB: the measure and the build ran in one command, so the build was not held back. It finished (exit 0). Every later build is measured first, alone.
- Session 7602's first two pushes to main (the resume file, then the progress and claims files) went out with no before snapshot. The snapshot taken after them (`c305-7602-a`, 25 pages) against session 7600's last (`c305-after-7600`): 0 differences. Every later push of the session has its snapshot before and after.
