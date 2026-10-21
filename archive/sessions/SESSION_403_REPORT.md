# Session 403 report: the ERCOT peak premium explorer

21 October 2026, from about 04:15 UTC, unattended, on samueloldlaptop (the code machine), in the worktree `C:\Users\lossa\Documents\erw-403` on `wip/403-s` (cut from `wip/381-382-land`). The chain `queue/done/015-day-20-october-code-pm.md`, "Session 403": platform tool 5, the first signature explorer. Model spend USD 0; no pull from any publisher; no warehouse data written.

## Read these first

- **The page is `/explore/ercot-peak-premium`**, in review and not in the menu (`site/lib/release.ts`; no line in `site/lib/pages.ts`). Its default view is the thesis's comparison: HB_HUBAVG, the whole year, 2015 (the first year held) against 2025 (the newest complete year). Filters in the address: `hub`, `month` (blank for the whole year from `ercot_peak_premium_annual`, 1 to 12 for that calendar month of each year from `ercot_peak_premium_monthly`), `from` and `to`.
- **How it relates to the older explorer.** `/explorer/ercot-peak-premium` (session 11) has redirected since session 239 to the ERCOT tab of `/prices` (`next.config.ts`; the view is `site/app/explorer/ercot-peak-premium/view.tsx`), which draws the same two tables one hub and one year at a time, in the browser. Both stay as they were: nothing removed or redirected. The new address sets two years side by side (the thesis chart), reads one month across the years, and draws every figure on the server from the address, so each view can be linked and every figure is checked. It reuses what the old one draws: `components/BoxChart.tsx` (the shared `BoxPlot`), `components/LineChart.tsx`, the same blocks, statistics and completeness rule. Whether the tab, the redirect and the new address should become one is under "For Samuel's ruling".
- **Stale since 29 September 2026, stated on the page from the data.** The freshness line reads each table's `last_run` and `ts_max` from the catalogue and the header's "Last input interval"; no date is written by hand (a test checks the sources). On 21 October it reads both tables as last computed on 29 September 2026, the newest period 2026 and September 2026, the newest interval 28 September 2026 04:45 UTC.
- **The shared parts for sessions 404 and 405**: `site/components/explore/Explore.tsx` (`ExploreFrame`: brand, sheet, header with the one-line definition, the freshness line, filters, method link, `TableDownloads`, `SourceLine`; `Freshness`; `FilterForm`, a GET form of `AutoSubmitSelect`s with a Show button and a Reset), `site/lib/explore/index.ts` (address and date helpers, no read, safe for a client component) and `site/lib/explore/fresh.ts` (the catalogue read). The explorer's own constants are `site/lib/explore/peakpremium.ts`.
- **check-values change**: `CHECK_VALUES_WRITE_FLOOR=1` with `CHECK_VALUES_PAGES` set used to refuse to write; a restricted run that passes in full now sets the floors of the pages it read and leaves every other line of `check-values-floor.json` as it was (the chain asked for a floor from a restricted run).
- **No production build tonight**: three tries (04:28, 04:50 and 05:07 UTC) each compiled and type-checked and then failed to prerender the home page `/` on the database's statement timeouts (`Supabase entities: HTTP 500 ... 57014`), as the chain's rules foresaw. So the production checks, the floor and the shots wait under "To finish". The page itself was seen working on `next dev` at port 3403 (below): **check-values 216 of 216** on its four views, the thesis values reproduced on the default view.

## What to review

