# Session 1449 report: the pages

Energy Research Warehouse (ERW), session 1449 (chain 149's "1446"), `queue/done/149-day-5-november-code-periodicals-excellent.md`, samueloldlaptop, 6 November 2026, about 02:52 to 03:10 UTC. Model Fable 5.1, high effort. Model spend USD 0. No warehouse data written; nothing sent or posted; web requests to the ERW's own database (the build's reads) only; a local build and server, stopped at the end. Branch `wip/1449-periodicals` over `wip/1448-periodicals`.

## What it did, with commits

- **`c07bd38b9`**, `site/lib/digest.ts`, `site/lib/markdown.ts`, `site/app/roundup/[week]/page.tsx`, `site/app/globals.css`:
  - **The source trail as a hover** (fault 18, the page's side): `sourceTrail` turns each `[n]` mark of a rendered issue into an `<abbr class="digest-mark" title="<table>">` (a hover names the table) and folds the "Tables:" paragraph closed under a "Sources" summary (`<details class="digest-tables">`), so the trail is one hover or one click away and no grey explanatory text stands in the prose (the owner's rule). The markdown keeps every line: the page's parser and the tracer read it; `check-values` read the three issue pages with every figure's key (17 of 17 match).
  - **The Roundup's five numbers on the page** (fault 26): `dedupeOpening` makes the row that is the opening number word for word read "the opening number, above"; `renderRoundup` is the Roundup page's one renderer (the fold, the trail, the opening once).
  - **The chart's hover answers with its figures** (fault 41, in part): the chart image carries a `title` with its caption's values; a point-by-point hover needs the series on the page, which the record does not hold (for chain 150).
  - Tests: two node cases in `site/scripts/test-digest-numbers.mjs` (13 pass); `tests/test_session177.py` and two `test_periodicals.py` cases re-pinned to the renderers.
- **The build and the pages read** (the gate's worktree at `c07bd38b9`, `npm ci` and `npm run build`, its own processes; the server on port 3449): screenshots under `runs/s1449/shots/` at 390 and 1280 of `/digest` (the index: today's issue, 6 November, the 00:48 UTC run's), `/digest/2026-11-06`, `/roundup` and `/roundup/2026-W44`. The pages are on the brand: Source Serif 4 headings, IBM Plex Sans text, the white page, light only; the stored issues are the old shape (the v2 pages come with Friday's run); the Digest's story sections are drawn as the news index's hold line; the Roundup's stories are shown.
- **AccessLint** (`audit_html` over each issue page's article in the internal view, since the audit's own browser has no internal cookie): no violation on `/digest/2026-11-06` or `/roundup/2026-W44`.
- **`check-links.mjs`** against the local build: its result is in `runs/s1449/check_links.out` (it ran as this report was written; its tail is appended below when read).
- The faults file: rows 18 (the page), 26 (the page) fixed; 41 fixed in part.

## Checks

| Check | Exit | Result |
|---|---|---|
| `node scripts/test-digest-numbers.mjs` | 0 | 13 passed |
| `tests.test_session177`, `test_periodicals`, `2207`, `402` | 0 | 141 passed |
| `npm run build` (c07bd38b9) | 0 | no statement timeout |
| `check-values.mjs` on `/digest/2026-10-23`, `/digest/2026-11-06`, `/roundup/2026-W44` | 0 | 17 of 17 values match |
| AccessLint `audit_html`, two pages | | no violations |

## Decisions made without you

- The Tables line folds closed rather than disappearing: a reader on a phone, with no hover, still reaches the trail in one tap; the owner's rule is read as "not visible as grey prose".
- The marks inside the folded Tables line are not wrapped; those in the text and the tables are.
- The audit ran over the article HTML fetched with the internal cookie, not over the live page: the audit tool's browser cannot hold the cookie, and the in-review page a visitor sees holds no article.
- The index pages' names ("ERW's Energy Digest", "ERW's Roundup") stand: `docs/voice.md`'s names and the v2 masthead's differ (session 2706's contradiction, unresolved), and the chain forbids branding work beyond the brand document.

## For Samuel's ruling

- The names on the index pages and in the page titles: "ERW's Energy Digest" and "ERW's Roundup" (`docs/voice.md`) or the v2 mastheads' "ERW Daily Digest" and "ERW Weekly Roundup" (`docs/brand.md` section 10).
