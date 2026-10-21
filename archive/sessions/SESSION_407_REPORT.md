# Session 407 report: ten LinkedIn posts, drafted, not posted

21 October 2026, about 04:29 to 05:25 UTC, unattended, on samueloldlaptop (the code machine), in the worktree `C:\Users\lossa\Documents\erw-407` on `wip/407-s` (from `wip/381-382-land` at `61c4c309`). Chain `queue/done/015-day-20-october-code-pm.md`, session 407. Model spend USD 0; no pull from any publisher; no warehouse data written; nothing posted anywhere (the roadmap's ruling of 12 October: nothing posts to LinkedIn; the tool prepares the image and the caption for Samuel).

## Read these first

- **The posts are `docs/reviews/linkedin/posts-001-010.md`**: ten posts, 88 to 110 words each, each one checked figure first, the reading second, the page's address and the source last, two or three hashtags, no em dash. Each names its check-values key (and every other figure in it has its own key, under "Also"). The figures: Uri's highest 15-minute price at ERCOT's hub average (9,051.55 USD/MWh), PJM in Winter Storm Elliott (41.76 percent above its usual December peak), PJM's highest hour of the June 2025 heat (160,560 MW), ERCOT in the January 2025 cold (47.97 percent above its usual winter peak, the most of six grids), California's curtailed solar in May 2026 (1,361,345.63 MWh), ERCOT's large loads approved to energize (8,927 MW against 3,675 MW served at one moment), ERCOT's 2025 intervals at or below zero (959 of 35,040), California's carbon intensity of generation (127.31 kg/MWh in July 2026, 213.51 in August 2018), SPP's 2023 queue cohort (340 of 435 withdrawn, 8 operating) and what each grid's load paid in August 2026 (NYC 58.53, ERCOT 36.70 USD/MWh).
- **None repeats session 406's newsletter** (the battery's income by stream, the `bs|` keys and the storage build-out): the test holds it.
- **`posts-notes.md`** proposes posts 6, 9 and 4 first, with why and what a sceptic says, and the rulings.
- **Every figure was read tonight** from Supabase with `docs/reviews/linkedin/read-407.mjs` (the query check-values runs for a series key) and is equal, to the last digit, to the raw value the page carried in the passing full check-values run of 20 October, 23:15 UTC (`runs/chain_oct20d/s372land/values_floor.out`); the text in each post is the page's own rounding of that value as that run recorded it. 26 keys, all equal (`read-3.txt`; two earlier runs read the 21 keys held then).
- **The images**: **not made.** The local build failed three times (04:38, 04:57 and 05:14 UTC) on the home page's required read (`Supabase series: HTTP 500 ... 57014 statement timeout`), as the chain's rules foresaw, so no page could be drawn. `docs/reviews/linkedin/shots-407.mjs` makes all ten from the next build; the posts file says the images wait, and the test then requires all ten at 1200 by 627 once that sentence is removed ("To finish").

## What to review

