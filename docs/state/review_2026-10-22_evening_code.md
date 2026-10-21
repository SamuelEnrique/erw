# The chain of 21 October 2026, evening, code machine (023): the note for Samuel

Energy Research Warehouse (ERW), session 506, written on the old laptop (samueloldlaptop) on 21 to 22 October 2026. Chain 023 (`queue/done/023-evening-21-october-code.md`, sessions 429, 430 and 497 to 506) ran on portable-laptop from 17:41 UTC until the owner took that laptop away; its last session, 506, moved here by `queue/done/025-night-21-october-code-506.md`. Every page is in review: open `https://erw-flame.vercel.app/internal/open` first. Model spend USD 0. No warehouse data written.

## First: what to know

1. **Chain 023 lands with chain 021.** `wip/506-combined` holds `wip/429-combined` (chain 021, sessions 416 to 428, with 427's note) and chain 023's nine other branches, main of 22:06 UTC merged. LANDING_LINE
2. **One build served every report's remaining checks**: check-values 6,457 of 6,457 values equal on 152 of 152 pages in 6.2 minutes, the ten held floors failing as session 408 counted them; check-routes, check-cross-checks (77 of 77), check-analysis (279), check-internal-waits, check-csp and check-findings-grids (163) all 0. Each report's new last section, "Finished (session 506)", says what it ran.
3. **check-holds (session 505) finds 88 held figures shown on 14 pages**: session 474's five-grid cards and one-grid views, and two kinds no one had named, the Digest's real-time price line (`/digest` and five issues) and the ISO-NE queue on `/grid?grid=isone` and `/grid/isone` (36 figures each). Nothing changed; yours to rule (below).
4. **The tall render frame still overlaps** on the two five-grid cards (session 497's after shots); the next file's session 573 places it in two columns.
5. **The q025 comparison could not be made**: `q025-before` stayed on portable-laptop; `q025-after` (22:59 UTC, 25 pages, 0 failed) is here. The landing took its own pair.

## What each session did

| Session | Branch | What it did | Address to open after the landing |
|---|---|---|---|
| 429 | `wip/429-combined` | chain 021's ten branches and 019's two merged on one branch; its checks finished by 506 | the branch's sessions' own pages |
| 430 | `wip/430-check-values` | check-values reads pages in batches with a timeout a page, retries a slow page once, lists pages not read, exit 3 when incomplete, resumable | `site/scripts/check-values.mjs` |
| 497 | `wip/497-faults` | the queue's active MW read whole; the five-grid cards' wide render frame side by side (the tall frame still overlaps) | `/research/card/peak_hour_grids?render=1` |
| 498 | `wip/498-digest-numbers` | every number of every Digest issue and the three Roundups traced by `check_digest.py` and `check_roundup.py`; no generator fault found | `scripts/check_digest.py` |
| 499 | `wip/499-500-row-license` | the site reads a row's own license when a table carries one (`row_license` in `extra`), holding the rest; no table carries it yet | `site/lib/license.ts` |
| 500 | the same branch | `/deals` and `/datacenters` show public rows with a held-rows count once a table is held by row; unchanged today | `/deals` |
| 501 | `wip/501-battery-rows` | session 448's battery rows against Lazard and the ATB in the battery note's cross-checks; "Checked against" 17 to 25 (B12 and B14 left out) | `/data/methods/battery_earns_algorithm#cross-checks` |
| 502 | `wip/502-license-lines` | one line under the title of `/board`, `/prices`, `/grid` and Ask naming the tables read and each one's license | `/board` |
| 503 | `wip/503-fresh-suite` | a fresh worktree writes the generated files its tests need; the suite in one, run by 506 | `docs/machines.md`, "Other checkouts" |
| 504 | `wip/504-buildlock` | `scripts/buildlock.py` (acquire, release, status), found from any worktree | `docs/machines.md`, "The build lock" |
| 505 | `wip/505-check-holds` | `site/scripts/check-holds.mjs`; its list in `docs/licenses.md` | `docs/licenses.md`, "Held figures that still show" |
| 506 | `wip/506-combined` | the remaining steps, the combined branch, two faults of the merge fixed, the landing, this note, the next file | this file |

## The screenshot folders

`docs/brand/review-497/` (before from portable-laptop, after from the combined build, with `measures.txt` and a README) and `docs/brand/review-502/` (before from production, after from the combined build, `/board`, `/prices`, `/prices?tab=ercot` and `/grid` at 1280 and 390). Chain 021's folders ride with `wip/429-combined`: `review-416`, `review-417`, `review-419`, `review-423`, `review-425`, `review-428`.

## Decisions made without you

1. **One build of the combined branch** for every report's checks, not one a branch.
2. **Four merge conflicts**, both sides kept each time (`check-values.mjs`'s whole-MW line, `site/lib/supabase.ts`'s retry with the public-rows read, `energy_deals.md`, `docs/machines.md`).
3. **Two faults of the merge fixed** in session 505's files: `check-holds.mjs` names its browser door statically (session 301's rule); the held figures' section of `docs/licenses.md` comes before the publishers' prices (session 378's rule).
4. **Session 497's shot script waits for fonts**; the tall frame left to session 573.
5. **The ten held floors read as a pass**; no floor lowered.
6. **The sync not restarted** after the harness stopped it in its restore of 103 tables.
7. **The merged remote branches deleted** once on main.
8. Each session's own, in its report: 430's exit 3 for an incomplete run; 498's "revised" for a row changed after the issue; 499's `row_license` in `extra` and the status file's `hold: row`; 500's count never a read; 501 leaving out B12 and B14; 502's one static line from `license_status.json`; 503's fix in the loader; 504's stale age of 3 hours; 505's page list read from check-values.

## Waiting for you

One item a line in each report, and on `/internal/waits` after the landing:

1. **Held figures that show** (505, 506): the five-grid cards' NYISO and ISO-NE panels and one-grid views; the Digest's real-time price line; the ISO-NE queue on the Grid page; and whether check-holds joins the gate.
2. **check-values** (430): exit 3 for an incomplete run; the gate's resume and its tries; `process.exit` to `process.exitCode` everywhere.
3. **The Digest and the Roundup** (498): W40's real-time price, revised since; the retrieval time beside each Roundup table; the fourteenth issue.
4. **Rows held by row** (499, 500): downloads and Ask on public rows; "public in part" on `/data`. The data machine's column (499's "To finish") comes first.
5. **The battery's cross-checks** (501): B14 (the tax credit's words), B12 (today's toll beside Lazard's).
6. **The license line** (502): a link to `/data/licenses`; the line on other pages.
7. **The machine**: whether a landing removes its worktrees (`erw-506`, `erw-506c` left).

## The queue

`python scripts/chain_queue.py list` at about 23:00 UTC on 21 October: 1 waiting, `031-night-22-october-sources.md` (machine: data), 0 for samueloldlaptop. So session 506 wrote **`queue/next/032-night-22-october-code.md`**, sessions 562 to 574 (the next free numbers: the queue's files and the branches use up to 561), thirteen sessions for the code machine, default-neutral, and pushed it to main with the landing. This session's queue step takes it next.
