# Session 7542 report: `/storage` read as a lender's analyst reads it (chain 304, part C, samueloldlaptop, 16 November 2026)

- Branch `wip/7542-storage-read`, from origin/main `aaa72c020`. The read: `docs/reviews/storage-read-2026-11-16.md` (16 rows).
- The reader: a lender's analyst sizing a merchant battery loan in ERCOT, with CAISO and PJM beside it. Five cases: ERCOT's operating fleet in EIA's September 2026 inventory on all three tabs; ERCOT's owners; ERCOT's cycle on 12 and 14 November 2026 and the 30 days before, beside the awards page; CAISO and ERCOT side by side (added in twelve months, 2027, hours); PJM.
- How: the page's own function drawn to HTML with the site's code on every tab, its reads answered by the live set with the public key (every table it reads is public), at 15:41 and 15:49 PST. No build, no browser.
- Rows: 16. Site, fixed: 5. Data machine: 5 (4 requested, 1 fixed by the data machine during the read). Browser: 3. Rulings: 3. License: 0. Key: 0.
- The sibling read's rows 5 and 6 (battery awards: two fleet counts, two discharge counts): fixed on the awards page, on main (session 7514). This page said nothing back: row 7 closes it. Its row 8 (hours) is that page's ruling, not written again.

## What changed

- `site/app/storage/page.tsx`: the fleet tab's headline note names the inventory month ("of September 2026"); the three hourly lines break at hours not held; the spark's hover says "the last 30 days held" and names the days not held; the "Discharged MWh" heading has a hover saying what it counts and naming the awards page's count.
- `site/lib/storagefleet.ts` (new, pure): `inventory`, `notHeld`, `DISCHARGED_TITLE` (a page file may export only what Next.js allows).
- `site/lib/data.ts`: `storageUnits` also reads `vintage`; the type gains an optional `vintage`.
- `site/components/LineChart.tsx`: an optional `gap` on a line, and `gapped` (exported). Without `gap` every chart is drawn as before (the old mapping is kept word for word).
- `site/components/TimeChart.tsx`: the thinning keeps a null point (a break), so a narrow chart breaks where a wide one does. With no null point the output is as before.
- `site/app/storage/buildout/parts.tsx`: the header "Planned, MW, by the year expected online" now reads "Under construction and planned, MW, by the year expected online", with a hover.
- New: `site/scripts/test-storage-read.mjs` (25 of 25), this report, the read file.
- Files of the other machine's stack touched: none of `replication/storage/`, `docs/reviews/storage-faults-2026-11-16.md`, the method notes or `site/lib/decisions.ts`. The page files above are the tool's own.

## Tests

- `node --import ./scripts/tsx-register.mjs scripts/test-storage-read.mjs`: 25 of 25.
- `site/scripts/test-buildout.mjs`: 935 checks pass (same on clean origin/main).
- `tsc` with the site's settings on the six changed files and what they import: exit 0.
- pytest, each file on its own: `test_session120_page, 122, 123, 153, 300, 87, 90, 92, 138, 144_page, 303, 403, 404, 405, 416, 794, 2203, 318, 332, 417, 584, 149_checks, 248, 410, 502, 88`: all pass. `test_session148` and `test_session161`: one failure each (their Ask node tests), the same failure on a clean origin/main worktree, not this change.

## What to review

- `https://erw-flame.vercel.app/storage`: under "Batteries operating in the US", the note ends "in EIA's monthly generator inventory (EIA-860M) of September 2026, nameplate power." In "The daily cycle", hover the heading "Discharged MWh": the hover says what it counts and names the awards page. Hover a spark: "the last 30 days held", then any days not held.
- `https://erw-flame.vercel.app/storage?tab=buildout&grid=ercot`: "By grid": the header reads "Under construction and planned, MW, by the year expected online"; ERCOT's All years 24,159 is the fleet tab's 7,899.50 plus 16,259.30.
- `https://erw-flame.vercel.app/storage?tab=owners&grid=ercot`: still August 2026 (18,205 MW) until data request 159 is done.

