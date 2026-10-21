# Performance review of the visitor pages, 20 October 2026 chain (session 411)

Energy Research Warehouse (ERW), session 411, run on 21 October 2026 from about 07:55 to 09:15 UTC on the code machine (samueloldlaptop), in the worktree `erw-411` on `wip/411-s` (from `origin/main` at `bb49c9e0`). Chain `queue/done/015-day-20-october-code-pm.md`, "Session 411". No figure on any page changed: the fixes move bytes and reserved room, not values (check-values below).

## How it was measured

- **Pages.** The 25 addresses of `site/scripts/snapshot-live.mjs` and the tool pages not among them (`/cost-of-power`, `/research`, which `/analysis` redirects to, and `/grid`; `/network` is one of the 25 and redirects to `/grid?view=network`): 28 pages, each at 1280 and at 390 px, 56 runs a set.
- **Where.** A local production build only (`npm run build`, `npx next start -p 3411`), never production, under the build mutex, one run at a time.
- **The internal view.** Every page is in review, so each run opens the internal view first: the token is posted to `/internal/unlock` in the body (`browser.mjs` `unlockPost`) and the two cookies it answers are set in the browser for `localhost` only. Each run checks that the page was not the in-review curtain: none of the runs was.
- **The tool.** `site/scripts/lighthouse-pages.mjs` (new), Lighthouse 13.4.1 from npm with its own puppeteer-core, the machine's Chrome 155 headless with a fresh profile, closed at the end. The copy of Lighthouse bundled in the installed chrome-devtools-mcp 1.10.1 was tried first and is not used: its performance audits are shims ("This audit was filtered out and is not available in this bundle"), so it scores every page 100 for performance whatever the page does. The runner refuses such a report.
- **The two forms.** 1280 by 800, desktop, Lighthouse's desktop throttling (40 ms, 10 Mbit/s, no CPU slowdown). 390 by 844, mobile, Lighthouse's default mobile throttling (simulated slow 4G, CPU 4x). Scores are Lighthouse's 0 to 100: performance, accessibility, best practices, SEO.
- **Noise.** Two pages that differ only in a query (the twelve battery addresses) differ by up to 7 points of mobile performance in one set, so a move of a few points is not a finding. Two "after" sets taken from 08:20 to 08:45 UTC were spoiled by the machine: in 20 and 26 of 56 runs the GPU process stalled the page for about 420 ms (a trace names it: one `GPUTask` of 413 ms, the page's main thread waiting, "Unattributable" in Lighthouse), against 1 of 56 in the "before" set. A side-by-side run of the two builds on six pages at 08:50 UTC scored them the same, and a third full set at 08:55 UTC had 1 such run of 56: that set is the "after" below. The spoiled sets are kept in `runs/chain_oct21/s411/` (`final.json`, `final2.json`).

## Scores before

Build of `origin/main` at `bb49c9e0`, set taken 08:00 to 08:10 UTC. Means: performance 97.9 at 1280 (84 to 100) and 88.1 at 390 (72 to 95); accessibility 96.5 and 92.8; best practices 100 and 100; SEO 100 and 100.

| Page | 1280 perf | 1280 a11y | 1280 bp | 1280 seo | 390 perf | 390 a11y | 390 bp | 390 seo |
|---|---|---|---|---|---|---|---|---|
| `/` | 100 | 96 | 100 | 100 | 92 | 92 | 100 | 100 |
| `/about` | 100 | 92 | 100 | 100 | 91 | 92 | 100 | 100 |
| `/storage` | 84 | 96 | 100 | 100 | 91 | 92 | 100 | 100 |
| `/cost-of-power/seller` | 99 | 97 | 100 | 100 | 87 | 93 | 100 | 100 |
| `/network` | 92 | 96 | 100 | 100 | 72 | 93 | 100 | 100 |
| `/cost-of-power/battery` | 99 | 97 | 100 | 100 | 87 | 93 | 100 | 100 |
| `/cost-of-power/battery?grid=ercot&dur=2&strat=foresight` | 99 | 97 | 100 | 100 | 88 | 93 | 100 | 100 |
| `/cost-of-power/battery?grid=ercot&dur=2&strat=dayahead` | 99 | 97 | 100 | 100 | 87 | 93 | 100 | 100 |
| `/cost-of-power/battery?grid=ercot&dur=4&strat=foresight` | 99 | 97 | 100 | 100 | 88 | 93 | 100 | 100 |
| `/cost-of-power/battery?grid=ercot&dur=4&strat=dayahead` | 99 | 97 | 100 | 100 | 86 | 93 | 100 | 100 |
| `/cost-of-power/battery?grid=ercot&dur=8&strat=foresight` | 99 | 97 | 100 | 100 | 88 | 93 | 100 | 100 |
| `/cost-of-power/battery?grid=ercot&dur=8&strat=dayahead` | 99 | 97 | 100 | 100 | 88 | 93 | 100 | 100 |
| `/cost-of-power/battery?grid=caiso&dur=2&strat=foresight` | 99 | 97 | 100 | 100 | 87 | 93 | 100 | 100 |
| `/cost-of-power/battery?grid=caiso&dur=2&strat=dayahead` | 99 | 97 | 100 | 100 | 92 | 93 | 100 | 100 |
| `/cost-of-power/battery?grid=caiso&dur=4&strat=foresight` | 99 | 97 | 100 | 100 | 86 | 93 | 100 | 100 |
| `/cost-of-power/battery?grid=caiso&dur=4&strat=dayahead` | 99 | 97 | 100 | 100 | 87 | 93 | 100 | 100 |
| `/cost-of-power/battery?grid=caiso&dur=8&strat=foresight` | 99 | 97 | 100 | 100 | 87 | 93 | 100 | 100 |
| `/cost-of-power/battery?grid=caiso&dur=8&strat=dayahead` | 99 | 97 | 100 | 100 | 93 | 93 | 100 | 100 |
| `/cost-of-power/seller?iso=caiso&asset=solar` | 99 | 97 | 100 | 100 | 86 | 93 | 100 | 100 |
| `/cost-of-power/seller?iso=caiso&asset=wind` | 99 | 97 | 100 | 100 | 87 | 93 | 100 | 100 |
| `/terms` | 100 | 96 | 100 | 100 | 93 | 92 | 100 | 100 |
| `/data/methods/battery_stack` | 100 | 96 | 100 | 100 | 92 | 92 | 100 | 100 |
| `/data/methods/cost_of_power` | 100 | 96 | 100 | 100 | 93 | 92 | 100 | 100 |
| `/data/methods/grid_network` | 100 | 96 | 100 | 100 | 92 | 92 | 100 | 100 |
| `/data/methods/storage` | 100 | 96 | 100 | 100 | 95 | 92 | 100 | 100 |
| `/cost-of-power` | 88 | 97 | 100 | 100 | 84 | 93 | 100 | 100 |
| `/research` | 100 | 97 | 100 | 100 | 79 | 94 | 100 | 100 |
| `/grid` | 93 | 96 | 100 | 100 | 89 | 93 | 100 | 100 |

## Fixed

What needed no ruling and was neither session 401's (the five tool pages' own files) nor session 412's (the shared components' accessibility):

