# Session 238 report: Automated Analysis becomes Research, at `/research`

13 October 2026, one session of the overnight chain. Branch `wip/238-research` (worktree `erw-142`), built on `a4c54722`. Not pushed, not landed: the landing is the orchestrator's.

## Read these first

- **Not clean, and not mine to fix in the time:** the route check exits 1 on one page this session did not touch. `/emissions` shows 2 "no data" blocks (0 on production). The build log of the same build holds 2 lines "canceling statement due to statement timeout" (the build before it held 1): the build cached a failed read while four sessions were using the database. Every `/research` and `/analysis` line of the route check is ok. I did not rebuild: the wait for the build mutex was 51 minutes for the first cycle and 17 for the second. The landing's own build must be read for "statement timeout" before its route check is believed.
- **What a visitor is answered at `/analysis`:** a permanent redirect (308) to `/research`, with the rest of the address and the query kept (`/analysis/2026-W40` to `/research/2026-W40`, `/analysis/card/gas_sets_price?form=lines` to `/research/card/gas_sets_price?form=lines`). `/research` is in review, so a visitor then reads the in-review page (200, noindex), as at `/analysis` before. In the internal view the redirect ends on the Research page.
- **`check-values` has nothing to check on `/research`:** 0 values. No number on the page is read from a Supabase table when the page is drawn; every one comes from a committed file (a card's JSON, a chart's record, a Roundup). That was so at `/analysis` too. The restricted run therefore exits non-zero by its own rule ("fewer than ten"), and on this machine node then died on a libuv assertion at exit (exit 127). The cards' numbers are held by `check-analysis.mjs` instead (279 of 279).
- **The menu's words change on every page:** the Analysis group now reads "Research" where it read "Automated Analysis". If the snapshot of the 25 pages keeps the menu's text, each page will list that one difference; it is expected.
- **All six daily charts held are proofs** (session 232 drew them to show the form; no Digest has carried one). The page says so on today's chart and in the archive.
- Time: about 100 minutes against the 90 asked, 68 of them waiting for the build mutex.

## What was built

