# Session 241, batch B report: the pages of words on the brand

13 October 2026, from 09:07 UTC, unattended, one session of the overnight chain of 12 to 13 October, on the old laptop (`samueloldlaptop`, a code machine). Worktree `erw-149b`, branch `wip/241b-brand`, from `71e4b084`. Not pushed and not landed: the landing is the orchestrator's. Model spend USD 0 (the local server was started with a model key that is no key, so that no request of a check could reach a model). Pulls: none. No warehouse table written. No em dash in anything written.

The owner's task: "the brand on every remaining page. Every page not yet on the brand, except the Games content and the home page: through the tokens and shared components only." Batch B is the pages of words: `/about`, `/terms`, `/privacy`, `/data` with the data standard, the faults page and the method notes, the digest, the Roundup, the email form, Ask, Thesis Builder, the two draft reports, the page a visitor is shown for a page in review, and the internal pages.

## Read these first

- **Not clean at the hand-back: the final build's log holds one "statement timeout" line** (a Supabase read of a static page while the build drew it; the first build of that cycle held two, the rebuild in the same cycle one). The route check on that build passed (0 failed), `check-values` on the batch's addresses is 385 of 385, and no page of the batch reads a series at build time but the two draft reports, which are drawn at each request. A third rebuild was not made: the mutex had been held nine minutes. The orchestrator's build at the landing is a new one.
- **Every page of batch B carries the brand's wrapper**: 25 page files, 36 addresses captured (and 7 of Thesis Builder against the check's stand-in). Each is white, with the serif title in ink, IBM Plex Sans text and IBM Plex Mono figures and code (`runs/session241b/cap/after2__facts.txt`: `brand: true`, the faces and the title's color in force at each address).
- **No page says anything it did not say.** On 34 of the 36 addresses the checked numbers (453 in all), every link, every control, every anchor and the visible text are identical before and after: 0 lines of difference at 1280 px and at 390 px (35 of 36 on the first build, ten minutes after the "before"). The two that differ are internal and differ by data, not by the page: `/internal/waits` lists this report, which is new, and `/internal/usage` shows the live counts, which grew between the two captures (1,001 events, then 1,120). Thesis Builder against the check's stand-in: 7 addresses, 0 lines. The "before" is a build of the branch's first commit (`71e4b084`) made in this session.
- **The 25 addresses of the live-page snapshot read the same.** A visitor is shown the page in review at each (no page is live). By the snapshot script's own two functions (`numbers`, `visibleText` of `site/scripts/snapshot-live.mjs`) on the local build, before against after: `diff` 0 lines. The page in review is restyled (white page, serif title in ink, the light rule over "Open now"); a visitor's text differs by nothing. At the landing the orchestrator's comparison should list no difference from this batch on the 25 pages.
- **The battery page did not move**: its checked numbers and its visible text are session 211's (`diff` 0 lines each) and its height at 1280 px is 5,016, on both builds.
- **One check's pins moved: `site/scripts/check-thesis.mjs`.** Three of its 129 assertions read the mark "differs" as "DIFFERS" from the page's drawn text; on the brand a label is in the letters it is written in, so the check now reads the mark whichever way the style cases it. No python test's pin moved.
- **One hold of the build mutex did two things.** The mutex was not had in two tries (10 and 30 minutes of waiting), so the capture of the "before" (the build already made, served) and the build and checks of the "after" were one hold of 13 minutes, not two shorter ones. A second, shorter hold (9 minutes) built and checked the last commit.
- **`/reports` is no page** (404): nothing to restyle. `site/lib/release.ts` lists the address.

## What to review

After https://erw-flame.vercel.app/internal/open (once landed):

1. https://erw-flame.vercel.app/data/methods/battery_stack and https://erw-flame.vercel.app/data/standard (rendered markdown: the title, the headings, the tables, the code)
2. https://erw-flame.vercel.app/digest and https://erw-flame.vercel.app/roundup (the same rules on a digest and a Roundup, with the archive beside)
3. https://erw-flame.vercel.app/data and https://erw-flame.vercel.app/data/faults (the catalogue's table, the titled blocks)
4. https://erw-flame.vercel.app/about , https://erw-flame.vercel.app/terms , https://erw-flame.vercel.app/privacy
5. https://erw-flame.vercel.app/subscribe (do not submit it for a look) and https://erw-flame.vercel.app/ask
6. https://erw-flame.vercel.app/thesis
7. In a private window, without the internal view: https://erw-flame.vercel.app/storage (the page in review, as every visitor is shown it today)
8. https://erw-flame.vercel.app/cost-of-power/battery (unmoved)

Before the landing: `docs/brand/review-241b/` on the branch (each page after, at 1280 and 390 px, with a `README.md`).

## What was done

1. **The wrapper.** 25 page files wrap what they draw in `<Brand>` (`site/components/Brand.tsx`), every return of each page's own component: the pages named above, a digest's and a Roundup's own page with their "no weekend issue" and "no data" returns, and the seven internal pages. `/internal/open` and `/internal/waits` carried `data-no-usage` on their root and say it on the wrapper too (`<Brand noUsage>`); every other page keeps the usage count it had.
2. **Rendered markdown, once.** `.brand-a .prose-erw ...` in `site/app/tokens.css`: the title in the serif at 36 px (24 on a phone), a section heading at 24 (20) with the light rule above it, a third heading at 20 (16); a line of text at most 68 characters while a table or a block of code takes the width there is; a table with one dark rule under its header, no band, no box around a cell; code in the mono face on fog, with no rounded corner. Every method note (69), the data standard, the data dictionary on `/data`, a digest, a Roundup and the items of `/internal/waits` take them. The site's own rules in `app/globals.css` are untouched, so a page outside the wrapper draws markdown as before.
3. **Generic rules for the pages of words**, in the same block (`/* ---- session 241b ... */`, at the end of the brand section, every selector scoped to `.brand-a` and named for markup): a titled block of `components/Section.tsx` has the light rule above its title; in an article a line of text is at most 68 characters; a link in a list of terms is underlined; preformatted text outside markdown is fog with a rule-colored edge; a status box is a fog panel with a solid edge, not a dashed one; a field of words takes the text face (a field of figures stays mono); a checkbox is 16 px in the brand's accent, in a label at least 24 px tall; a table header that stays in place keeps white behind it; a column a document sets to the right is right-aligned.
4. **The page in review** (`site/app/in-review/page.tsx`) draws "Open now" with the shared `ToolSection`; its title and its sentence keep their own two lines. Its words, their order, its links and `data-in-review="1"` are as they were.
5. **A form's one action is the brand's** (cardinal with white words, the battery form's classes): "Sign up" and "Unsubscribe" on `/subscribe`, "Open the internal view" on `/internal/open`. The first was a grey outline and the two others would have turned dark red under the pointer with words that could not be read (the brand's rule for a submit button's hover).
6. **Thesis Builder**: the tab in view wrote its words in `"#fff"`, the one color literal of the batch; it names the token `--color-surface`. Its two charts read the tokens and the text face at their own box (`token(name, el)`, `baseStyle(el)`, session 236's additions to `components/echarts.ts`, which is not changed).
7. **`tests/test_session241b.py`** (23 tests): each page carries the wrapper on every return; no color literal and no font in a page's own files or in `components/thesis/`; the prose rules; the block (scoped, no page's name, no literal, after session 211's, the rules before it as they were); the page in review, the email form and Ask keep their words, fields and addresses.

## The pages

| Page | On the brand | What remains |
|---|---|---|
| `/about` | yes | |
| `/terms`, `/privacy` | yes | |
| `/data` | yes | "model-extracted" in cardinal is no link; on a phone the catalogue is still one wide table |
| `/data/standard`, `/data/methods/<slug>` (69 notes) | yes | text at 68 characters beside tables that can be twice as wide |
| `/data/faults` | yes | |
| `/digest`, a digest's own page, "No weekend issue" | yes | |
| `/roundup`, a Roundup's own page | yes | a date breaks over two lines in "Deals of the week" |
| `/subscribe` | yes | not submitted; the answers a submission shows (`?state=`) were not looked at |
| `/ask` | yes | no question sent: an answer was not looked at |
| `/ask/ercot` | partly | the page is wrapped; its panel (`components/ask/AskPanel.tsx`) is shared with the grid pages and is not edited; an answer and its chart were not looked at (no question may be sent) |
| `/thesis` | partly | wrapped, its one color literal a token, its charts on the brand's tokens; the report's own classes remain (a cardinal rule under a trend's title, 10 and 11 px labels the brand's rules do not reach, the mix's palette for two series) |
| `/reports` | no | no page at the address (404) |
| `/reports/draft/ai-gigawatts`, `/reports/draft/shape-premium` | partly | wrapped; their SVG charts keep rounded bars, size attributes and the up and down colors |
| the page in review (`/in-review`, and every address a visitor asks today) | yes | |
| `/internal/open`, `/internal/health`, `/internal/costs`, `/internal/usage`, `/internal/waits`, `/internal/findings`, `/internal/ask` | partly | wrapped, and they take the brand's generic rules; two keep an inline `minWidth` or an off-screen trap field's inline style (no color); `/internal/findings` draws the cards of `/analysis`, which another session holds |

## Checks, with exit codes

None piped; outputs under `runs/session241b/` in the main copy.

The first cycle (`after1_*`, commit `5a5fe977`, mutex held 10:03:45 to 10:16:49 UTC), then the python tests (`after1_tests*`, held 10:16:50 to 10:23:58):

| Command | Exit | Result |
|---|---|---|
| `npm ci` (once, in the cycle that built the "before") | 0 | |
| `npx tsc --noEmit` | 0 | |
| `npm run build` | 0, then 0 | the first build logged two "statement timeout" lines (a Supabase read of a static page); rebuilt in the same cycle: 0 such lines |
| `runs/session241b/capture.mjs`, the 36 addresses, before (the build of `71e4b084`), after at 1280, after at 390 | 0, 0, 0 | no address failed; before: 0 of 36 carry the wrapper; after: every page of the batch does (`/reports`, a 404, does not) |
| `runs/session241b/compare.py`, before against after at 1280 and at 390 | 1, 1 | 35 of 36 addresses: 0 lines differ (numbers, links, controls, anchors, text). `/internal/waits`: 43 lines, all of them this report listed on the page and the build's time |
| `runs/session241b/vis.mjs` (the snapshot's own `numbers` and `visibleText` on its 25 addresses, as a visitor), before against after, `diff` | 0 | 0 lines |
| `runs/session208/capture.mjs` on `/cost-of-power/battery`, `diff` with session 211's numbers and text | 0, 0 | 0 lines each; height 5,016 |
| `check-values`, restricted to the batch's addresses, twice | 0, 0 | 385 of 385 values match (`/data`, the two draft reports) |
| `check-routes.mjs` | 0 | 0 failed (1 live page and 159 in review asked as a visitor) |
| `check-internal-health.mjs`, `check-internal-waits.mjs` | 0, 0 | 19 checks; 24 of 24 |
| `check-ask-words.mjs`, `check-ask-ercot.mjs` (no question is sent by either) | 0, 0 | 9 of 9; 23 checks |
| `check-security.mjs` (without `--recorded`) | 0 | 50 of 50 |
| `check-csp.mjs --phone` | 0 | 5 pages at 390 px: 0 enforced, 0 report-only violations, none wider than the screen |
| `check-review-pages.mjs`, 13 of the batch's addresses | 1 | 12 of 13. The one: `/ask/ercot` "0 figures" in its text. The page is a question box and holds no figure; its text is identical before and after, so the check fails on it at the commit before too |
| `check-thesis.mjs` against the stand-in (`scripts/thesis-stub.mjs`), the server started with `THESIS_GATE_MODEL=0` | 1 | 126 of 129: the three read "DIFFERS" from the drawn text (see "Read these first"); the check was changed and run again in the second cycle |
| `python -m unittest`, 121 modules that name a file, an address or a class of the batch, one process each | 0 for each | 0 failing. `test_session67`, `150`, `158`, `160`, `235` and `241b` were run again after the last edit: 0 each |
| server, stand-in and ports after each phase | | ports 3244 and 54444 free; `EADDRINUSE` 0 in each server log |

The second cycle (`after2_*`, the branch's last code commit `cef31fa2`: the page in review's title, a prose title's width, the check of Thesis Builder; mutex held 10:45:31 to 10:54:59):

| Command | Exit | Result |
|---|---|---|
| `npx tsc --noEmit` | 0 | |
| `npm run build` | 0, then 0 | two "statement timeout" lines, then one after the rebuild (see "Read these first") |
| the capture of the 36 addresses at 1280 and at 390 | 0, 0 | none failed; at 390 px no address is wider than the screen (36 of 36: 390 of 390) |
| `compare.py`, before against after at 1280 and at 390 | 1, 1 | 34 of 36: 0 lines. `/internal/waits` (this report) and `/internal/usage` (the live counts moved) |
| `vis.mjs`, the snapshot's view of its 25 addresses, `diff` | 0 | 0 lines |
| the battery page against session 211 | 0, 0 | numbers 0 lines, text 0 lines, height 5,016 |
| `check-values`, restricted | 0 | 385 of 385 |
| `check-routes.mjs` | 0 | 0 failed |
| `check-internal-waits.mjs` | 0 | 24 of 24 |
| Thesis Builder against the stand-in: the capture of 7 addresses, compared with the "before" | 0 | 0 of 7 differ, 0 lines (the first cycle captured after the check had changed the stand-in's runs, so its comparison was of no use; this one captures first) |
| `check-thesis.mjs` against the stand-in | 0 | 129 of 129 |
| ports after each phase | | 3244 and 54444 free; `EADDRINUSE` 0 |

Not run again in the second cycle (their pages were not touched by its commit): `check-security`, `check-csp --phone`, `check-ask-words`, `check-ask-ercot`, `check-internal-health`, `check-review-pages`.

Not run: `check-lights.mjs` (the Games content); `check-csp.mjs` on every page of the release list; the `/ask` evaluation scripts and `check-ask-conversation.mjs` (they call a model); `check-thesis-real.mjs` (a real run); the whole suite on a clean copy, `freeze.py status` and the live snapshot (the orchestrator's, at the landing).

Tests whose pins moved: none in `tests/`. One check script: `site/scripts/check-thesis.mjs` (two lines, each with a "session 241b" note).

## Decisions made without you

1. **The measure is 68 characters for text, not for tables.** In rendered markdown a paragraph, a list and a heading stop at 68 characters; a table or a block of code may be as wide as the page. A method note's tables (eight columns in places) would not be readable in 68 characters.
2. **The page in review takes the shared section** (`ToolSection`) for "Open now" and keeps its own title and sentence. With the shared header too (the first build) the header's rule stood 32 px over the section's, two rules with nothing between; the second build has one. Its words are exactly as they were. Every other page of the batch keeps its own structure and is restyled by the brand's rules, as the brief allows for a page of words.
3. **A rule that reaches pages beyond the batch.** The rule for a titled block (`components/Section.tsx`) and the one for a status box (`components/NoData.tsx`) are written for the component, so every page on the brand that uses one takes them: today the datacenter page's "Grid by grid" view (session 236) gets the light rule above its section titles. Batch A's pages use the same two components; if batch A wrote the same rule in its own block, the two agree.
4. **Three buttons changed their classes** (item 5 above). The words on them, their forms and what they send are as they were.
5. **Labels written in capitals by a style are in sentence case** (the brand's existing rule `.brand-a .uppercase`): the group names in "The site" on `/about`, the header of the runs table on `/thesis`. The letters in the source are unchanged; the capture compares them with the style switched off on both sides.
6. **The "before" is a build of the branch's first commit**, captured on this machine in the same hour, not production: the comparison is then free of a deploy's or a day's difference.
7. **`check-csp.mjs` was run with `--phone` only** (the five pages it names, at 390 px), not on all 160 pages of the release list: the full run is other sessions' pages and several minutes of the build mutex. It posts the sign-up form with neither email chosen, as the check is written (the route answers "choose one" and stores nothing); the brief names the check, so it was run.
8. **`check-lights.mjs` was not run**: it reads `/play/battery`, the Games content, which this batch does not touch.
9. **The reports' SVG charts keep their size attributes** (`fontSize={12}` and the like in the two draft reports). The brand's rule for a chart's text sets 12 px over them; their colors were already tokens. Redrawing them with the shared chart components is not a change of look only.

## For Samuel's ruling

1. **Marks that a style set in capitals are in small letters on the brand.** The brand's rule (labels in sentence case, as they are written) reaches Thesis Builder's marks "differs", "run anyway" and "vendor page", and the group names of "The site" on `/about`. Keep them as written, capitalize their first letter in the source (a change of words, not made here), or give the brand a rule for a mark.
2. **"model-extracted" on `/data` is cardinal words that are no link**, a job the brand does not give cardinal (`docs/brand.md`, section 2). Keep it as the catalogue's one warning, or mark it another way.
3. **`/reports` answers 404**: `site/lib/release.ts` lists the address and no page is at it (the two drafts are at `/reports/draft/...`, each behind the token). A page that lists the drafts, a redirect, or the address off the list.
4. **The two draft reports' bars** keep rounded ends (`rx` in the SVG) and the up and down colors of the price board; the brand's corners are square and its charts take five series colors. Redraw them with the shared chart components, or leave the drafts.
5. **The page a visitor is shown for a page in review is on the brand** (white page, the serif title in ink, the light rule over "Open now"). Its words are identical; it is what every visitor sees at every address today. Say if it should wait for the launch.
6. **`/data` on a phone** is still one wide table that scrolls sideways with tall rows (the source reports break in a narrow column). A list of cards at 390 px would be a change of structure.

## Not done, not verified

- **No question was sent on `/ask` or `/ask/ercot`, no run was started on `/thesis`, and `/subscribe` was not submitted by this session's own captures** (spend USD 0, no table written). What those pages draw after a submission (an answer with its sources and chart, a run in progress, the sign-up's answer) was checked by the scripts above on recorded data where one exists, and was not looked at on the brand otherwise. `check-csp.mjs --phone` posts the sign-up form with neither email chosen, as it is written; the route answers "choose one" and stores nothing.
- **Thesis Builder with a report in it was seen only against the check's stand-in** (made-up runs). The real list of runs was read (a read only).
- **No accessibility or design tool was run.** The look was judged from the screenshots at 1280 and 390 px, the first 2,200 and 2,600 px of each page; the rest of a long page (the registry on `/terms`, the catalogue on `/data`, the notes) was not looked at below that.
- **63 of the 69 method notes were not opened**; they take the same rules as the six captured.
- **The digests' and Roundups' own pages for other days and weeks** were not opened beyond the two captured.
- The whole suite on a clean copy was not run: 121 modules were.

## The landing

- Landed in one push with batch A and the two home page mockups (`docs/brand/home-mockups/`), on `task/241-brand` (`c2144c8e`). `tokens.css` keeps every session's block, each identical to its own branch's (checked block by block after the merge).
- The whole suite in a clean worktree at `8d9ce33e`: exit 0, 3,894 tests OK, 237 skipped; after a merge of `main` (session 252, documents and one test) the modules it changed were run on the clean copy: exit 0.
- `npm run build`: exit 0, no "statement timeout" line. `check-values` on every page: exit 0, 4,530 of 4,530. `check-routes`: exit 0, 203 pages as a visitor, 0 failed. Exit 0 each: `check-no-request`, `check-supply` (27 of 27), `check-policy` (46 of 46), `check-queues` (55 of 55), `check-curtailment` (118 of 118), `check-analysis` (279 of 279), `check-battery-scenarios`.
- **Seen at this landing, not this batch's:** the first `check-values` run found 16 checked values on `/cost-of-power` where the run before had found 76, and passed: on a cold cache one read of the datacenter page's answers had failed and the page drew its answers' "no data" state, which carries no key, so the check had nothing to compare. A second run on the same build found 76 of 76, and production 76 of 76. The check cannot see a page that silently shows fewer numbers: for your ruling (a floor of keys a page, read from the last passing run).
- `python scripts/freeze.py status`: exit 0, no freeze. Before snapshot `s241-before` (11:23:36 UTC, 25 pages, 0 failed), then the push.
- Check run 38389922595: success at 11:34 UTC; merged into `main`. Production served the new build from 11:35:48 UTC. After snapshot `s241-after` (11:36:09 UTC, 25 pages, 0 failed); `compare s241-before s241-after`: exit 0, "0 differences in all". Expected: the page a visitor is shown for a page in review was restyled and its words did not change.
- The remote branches `wip/241a-brand` and `wip/241b-brand` are deleted: all of each is on `main`.