- The posts: `https://github.com/SamuelEnrique/erw/blob/wip/407-s/docs/reviews/linkedin/posts-001-010.md`
- The notes: `https://github.com/SamuelEnrique/erw/blob/wip/407-s/docs/reviews/linkedin/posts-notes.md`
- The pages, in the internal view: `/events/uri-2021`, `/events/elliott-2022`, `/events/east-heat-2025`, `/events/cold-2025`, `/curtailment`, `/datacenters`, `/prices?tab=ercot`, `/emissions` (the Grid page's Clean view), `/map?tab=queues&iso=spp`, `/cost-of-power?view=grids`.

## Checks

Every gate redirected to a file under `runs/chain_oct21/s407/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `read-407.mjs`, the first 21 keys from Supabase (04:34) | 0 | every key read, every value equal to the page's (`read-1.txt`) |
| `read-407.mjs` again, after two keys changed (04:40) | 0 | 21 of 21 (`read-2.txt`) |
| `read-407.mjs`, the final 26 keys, five added for post 4's comparison (05:20) | 0 | 26 of 26 equal (`read-3.txt`) |
| `duty.py beat` before `npm ci` and build 1 | 0 | `beat-1.txt` |
| `npm ci` in the worktree's `site/` | 0 | `npm-ci.txt` |
| `npm run build`, try 1 (04:38) | 1 | `/` failed to prerender: `Supabase series: HTTP 500 ... statement timeout`, 12 timeouts in the log (`build-1.txt`); the mutex released |
| `duty.py beat` before try 2 | 0 | `beat-2.txt` |
| `npm run build`, try 2 (04:57) | 1 | the same, 10 timeouts (`build-2.txt`, `build2.status`); the mutex released |
| `duty.py beat` before try 3 | 0 | `beat-3.txt` |
| `npm run build`, try 3 (05:14) | 1 | the same, 24 timeouts (`build-3.txt`, `build3.status`); the mutex released |
| `node --check` on `shots-407.mjs` and `read-407.mjs` | 0, 0 | both parse; `shots-407.mjs` has not run (no build) |
| `tests.test_session407`, first runs | 1, 1 | the test's number pattern took a trailing comma; its rounding was Python's, not the page's (fixed: half up, as `toLocaleString`); then post 4 listed two keys it did not use (the post now names them) |
| `tests.test_session407` | 0 | 17 tests OK (`t407-3.txt`) |
| The whole suite (`ERW_LOCK_EXEMPT=1 ... unittest discover -s tests`) | 1 | 4,799 tests, 252 skipped, one failure: `test_session156` (the ask fixtures), which the chain's rules say may fail tonight; nothing else (`suite.txt`) |
| Server on port 3407 | none | never started (no build), so none to stop |

## Decisions made without you

1. **Series keys only.** Every figure is a `series|` key (a row of the series table), so it can be read back from Supabase without the page's library code and without a build; the battery's `bs|` keys, the datacenter tool's `dc|` keys and the like were left out. The pages chosen draw their figure beside a shared chart component.
2. **Two pages were dropped for their charts**: the Flex Alert scorecard (`/grid/caiso/alerts`, its pooled estimate is a strong post) and the shoulder hours (`/shoulder`) draw their charts in their own SVG, not the shared components, so neither can give an image "from the shared components".
3. **The image is a 1200 by 627 viewport, not a crop scaled up.** The script sets the browser to 1200 by 627 at scale 1 and scrolls to the chart (its section title with it when both fit), so the image is the page's pixels at LinkedIn's size; fixed and sticky bars are laid in the flow so they do not cover the chart.
4. **The chart is found from the figure**, not named by hand: the nearest ancestor of the figure's `data-check` element that holds a shared chart, its first chart. For posts 7, 9 and 10 the chart the script will take is not certain from the code alone; it prints the chart's kind, id and title, and the "To finish" step is to look at each image.
5. **Hashtags on the line before the address**, so the address and the source are the post's last lines as the chain asked.
6. **The address is `https://erw-flame.vercel.app`**, the site's Vercel address used in the session reports.
7. **No figure without its key in a post.** Every number a post shows is a key in `posts.json` (or a date, the baseline's 364 and 728 days, or plain arithmetic: "one interval in 37", "about 40 percent", "more than eight times", "more than twice"); the test fails otherwise.

## For Samuel's ruling

- The first three posts: 6, 9 and 4, in that order (`posts-notes.md`), or another three.
- Post while the pages are in review (a reader who follows a link sees the in-review page), or wait until the pages open, or post the image and caption without a link.
- The address `https://erw-flame.vercel.app` in every post, or the site's own domain once it has one.
- The source line's form: "the Energy Research Warehouse table event_window_daily", or the name without the table.
- Hashtags: two or three a post on the line before the address, none, or under the source line.

## To finish

The ten images, on the next night the database answers (the mutex as the chain's rules say; port 3407):

```bash
cd C:/Users/lossa/Documents/erw-407/site
C:/Users/lossa/Documents/erw/.venv/Scripts/python.exe C:/Users/lossa/Documents/erw/scripts/duty.py beat
npm run build > C:/Users/lossa/Documents/erw/runs/chain_oct21/s407/build-4.txt 2>&1; echo "exit=$?"
npx next start -p 3407 > C:/Users/lossa/Documents/erw/runs/chain_oct21/s407/server.txt 2>&1   # in its own background call
node ../docs/reviews/linkedin/read-407.mjs > C:/Users/lossa/Documents/erw/runs/chain_oct21/s407/read-3.txt 2>&1; echo "exit=$?"
node ../docs/reviews/linkedin/shots-407.mjs http://localhost:3407 > C:/Users/lossa/Documents/erw/runs/chain_oct21/s407/shots.txt 2>&1; echo "exit=$?"
```

Then: look at each PNG and check it against its post (posts 7, 9 and 10 name their chart only in `shots.txt`: if the chart taken is not the one beside the figure, give that post a chart of its own in `shots-407.mjs` or pick another figure); `shots-407.mjs` exits 1 if a page's text for a figure is not the text in `posts.json`, which is the read from the page itself; write the chart each image shows into its post's "Image:" line; remove the sentence ending "point at files that do not exist yet" from `posts-001-010.md` (the test then requires all ten PNGs at 1200 by 627); run `tests.test_session407`; stop the process listening on port 3407.


## Files

- `docs/reviews/linkedin/posts-001-010.md`, `posts-notes.md`, `posts.json`, `read-407.mjs`, `shots-407.mjs` (new); the ten PNGs wait.
- `tests/test_session407.py` (new).
- This report.
