# Session 405 report: the interconnection explorer

21 October 2026, from about 05:00 UTC, unattended, on samueloldlaptop (the code machine), in the worktree `C:\Users\lossa\Documents\erw-405` on `wip/405-s` (cut from `wip/403-s`, which holds session 403's explorer and its shared parts). The chain `queue/done/015-day-20-october-code-pm.md`, "Session 405": the third signature explorer, `/explore/interconnection`, from `iso_queue_statistics`. Model spend USD 0; no pull from any publisher; no warehouse data written.

## Read these first

- **The page is `/explore/interconnection`**, in review and not in the menu (`site/lib/release.ts`; no line in `site/lib/pages.ts`). Filters in the address: `queue` (caiso, ercot, nyiso, miso, spp, isone; CAISO by default, as on the map's Queues tab), `measure` (`positions` or `mw`), `from` and `to` (the first and last entry year; by default every year the queue holds, to the newest whose year is over).
- **It stands on session 403's shared parts, unchanged**: `ExploreFrame`, `Freshness` and `FilterForm` (`site/components/explore/Explore.tsx`), the helpers of `site/lib/explore/index.ts`; no existing export was altered, so session 404's branch merges with it. Its own constants are `site/lib/explore/interconnection.ts`.
- **The fault of the first build, in one line, from the table's own header.** While the header's "Retrieved" time is before session 367's fix (commit `005b590d`, 20 October 2026 19:45:54 UTC), the page says its counts are the first build's (the read that cut rows at a "#" in a cell and lost their queue dates, most of them ERCOT's), not the queues', that it corrects none, and that they stand right once the data machine rebuilds the table, with the method note's link. The page writes none of the method note's lost-row counts and shows only what the table holds. The line goes by itself when a rebuild writes a later time; a header that cannot be read is said so.
- **The license holds of 21 October**: NYISO, MISO and ISO-NE are held as `app/map/QueuesView.tsx` holds them: a held queue is not read, its view shows "{queue}'s queue is held: license needed. Its figures are not shown; the queues of CAISO, ERCOT and SPP are." (`data-license-held="iso_queue_statistics"`), the queue list marks them "(license needed)", and in the six-queue table their rows read "license needed".
- **Every figure is a `Num` with a check key**: `series|iso_queue_statistics|<iso>:queue_<year>|<variable>|<year>-01-01T00:00:00Z` for the rows, and a new key form `series_hdr|iso_queue_statistics|iso:<grid>|Positions with no queue date|<name>` for the one count the header states (the queue's positions with no queue date). `check-values.mjs` reads the new form from the `headers` table; `Num` holds it by grid as it holds the rows (the key names `iso:<grid>`).
- **The production build passed tonight** (05:34 to 05:36 UTC, exit 0): the database answered. So the checks ran on `next start`, the floors were written from a restricted run and the shots are committed.

## What to review

In the internal view (https://erw-flame.vercel.app/internal/open first), once landed:

1. https://erw-flame.vercel.app/explore/interconnection : the default, CAISO in positions, 1999 to 2023. Headline: entered 2023, 4 (1999: 1); reached operation 0 (1999: 1); withdrawn share 1 (1999: 0). CAISO's dated positions end in 2023 (the method note), so its newest years are thin: see "For Samuel's ruling". The table's header counts 169 of CAISO's positions with no queue date. Seen on the production build at 05:38 UTC.
2. https://erw-flame.vercel.app/explore/interconnection?queue=ercot&measure=mw&from=2018&to=2025 : ERCOT in MW. 2025: entered 55,479.19 MW, reached operation 9,936.58, still waiting 45,542.61 (2018: 5,929.53, 5,744.93, 184.60). ERCOT holds no withdrawn positions; the page says so in the method note's words. The header counts 456 ERCOT positions with no queue date (the faulty build's count).
3. https://erw-flame.vercel.app/explore/interconnection?queue=spp : SPP, every status held, 2024 still waiting 61, status not stated 7.
4. https://erw-flame.vercel.app/explore/interconnection?queue=nyiso : a held queue, the words only.
5. https://erw-flame.vercel.app/explore/interconnection?queue=bogus&measure=x&to=1900 : the default, with one line saying the address asked for what the table does not hold.
6. The shots: `docs/brand/review-405/` (01 default, 02 ERCOT in MW, 03 SPP, 04 NYISO held; 1280 and 390 px each). I looked at 01_1280, 04_1280 and, on `next dev`, the 390 px views of the default and of ERCOT in MW.

## What was done

- `site/app/explore/interconnection/page.tsx` (new). Reads: the table's header (`headers`), the chosen queue's rows (`entity like <iso>:queue_*`, not asked for a held queue), and the unheld queues' rows of the last entry year (one `in.(...)` read, held grids not named). Draws: three headline figures for the last entry year with the first year's beside them (entered, reached operation, and the withdrawn share, or still waiting where the queue holds no withdrawn count), in positions or MW; the entry years by status as stacked bars through the shared `SeriesChart` (operating, withdrawn, waiting, no status: each part a row of the table, an entry year not over hatched); the withdrawn share and the median wait by entry year through `LineChart` where the queue holds them; every entry year in a table; the six queues side by side in the last entry year; a line naming the map's Queues tab and `/queues` (Berkeley Lab's Queued Up); the method link, the downloads line and the source line from the frame. The page adds nothing up.
- `site/lib/explore/interconnection.ts` (new, no import, no read): the six queues, the not-held lines (the map tab's words), the four statuses, the header readers (`builtAt`, `faultyBuild`, `inputRetrieved`, `headerCount`), the key of the header's count, the partial-year rule.
- `site/lib/release.ts`: the page in review (its line beside `/queues`, away from 403's and 404's lines).
- `site/scripts/check-values.mjs`: four views in its list (beside the map's Queues tab lines); the `series_hdr|` key form. `site/scripts/check-values-floor.json`: the floors of the four views from a restricted run that passed (10, 10, 10, and 0 for the held NYISO view). `site/scripts/check-routes.mjs`: three addresses (beside `/queues`).
- `docs/methods/energy_projects.md`: a section "The explorer (session 405, 21 October 2026)" under Queue statistics.
- `tests/test_session405.py` (new, 12 tests).

## Checks

| Check | Exit | Result |
|---|---|---|
| `npm ci` (the worktree had none) | 0 | |
| `npx tsc --noEmit`, after `npm run content` and `next typegen` | 0 | the first run (2) came before `next typegen`: only the generated `PageProps` were missing |
| `npx eslint app/explore/interconnection lib/explore` | 0 | |
| The page through the internal door on `next dev` (3405), five addresses | 0 | status 200 each; 218, 38, 229, 0 and 218 keys; no "undefined" or "NaN" in the visible text |
| `check-values`, `CHECK_VALUES_PAGES=/explore/interconnection`, on `next dev` | 0 | 452 of 452 (before the headline followed the measure) |
| `npm run build` (05:34 to 05:36 UTC) | 0 | the database answered tonight |
| `check-values` restricted, on `next start`, twice | 0, 0 | 449 of 449 each |
| `check-values` restricted with `CHECK_VALUES_WRITE_FLOOR=1` | 0 | 449 of 449; the floors of the four views written, every other floor as it was |
| `check-values`, `CHECK_VALUES_PAGES=/map` (the Queues tab, unchanged) | 1 | 566 of 566 values match; one failure: `/map` (the projects tab) carries 0 checked numbers against its floor of 1, because its one number is held since the license holds of 21 October (`data-license-held` on the page). Not this session's change: see "For Samuel's ruling" |
| `check-table-downloads` on the page | 0 | 1 of 1; the line says the table is not in the live catalogue |
| Eight shots, `docs/brand/review-405/` | 0 each | |
| `tests.test_session405` | 0 | 12 tests |
| Tests near the change (the 36 modules that name `iso_queue_statistics`, `/explore/`, the floor, `check-routes.mjs`, `energy_projects.md`) | 0 | 514 tests, 32 skipped |
| Whole suite (`ERW_LOCK_EXEMPT=1 ... unittest discover -s tests`) | 1 | 4,807 tests, 253 skipped, one failure: `test_session156` (the ask fixtures), foreseen by the chain's rules |

`next dev` rewrote `site/AGENTS.md`; it was restored and not committed. The dev and production servers on 3405 were stopped and the build mutex released.

## Decisions made without you

- **The default queue is CAISO**, as on the map's Queues tab; the default window runs from the first entry year held to the newest whose year is over (403's rule of the newest complete period).
- **An entry year is partial** when it is at or after the year the queue was retrieved (the header's "Inputs read" line), so 2026 is hatched and marked.
- **The fault line keys on the header's build time** against the fix's commit time, not on a hand-set flag, so it goes by itself after the rebuild; the page does not write the method note's lost-row counts (450 ERCOT and the others: they are a measurement in `runs/`, not a row of a table).
- **The header's count of positions with no queue date is a figure**, so it got a check key; `series_hdr|` is the new key form, read by check-values from the `headers` table.
- **The stacked chart names its series short** (Operating, Withdrawn, Waiting, No status): the four long names ran over the unit label at 390 px. The tables keep the full words.
- **Withdrawn is drawn in the muted token**, not the rule color `/queues` uses: on the paper background the rule color made the name of the series and its bars nearly invisible.
- **The headline follows the measure** (MW in the MW view); the withdrawn share stays a share of positions, as the table defines it.

## For Samuel's ruling

- `iso_queue_statistics` is not in the live catalogue (the page's freshness line says "not in the site's catalogue" and its downloads line says the table is not in the live set): the data machine's catalogue load.
- `/map`'s floor of 1 checked number fails since 21 October, its one number being held by the license hold: (a) set its floor to 0; (b) leave it to the landing's ruling.
- The default view: CAISO's newest complete entry year held is 2023, with 4 positions (CAISO's dated positions end in 2023), so the headline compares 4 against 1999's 1: (a) keep CAISO; (b) default to SPP or ERCOT, whose recent years are full.
- Queues are drawn at three addresses now: `/map?tab=queues` (this table, one queue), `/queues` (Berkeley Lab's Queued Up) and `/explore/interconnection`: keep all three, or send the map's tab to the explorer.
- The shared `LineChart` writes a year twice on its axis when a chart holds few years (ERCOT's median wait, 2018 to 2025: "2020" twice): a fix in `components/TimeChart.tsx` for another session.

## To finish

- **The data machine rebuilds `iso_queue_statistics`** (the fix is on main): then the fault line leaves the page by itself; run `MSYS_NO_PATHCONV=1 CHECK_VALUES_PAGES=/explore/interconnection node scripts/check-values.mjs <base>` again, since every count moves.
- **Merging with session 404**: both branches add floor lines to `site/scripts/check-values-floor.json` between `/events/uri-2021` and `/grid`; if git marks a conflict there, keep both blocks.
- The landing's full `check-values` and `check-routes` read the page with the rest.

## Files

- `site/app/explore/interconnection/page.tsx`, `site/lib/explore/interconnection.ts` (new)
- `site/lib/release.ts`, `site/scripts/check-values.mjs`, `site/scripts/check-values-floor.json`, `site/scripts/check-routes.mjs`, `docs/methods/energy_projects.md`
- `tests/test_session405.py` (new), `docs/brand/review-405/` (eight shots), this report
- Run outputs (not in git): `C:\Users\lossa\Documents\erw\runs\chain_oct21\s405\`

## Finished on the combined branch (21 October)

On `wip/015-finish` (the worktree `C:\Users\lossa\Documents\erw-finish`, cut from `wip/015-land`: sessions 401 to 410, 413 and 414 merged on main), 21 October 2026, 09:17 to 09:42 UTC under the build mutex: `duty.py beat` exit 0, `npm ci` exit 0, **one build, `npm run build` exit 0** (no statement timeout in its log), `npx next start -p 3415`. Every output is under `runs/chain_oct21/finish/` (outside git). Common to every section below: the **full `check-values.mjs`** (no restriction) exit 1: **6,359 of 6,359 values match Supabase**; 10 pages below their floors, exactly session 408's list with its counts (`/deals` 0 of 10, `/map` 0 of 1, `/events` 2 of 9, `/events/uri-2021` 9 of 10, `/events/covid-2020` 7 of 10, `/events/caiso-heat-2020`, `/events/caiso-heat-2022` and `/events/east-heat-2025` 0 of 10, `/learn/bill` 5 of 10, `/research/card/gas_sets_price` 4 of 6), every one license-held, expected; no other failure. **`check-routes.mjs`** exit 0 (1 live page and 223 in review asked as a visitor, 0 failed). The **whole suite** (`ERW_LOCK_EXEMPT=1 python -m unittest discover -s tests`, 09:43 to 09:49 UTC, the server stopped) exit 1: 4,911 tests, 1 failure, `test_session156` (the ask fixtures, the chain's known failure tonight), 254 skipped; the ten sessions' own modules (402 to 410, 414) exit 0, 107 tests. The server was stopped and the mutex released at 09:42 UTC.

- **The page after the queue table's rebuild:** the build of 09:18 UTC read `iso_queue_statistics` after the data machine rebuilt it (SPP's 2023 cohort reads 436 entered and 341 withdrawn, where the 20 October run read 435 and 340). The restricted `/explore/` run (exit 0, 867 of 867) read `/explore/interconnection` with its new counts, and the line on the first build's fault is gone from the page (read in the browser on the default view and `?queue=ercot`: no such line). The four floor lines stayed as written.
- The MW view's four statuses were named by no note when session 409's script read the site; `docs/methods/energy_projects.md`, "The explorer", gained the line "The figures in MW and their keys" (commit `fc1496c4`).
- The full check-values and check-routes read the page with the rest (above). `tests.test_session405`: exit 0 within the ten sessions' modules.