## Needs the key

- Nothing.

## Decisions made without you

- The live set was read with the public key to draw the page as a visitor gets it (all six tables are public; nothing saved to the repository).
- The owners tab's words "Planned" left as they are (row 4); its figures wait on data request 159.

## For Samuel's ruling

- Row 4: "Planned" on the owners tab means under construction and planned together. Default: unchanged (its fold says so). Other choice: the build-out's new words there too.
- Row 12: no month's discharge total on the fleet tab. Default: none added. Other choice: a month column from the daily cycle's rows.
- Row 13: the decisions block on the build-out and owners tabs is the fleet tab's nine. Default: unchanged. Other choice: one block a tab.

## Rows for the coordinator

### (a) Landing request, row 40

| 40 | `wip/7542-storage-read` | the branch head (in the return) | `7542-storage-read` | 7542 | 2026-11-16 | `site/scripts/test-storage-read.mjs` (25 of 25, the line chart drawn to HTML without a build, the helpers on made-up rows, the page files read); `site/scripts/test-buildout.mjs` (935 checks); `tsc` on the six changed files, exit 0; pytest `test_session120_page, 122, 123, 153, 300, 87, 90, 92, 138, 144_page, 303, 403, 404, 405, 416, 794, 2203, 318, 332, 417, 584, 149_checks, 248, 410, 502, 88` pass; `148` and `161` fail one Ask node test each, as on clean origin/main; not built here (memory); `check-values` and `check-routes` not run | requested |

## Row 40: what it holds (chain 304, part C, session 7542, `/storage` read as a lender's analyst)

- **Stacked on** origin/main `aaa72c020`. Report: `archive/sessions/SESSION_7542_REPORT.md` on the branch.
- **What changes:** `site/app/storage/page.tsx` (the fleet tab names its inventory month; the hourly lines break at hours not held; the spark's hover names days not held; the "Discharged MWh" heading's hover), `site/app/storage/buildout/parts.tsx` (the header of the planned columns, with a hover), `site/lib/data.ts` (`storageUnits` reads `vintage`), `site/components/LineChart.tsx` (optional `gap`, new export `gapped`), `site/components/TimeChart.tsx` (the thinning keeps a break). New: `site/lib/storagefleet.ts`, `site/scripts/test-storage-read.mjs`, `docs/reviews/storage-read-2026-11-16.md`.
- **What does not change:** any table or builder, `site/data/storage_owners.json`, `replication/storage/`, the storage method notes and faults file, `site/lib/decisions.ts`, `site/lib/license.ts`, `site/components/Num.tsx`, `site/lib/release.ts`, `check-values.mjs`. No figure or check key on the page changes. Every other chart on the site: drawn as before (no `gap` given; no null point to keep).
- **Before landing:** a site build on the landing machine; `node --import ./scripts/tsx-register.mjs scripts/test-storage-read.mjs`; `node --import ./scripts/tsx-register.mjs scripts/test-buildout.mjs`; `check-values` on `/storage` (its keys are unchanged).
- **Snapshot differences to expect:** none on the 25 addresses (`/storage` is in review; a visitor is shown the in-review page). **Tables:** none.
- **After the landing:** browser reads 186 to 188; data requests 159 to 162 are the data machine's and do not hold this row.

### (b) Browser reads