1. **The home page's chart of the day was fetched by every page that shows the header's ERW mark** (`site/app/layout.tsx`). React's server renderer adds a preload for every eager `<img>` it renders; the header's link to `/` is prefetched when it is on screen, and the prefetched home page carried the preload of `/digest-charts/<day>.png` (156 KB, a 1200 by 880 PNG) into the page being read. Lighthouse saw it on `/about`, `/terms`, the four methods pages, `/storage`, `/grid`, `/network` (both widths) and `/research` (at 390 px); the battery, seller and cost-of-power pages do not prefetch (`components/SiteLink.tsx` `NO_PREFETCH`). The link is now `prefetch={false}`: a visitor going home waits for the page as for any first visit; nothing else changes. Measured: 165 to 172 KB less on each of those pages (for example `/about` 521 to 355 KB, `/terms` 534 to 368 KB, `/grid` at 1280 650 to 481 KB); mean weight of the 28 pages 492 to 438 KB at 1280 and 487 to 427 KB at 390. A visitor sees the link greyed today (the home page is in review, so for a visitor it is not a link and nothing was prefetched); the waste was the internal view's, and would have been every visitor's once the home page opens.
2. **The chart of the day reserved the wrong room** (`site/app/page.tsx`, `site/scripts/build-content.mjs`, `site/lib/markdown.ts`). The home page wrote `width=1600 height=900` for a picture of 1200 by 880, so until it arrived the browser kept a box of the wrong shape (16:9 for 15:11) and the content under it moved when it came. `build-content.mjs` now reads each chart's size from its PNG header into the content bundle, and the page writes it (1200 by 880 for all eight charts held). The page drawn after load is the same: shots `docs/brand/review-411/home_today_{1280,390}_{before,after}.png`. The same `1600 by 900` is written in `site/app/research/page.tsx`, a file of session 401's: listed below for it.
3. **Unused imports** (ESLint's `no-unused-vars`, files neither session touches): `ReactNode` in `site/app/deals/v2/view.tsx`, `NoData` in `site/components/grid/YourGrid.tsx`, `hrefOf` in `site/components/mix/views.tsx`, `type Fuel` in `site/app/cost-of-power/seller/tables.csv/route.ts`. No change to any page's output; the bundler dropped most of them already.

Tried and reverted:

- **Inter not preloaded.** On every branded page (all but `/ask`, `/home/v2`, `/severance/finder` and `/severance/lease/real`) no element is drawn in Inter once the page has loaded, yet its 49 KB file is fetched first, beside the brand's four. With `preload: false` the file was still fetched (by the stylesheet, about 100 ms later: some element is laid out in Inter for a moment, most likely the header before the brand's rule for it, which `components/Brand.tsx` writes inside the page's body, has been read), and Lighthouse's first paint at 390 px moved from about 1,060 to 1,360 ms on every page. So no bytes were saved and the first paint was later: the change was undone before the final build. The cause is listed below.

Not found: no chart drew twice in any run (no console error, no duplicate render in the traces read); `best-practices` and `SEO` are 100 on every page at both widths before and after.

## Scores after

Build of `wip/411-s` with the three fixes, set taken 08:55 to 09:04 UTC (see "Noise"). Means: performance 98.3 at 1280 (85 to 100) and 88.8 at 390 (79 to 94); accessibility, best practices and SEO as before (the fixes touch none of their audits).

| Page | 1280 perf | 1280 a11y | 1280 bp | 1280 seo | 390 perf | 390 a11y | 390 bp | 390 seo |
|---|---|---|---|---|---|---|---|---|
| `/` | 100 | 96 | 100 | 100 | 93 | 92 | 100 | 100 |
| `/about` | 100 | 92 | 100 | 100 | 92 | 92 | 100 | 100 |
| `/storage` | 85 | 96 | 100 | 100 | 92 | 92 | 100 | 100 |
| `/cost-of-power/seller` | 99 | 97 | 100 | 100 | 87 | 93 | 100 | 100 |
| `/network` | 93 | 96 | 100 | 100 | 79 | 93 | 100 | 100 |
| `/cost-of-power/battery` | 99 | 97 | 100 | 100 | 89 | 93 | 100 | 100 |
| `/cost-of-power/battery?grid=ercot&dur=2&strat=foresight` | 99 | 97 | 100 | 100 | 89 | 93 | 100 | 100 |
| `/cost-of-power/battery?grid=ercot&dur=2&strat=dayahead` | 99 | 97 | 100 | 100 | 89 | 93 | 100 | 100 |
| `/cost-of-power/battery?grid=ercot&dur=4&strat=foresight` | 99 | 97 | 100 | 100 | 88 | 93 | 100 | 100 |
| `/cost-of-power/battery?grid=ercot&dur=4&strat=dayahead` | 99 | 97 | 100 | 100 | 88 | 93 | 100 | 100 |
| `/cost-of-power/battery?grid=ercot&dur=8&strat=foresight` | 99 | 97 | 100 | 100 | 88 | 93 | 100 | 100 |
| `/cost-of-power/battery?grid=ercot&dur=8&strat=dayahead` | 99 | 97 | 100 | 100 | 88 | 93 | 100 | 100 |
| `/cost-of-power/battery?grid=caiso&dur=2&strat=foresight` | 99 | 97 | 100 | 100 | 88 | 93 | 100 | 100 |
| `/cost-of-power/battery?grid=caiso&dur=2&strat=dayahead` | 99 | 97 | 100 | 100 | 88 | 93 | 100 | 100 |
| `/cost-of-power/battery?grid=caiso&dur=4&strat=foresight` | 99 | 97 | 100 | 100 | 88 | 93 | 100 | 100 |
| `/cost-of-power/battery?grid=caiso&dur=4&strat=dayahead` | 99 | 97 | 100 | 100 | 88 | 93 | 100 | 100 |
| `/cost-of-power/battery?grid=caiso&dur=8&strat=foresight` | 99 | 97 | 100 | 100 | 88 | 93 | 100 | 100 |
| `/cost-of-power/battery?grid=caiso&dur=8&strat=dayahead` | 99 | 97 | 100 | 100 | 83 | 93 | 100 | 100 |
| `/cost-of-power/seller?iso=caiso&asset=solar` | 99 | 97 | 100 | 100 | 87 | 93 | 100 | 100 |
| `/cost-of-power/seller?iso=caiso&asset=wind` | 99 | 97 | 100 | 100 | 87 | 93 | 100 | 100 |
| `/terms` | 100 | 96 | 100 | 100 | 94 | 92 | 100 | 100 |
| `/data/methods/battery_stack` | 100 | 96 | 100 | 100 | 92 | 92 | 100 | 100 |
| `/data/methods/cost_of_power` | 100 | 96 | 100 | 100 | 93 | 92 | 100 | 100 |
| `/data/methods/grid_network` | 100 | 96 | 100 | 100 | 92 | 92 | 100 | 100 |
| `/data/methods/storage` | 100 | 96 | 100 | 100 | 94 | 92 | 100 | 100 |
| `/cost-of-power` | 99 | 97 | 100 | 100 | 89 | 93 | 100 | 100 |
| `/research` | 99 | 97 | 100 | 100 | 83 | 94 | 100 | 100 |
| `/grid` | 93 | 96 | 100 | 100 | 89 | 93 | 100 | 100 |

Before and after, with the largest paint and the weight (KB transferred):

| Page | width | perf before, after | LCP ms before, after | bytes KB before, after |
|---|---|---|---|---|
| `/` | 1280 | 100, 100 | 667, 782 | 820, 810 |
| `/` | 390 | 92, 93 | 3269, 3201 | 686, 675 |
| `/about` | 1280 | 100, 100 | 644, 652 | 521, 355 |
| `/about` | 390 | 91, 92 | 3118, 3126 | 521, 356 |
| `/storage` | 1280 | 84, 85 | 703, 698 | 596, 429 |
| `/storage` | 390 | 91, 92 | 3435, 3287 | 596, 430 |
| `/cost-of-power/seller` | 1280 | 99, 99 | 701, 690 | 407, 407 |
| `/cost-of-power/seller` | 390 | 87, 87 | 3458, 3435 | 407, 407 |
| `/network` | 1280 | 92, 93 | 815, 807 | 1056, 890 |
| `/network` | 390 | 72, 79 | 3976, 3920 | 1052, 881 |
| `/cost-of-power/battery` | 1280 | 99, 99 | 710, 688 | 383, 383 |
| `/cost-of-power/battery` | 390 | 87, 89 | 3455, 3436 | 383, 383 |
| `/cost-of-power/battery?grid=ercot&dur=2&strat=foresight` | 1280 | 99, 99 | 710, 686 | 383, 383 |
| `/cost-of-power/battery?grid=ercot&dur=2&strat=foresight` | 390 | 88, 89 | 3456, 3433 | 383, 383 |
| `/cost-of-power/battery?grid=ercot&dur=2&strat=dayahead` | 1280 | 99, 99 | 708, 691 | 383, 383 |
| `/cost-of-power/battery?grid=ercot&dur=2&strat=dayahead` | 390 | 87, 89 | 3445, 3436 | 383, 383 |
| `/cost-of-power/battery?grid=ercot&dur=4&strat=foresight` | 1280 | 99, 99 | 699, 685 | 383, 383 |
| `/cost-of-power/battery?grid=ercot&dur=4&strat=foresight` | 390 | 88, 88 | 3446, 3451 | 383, 383 |
| `/cost-of-power/battery?grid=ercot&dur=4&strat=dayahead` | 1280 | 99, 99 | 708, 686 | 383, 383 |
| `/cost-of-power/battery?grid=ercot&dur=4&strat=dayahead` | 390 | 86, 88 | 3465, 3428 | 383, 383 |
| `/cost-of-power/battery?grid=ercot&dur=8&strat=foresight` | 1280 | 99, 99 | 738, 686 | 382, 382 |
| `/cost-of-power/battery?grid=ercot&dur=8&strat=foresight` | 390 | 88, 88 | 3443, 3437 | 382, 382 |
| `/cost-of-power/battery?grid=ercot&dur=8&strat=dayahead` | 1280 | 99, 99 | 721, 683 | 382, 382 |
| `/cost-of-power/battery?grid=ercot&dur=8&strat=dayahead` | 390 | 88, 88 | 3448, 3434 | 382, 382 |
| `/cost-of-power/battery?grid=caiso&dur=2&strat=foresight` | 1280 | 99, 99 | 696, 703 | 375, 375 |
| `/cost-of-power/battery?grid=caiso&dur=2&strat=foresight` | 390 | 87, 88 | 3444, 3441 | 375, 375 |
| `/cost-of-power/battery?grid=caiso&dur=2&strat=dayahead` | 1280 | 99, 99 | 681, 687 | 374, 374 |
| `/cost-of-power/battery?grid=caiso&dur=2&strat=dayahead` | 390 | 92, 88 | 2877, 3427 | 374, 374 |
| `/cost-of-power/battery?grid=caiso&dur=4&strat=foresight` | 1280 | 99, 99 | 691, 689 | 374, 374 |
| `/cost-of-power/battery?grid=caiso&dur=4&strat=foresight` | 390 | 86, 88 | 3452, 3430 | 374, 374 |
| `/cost-of-power/battery?grid=caiso&dur=4&strat=dayahead` | 1280 | 99, 99 | 712, 686 | 374, 374 |
| `/cost-of-power/battery?grid=caiso&dur=4&strat=dayahead` | 390 | 87, 88 | 3467, 3445 | 374, 374 |
| `/cost-of-power/battery?grid=caiso&dur=8&strat=foresight` | 1280 | 99, 99 | 703, 683 | 374, 374 |
| `/cost-of-power/battery?grid=caiso&dur=8&strat=foresight` | 390 | 87, 88 | 3456, 3439 | 374, 374 |
| `/cost-of-power/battery?grid=caiso&dur=8&strat=dayahead` | 1280 | 99, 99 | 705, 690 | 374, 374 |
| `/cost-of-power/battery?grid=caiso&dur=8&strat=dayahead` | 390 | 93, 83 | 2862, 3440 | 374, 374 |
| `/cost-of-power/seller?iso=caiso&asset=solar` | 1280 | 99, 99 | 694, 688 | 396, 396 |
| `/cost-of-power/seller?iso=caiso&asset=solar` | 390 | 86, 87 | 3447, 3435 | 396, 396 |
| `/cost-of-power/seller?iso=caiso&asset=wind` | 1280 | 99, 99 | 689, 692 | 396, 396 |
| `/cost-of-power/seller?iso=caiso&asset=wind` | 390 | 87, 87 | 3444, 3431 | 396, 396 |
| `/terms` | 1280 | 100, 100 | 648, 646 | 534, 368 |
| `/terms` | 390 | 93, 94 | 3127, 2979 | 535, 368 |
| `/data/methods/battery_stack` | 1280 | 100, 100 | 700, 688 | 577, 410 |
| `/data/methods/battery_stack` | 390 | 92, 92 | 3272, 3319 | 577, 410 |
| `/data/methods/cost_of_power` | 1280 | 100, 100 | 646, 663 | 576, 410 |
| `/data/methods/cost_of_power` | 390 | 93, 93 | 3130, 3125 | 576, 409 |
| `/data/methods/grid_network` | 1280 | 100, 100 | 687, 679 | 587, 421 |
| `/data/methods/grid_network` | 390 | 92, 92 | 3281, 3324 | 587, 421 |
| `/data/methods/storage` | 1280 | 100, 100 | 615, 613 | 545, 378 |
| `/data/methods/storage` | 390 | 95, 94 | 2972, 3020 | 545, 377 |
| `/cost-of-power` | 1280 | 88, 99 | 614, 727 | 407, 407 |
| `/cost-of-power` | 390 | 84, 89 | 3012, 3580 | 407, 407 |
| `/research` | 1280 | 100, 99 | 819, 835 | 793, 782 |
| `/research` | 390 | 79, 83 | 4207, 4197 | 793, 625 |
| `/grid` | 1280 | 93, 93 | 744, 728 | 650, 481 |
| `/grid` | 390 | 89, 89 | 3737, 3732 | 646, 474 |

## What the scores do not say

- **Layout shift in the internal view is not a visitor's.** Every page shifts once at 1280 px (0.037 on a text page, 0.305 on `/storage`, 0.153 on `/grid` and `/network`): the page is built for a visitor, with each link to a page in review drawn as greyed text with an "in review" label, and in the internal view the browser then redraws those as links (`components/SiteLink.tsx`, `components/GateRestore.tsx`), so the header's menu goes from two lines to one and everything under it moves up 24 px (a probe of the layout-shift entries names the header's grey links and `main`). At 390 px the same redraw moves the battery and seller pages' tabs (0.09 to 0.12). A visitor's page has no such redraw. Real shifts can only be measured once a page is live, or by a visitor-shaped build, which is not built.
- **Mobile largest paint is about 3.1 to 3.5 s on every page**, text pages included: it is the simulated slow 4G fetching the two stylesheets (13 and 3 KB compressed, render-blocking) behind four to five preloaded font files (134 KB with Inter). The causes are listed below; none is a fix without a ruling.

## For session 401 (the five tool pages' own files)

- `site/app/research/page.tsx` line 136: the chart of the day written `width={1600} height={900}` for a 1200 by 880 picture; `today.width` and `today.height` now exist in the content bundle (`lib/markdown.ts` `DigestChart`), as `app/page.tsx` uses them.
- `/cost-of-power`: 410 ms of blocking time at 390 px before, 2.5 s speed index at 1280; the layout shift there at 1280 was laid partly to the brand's fonts arriving (Lighthouse names five font files as the cause of a 0.083 shift of `#pays p.mb-6`).
- `/grid?view=network` (`/network`): 3.1 s of script at 390 px from one chunk of 841 KB (3d-force-graph with three.js, `app/network/Network.tsx`), blocking time 595 ms before and 346 ms after (noise, no change there), mobile performance 72 before and 79 after: the lowest mobile score of the 28 pages. Loading the 3D view only when it is asked for is the page's own change.
- Forced reflow on the battery and seller pages (Lighthouse's `forced-reflow-insight` on every run of them).
- Unused values (not imports) in its files: `METHOD` in `app/cost-of-power/GridsView.tsx`; `one`, `usd` and `flat` in `app/cost-of-power/LoadAnswers.tsx`.

## For session 412 (the shared components' accessibility)

- `link-in-text-block` on all 56 runs: the footer's links `/data`, `/terms` and `/privacy` (`site/app/layout.tsx`) are told from the text around them by colour alone; also the link to `/grid?grid=us48&view=gravity` on `/grid` at both widths. The internal view's "lock" link counts too, but no visitor sees it.
- `target-size` on every run at 390 px: the header's grey links (`span.nav-aside`, `/digest` first; `components/Nav.tsx`); on `/about`, the links of its list (`dl.mb-6 dd a`: `/battery/customer`, `/contracts`, `/shoulder`).
- These are why accessibility is 92 to 97 and not 100 on every page.

## For Samuel's ruling

- The brand's header face: `components/Brand.tsx` sets the header's and footer's face with a `<style>` inside the page's body, after the header, so the header is first laid out in Inter and Inter's 49 KB file is fetched on every branded page though nothing ends drawn in it. Options: (a) the rule in `app/tokens.css` and the brand's font variables on `<html>`, keeping the four pages outside the brand as they are; (b) the brand's face on the header of every page, those four included (a visible change on them); (c) leave it.
- Two shared reads of every page that Next.js decides: the framework's own polyfills (14 KB, `legacy-javascript-insight`: `Array.prototype.at`, `flat`, `flatMap`) and its unused code on first load (26 KB, `unused-javascript`, the same chunk). A browser target in `package.json` (`browserslist`) would drop the first; it decides which old browsers the site still works in.
- Render-blocking stylesheets (Lighthouse's estimate: about 50 ms of the first paint at 1280, 200 to 300 ms at 390): Next.js can inline the page's CSS (`experimental.inlineCss`), an experimental switch that changes how every page is served and cached.
- The chart of the day is a 156 KB PNG drawn 653 px wide at most (Lighthouse: about 110 KB could be saved). Options: (a) the chart maker (`warehouse/analysis/`, the data machine) writes a smaller or WebP picture beside the PNG; (b) `next/image`, which resizes on Vercel and counts against its image quota (money); (c) leave it.
- `/network` is one of the 25 snapshot addresses and answers a redirect to `/grid?view=network` (170 ms at 1280, 610 ms simulated at 390, every visit): the snapshot list and any link may name `/grid?view=network` instead.
- The two `grep.exe` processes left running on the code machine since 14 October 2026, 02:08 and 02:13 local time (process ids 2028 and 18568, each about 2,200 s of processor time so far, waiting on "exit=|stopped|mutex given|NOT MINE"): left alone, as they are not this session's.

## Files

- Runner: `site/scripts/lighthouse-pages.mjs`; test: `tests/test_session411.py`.
- Records (not in git, `runs/` is ignored): `runs/chain_oct21/s411/before.json`, `final3.json` (the "after" above), `after.json` (with Inter not preloaded), `final.json` and `final2.json` (the spoiled sets), `ab_before1.json` and `ab_after1.json` (the side-by-side), each run's full report under `lhr_<set>/`.
- Shots: `docs/brand/review-411/`.

To run again on a local build: `npm install lighthouse@13.4.1 --ignore-scripts` in a folder outside the repository, then `LIGHTHOUSE_DIR=<that folder> node scripts/lighthouse-pages.mjs http://localhost:<port> <out.json>` from `site/` (Git Bash: `MSYS_NO_PATHCONV=1`, or an address like `/about` becomes a Windows path).
