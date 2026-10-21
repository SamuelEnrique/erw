# Accessibility of every visitor page, 20 October 2026

Energy Research Warehouse (ERW), session 412 (chain 015, "Session 412: accessibility on every page"), run on 21 October 2026 between 06:10 and 08:10 UTC on samueloldlaptop. The chain named this file as the list of findings to fix; it did not exist on any branch, so this session wrote it from its own audit, before and after the fixes. A tool's finding is a reading, not a ruling (`docs/tooling.md`): what asks for a change of words, layout or a ruled color is under "For Samuel's ruling".

## How the pages were read

- **Pages (47 addresses, 49 audits).** The distinct pages of `site/scripts/snapshot-live.mjs` (`/`, `/about`, `/terms`, `/storage`, `/network`, `/cost-of-power/battery`, `/cost-of-power/seller`, the four methods pages) and every page of the menus (`site/lib/pages.ts`, 41 addresses: the tools, the seven grid pages, the games, the digest, the roundup, `/ask`, `/data`, `/subscribe`). Of the snapshot's query variants, `/cost-of-power/battery?grid=caiso&dur=8&strat=dayahead` and `/cost-of-power/seller?iso=caiso&asset=wind` were audited as well. The list is `docs/brand/review-412/pages-412.txt`.
- **The internal view.** Every page is in review, so each tool opened it first by the form at `/internal/open` (the token posted, never in an address): `site/scripts/browser.mjs` `unlock()` for the session's own browser, and for AccessLint a headless Chrome on port 9412 unlocked the same way (`docs/brand/review-412/unlock9412-412.mjs`), which `audit_live` attached to. Both browsers were closed at the end.
- **AccessLint** `audit_live` (WCAG 2.2 A and AA, the plugin's default rules) on each page of a local production build at `http://localhost:3412`, at the Chrome's 1280 px window.
- **The accessibility tree and the keyboard** (`docs/brand/review-412/a11y-412.mjs`): the browser's full accessibility tree by the DevTools protocol (every button, link, field, slider, tab and option without a name), then Tab pressed from the top of each page up to 80 times, each stop's place, size and focus ring read. Results: `keyboard-walk-before.txt`, `keyboard-walk-after.txt`.
- **Screenshots** before and after at 1280 and 390 px, of the window at the place of each finding: `docs/brand/review-412/` (13 places, 52 files).

## What was found, and what was done

Before: 13 of the 49 audits with AccessLint findings (250 in all, 218 of them the board's rows; the two query variants repeat their page's), 2 fields with no name in the accessibility tree, 2 fields and 3 footer links without the brand's focus ring. After: AccessLint finds nothing on any of the 49, every field has a name, and every one of the 2,651 stops of the keyboard walk shows the brand's ring (2 px ink).

| # | Where | Finding (tool, rule) | Before | Fix | After |
|---|---|---|---|---|---|
| 1 | every page | The footer's three links (Data and methods, Terms, Privacy) took the browser's thin ring, not the brand's (keyboard walk) | 85 stops with "auto 1px" | `app/tokens.css`: the footer joins the brand's one focus rule | 0 |
| 2 | `/network`, `/policy` | A date field (the replay day; the policy tracker's dates) showed no outline while one of its parts had the keyboard (keyboard walk) | 2 stops, "outline: none" | `app/tokens.css`: `input[type="date"]:focus-within` takes the ring | 0 |
| 3 | every menu | The page in view was told only by its color in the menus (accessibility tree) | `aria-current` only on the three grey links | `components/Nav.tsx`: `aria-current="page"` on every menu link | every kind of link |
| 4 | `/cost-of-power/battery` (`#earned`), `/cost-of-power/seller` (`#capture`), `/cost-of-power` (the sensitivity chart's table), `/contracts`, `/demand` (by year), `/shoulder` (`#worst`), `/data` (the install line) | A box that scrolls sideways holds nothing the keyboard can reach (AccessLint, keyboard-accessible/scrollable-region, WCAG 2.1.1) | 7 | `components/ScrollRegions.tsx`, mounted once in `app/layout.tsx`: a scrolling box under `<main>` with nothing focusable becomes one stop of the keyboard, a region named by its table's caption (else its figure's or section's title); `lib/cells.ts` `scrollRegion()`: the shared tables (`ToolTable`, `DataTable`) carry the same marks from the server, taken back by the script where the table fits | 0 (the install line on `/data` once the page's script has run: AccessLint reads it before; listed below) |
| 5 | `/cost-of-power/seller`, `/cost-of-power` (3), `/curtailment`, `/demand` (2) | A header cell with nothing in it (AccessLint, adaptable/empty-table-header, minor) | 7 | `lib/cells.ts` `emptyCell()`: `ToolTable` and `DataTable` draw an empty header cell, and an empty row header (demand's "Lower 48", not ranked), as a plain cell; `app/tokens.css` keeps it in the first column's sticky place | 0 |
| 6 | `/board` | Each price row was a table row made a stop of the keyboard, with `aria-selected`, which a screen reader announces as a row with nothing to press (AccessLint, keyboard-accessible/focus-order) | 218 | `components/board/BoardView.tsx`: the row's name is a button (`aria-pressed` while its series is in the workbench); the row still opens on a click anywhere; the week table's rows the same; a blank row (paused, licensed) has no button | 0 |
| 7 | `/demand` (the ranking) | The three column headers (Average demand, Peak demand, The year so far) were white on the brand's white header: invisible (AccessLint, color-contrast, 1 to 1) | 3 | `app/demand/page.tsx`: the inline white is gone; they are links, cardinal and underlined | 0 |
| 8 | `/curtailment` (where free energy is) | The tiles' words were white from 48 percent shading, 2.84 to 1 at the switch (AccessLint read 2.91 on NP15) | 2 | `app/curtailment/Sections.tsx` `TILE_WHITE`: the words turn white where white and ink give the same contrast (s = 0.655, about 61 percent), at least 3.6 to 1 either side; the shade is unchanged | 0 (but see the ruling) |
| 9 | `/curtailment` | "Where free energy is", a link in a grey note, was told from the note by its color alone (AccessLint, link-in-text-block) | 1 | underlined, as the brand's links in running text are | 0 |
| 10 | `/events` | The nine events' titles, links in a card of text, were told by their color alone (AccessLint, link-in-text-block) | 9 | `app/events/page.tsx`: underlined | 0 |
| 11 | `/network` | The replay day's name ("Replay a day", an aria-label) did not contain its visible label "A day since 2019:" (AccessLint, label-content-mismatch, WCAG 2.5.3) | 1 | `app/network/Network.tsx`: the aria-label is gone; the label names the field | 0 |
| 12 | `/impact` | Four number fields (size, capital cost, local content, life) had no name, or their placeholder for one: each sat in a label whose first labelable element was the hover tip's button, so the label named the button (accessibility tree; AccessLint did not see it) | 2 with no name, 2 named by their placeholder | `app/impact/page.tsx`: each label names its field by `htmlFor` | 0 |

No page's figure or words changed. The words added are for a screen reader only: the name of each scrolling region (its table's caption, already in the page for a screen reader; "Table" where a shared table has none).

## Keyboard order

The walk found the order the page is read in on every page: the skip link first, the header, the page, the footer. Three things read out of the place they are drawn in, none a fault of the order of the page:

- On `/network`, `/grid` and `/ask` the Ask panel is drawn at the top right beside the page, and is reached after the whole page (it comes last in the page's order). A ruling, below.
- On the battery, generator, cost of power and impact pages the settings column is read before the results beside it: the order of the columns, the same at every width.
- On `/digest` and `/severance` the order runs back up once to a list of links drawn higher in a second column, for the same reason.

## For Samuel's ruling

- The curtailment tiles between about 53 and 69 percent shading: no color can carry their 12 px words at 4.5 to 1 there (white reaches it only from 70 percent, ink only to 53); the switch now gives at least 3.6 to 1. Options: (a) the place's name and count on a white band inside the tile; (b) the words under the tile, the tile a swatch; (c) leave 3.6 to 1.
- The Ask panel on `/network`, `/grid` and `/ask` is read after the whole page while drawn at its top: (a) move it first in the page's order (it is then read before the page); (b) a skip link to it beside "Skip to content"; (c) leave it.
- The menus' names (Economics, Grid and the rest) are 20 px tall, the brand's rule is 24 px for a target (`docs/brand.md`, section 3); WCAG 2.2's 24 px rule is met by their spacing. Raising them to 24 px moves the header 4 px. (a) Raise; (b) leave.
- The hover tip's mark (`Tip`, the small "i") is 16 by 16 px, under the brand's 24; it is met by spacing on the pages read. (a) A 24 px target around the same mark; (b) leave.
- `/data`'s install line (`pip install ...`) is reached by the keyboard only once the page's script has run (the shared tables are marked on the server, a plain block of code is not). (a) Mark it on the server as the tables are, with a name for it; (b) leave.

## What was not read

- AccessLint at 390 px: its tool reads the window it is given (1280 px). The 390 px shots show the pages; the scrolling fix is the one that matters most at that width, and the script marks a box by whether it scrolls, at any width.
- A screen reader by ear, zoom to 200 percent, and reduced motion: not exercised.
- The tabs of each merged page beyond the one each address opens, and the internal pages (`/internal/*`).
