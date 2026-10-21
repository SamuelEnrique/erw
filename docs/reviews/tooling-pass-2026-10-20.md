# The five tool pages through the installed design tools

Energy Research Warehouse (ERW), session 401, chain `queue/done/015-day-20-october-code-pm.md` (the evening of 20 October 2026, run from 06:15 to about 08:30 UTC on 21 October). The roadmap's item 4 asks that each installed tool be used in at least one session's checks; this is the pass that runs every one of them on the five tool pages, records what each found with the tool that found it, fixes what needs no ruling within `docs/brand.md`, and lists the rest. `docs/tooling.md` now gives each tool's first use.

The pages: `/cost-of-power/battery`, `/cost-of-power/seller`, `/cost-of-power` (with its `?view=grids`, "Grid by grid"), `/research` (where `/analysis` redirects since session 238) and `/grid`. Every page is in review, so each was read in the internal view, opened by the form (no token in an address), on a local production build at `http://localhost:3401`.

**Every value unchanged.** Every figure that carries a check key was read before and after the fixes, at 1280 and at 390 px: 1,646 figures each time (the same 823 at each width), every key, raw value and shown text the same. `check-values` on the final build, restricted to `/cost-of-power` and `/grid` (every address under them in its list): exit 0, 2,589 of 2,589 values match the live set. With `/research` and `/analysis` added: 2,709 of 2,709 values match, `/research` itself 120 of 120, and one line fails, the floor of `/research/card/gas_sets_price` (4 numbers where its floor is 6). That card page is not one of the five and nothing on it changed; its ISO-NE callout is the one now drawn as held (the license hold that begins on 21 October 2026, `lib/license.ts`). The restriction cannot keep `/research` and leave its cards out (the variable takes address prefixes).

Shots, before and after, at 1280 and 390 px: `docs/brand/review-401/<page>_<width>_<before|after>.png` (the top of each page; the script that took them and measured the pages is `docs/brand/review-401/shots-401.mjs`). The tools' raw outputs are kept on the code machine under `runs/chain_oct21/s401/` (not in git).

## How each tool was run