In the internal view (https://erw-flame.vercel.app/internal/open first), once landed:

1. https://erw-flame.vercel.app/explore/ercot-peak-premium : the default, HB_HUBAVG 2015 against 2025, whole year. The headline row reads peak-block IQR 34.12 (2015: 7.64), peak median minus midday median 14.52 (2015: -0.16), median 25.68 (2015: 20.49) USD/MWh; the thesis's figures table has the 99.9th percentile 583.96 and 311.80 and the midday minimum -3.98 and -18.25 (the method note's reproduction table, to the cent). Seen on `next dev`, 21 October about 05:12 UTC.
2. https://erw-flame.vercel.app/explore/ercot-peak-premium?month=8 : August of each year from the monthly table (default August 2015 against August 2026, the newest complete August).
3. https://erw-flame.vercel.app/explore/ercot-peak-premium?hub=ercot%3AHB_HOUSTON&month=2&from=2020&to=2021 : Houston's February of Winter Storm Uri against the year before (the box plot's axis runs to about 1,000 USD/MWh and squeezes the 2020 boxes: that is the data).
4. https://erw-flame.vercel.app/explore/ercot-peak-premium?hub=bogus&to=1999 : a value not held falls back to the default, with one line saying so.
5. The freshness block at the top: "Stale since 29 September 2026" for each table, the newest period (2026; September 2026) and the newest interval (28 September 2026 04:45 UTC), all read from the catalogue and the header.

## What was done

- `site/app/explore/ercot-peak-premium/page.tsx` (new): the explorer. Its reads, all small and keyed by hub: the annual table's `n_intervals` for every hub (the hub and year lists, and which years are complete), the hub's rows of the annual table (or, with a month, of the monthly table at that month of every year, one `in.(...)` read), the hub's monthly block medians, and the header. It draws three headline numbers, the thesis chart (`BoxChart`: four blocks, two years each), the five numbers of each block, the thesis's nine figures for both years, the peak premium along the years (`LineChart`), the monthly medians by block (`LineChart`), a line saying how it relates to the ERCOT tab of `/prices`, the method link, the downloads line and the source line. Every figure is a `Num` with key `series|<table>|<hub>|<variable>|<period>`; the page computes no figure.
- `site/components/explore/Explore.tsx`, `site/lib/explore/index.ts`, `site/lib/explore/fresh.ts` (new, shared); `site/lib/explore/peakpremium.ts` (new: this explorer's constants, the year and month completeness rules, the header's last interval).
- `site/lib/release.ts`: `/explore/ercot-peak-premium` in review. Not in `site/lib/pages.ts`, so not in the menu.
- `site/scripts/check-values.mjs`: four views of the page in its list; a restricted run with `CHECK_VALUES_WRITE_FLOOR=1` that passes in full sets the floors of the pages it read only (it refused before). `site/scripts/check-routes.mjs`: the page in its list.
- `docs/methods/ercot_peak_premium.md`: the note existed; a section "The explorer (session 403, 21 October 2026)" says what the page draws, its filters, its partial-period rules and where its dates come from.
- `tests/test_session403.py` (new, 13 tests): the release line, no menu line, the old redirect untouched, the two tables and the key form, the shared charts only, the frame's freshness read and no hand-written date, the fallback line, the helpers run through node (partial months, the header line, the address helpers), every past month of the monthly table complete by the page's rule (run once against the main copy's `warehouse/output/ercot_peak_premium_monthly.csv`, 846 months, none misread; skipped where the table is absent), the check lists and the floor code, the method note.

## Checks

| Check | Exit | Result |
|---|---|---|
| `tests.test_session403` | 0 | 13 tests, 1 skipped in the worktree (the monthly CSV is not there); the skipped one passed against the main copy's table |
| Tests near the change: `test_session268`, `328`, `239`, `317`, `300`, `332` | 0 | 62 OK |
| The 121 test modules that name the explorer, `release.ts` or `check-values.mjs`, first run | 1 | run while `npm ci` and the first build were writing `node_modules` and `content/`: seven node-backed tests failed on "nothing at @/content/docs.json", plus one empty module name from my own list. Rerun after the build: `test_session121`, `137`, `143`, `148`, `153`, `161` pass; `test_session156` fails (the ask fixtures, foreseen by the chain's rules) |
| `npx tsc --noEmit` | 2, then 0 | the first run came before the build's content step (generated `PageProps` and `content/*.json` missing); 0 on builds 2 and 3 and after the last edit |
| `npx eslint app/explore components/explore lib/explore` | 0 | |
| Impeccable `detect --json` on the page and the frame | 0 | `[]` |
| `npm run build`, three tries (04:28, 04:50, 05:07 UTC) | 1, 1, 1 | compiled and type-checked; the prerender of `/` failed on `Supabase entities: HTTP 500 ... statement timeout` each time |
| `check-values`, `CHECK_VALUES_PAGES=/explore/`, against `next dev` on 3403 | 0 | 216 of 216 values match Supabase on the four views (not the production build; the floor was not written from it) |
| The page through the internal door on `next dev`, five addresses | 0 | status 200 on each, 64 keys a view, no "undefined"; `?month=8` answered "no data" once on its first read (a statement timeout) and in full on the next |
| Whole suite (`ERW_LOCK_EXEMPT=1 ... unittest discover -s tests`) | 1 | 4,795 tests, 253 skipped, one failure: `test_session156` (the ask fixtures), foreseen by the chain's rules |

Two dev-server shots were looked at (1280, the default; 390, Houston's February 2021) and not committed: the page lays out at both widths; at 390 the five-number table scrolls inside its frame (seven columns), as the site's tables do, and the thesis-figures table was narrowed to fit. The dev server's "1 issue" badge is its own `eval` warning (development only).

## Decisions made without you

- **The thesis chart** is read as the method note's thesis comparison: the distribution by time-of-day block, two years side by side (default 2015 against the newest complete year), with the thesis's four figures and the five others the note defines. If the thesis's own chart is another drawing, the page's first chart is the place to change.
- **Month as a filter** reads one calendar month across the years from the monthly table (the box plot, the figures and the along-the-years chart all follow it); the whole-year view reads the annual table.
- **A month is partial** when its interval count is below its days times 96 less four (the clock change); checked against every month of the table.
- **Stale** is more than three days since the catalogue's last run; the line names the date, so the threshold only decides the emphasis.
- **The floor rule of check-values** was extended: a passing restricted run may set its own pages' floors and only those. A full run still rewrites the whole file as before.
- **The old explorer** (`/explorer/ercot-peak-premium`, redirecting to `/prices?tab=ercot`) is untouched, as the chain asked.
- **A `next dev` server** stood in for the production build to see the page and check its values, under the build mutex; the production checks wait. `next dev` rewrote `site/AGENTS.md`; the change was restored and not committed.

## For Samuel's ruling

- The ERCOT peak premium is drawn at two addresses now, the ERCOT tab of `/prices` (where `/explorer/ercot-peak-premium` redirects) and `/explore/ercot-peak-premium`: (a) keep both; (b) send the old address to the new explorer; (c) make the tab link to the explorer and draw less.
- `ercot_peak_premium_annual` and `_monthly` have not been computed since 29 September 2026 (the page says so): the data machine's daily derived step for them.

## To finish

On the code machine, in `C:\Users\lossa\Documents\erw-403` (or the landing's copy), once the database answers the build's reads, under the build mutex (`runs/build.lock` with `owner.txt`, `scripts/duty.py beat` first):

```bash
cd C:/Users/lossa/Documents/erw-403/site
npm run build > C:/Users/lossa/Documents/erw/runs/chain_oct21/s403/build4.out 2>&1; echo "build exit=$?"
npx next start -p 3403        # in the background
bash C:/Users/lossa/Documents/erw/runs/chain_oct21/s403/checks.sh      # check-values on /explore/ twice, /prices (the older view), check-table-downloads, eight shots into docs/brand/review-403/
MSYS_NO_PATHCONV=1 CHECK_VALUES_WRITE_FLOOR=1 CHECK_VALUES_PAGES=/explore/ node scripts/check-values.mjs http://localhost:3403; echo "exit=$?"   # the floors of the four views
git add scripts/check-values-floor.json ../docs/brand/review-403 && git commit -m "Session 403: the explorer's floor and shots"
# then stop the process listening on 3403, remove owner.txt and rmdir the lock
```

Then the landing's full `check-values` and `check-routes` read the page with the rest. Look at each PNG before describing it.

## Files

- `site/app/explore/ercot-peak-premium/page.tsx`, `site/components/explore/Explore.tsx`, `site/lib/explore/index.ts`, `site/lib/explore/fresh.ts`, `site/lib/explore/peakpremium.ts` (new)
- `site/lib/release.ts`, `site/scripts/check-values.mjs`, `site/scripts/check-routes.mjs`, `docs/methods/ercot_peak_premium.md`
- `tests/test_session403.py` (new), this report
- Run outputs (not in git): `C:\Users\lossa\Documents\erw\runs\chain_oct21\s403\`
