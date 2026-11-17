# Sessions 7611 to 7619 report (portable-laptop, 17 November 2026)

Energy Research Warehouse (ERW). Part 2 of the prompt of 17 November: for each line marked "Changes a figure" in `docs/reviews/rulings-for-samuel-2026-11-17.md` (branch `wip/7560-six-reads`), tool by tool from the bottom of its count table up, each tool claimed alone first, the figure under the default and the other choice computed from the warehouse's tables, one file per tool. The old laptop (samueloldlaptop, sessions 7570 to 7599) took the table from the top; the two met at `/cost-of-power`. One session number per tool, as the claims file records them; this one report covers the nine (each is a short session of one tool). About 08:25 to 09:10 UTC. Model spend: USD 0.

## The nine tools (claims file `docs/state/ruling_impact_claims.md`, each `done`)

| Session | Tool | File | Biggest change found |
|---|---|---|---|
| 7611 | Site-wide: Ask (the chat) | `docs/reviews/ruling-impact-site-ask-2026-11-17.md` | Leaving Berkeley Lab's ISO-NE, NYISO and MISO regions out: 9 figures gone, a national active total -21.0 percent |
| 7612 | Site-wide: the Digest and the Roundup | `...-site-digest-...` | A US day for the Lower 48: the peak moves on 14 of 33 days (up to -9.45 percent): the UTC day hands yesterday the evening before |
| 7613 | Site-wide: the data machine and its tables | `...-site-data-machine-...` | The interchange fill: 1,067 to 3,846 authority days of November and December 2025; the filled values are on the data machine only |
| 7614 | Site-wide: the warehouse's sources and publishers' terms | `...-site-sources-...` | ERCOT's absent days: the refilled figures cannot be computed (not held); the board's 30-day averages stand on 28 and 26 of 30 days |
| 7615 | Site-wide: licenses and holds | `...-site-licenses-...` | EIA-930 keys named to their grids: 931 of 1,064 held figures come back on the event pages and set C |
| 7616 | /grid | `...-grid-...` | All three Mix figures at carbon's hour: the exchange turns over for ERCOT, CAISO and SPP |
| 7617 | /research | `...-research-...` | Withdrawing 3 internal-table cards: 3 of 14 cards, 49 numbers; the Wyoming record cell +35.2 percent |
| 7618 | /policy | `...-policy-...` | PJM-wide records under each PJM state: Virginia 7 to 14 (+100 percent) |
| 7619 | /cost-of-power/seller | `...-seller-...` | The worst contracted month over three years: USD 750,064 to 1,016,595 (+35.5 percent) |

## How the figures were read

- This machine holds 11 of the warehouse's tables. The figures were read from the live set (Supabase, read-only transactions, `runs/ruling_impact/live.py`) and from Redivis's draft (`runs/ruling_impact/redivis_read.py`, cached under `runs/ruling_impact/cache/`, not committed); nothing was written to `warehouse/output` or to any table.
- Page counts came from a local build of `wip/7610-fault-rows` served in the internal view. For session 7615 only, `site/components/Num.tsx` in that worktree drew each held figure's key (`data-held-key`) for the build, and was restored right after; the change is on no branch.
- Every script and printout is under `runs/ruling_impact/` (`<slug>_impact.py` and `.out`), committed with `git add -f` as the old laptop's are.
- No held value is written in any file or printout: this repository is public. Held tables appear as counts and places only; the held grids' EIA-930 rows as hours and percent changes.

## Not as the rules expected

- Session 7615's build started with 1,873 MB free, under the 2 GB rule (it finished).
- Two pushes raced the old laptop's and were rejected, then pulled and pushed again; one merge conflict in the claims file (both machines' rows) was resolved by keeping every row. No force push.
- Git Bash rewrote `/grid` into a Windows path in the done step's call to Python; caught by the script's own assertion, run again with `MSYS_NO_PATHCONV=1`.
- Snapshots around the pushes to main: `c311-a`, `c311-b` and `c311-c`, 0 differences each against the one before; no live page was touched.

## Decisions made without you

- The count table's site-wide subjects were taken as "tools" (each has its own count of figure lines).
- Where a figure needed data not held (the interchange fill's values, ERCOT's absent prices, the seller page's October run, August 2026 in Redivis's copy), the file says so on the line and gives what could be counted; for Wyoming the stored chart's own August figure was used and named.
- The Digest is paused this week: its line was computed from the tables only; nothing of the Digest was touched.

## Needs the key

- Nothing.

## For Samuel's ruling

- Each impact file ends with "What a ruling would also have to fix": the choices a ruling would have to set beside the line itself.
- Session 7618 found `/policy?view=monitor` drawing 149 checked figures in the internal view of main's build while `/policy` as it opens draws only "license needed": whether the monitor view is meant to be held as the rulings line says was not settled here.
