# Accessibility of the review pages, 22 October 2026

Energy Research Warehouse (ERW), session 583 (chain 034, "Session 583: an accessibility scan of the review pages"), on samueloldlaptop, 22 October 2026 between 01:00 and 02:45 UTC. The pass before this one is `docs/reviews/accessibility-2026-10-20.md` (session 412: 47 addresses at 1280 px, nothing found after its fixes). A tool's finding is a reading, not a ruling (`docs/tooling.md`): what asks for a change of words beyond a missing label, or of design, is under "For Samuel's ruling".

## How the pages were read

- **Pages.** Every address of check-values' list (`node site/scripts/check-values.mjs --list`): 149 pages and the 2 internal drafts, 151 addresses, each at 1280 by 900 and at 390 by 844: 302 scans before and 302 after.
- **The tool.** AccessLint's automated scan, the command its MCP tool `audit_live` runs (`accesslint scan <url> --format json --port P`, @accesslint/cli 0.13.0, engine @accesslint/core 0.21.0, WCAG 2.2 A and AA), from the copy npx already held (no download). One spot check through `audit_live` itself agreed. No `--snapshot`: the tool wrote no file of its own.
- **The internal view.** Every page is in review, so a headless Chrome on port 9583 opened the internal view by the form (`docs/brand/review-583/chrome-583.mjs`, the token posted, never in an address). The browser was stopped at the end; none is left running.
- **The widths.** Headless Chrome will not make a window narrower than about 500 px (asked for 390, it gave 496). So `docs/brand/review-583/scan-583.mjs` opens each tab itself, sets the width by the DevTools protocol's device emulation (390 as a phone, 1280 as a desktop), loads the page, waits 5 s for its scripts and charts to settle, and has the scan attach to that tab (`--attach`). Each tab's address carries a fragment of its own (`#a11y-scan-N`): the first run, without it, let the scan attach to the same page open at the other width, and 1280 was credited with 390's findings. Only the third run, with both, is the "before" below.
- **A local production build** of the branch at `http://localhost:3583`: one build before the fixes, one after the first round, one after the second (the first round's own scan found two things to correct, below).

## Before and after

Before: **271 findings on 73 of the 302 scans** (110 at 1280, 161 at 390). After: **30 on 15** (15 at each width), every one of them listed below with the reason it was left.

| Rule (AccessLint) | WCAG | Before, 1280 | Before, 390 | After | What was done |
|---|---|---|---|---|---|
| keyboard-accessible/scrollable-region | 2.1.1 | 0 | 39 | 0 | Fixed in `components/ScrollRegions.tsx` |
| landmarks/landmark-unique | best practice | 0 | 12 | 0 | Fixed in `components/ScrollRegions.tsx` |
| distinguishable/link-in-text-block | 1.4.1 | 46 | 46 | 2 | Fixed in `app/tokens.css` and `components/grid/YourGrid.tsx`; one link left (a page file) |
| labels-and-names/label-content-mismatch | 2.5.3 | 50 | 50 | 0 | Fixed in `app/network/NetworkGravity.tsx` |
| distinguishable/color-contrast | 1.4.3 | 1 (+1) | 1 | 2 | The 3D network's line of help fixed in `app/tokens.css`; the game's line left (inactive control) |
| navigable/heading-order | best practice | 3 | 3 | 6 | Left (a page file) |
| aria/aria-allowed-role | 4.1.2 | 10 | 10 | 20 | Left (the tool's reading, against ARIA in HTML) |

(+1): the 3D network's line of help (`/grid?grid=ercot&view=network` and `?grid=us48&view=network`, 2.48 to 1) drew after the before scan read those pages; the first after scan found it.

## The fixes

1. **Scrolling figures and markdown tables** (scrollable-region, 39 at 390 px). `ScrollRegions` made a scrolling box one stop of the keyboard only when a class made it scroll (`overflow-x-auto` and its kin, `pre`). Two kinds scroll by the stylesheet: a chart's figure on a phone (`app/tokens.css`, "charts": the year chart keeps its width and scrolls inside its frame; `/shoulder`, `/storage?tab=owners`, the demand growth explorer, the datacenters' grids, the battery awards) and a table of rendered markdown (`app/globals.css`, `.prose-erw table`: the 13 digests, the roundup, `/data/licenses`, the resources map's file list). Both are now read, and marked only while they scroll, as every other box is. A figure is made a stop of the keyboard and nothing more: it is already a figure named by its caption, and the role of a region is not allowed on a figure (the first round gave it one, and AccessLint's after scan found 21 aria-allowed-role on those figures; the second round took it away).
2. **Region names told apart** (landmark-unique, 12 at 390 px). Two scrolling tables under one heading took one name ("Reliability" on the CAISO and grid pages, "Method, the table of estimates" on the research cards, "Access" on `/data`, the calculator on `/cost-of-power`, the industrial load table on `/demand`). A name the script or the server's `scrollRegion()` gave now takes its place among those that share it ("Reliability, 1 of 2", "Reliability, 2 of 2"), and goes back to its own words when the other is gone. A name a page wrote itself is never changed. Words for a screen reader only.
3. **Links in a grey note underlined** (link-in-text-block, 90 of 92). The brand's rule (`docs/brand.md`: a link in running text is underlined) is drawn for paragraphs, lists, cells and terms; a note set as a block (`div.text-muted`) was missed: "Each neighbour" and "the exchange of each" under the headline numbers of every grid page and `/mix`, and "Method" in each event's caveat. `app/tokens.css` underlines a link without a class of its own in such a note (a button, a segment or an ink link keeps its drawing). The same rule also underlines "ERCOT's grid page" and its six kin in the Exchange view's list, which AccessLint did not flag. "All datacenters" on the grid pages sits in a line of figures, not a note: `components/grid/YourGrid.tsx` gives it the underline itself.
4. **The gravity circles' names** (label-content-mismatch, 100). A circle on the gravity shape was named "California Independent System Operator" under the drawn label "CAISO", so a voice command that says what it sees could not reach it. Its name now begins with the label: "CAISO, California Independent System Operator" (`app/network/NetworkGravity.tsx`, drawn on `/network` and the Grid tool's gravity and exchange views; a name that already holds its label, PJM's, is unchanged).
5. **The 3D network's line of help** (color-contrast). Its library draws "Left-click: rotate, ..." in slate grey at 70 percent on the white sheet, 2.48 to 1. In the captions grey, whole, it is about 5.6 to 1; its place and size are unchanged (`app/tokens.css`).

No figure moved: check-values on the pages the fixes reach (`/grid`, `/mix`, `/events`, `/datacenters`, `/shoulder`, `/storage`, `/explore/demand-growth`, a digest, `/roundup`, `/data`) matched 2578 of 2578 values against Supabase; its six floors not met are event pages whose figures show "license needed" in place (a license hold; the before shot `event-method_1280_before.png` shows the same), not a change of this session. The words added are a screen reader's only, except the underlines, which are the brand's rule drawn where it was missed.

Shots of the window at each visible fix, before and after, at 1280 and 390: `docs/brand/review-583/` (the grid page's "Each neighbour" and "All datacenters", an event's "Method", the Exchange view's grid link). The counts a page and width: `docs/brand/review-583/counts-583.csv`.

## Left, and why

- **`/cost-of-power?view=grids`: "SPP" in a heading** (link-in-text-block, 1 at each width). A grid's heading on the Grid by grid view holds a link to its grid page beside the heading's other words, told by color alone. It is drawn in `app/cost-of-power/GridsView.tsx`, a page's own file (and session 581's, in parallel): a page session's fix (an underline on the link, as item 3), listed here.
- **`/map?tab=queues` (3 addresses): "Every entry year" is an h3 after the page's h1** (heading-order, best practice). In `app/map/QueuesView.tsx`, a page's own file: an h2 with the same classes would read the same. Listed for a page session.
- **`/play/battery?mode=hard`: "Not available for 2026-10-20: ..."** (color-contrast, 3 to 1). The line explains why the solar add-on is switched off; the whole option, the switch with its words, is dimmed to 70 percent while it cannot be chosen (`app/play/battery/Game.tsx`). WCAG 1.4.3 exempts the text of an inactive control; whether the reason should stay dimmed with it is a design question, below.
- **The gravity drawing's `svg` with `role="group"`** (aria-allowed-role, 10 addresses at each width). AccessLint does not allow a role on an `svg`; ARIA in HTML allows any role there, and the group is what tells a screen reader that the eight circles inside it, each a button, belong together. Left as it is: the tool's reading against the specification.
- **Wider than the window at 390 px**: the demand growth explorer (5 addresses, 398 px) and `/policy` (429 px) are wider than a 390 px phone. Not an AccessLint rule; session 584's subject (390 px on every page), named here only.

## For Samuel's ruling

- The battery game's dimmed reason ("Not available for <day>: the warehouse holds no solar shape ..."), 3 to 1 at 70 percent: (a) leave it dimmed with its switch (WCAG exempts an inactive control); (b) dim the switch and its name only, and draw the reason in the full captions grey (4.5 to 1 or more).

## What was not read

- Keyboard order, a screen reader by ear, zoom to 200 percent and reduced motion: AccessLint's automated tier only (session 412 walked the keyboard on 47 addresses two days ago).
- The tabs of a page beyond the address check-values reads, and a page's state after a click (a fold opened, a tab chosen): only what each address shows when it loads.

## Count a page and width

Every address not in this table had no finding at either width, before or after.

| Address | 1280 before | 1280 after | 390 before | 390 after |
|---|---|---|---|---|
| `/data` | 0 | 0 | 1 | 0 |
| `/grid` | 1 | 0 | 1 | 0 |
| `/datacenters?view=grids` | 0 | 0 | 1 | 0 |
| `/roundup` | 0 | 0 | 1 | 0 |
| `/mix` | 1 | 0 | 1 | 0 |
| `/mix?ba=erco&state=TX` | 2 | 0 | 2 | 0 |
| `/demand?view=consumption` | 0 | 0 | 1 | 0 |
| `/explore/demand-growth` | 0 | 0 | 3 | 0 |
| `/explore/demand-growth?grid=us48&window=peak` | 0 | 0 | 2 | 0 |
| `/explore/demand-growth?grid=pjm&window=ytd` | 0 | 0 | 3 | 0 |
| `/explore/demand-growth?grid=caiso&window=m08` | 0 | 0 | 3 | 0 |
| `/explore/demand-growth?grid=ercot&window=h17` | 0 | 0 | 3 | 0 |
| `/data/licenses` | 0 | 0 | 1 | 0 |
| `/grid/ercot` | 2 | 0 | 2 | 0 |
| `/grid/caiso` | 2 | 0 | 4 | 0 |
| `/grid/pjm` | 2 | 0 | 2 | 0 |
| `/grid/nyiso` | 2 | 0 | 2 | 0 |
| `/grid/isone` | 2 | 0 | 2 | 0 |
| `/grid/miso` | 2 | 0 | 2 | 0 |
| `/grid/spp` | 2 | 0 | 2 | 0 |
| `/cost-of-power?view=grids` | 1 | 1 | 2 | 1 |
| `/map?tab=queues` | 1 | 1 | 1 | 1 |
| `/map?tab=queues&iso=ercot` | 1 | 1 | 1 | 1 |
| `/map?tab=queues&iso=spp` | 1 | 1 | 1 | 1 |
| `/play/battery?mode=hard` | 1 | 1 | 1 | 1 |
| `/events/caiso-heat-2020` | 1 | 0 | 1 | 0 |
| `/events/elliott-2022` | 1 | 0 | 1 | 0 |
| `/events/ercot-heat-2023` | 1 | 0 | 1 | 0 |
| `/events/caiso-heat-2022` | 1 | 0 | 1 | 0 |
| `/events/cold-2025` | 1 | 0 | 1 | 0 |
| `/events/east-heat-2025` | 1 | 0 | 1 | 0 |
| `/events/cold-2026` | 1 | 0 | 1 | 0 |
| `/storage?tab=owners` | 0 | 0 | 1 | 0 |
| `/map?tab=resources` | 0 | 0 | 3 | 0 |
| `/shoulder` | 0 | 0 | 2 | 0 |
| `/shoulder?grid=caiso&month=2025-07` | 0 | 0 | 2 | 0 |
| `/research` | 0 | 0 | 4 | 0 |
| `/research/card/batteries_lunch_grids` | 0 | 0 | 1 | 0 |
| `/grid?grid=ercot` | 2 | 0 | 2 | 0 |
| `/grid?grid=ercot&view=exchange` | 6 | 1 | 6 | 1 |
| `/grid?grid=caiso` | 2 | 0 | 4 | 0 |
| `/grid?grid=caiso&view=exchange` | 6 | 1 | 6 | 1 |
| `/grid?grid=pjm` | 2 | 0 | 2 | 0 |
| `/grid?grid=pjm&view=exchange` | 6 | 1 | 6 | 1 |
| `/grid?grid=miso` | 2 | 0 | 2 | 0 |
| `/grid?grid=miso&view=exchange` | 6 | 1 | 6 | 1 |
| `/grid?grid=nyiso` | 2 | 0 | 2 | 0 |
| `/grid?grid=nyiso&view=exchange` | 6 | 1 | 6 | 1 |
| `/grid?grid=isone` | 2 | 0 | 2 | 0 |
| `/grid?grid=isone&view=exchange` | 6 | 1 | 6 | 1 |
| `/grid?grid=spp` | 2 | 0 | 2 | 0 |
| `/grid?grid=spp&view=exchange` | 6 | 1 | 6 | 1 |
| `/grid?grid=us48` | 1 | 0 | 1 | 0 |
| `/grid?grid=us48&view=exchange` | 6 | 1 | 6 | 1 |
| `/grid?grid=ercot&view=mix` | 2 | 0 | 2 | 0 |
| `/grid?grid=us48&view=mix` | 1 | 0 | 1 | 0 |
| `/grid?grid=pjm&view=mix&mix=stress` | 2 | 0 | 2 | 0 |
| `/grid?grid=ercot&view=gravity&shape=gravity` | 6 | 1 | 6 | 1 |
| `/grid?grid=us48&view=gravity&shape=gravity` | 6 | 1 | 6 | 1 |
| `/digest/2026-10-21` | 0 | 0 | 1 | 0 |
| `/digest/2026-10-20` | 0 | 0 | 1 | 0 |
| `/digest/2026-10-14` | 0 | 0 | 1 | 0 |
| `/digest/2026-10-13` | 0 | 0 | 1 | 0 |
| `/digest/2026-10-12` | 0 | 0 | 1 | 0 |
| `/digest/2026-10-09` | 0 | 0 | 1 | 0 |
| `/digest/2026-10-08` | 0 | 0 | 1 | 0 |
| `/digest/2026-10-07` | 0 | 0 | 1 | 0 |
| `/digest/2026-10-02` | 0 | 0 | 1 | 0 |
| `/digest/2026-09-28` | 0 | 0 | 1 | 0 |
| `/digest/2026-09-27` | 0 | 0 | 1 | 0 |
| `/digest/2026-09-26` | 0 | 0 | 1 | 0 |
| `/digest/2026-09-25` | 0 | 0 | 1 | 0 |
| `/cost-of-power/battery/awards` | 0 | 0 | 1 | 0 |
| **All 151 addresses** | 110 | 15 | 161 | 15 |