| 186 | 2026-11-16 | 7542 | `wip/7542-storage-read` (row 40) | `https://erw-flame.vercel.app/storage` | The note under "Batteries operating in the US"; hover the heading "Discharged MWh" of "The daily cycle"; hover a spark | The note ends "of September 2026" (or the newest inventory held); the heading's hover says it is net output by hour from EIA-930 and names `/cost-of-power/battery/awards`; the spark's hover begins "the last 30 days held" and names any days not held | wanted |
| 187 | 2026-11-16 | 7542 | `wip/7542-storage-read` (row 40) | `https://erw-flame.vercel.app/storage`, at 1280 and at 390 px | "Hour by hour, the last 30 days" and "The last 24 hours" | Where EIA-930 has not given an hour the line breaks, at both widths (none may be missing on the day; then the lines are whole); the charts draw at 390 px | wanted |
| 188 | 2026-11-16 | 7542 | `wip/7542-storage-read` (row 40) | `https://erw-flame.vercel.app/storage?tab=buildout&grid=ercot`, at 390 px | "By grid": the header and its hover | "Under construction and planned, MW, by the year expected online", the hover says the fleet tab gives the two apart; the table scrolls in its frame, the page does not scroll sideways | wanted |

### (c) Data requests

| 159 | 2026-11-16 | 7542 (chain 304, samueloldlaptop; branch `wip/7542-storage-read`) | `site/data/storage_owners.json` (`storage_owners_monthly`) | Rebuild the owners tab's copy from the newest inventory (`warehouse/derived/storage_owners.py --snapshot`): it holds August 2026 (built 13 October) while the fleet and build-out tabs read September 2026 from the live set, which already holds September for this table. ERCOT: 18,205 MW and 259 units on the owners tab against 19,195 MW and 266 units on the other two; the method note's rule that each grid's operating MW and MWh equal the build-out's newest month fails on the page | EIA-860M; the read's row 1 | requested |
| 160 | 2026-11-16 | 7542 (chain 304, samueloldlaptop; branch `wip/7542-storage-read`) | `storage_daily_cycle` (live set) | At 15:41 PST the EIA-930 grids' newest day was 14 November 2026; at 15:49 it was 12 November, while `eia930_all_storage` held every hour to 15 November 23:00 UTC. Rebuild the cycle from the hourly table as now held and load it; say which copy the 15:49 load came from | the read's rows 8 and 9 | requested |
| 161 | 2026-11-16 | 7542 (chain 304, samueloldlaptop; branch `wip/7542-storage-read`) | `eia930_all_storage` (`eia930:ERCO`) | ERCOT's 14 November 2026 (Central) is 3,755 MWh discharged against 24,833 charged, out over in 0.15 (every other day of 1 October to 12 November: 0.39 to 1.63). Read EIA-930's BAT series for ERCO again for 12 to 16 November once EIA's revisions have passed, compare hour by hour, write what changed; nothing adjusted. The daily run asks for its last 3 days only, so a later revision is not taken | EIA-930; the read's row 10 | requested |
| 162 | 2026-11-16 | 7542 (chain 304, samueloldlaptop; branch `wip/7542-storage-read`) | `storage_daily_cycle` (`caiso:ISO`), `warehouse/derived` builder | CAISO's row leaves out the autumn clock-change day in both years held (2 November 2025, 1 November 2026); the spring day (8 March 2026) and every EIA-930 grid's autumn day are held. Count `caiso_battery_storage`'s 5-minute values on those Pacific days against the rule's 300; fix the builder if the rule or the day's bounds miss them, or record why the source lacks them | CAISO Today's Outlook; the read's row 11 | requested |

### (d) Progress, part C

| `/storage` | lab-desktop | done the branch head (in the return) on `wip/7542-storage-read` (landing row 40): the reader a lender's analyst sizing a merchant battery loan in ERCOT, with CAISO and PJM beside it; five cases (ERCOT's fleet in the September 2026 inventory on three tabs: 19,195 MW, 1.65 hours, the owners tab still August's 18,205; ERCOT's owners: Engie North America 1,953.5 MW, the five largest 22.0 percent; ERCOT's cycle on 12 and 14 November 2026, 0.70 and 0.15, beside the awards page; CAISO and ERCOT built in twelve months, 2,876 and 7,357 MW; PJM 666 MW and no battery series); rows: 16 (5 site fixed, 5 data machine, 3 browser, 3 rulings) |
