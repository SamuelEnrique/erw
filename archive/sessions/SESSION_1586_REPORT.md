# Session 1586 report: AccessLint on the site's other main pages, and three faults fixed

Energy Research Warehouse (ERW), session 1586, chain 187, samueloldlaptop, 6 November 2026, 15:03 to 15:11 UTC. Model: Claude Opus 5.5 (the file names Fable 5.1). Model spend USD 0. No warehouse data written; nothing sent or posted. Branch `wip/1586-a11y`, cut from `wip/1542-periodicals` (the newest unlanded branch).

## What it did, with commits (`7bd697577`)

- **Why this read.** The faults left for this chain were the board's (its chain's stack is in flight) and the desktop's, so none was this chain's to fix. Sessions 1504 and 1524 had run AccessLint on 24 of the 225 pages in review. This session read the site's other main sections, on a build of main (`npm ci` and `npm run build` in a clean worktree, under `scripts/buildlock.py`, with `site/.env.local` copied in as the gate copies it), in the internal view.
- **32 pages read in the internal view, four with faults** (and `/privacy`, clean, read on a first build that lacked `site/.env.local`). These 28 are clean: `/prices`, one hub's price page, `/grid`, `/mix`, `/mix/v2`, `/curtailment`, `/curtailment/v2`, `/map`, `/companies`, `/policy`, `/digest`, `/roundup`, `/analysis`, `/research`, `/queues`, `/demand`, `/demand/weather`, `/supply`, `/emissions`, `/events`, `/learn`, `/resources`, `/reports`, `/thesis`, `/contracts`, `/shoulder`, `/impact` and `/deals`. The faults:
  - **`/data`**: 67 scrolling `<pre>` blocks a keyboard cannot reach (each table row's "Python, Stata, R" fold, `#<table> > td:nth-of-type(11) > details > pre`, serious). The two install blocks are the same fault where they overflow.
  - **`/consumption`**: `#states > div:nth-of-type(2)`, the states table's frame (serious).
  - **`/prices/compare`**: five sort links in the table's head at a contrast ratio of 1:1 (serious). The browser's computed colours confirm it: the link is `rgb(255, 255, 255)` on a transparent head over a white page, so the five column headings could not be seen. The inline `color: var(--color-surface)` dates from before the table head lost its dark fill.
  - **`/data/licenses`**: `article > table:nth-of-type(3)`, a scrolling Markdown table (serious). Not fixed: the table comes from `lib/markdown.ts`, which also renders the Digest and the methods pages, and a fix there reaches every one of them (session 1589).
- **The fixes** (sessions 1586 to 1588):
  - `/data`: `scrollRegion` on the three `<pre>` blocks, the row's named for its table ("The calls for <table> in Python, Stata and R").
  - `/consumption`: `scrollRegion` on all three table frames. AccessLint named the one that overflows at 1280; the other two overflow on a phone.
  - `/prices/compare`: the inline colour removed, so the links take the page's link colour.
  - `tests/test_session1586.py` (4 tests). `tests/test_session241c.py` now reads a frame that carries `scrollRegion` as a frame. The 614 tests that read the three files pass.
- **How serious the keyboard faults are, read after the fixes** (session 1590). `site/components/ScrollRegions.tsx`, mounted once in the layout (sessions 412 and 583), marks every scrolling box under `<main>` as a named, focusable region. It runs 150 ms after load, again whenever a `<details>` opens, and it covers `.prose-erw table`.
  - AccessLint reads the page before that pass, and it counts boxes inside closed folds. In a browser that runs scripts, the keyboard could most likely reach `/data`'s and `/consumption`'s boxes after a moment.
  - The server-side `scrollRegion` makes them reachable from the first paint and without scripts, as session 412 did for the tool tables. They are worth having, but less grave than "serious" says.
  - The `/prices/compare` headings are a real fault either way.
- The browser and the server were stopped after the read.

## Decisions made without you

- The sort links' white was treated as a fault, not a design choice: white text on a white page hides the headings. The fix gives the links the page's own link colour and changes no layout.
- `/data/licenses` is left for a session that can check every Markdown page.

## For Samuel's ruling

- None.