| Tool | How | Raw output |
|---|---|---|
| Impeccable | `critique` as its playbook asks: Assessment A (design review, ten heuristics, priority issues) and Assessment B (the detector, `impeccable detect --json`, on the pages' files and on the shared components they draw) in two separate agents, A finished before B's findings were read. The live overlay was not injected (no server or browser of its own may be left running); B read the captures and measurements instead. Nothing was written to `.impeccable/`; no `PRODUCT.md` or `DESIGN.md`; no hook. Questions skipped: the session is unattended (its rule: no question is asked); every question the skill would put to a brief was answered from `docs/brand.md` | `impeccable_A.md`, `impeccable_B.md`, `impeccable_detect_before.json` |
| UI/UX Pro Max | its search script, 12 queries of its guidelines (targets, labels, focus, tables, charts, text size, hover-only content, live regions, number inputs), each result held against the rendered pages and their measurements | `uiux/q1.txt` to `q12.txt` |
| frontend-design | its principles and its list of the traits a generated page falls into, held against the captures | this file |
| web-design-guidelines | the rules from the copy kept by session 201 (`runs/session201/vercel-skills/guidelines_command.md`; no fetch), applied to every page-own `.tsx` by an agent told which rules `app/tokens.css` already enforces | `web_design_guidelines.md` |
| react-best-practices | the skill's 70 rules applied to the same files and to the pages' two model modules, by an agent | `react_best_practices.md` |
| AccessLint | `audit_live` (WCAG 2.2 A and AA) on each of the six addresses, before and after the fixes, in a headless browser on port 9222 holding the internal view's cookie (stopped after) | `accesslint_before.txt` |
| (measurement) | `shots-401.mjs`: every checked figure, text under 12 px, targets under 24 px, a page wider than the window, the heading outline, fields with no name, cardinal outside a link or a control, round corners | `shots/measure-<width>-<stage>.json` |

## What the tools agree on

- **The calculators read as made for this product** (Impeccable A, frontend-design): the serif summary sentence with three sourced headline figures, assumptions with their default and source beside the field, the battery's broken 2021 bar. The battery scores 29 of 40 (Good) on Impeccable's heuristics; the seller 27, the datacenter 26, Grid by grid 21, Research 24, the Grid 26 (all Acceptable).
- **Most of what fails is in shared components**, not in the pages' own files: the help "i" button (16 by 16 px, a 10 px glyph), the Chart and Table toggles (22 px tall), the menu (20 px tall), the scrollable tables, the research cards' 10 and 11 px text, the grid page's chips and legend swatches. These are listed for session 412 below and were not touched here.
- **No page is wider than the window** at 390 or 1280 px, no heading level is skipped, every field has a name, no positive tabindex (the focus order follows the page), and no page logs an error (measurement).
- **AccessLint** finds nothing on Grid by grid, Research and the Grid; on the three calculators one serious finding each (a scrolling table with nothing focusable in it) and four minor (an empty header cell), all in shared components.

## Fixed (the pages' own files; no ruling needed within docs/brand.md)

Each line: what, where, the tool that found it, the brand rule.

| Fix | File | Found by | Brand |
|---|---|---|---|
| The "derived" tier tags of Grid by grid at 12 px (were 10), square (were round), a 24 px target (was 44 by 15); their capitals and letter-spacing classes removed (the brand already undid them) | `app/cost-of-power/GridsView.tsx:37` | web-design-guidelines, measurement, Impeccable B | section 1 (nothing under 12 px), 3 (square corners, 24 px targets) |
| The calculator's fields square (were round) | `app/cost-of-power/charts.tsx:43` | frontend-design, measurement | section 3 |
| Header cells say what they head (`scope="col"`), and each row's first cell is its header (`th scope="row"`, same look) in the four hand-written tables | `GridsView.tsx:146, 151, 201, 204, 222, 227`; `charts.tsx:61, 66`; `app/research/page.tsx:198 to 213` | web-design-guidelines | a label |
| The folds' summaries 26 to 29 px tall (were 18 to 21): the month bands, the four peaks, the large-load statements, the storage nodes, the basis, the Grid's decisions, the citations | `app/cost-of-power/page.tsx:264, 330`; `LoadAnswers.tsx:250`; `battery/page.tsx:263`; `seller/page.tsx:356`; `app/grid/page.tsx:58`; `app/research/view.tsx:44` | web-design-guidelines, measurement | section 3 (24 px) |
| The Reset link of "Your load" a 26 px target (was 18) | `app/cost-of-power/LoadForm.tsx:100` | web-design-guidelines | section 3 |
| The income table's Table and Chart buttons 26 px (were 22) | `battery/Income.tsx:66` | web-design-guidelines, UI/UX Pro Max (target size) | section 3 |
| The research page's index links 25 px (were 21) | `app/research/page.tsx:114 to 118` | Impeccable B, measurement | section 3 |
| The pasted profile's Clear button 26 px (was 22) | `seller/SellerProfile.tsx:98` | web-design-guidelines | section 3 |
| The window's two selects named from the word on screen ("From: your window's first year", "to: your window's last year"; the names did not contain "From" and "to") | `battery/Income.tsx:74, 77` | web-design-guidelines | a label |
| The pasted profile's field at 16 px on a phone (a smaller field makes a phone zoom); 12 px with the same line height from 640 px, as before | `seller/SellerProfile.tsx:86` | web-design-guidelines | section 1 (16 px in a field on a phone) |
| The "hours priced" line, which changes once the prices are read, is announced (`aria-live="polite"`) | `seller/SellerProfile.tsx:102` | web-design-guidelines, UI/UX Pro Max (live region) | a label |
| The duration links not in view get the buttons' hover (fog) | `battery/BatteryForm.tsx:70` | web-design-guidelines | section 2 |
| Number fields ask for no browser suggestion (`autoComplete="off"`), 15 fields | `LoadForm.tsx:68, 78 to 80`; `BatteryForm.tsx:89`; `Settings.tsx:120`; `Scenarios.tsx:345`; `SellerForm.tsx:82, 86, 92, 95, 103`; `charts.tsx:47, 48, 56` | web-design-guidelines | none (behavior of the browser only) |
| "(picked)" in the research rule's table is ink, not cardinal (cardinal is a link, a control or the highlighted series) | `app/research/page.tsx:212` | Impeccable A and B, measurement | section 2 |
| 32 px of air before "Your own inputs" in Grid by grid (it sat 8 px under the table above) | `GridsView.tsx:238` | Impeccable A | section 3 (a title inside a section) |

Measured after: text under 12 px on Grid by grid 5 to 0; targets under 24 px on the battery 22 to 19 (1280) and 21 to 19 (390), the datacenter page 19 to 16, Grid by grid 27 to 22, Research 62 to 57, the Grid 17 to 16; cardinal text outside a link or control on Research 2 to 1 (the one left is the shared scanner card). AccessLint's findings are unchanged (all in shared components).

## For Samuel's ruling

One a line. A tool's finding is a reading, not a ruling.

- Grid by grid's compute calculator writes "license needed MWh" for the energy its own inputs produce, while the note under the table prints the same figure (194,400 MWh): the check key `cop|energy|...` is held by the license gate (`GridsView.tsx:215, 217`). Intended, or should a figure computed from the reader's inputs never be held? (Impeccable A)
- On a phone the three calculators open with their whole form: the first answer is about 1,800 to 2,150 px down. Show the summary sentence and headline figures first, or fold the form to one line? (Impeccable A, UI/UX Pro Max)
- Grid by grid's bars and scatter points are all cardinal with nothing highlighted, and its monthly line does not break its 2021 spike; session 317 kept the charts' props from the canvas. Ink with cardinal for a highlight, and a broken 2021, as the battery chart? (Impeccable A, frontend-design)
- Grid by grid: the two tables list the ISOs in opposite orders, and one column holds "7.46 million" above "7,462,511" (brand section 5: one magnitude a column). (Impeccable A)
- About twenty places give a reason, a definition or a source only in a hover title (the "not held" and "license needed" marks, the column definitions, the strategy and duration words, the pasted profile's accepted format): a keyboard or touch reader cannot reach them (brand section 6 asks that a hover card's words be reachable by keyboard). (web-design-guidelines, UI/UX Pro Max)
- The Grid and Asset radios of the calculators open a new page on change: arrow keys through the group load one page a step. (web-design-guidelines)
- The "#financing" links land on a fold that starts closed and do not open it (`battery/Settings.tsx:85`, `battery/Scenarios.tsx:381`). (web-design-guidelines)
- The battery's box has the title "Assumptions" and, directly under it, a fold also called "Assumptions" (`battery/Settings.tsx:72, 73`). (web-design-guidelines)
- "Show" names no result, and nothing says the page is loading between Show and the new figures (three calculators). (web-design-guidelines)
- "Reset" (Your load) does not name what it resets (brand section 7: "named for its field"). (web-design-guidelines)
- Empty table header cells over the label and note columns (`cost-of-power/page.tsx:228`, `LoadAnswers.tsx:91`, `seller/page.tsx:130`): words for them, or a header only screen readers hear? (AccessLint, minor)
- A cell that holds nothing is empty where the brand says "not held": the research rule's percentile (`research/page.tsx:221`) and the cheapest-hours price (`GridsView.tsx:231`). (web-design-guidelines, frontend-design)
- `research/view.tsx:25` writes the percentile as "{n}th": "1th", "2th", "3th", "22th" are possible. (web-design-guidelines)
- Three empty-state lines of Research begin in lower case ("no card yet", `research/page.tsx:245, 256, 272`). (web-design-guidelines)
- "Method note" is the name of two links on the datacenter page (`cost-of-power/page.tsx:109` and its source line). (measurement, Impeccable B)
- The tabs of the cost of power wrap to three lines each at 390 px ("What a / datacenter / pays"). (frontend-design, the 390 shot)
- The section titles "Is it worth building?" and "Which option is better?" read as a judgment; the source footers name session numbers. (Impeccable A)
- The finding card's render frame (the social pictures, `app/research/card/render.css`) sets Inter where the brand names IBM Plex Sans; the detector's only two findings, false positives for the pages themselves. (Impeccable B)
- The datacenter page's notes run about 120 characters a line in places (brand: 68). (Impeccable A)
- The calculator of Grid by grid keeps its inputs out of the address and has no reset; its fields cannot be emptied to type a new value (`charts.tsx:34, 47`). (web-design-guidelines, Impeccable A)
- `LoadAnswers.tsx:183` reads the year from the browser's clock in a client component: server and browser can disagree on 1 January. (web-design-guidelines, react-best-practices)

## For session 412 (shared components; not touched here, so that one component gets one fix)

- `components/tool/ToolPage.tsx:32`: the "i" help button 16 by 16 px with a 10 px glyph, beside nearly every label of the battery and seller pages; its tip has no Escape. (all six tools)
- `components/tool/ToolPage.tsx:124` (`ToolTable`) and the sensitivity block's table (`components/decisions/ScenarioBlock.tsx`): a table that scrolls sideways has nothing focusable, so a keyboard cannot scroll it (`tabIndex={0}`, `role="region"` and the caption as its name). AccessLint: serious, on the battery (`#earned`, the income table), the seller (`#capture`) and the datacenter page (the sensitivity table). `ToolTable` also draws a head of "" as an empty header cell (minor, three places).
- The Chart and Table toggles of the shared charts (`components/svgchart.tsx`, the Grid's time chart): 22 px tall.
- `components/Nav.tsx:48`: the menu's summaries 20 px tall (44 px on a phone in the brand).
- `components/analysis/` (FormPicker, FormChart, MultiChart, FindingCard): 59 texts at 10 and 11 px on Research; "show the card" is the name of five links; "Found by the scanner" set in cardinal.
- Research's charts draw at a fraction of their column at both widths (the week chart's axis runs together, the five-grid small multiples are about 40 px wide): `components/analysis/CardChart` and the chart host. (Impeccable A, P1)
- `components/grid/`: "Select grids" and the seven grid chips at 11 px (`components/mix/views.tsx:29`); 34 round legend swatches (`components/grid/Conditions.tsx:251`); the Tier tag at 10 px and about twenty notes at 11 px (`YourGrid.tsx`, `Emissions.tsx`); the Net export headline reads "by grid MW" (`NowView.tsx:99`); the missing-day box shows `RuntimeError` text and lacks `role="status"`.
- `components/CaisoBreakNote.tsx:23`: a cardinal left stripe on the callout (brand: a panel is fog with a rule-colored edge).
- `app/tokens.css:223`: every select is set in IBM Plex Mono, so word labels in selects read in mono and truncate ("The last twelve months (defa"); the brand keeps mono for figures.
- `components/Num.tsx`: pulls the 38 KB `license_status.json` into the calculators' client bundles. (react-best-practices)

## Performance (react-best-practices), listed, not changed

None of these is spacing, contrast, focus order or a label, and several would send the live set's reads at once on a night it answered heavier reads with statement timeouts; none was made. Each would leave every value as it is.

- `battery/Scenarios.tsx:285`: `useBlock` runs the sensitivity (an NPV or IRR solve per assumption) three times a keystroke where one is used; the same twice in `LoadScenarios.tsx:82` and `seller/SellerScenarios.tsx:184`.
- `cost-of-power/model.ts:185`: six reads of the live set wait on one another though every gate is known before the first; `cost-of-power/page.tsx:148`: the two large-load reads wait for the model.
- `grid/page.tsx:76`: `await load(cfg)` holds the whole tree before the blocks' own reads start.
- `battery/page.tsx:114, 121`: five reads in sequence that could be two steps; `seller/model.ts:268`: two reads in sequence.
- `research/page.tsx:125`: every default card's full JSON is sent to the request flow (about 320 KB of cards), and the cards are drawn again in the library.
- Smaller: repeated `find` scans inside loops (`GridsView.tsx:65`, `charts.tsx:20`, `battery/page.tsx:125`), a component defined inside a component (`LoadAnswers.tsx:199`), repeated pure calls (`LoadScenarios.tsx:173`, `research/page.tsx:85`).
- Code drawn by nothing: `LoadContract.tsx`, `LoadWaits.tsx`, `RulesInMotion.tsx`, `grid-cells.tsx`, `battery/Contract.tsx`, `seller/SellerContract.tsx`, `seller/SellerHubYears.tsx` (their 10 and 11 px text is not seen by anyone), and four unused exports (`CoverOfA`, `MonthsOfA`, `CoverageOfA`, `DscrOfA`).

## Where the tools and the brand disagree (the brand wins)

- frontend-design names a broadsheet layout with hairline rules and square corners, and a cream page with a serif display, among the traits of a generated page: the brand chose both on purpose (FT-like hairlines as information, a white page with fog panels). Kept.
- web-design-guidelines asks for Title Case headings, curly quotes, `Intl` number formats for other locales and smooth scrolling: the brand writes sentence case, the site has one locale which `check-values` reads, and the brand has no motion.
- UI/UX Pro Max asks for a legend on every chart and 44 px targets: the brand labels series directly and asks 24 px (44 px tall on a phone), as WCAG 2.2 AA does.
- The seller's load-zone links in its table (18 px tall) and the datacenter page's document links in table cells sit in rows 32 to 36 px apart: WCAG's spacing exception holds; not changed.
- The skip link measures 1 by 1 px: it is hidden until it has focus.
