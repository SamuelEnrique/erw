# Session 581: every internal link and anchor resolves

Chain 034 (`queue/done/034-night-22-october-code.md`), samueloldlaptop, the code machine, unattended, 22 October 2026, about 00:30 to 02:00 UTC. Branch `wip/581-s`, cut from `origin/wip/506-combined` (origin/main merged: already up to date). Not landed: session 589 lands the chain.

## Summary

`site/scripts/check-links.mjs` reads the 151 pages of check-values' list (`--list`: its pages and its two internal drafts) and the 84 method pages under `/data/methods/` (235 pages) in the internal view, in a real browser, takes every link that stays on the site and every id, asks for each address linked with the internal cookie (redirects followed by hand), and looks each fragment up among the ids of the page it names. Its first run on a build of this branch found 85 findings: 58 broken, 3 missing anchors, 24 redirects. After the fixes and a second build: **0 findings**, 1 link waiting for a ruling, 4 aliases (by design), 93 addresses under `/api/` not asked.

## What was found, and done

1. **`/curtailment?period=2023` answered 500** (a real fault, linked from the page's own period list). `data/curtailment/worth.json` writes CAISO's 2023 as `{ missing: ... }` (five of its months); `worthPeriod` took the year as held and the "What it is worth" section read `usd_per_mwh_curtailed` of a record without it. Fixed in `site/app/curtailment/Sections.tsx`: a period whose record holds no value is not held, as a year with no record is not (the section shows the newest held year, as for 2019 to 2022). The default (`/curtailment`, newest year) is unchanged.
2. **Seventeen company websites linked as pages of this site** (`/amperon.co`, 404) on `/deals?tab=companies`: energy_companies writes most as a bare domain. `websiteHref` in `site/lib/companies.ts` opens a bare domain over https; a value that is no address ("not disclosed") is shown as text, no link. The words shown are unchanged.
3. **Three anchors to method pages held no id** (`/impact` to `economic_impact#what-jedi-cannot-see` and `#2-the-tax-side-...`, `/map` to `energy_projects#coordinates`): no rendered markdown heading carried an id. `site/lib/markdown.ts` now gives each heading the id GitHub gives it (`headingSlugs`, a counter a document for repeated headings), so the documents' own `x.md#y` links land too. `scripts/test-markdown-safe.mjs` updated (its `<h1>Title</h1>` expectation) and a case added.
4. **21 links answered through a redirect** to an address the site moved (session 237's Grid tool, session 239's tabs): each now names where it lands, words unchanged. `/grid/<slug>` to `/grid?grid=<slug>` (the cost-of-power grids view, the event pages, the Flex Alert scorecard, `/learn/bill`, the battery game, the know-your-grid problem set), `/grid/caiso#reliability` to `/grid?grid=caiso#reliability`, `/mix?view=clean|stress&grid=` to the Grid views, `/emissions`, `/network`, `/storage/buildout` (`/shoulder`, `/queues`), and `docs/methods/ask_ercot.md`'s `/resources`. Two older tests that pinned the old strings follow (`tests/test_session56.py`, `tests/test_session138.py`).
5. **The 40 download links answered 429** on the first run: a check artifact (sixty downloads an hour a visitor, each a table read). The checker no longer asks for `/api/` routes; `check-table-downloads.mjs` is their check.

## Checks

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 581"` | 0 | on duty |
| `scripts/db_probe.py` (twice, before each build) | 0, 0 | open, 1.08 s and 0.66 s |
| `npm run build` (twice, under the build lock) | 0, 0 | no "statement timeout" in either log |
| `node scripts/test-check-links.mjs` (with `CHECK_LINKS_BROWSER_TEST=1`) | 0 | 27 of 27 |
| `node --import ./scripts/alias-register.mjs scripts/test-markdown-safe.mjs` | 0 | 7 tests, 109 documents rendered |
| `node scripts/check-links.mjs http://localhost:3581`, first build | 1 | 235 pages, 16,789 links, 1,750 addresses; 85 findings |
| the same, second build | 0 | 235 pages, 16,785 links, 1,629 addresses; 0 findings, 1 waits, 4 aliases, 93 under /api/ not asked |
| `unittest tests.test_session581` | 0 | 5 tests |
| `unittest` of the 149 test modules naming a touched file | 1, then 0 | 2,181 tests; one failure (`test_session56` pinned `href: "/grid/caiso"`), updated; rerun OK |
| `check-values.mjs` on the touched pages (`CHECK_VALUES_PAGES=/curtailment,/deals?tab=companies,/cost-of-power,/events,/grid/caiso/alerts,/learn,/play/battery,/shoulder`), run twice | 1, 1 | 2,857 of 2,857 values match Supabase; the failures are floors only, all of session 408's license-held list (`/events` and event pages, `/learn/bill`, which shows "license needed" 32 times); the second run passed every event page but `/learn/bill`. No default figure moved |
| screenshots at 1280 and 390, before and after, 17 addresses | 0, 0 | byte-identical but `/curtailment?period=2023` (the error page before, the page after) and `/deals?tab=companies` at 1280 (the before shot caught the header before the internal view redrew it; the table is the same) |

## Decisions made without you

- docs/brand.md section 7 is "Assumptions" and says nothing of a link's words; I kept every link's words as they were and changed only where links point (section 2's underlining is the shared components' and untouched).
- A link that answers through a redirect counts as a finding unless it is named in `ALIASES`: `/ask` (the owner's merge of 18 October made it the Ask panel's own address) and `/internal/lock` (an action). Both stay.
- The checker does not ask for `/api/` routes (downloads are limited to sixty an hour and each reads a table; the first run's 40 downloads were rate-limited, and the ones before them each read a whole table).
- Two builds, each under the build lock: the second was needed to prove the fixes.
- Heading ids go on every rendered markdown document (digests, Roundup, methods, standard), not only method pages: the documents' own `#` links need them. Invisible on the page.
- `site/lib/audience.ts` (the draft `/home/v2`) and `site/lib/chat/pagelinks.ts` (Ask's answer links) still name `/network`, `/mix?view=day`, `/emissions` and `/resources`; neither is on the checker's list, so they were left.

## For Samuel's ruling

- `/data` lists "The price board, version 4" (`docs/methods/price_board_v4.md`), whose address redirects to the price board's note (session 132): keep the line or drop it (listed as "waits" in check-links' `WAITS`, not changed).

## To finish

Nothing for this session. Session 589 lands `wip/581-s` with the chain.

## Files changed

- `site/scripts/check-links.mjs`, `site/scripts/test-check-links.mjs`, `tests/test_session581.py` (new)
- `site/app/curtailment/Sections.tsx`, `site/lib/companies.ts`, `site/app/companies/CompaniesTable.tsx`, `site/lib/markdown.ts`, `site/scripts/test-markdown-safe.mjs`
- `site/app/cost-of-power/GridsView.tsx`, `site/app/cost-of-power/page.tsx`, `site/app/events/EventWindow.tsx`, `site/app/events/covid-2020/page.tsx`, `site/app/events/caiso-heat-2022/page.tsx`, `site/app/grid/caiso/alerts/page.tsx`, `site/app/learn/bill/page.tsx`, `site/app/play/battery/Game.tsx`, `site/app/play/battery/page.tsx`, `site/app/queues/page.tsx`, `site/app/shoulder/page.tsx`, `site/lib/problems.ts`, `docs/methods/ask_ercot.md`
- `tests/test_session56.py`, `tests/test_session138.py`
- This report. Run detail (not committed): `runs/s581_links1.out` and `.json`, `runs/s581_links2.out` and `.json`, `runs/s581_cv.out`, `runs/s581_shots/`.