1. **The address.** `site/app/analysis/` moved to `site/app/research/` (`git mv`, no copy left). `site/next.config.ts`: `/analysis` and `/analysis/:path*` redirect to `/research` and `/research/:path*`. `site/lib/release.ts`: `/research` is `review`; the line of `/analysis` stays, as for every retired address. The request route `/api/analysis`, the queue and `/analysis-files/` keep their names.
2. **The menu.** `site/lib/pages.ts`: the entry is `{ href: "/research", label: "Research" }` under Analysis, with a new line of description; the Roundup's related line points at `/research`. Nothing else in the menu moved.
3. **The links.** Every link of the site's source names `/research` (About, the Roundup's page, the card and week pages, the request flow's card link, the internal findings pages' words). A Roundup written before the move still says `[/analysis](/analysis)` in its markdown: `site/lib/markdown.ts` now opens such a link at `/research` and rewrites its words where the words were the address. The published Roundups were not rewritten. The two writers (`warehouse/news/roundup.py`, `warehouse/analysis/findings/roundup_pick.py`) write `/research` from the next Roundup on.
4. **The page, in the owner's order:** the request form (the flow and the list of requests, untouched in what they send and store); today's chart; this week's chart; the findings library; the chart archive. A row of five links under the title goes to each.
5. **Today's chart:** the newest record of `docs/digest/charts/` (13 October 2026): the picture, the title, the one fact as the warehouse wrote it, the date, the source (`eia:electricity/electric-power-operational-data`, table `eia_state_generation_monthly`), the rule, and that it is a proof. `site/scripts/build-content.mjs` now bundles each day's record.
6. **This week's chart:** the chart the newest Roundup carried, read from the Roundup's own section. For 2026-W41 that is the finding chosen for it, "The peak hour moved": its chart drawn live, its claim, its three callouts, its source, links to the card, the Roundup and the rule's own pick. A week whose Roundup carried the rule's pick draws that. The week's results by the rule are folded under it.
7. **The findings library:** 9 cards (11 committed; the 2 superseded ones are linked under their successors, as before), one a screen, with a card index beside them (above them under 1024 px) that marks the card in view; a click goes to it. Filters by grid (6 choices) and by topic (10), kept in the address (`/research?grid=caiso&topic=curtailment`). Each card says how it is filed and links its data (CSV), its Python file and its Stata do-file; a file not held would read "not held" (today all 33 are held). The method footnote, the table of estimates and a further chart stand under one fold on each card.
8. **How a card is filed** (no card has a grid or a topic field): grids are the seven grid names found in the card's own tables, input words and chart series and categories, less the grids the card lists as not held; topics are the kinds of table it read, one rule a table. `site/lib/researchrules.ts`; the page and `docs/methods/automated_analysis_findings.md` say it; `tests/test_session238.py` computes both again in Python.
9. **The archive:** 6 daily charts (each opens its picture) and 3 weekly charts (each opens its page), newest first, as a small grid.
10. **The brand:** `<Brand>` and `ToolPage`, `ToolHeader`, `ToolSection`, `Fold` on the page, the week page and the card page (not on the renderer's frame). The new markup carries class names only; `site/app/tokens.css` gained one block of generic rules at its end. The charts are drawn in the tokens (below).

## Shared files touched (small and additive)

- `site/app/tokens.css`: one block appended ("session 238"), every rule under `.brand-a`: `.page-index`, `.sub-note`, `.sub-title`, `.lead-chart`, `.filter-row`, `.with-index`, `.index-list`, `.screen-card`, `.fold-more`, `.chart-archive`. No rule above it changed. The battery page: 0 lines of difference in its numbers, height 5016 at 1280.
- `site/components/echarts.ts`: inside an element marked `data-chart-tokens` a chart's color literals are replaced by tokens when it draws. Outside such an element nothing changes; only the three research pages carry the mark.
- `site/components/analysis/FindingCard.tsx`: two optional props, `held` and `fold`; without them the card is as it was.
- `site/lib/pages.ts` (two lines), `site/lib/release.ts` (one line added), `site/next.config.ts` (two redirects), `site/lib/markdown.ts`, `site/scripts/build-content.mjs` (two additions to the bundle), `site/scripts/check-routes.mjs` (four addresses added, `/analysis` kept), `docs/tools.md` (the page's row).

## What to review

Open `https://erw-flame.vercel.app/internal/open` first (after the landing).

- `https://erw-flame.vercel.app/research`: the order; today's chart; this week's chart.
- `https://erw-flame.vercel.app/research#card-gas_sets_price`: one card on its screen, the index marking it.
- `https://erw-flame.vercel.app/research?grid=caiso&topic=curtailment#library`: a filtered view from its address (2 of 9).
- `https://erw-flame.vercel.app/research#archive`: the archive.
- `https://erw-flame.vercel.app/analysis/card/queue_divorce`: the old address arrives at `/research/card/queue_divorce`.
- `https://erw-flame.vercel.app/roundup/2026-W41`: its link under the chart of the week opens `/research/card/peak_hour_moved`.
- Screenshots at 1280 and 390: `docs/brand/review-238/` (12 files, 1.4 MB).

## Checks, with exit codes

One local build of the final code, port 3238, under the build mutex (taken 08:04:42, given back 08:17:51 UTC).

| Check | Exit | Result |
|---|---|---|
| `npm run build` | 0 | 2 "statement timeout" lines in its log (see the top) |
| `npx tsc --noEmit` (after the build, which writes the route types) | 0 | |
| `check-analysis.mjs` | 0 | 279 of 279, with 18 new checks: the order, the brand, today's chart, the library, the archive, the three redirects |
| `check-analysis-flow.mjs` (no stub: nothing queued) | 0 | 229 of 229 |
| `check-findings-grids.mjs` | 0 | 163 of 163 |
| `test-analysis-flow.mjs` | 0 | all passed |
| `test-digest-chart.mjs` | 0 | |
| `check-values.mjs`, `/research` only | 127 | 0 of 0 values: nothing on the page carries a check key (see the top) |
| `check-routes.mjs` | 1 | 328 lines ok, 1 failed: `/emissions`, not touched here |
| battery page capture, numbers against session 211 | 0 | 0 lines differ; height 5016 |
| `python -m unittest discover -s tests` (this worktree) | 0 | 3,657 tests, OK, 224 skipped |
| em dash over every changed file | | none |

Not run: `check-internal-findings.mjs` (it needs the local stand-in server), `render-cards.mjs` (the photographs are unchanged), the full `check-values`, any design or accessibility tool. No request was submitted (spend USD 0); the request's markup was read by `check-analysis-flow.mjs`.

Test pins moved, each with a note "session 238": `test_session170.py` (the page's path; the card's address in the Roundup's lines; "no `ChartOfWeekView` on the page" became "the week drawn is the newest, and the check proves it is later than W40"), `test_session173.py` and `test_session182.py` (paths), `test_session181.py` (path; the scanner's group is a title inside the library), `test_session182_flow.py` (paths; the archive's section), `test_session203.py` (the menu's addresses, with `/analysis` moved to `/research` and its redirect asserted), `test_session231.py` (one line added). New: `tests/test_session238.py`, 23 tests.

## Figures

- The page: 15,083 px tall at 1280 (the review measured about 29,000), 23,392 px at 390; no sideways scroll at either.
- Cards at 1280 by 900: 893, 897, 897, 921, 931, 939 and 1,093 px for seven; 2,062 and 2,154 px for the two five-grid cards.
- Filed: ERCOT 6, CAISO 5, SPP 5, NYISO 4, ISO-NE 3, not one grid 1. Topics: power prices 5, batteries 3, fuel prices 2, curtailment 2, generation by fuel 2, the other five 1 each.

## Decisions made without you

1. "This week's chart (the Roundup's)" is the chart the Roundup carried, so a chosen finding when there was one, not always the rule's pick. It is not drawn as a library card, so a superseded card stays out of the list.
2. On a library card the method footnote, the table of estimates and a further chart are under one fold, closed. Without it seven cards were up to 1,715 px. A card's own page shows everything open.
3. The topic is the kind of table a card read, not what the card is about; the grid is what the card's own fields name. `who_rescues_whom` is filed under ERCOT and SPP because its chart's categories name them; `queue_divorce` under "Not one grid".
4. The brand has five series colors and the old palette six: a sixth series is drawn in the fifth's light grey.
5. Held Roundups are not rewritten; their links are redirected when drawn. The renderer's foot line now names `/research`; the photographs already made still name `/analysis`.
6. The list of held downloads is made at build (`findings_files` in the bundle), because a page drawn again an hour later is drawn by a server function that does not hold the public folder.
7. The old check "the chart of the week is not drawn on the page" was changed to "the week drawn is the newest and later than W40", since the owner asked for this week's chart on the page.
8. After 45 minutes without the mutex I made my waiter look every 3 seconds instead of every 20. My last hold was 13 minutes, the suite included.

## For Samuel's ruling

- The two five-grid cards are more than two screens each (small multiples of five grids, then one grid large). Fold the multiples, or accept.
- Today's chart is a picture the warehouse drew in its own palette (`daily_chart.py`), not in the brand's tokens. Bringing it to the brand is a change on the data machine.
- The finding titles are written in capitals in the cards' data and are shown as written.
- The request form comes first, as asked, and is 1,279 px at 1280 before the first chart.
- At phone width a card chart's legend runs over its axis title; the chart's option did that before this session.
- The archive's one line for 7 October reads `iso:pjm battery_operating_mw_net_added_12m`: it is the record's own fact up to its first colon.
- Platform tool 26 is still named "Automated Analysis" in `docs/platform-tools.md`; `package/llms.txt` and `docs/release-gate.md` still say `/analysis` (the redirect serves them).

## To finish

- Rebuild until the build log holds no "statement timeout" line, then `node scripts/check-routes.mjs http://localhost:<port>` (expected: 0 failed).
- Nothing else is open on this branch.

## The finishing pass

13 October 2026, 08:45 to 10:10 UTC, on the merged branch `task/237-238-grid-research` (this session with 237 and main). The full account is in `SESSION_237_REPORT.md`, "The finishing pass"; what concerns Research:

- **Said plainly: the merged tree was never built in this pass**, so `check-analysis.mjs`, `check-analysis-flow.mjs`, `check-findings-grids.mjs`, the whole `check-values` and `check-routes` were NOT run on it. The merge failed to build on a brace lost from `site/app/tokens.css` between session 237's block and this session's (fixed, commit `451080dd`; this session's block is untouched), a second build was served the same failure from `site/.next/cache/turbopack`, and the orchestrator then asked for the hand-back. "To finish" above still stands, on the landing's own build.
- **Run, with exit codes:** `test-analysis-flow.mjs` 0 (all passed). `test-digest-chart.mjs` 0. The python tests in one process, 95 modules with `test_session170`, `173`, `181`, `182`, `182_flow`, `203`, `231` and `238` among them: 1,749 tests, OK, 130 skipped, exit 0.
- **The documents this report named as still saying the old name:** tool 26's row of `docs/platform-tools.md` says Research at `/research`; `package/llms.txt` says `/research`, and the chat's exported spec (`site/lib/chat/spec.json`) follows it. `docs/release-gate.md` was not touched.
- **No link inside Research's components names `/analysis`:** what remains is `/analysis-files/` and `/api/analysis`, which keep their names.
- **The exit 127 of `check-values`:** it is the failing path only (`process.exit(1)` after the lines, then a libuv assertion in Windows-only code). A run that passes ends without `process.exit`. GitHub's runner does not run `check-values`. Read from the script and the workflow, not run.

## The landing

filled by the orchestrator
