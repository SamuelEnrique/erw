# Session 1412 report: the Flex Alert scorecard's small charts on hover

24 October 2026, from about 08:00 to 08:40 UTC, on samueloldlaptop (the code machine, the old laptop), the third session of `queue/done/107-day-27-october-code-grid-tool-5.md`. Branch `wip/1412-grid`, cut from `wip/1411-grid` (sessions 1152 to 1411 stacked, not on main), worktree `C:\Users\lossa\Documents\erw-1412`. Code, tests and documents only (`runs/c077/brief.md`: no build, no server, no browser). Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher; light reads of Supabase's REST API with the anon key (one read of `flex_alert_effects`' hourly rows, 2,280 rows in three pages, and one same-figures walk of 6 requests).

## Read these first

- **`/grid/caiso/alerts`, "Each alert day through the evening": each of the 38 small charts now answers a hover, and on a phone a tap.** The card gives one hour: the hour on the Pacific clock as the axis writes it ("17:00 Pacific", ", an alert hour" where it is one), demand served, the model's estimate, its 90 percent band, all in MW, and the estimate less demand (the page's sign: positive is a cut). While it is open the chart draws a dashed guide at the hour and a dot on each line.
- **The drawing is session 60's, unchanged.** Its arithmetic moved word for word from `page.tsx` to `site/lib/alertDayChart.ts`; the client chart `site/app/grid/caiso/alerts/DayChart.tsx` draws it with the same elements and attributes (viewBox 260 by 120, the same scale, points, colors, labels). `site/scripts/test-alert-day-chart.mjs` runs session 60's code (copied as it stood at `f448db93`) and the lib on the committed rows (seven alert days) and on rows missing a value: every drawn string the same. On the live answers of today the two gave the same strings for **all 38 days (456 hours)** (a one-off, `runs/s1412` and the scratchpad).
- **The card is the shared charts' card**: `Card` of `site/components/svgchart.tsx`, now exported (nothing else in that file changed). No shared chart draws this shape (a band, a dashed estimate and boxed hours on a fixed viewBox) at this size without changing its scale and look, so the chart keeps its own drawing and takes the shared card.
- **The card's figures are the chart's own points** (the rows of `flex_alert_effects`, freq PT1H, that the page already read), not written figures: **no new key**, as no shared chart's card has one.
- **The 433 keys are unchanged**: `same-figures.mjs` on `/grid/caiso/alerts`, the code before (`f448db93`) and after, the same live answers: 433 figures before, 433 after, every one the same.
- **Each chart's aria-label now begins with its day** ("2024-07-24: actual and predicted demand through the evening"; the 38 had one name). One sentence added under the section's intro: "A hover or a tap on a chart gives the hour's demand, the model's estimate and the difference, in MW."
- **A render case for the scorecard**: `alerts_days on /grid/caiso/alerts` in `site/scripts/test-grid-render.mjs` (drawn by the stand-in's new `drawAlerts()` on session 1411's committed rows), and a check that each small chart is named by its day with its keyed cut above it. 74 cases, every one holds.

## What to review

After the landing (none yet; below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid/caiso/alerts`, scroll to **Each alert day through the evening**. The 38 charts look as before.
3. Move the mouse over a chart: a card at the top of the chart with the hour (Pacific), demand served, the model's estimate, the 90 percent band, the estimate less demand; a dashed guide and two dots at the hour. Move along: the card follows the hours; leave the chart: it goes. In a boxed (alert) hour the card's first line ends ", an alert hour".
4. At 390 pixels (a phone, or the browser's device view): tap a chart: the card opens and stays when the finger lifts; tap the same hour: it closes; tap another chart or the page: it closes. The card stays inside the chart's panel.
5. Read `docs/methods/flex_alert_scorecard.md`, section 12, and its Decisions.
6. From `site/`: `node scripts/test-alert-day-chart.mjs`; `node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-render.mjs` (the last two cases).
7. Screenshots: not taken, no build.

## Checks

- Precheck for session 1412: run by the orchestrator, exit 0.
- `node scripts/test-alert-day-chart.mjs` (new): exit 0, 14 cases.
- The one-off on live answers (session 60's code against the lib, every alert day's hourly rows): exit 0, 38 days of 38 the same, 456 hours.
- `test-grid-render.mjs`: exit 0, 74 cases (72 before, the scorecard's case and its check added).
- `same-figures.mjs --only /grid/caiso/alerts --sizes` (a temporary worktree of `f448db93`, removed): exit 0, 433 figures the same; sizes: the estimate fell from 434,843 to 297,402 bytes because `sizeOf` does not count a client component's own markup (the svg is now drawn by the client chart; Next still renders it into the HTML on the server), 0 pages over.
- Node tests that read a changed file, one at a time: `test-grid-failed-reads` (107 cases), `test-grid-addresses`, `test-grid-stress`, `test-grid-units`, `test-grid-files` (104), `test-caiso-alerts` (12): each exit 0.
- `python -m unittest`, one module at a time, each exit 0: `test_session1412` (new, 7 tests), `241a` (the page's files extended with `DayChart.tsx`), `1404` (exit 1 on a first try: its pin reads every case line at two spaces as a `/grid` case; the scorecard's case now sits in its own list at four spaces, so the pin is unchanged), `1155`, `1159`, `1411`, `473`, `237`, `1152`, `1154`, `1157`, `1165`, `1166`, `1167`, `1170`, `1171`, `1174`, `1180`, `1181`, `1185`, `1406`, `144_page`, `168_network`, `236`, `241b`, `241c`, `266`, `299`, `317`, `318`, `328`, `331`, `351`, `370`, `412`, `416`, `533`, `584`, `588`, `78`.
- `npx eslint` on the seven changed code files: exit 0.
- Type check through the junction (`mklink /J` to the main checkout's `node_modules`): `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0; the junction removed with `rmdir`, the main copy's `node_modules` intact.
- Not run (the brief): the build, check-values, check-routes, screenshots.

## The landing

- None in this session: chain 107 works code-only, stacked on `wip/1411-grid`. This branch lands with the chain's combined landing. Pushed: `wip/1412-grid`.

## To finish

- Land with the chain. At that build: check-values on `/grid/caiso/alerts` (Git Bash, `MSYS_NO_PATHCONV=1`): every key as before; the snapshots before and after, every difference listed (expected from this session: the scorecard's small charts' `aria-label`s now begin with the day, and the one added sentence; the svg markup otherwise the same).
- With a running site: the hover and the tap of "What to review" 3 and 4, at 1280 and 390 pixels.

## Decisions made without you

- **The chart keeps its own drawing and takes the shared card** (`Card`, exported from `svgchart.tsx`), not `CategoryChart`: that chart measures its width and sets its own ticks, axis text and padding, so the small charts' scale, size and look would all have moved.
- **No key for the card's figures**: they are the drawn points, as in every shared chart's card.
- **No Chart or Table toggle on each of the 38 charts, and no keyboard stop on each hour** (as for the shared charts, session 1158): 38 toggles would crowd the cards. Each day's headline cut is a keyed figure above its chart and in the ranked table.
- **A tap on the same hour closes the card, and a tap anywhere off the chart closes it** (session 1158's rules: a finger lifting leaves the card; there is no empty part of this drawing, every point is nearest some hour).
- **The figures in the card are rounded to a whole MW** (the table's figures keep their own format).
- **The aria-label names the day** (it was one name for 38 charts); the sentence under the intro says the charts answer a hover.
- **The scorecard's render case sits in its own list** (`OWN_PAGE_CASES`), drawn by `drawAlerts()` with the scorecard's two tables held only during that draw, so every `/grid` case and `tests/test_session1404.py` read as before.
- **The stand-in learned `not.`** (the scorecard's model read, `variable=not.like.coef_*`), as session 1411's failed-read stand-in did.

## For Samuel's ruling

- "Year by year": the note still says the bars are "green" though they are ink (session 1159's item); not changed here.
- A table of the 38 days' hours (one toggle for the section, or one per chart), for a reader without a pointer.

## Files

- New: `site/lib/alertDayChart.ts`, `site/app/grid/caiso/alerts/DayChart.tsx`, `site/scripts/test-alert-day-chart.mjs`, `tests/test_session1412.py`, this report.
- Changed: `site/app/grid/caiso/alerts/page.tsx` (`DayChart` hands the day's points to the client chart; `data-alerts-days`; one sentence), `site/components/svgchart.tsx` (`Card` exported), `site/scripts/grid-render-standin.mjs` (`drawAlerts`, `not.`, the block name), `site/scripts/test-grid-render.mjs` (the scorecard's case and check), `tests/test_session241a.py` (the page's files), `docs/methods/flex_alert_scorecard.md` (section 12).
- On this machine only, in `runs/s1412/` and the scratchpad: every test's output, the same-figures lists, the live geometry one-off.
