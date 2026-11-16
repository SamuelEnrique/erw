# The large-load rules read in a browser, 16 November 2026

Energy Research Warehouse (ERW). Session 7600, chain 305 (`queue/done/305-night-16-november-portable-done-line-and-browser-reads.md`, part A), on the portable laptop. Chain 302 put the large-load rules of US utilities on two pages from the old laptop, which cannot build the site: the pages were held by tests and by the components drawn to HTML, and no one had seen them. This is the first look.

## What was read, and how

- **The stack:** `wip/7200-large-load` at `d192de75c` (landing row 15 of `docs/state/landing_request_oldlaptop.md`, not landed), built here in the foreground and served on this machine; the fixes on `wip/7600-large-load-read`, cut from it, built and read again the same way. Production was read only for a baseline of axe (the two pages as they are on main).
- **The pages:** `/cost-of-power?view=allgrids` and `/policy?view=monitor&state=VA#large-load-laws` (and the same with MD, TX, IN, WY and with every state), in the internal view (the token posted by the site's own form), at 1280 by 900 and at 390 by 844 as a phone.
- **The browser:** the machine's own Chrome, headless, driven over the DevTools protocol (`site/scripts/browser.mjs`). A hover is the mouse moved onto the trigger; on the phone, the trigger focused, as a tap does. The scripts and what they recorded are in `runs/c305/` on this machine (not in git).
- **The measure of a hover:** its box is shown; it is inside the window's width; and at its four corners and its centre the box itself is what is drawn there (not cut by a frame, not covered). 

## What was done, against the chain's list

| The chain asked | Done | Result |
|---|---|---|
| The Utility cell and the Time to connect cell opened for five rows of different kinds | Eight rows: a utility's own rule with the state's (ERCOT LZ_AEN), a state's rule alone (ERCOT HB_NORTH), "no large-load rule found" (CAISO SP15), "no large-load rule read" (ISO-NE Connecticut), PJM's row, and three more (NYISO Long Island, NYISO Hudson Valley, CAISO NP15) | Each link opens its panel under the table, in view, from either cell; each "found" and "read" line opens its hover; "2 in CA" and "7 in NY" open the table on that state. Faults: rows 1, 2, 3, 5, 6, 7 |
| The rules table sorted | Each of the 13 columns, both ways (26 sorts) | Each sort takes; the head says "(up)" or "(down)" and a screen reader is told the same; rows with nothing printed stand last either way |
| Each filter used | Every choice of State (42), Grid (8) and Status (6), and the name box | Every choice draws the count its label names (VA 8, TX 11, PJM 22, license needed 22); "Every rule" clears them |
| Two rules set side by side as A and B | Old Dominion Electric Cooperative as A, NOVEC as B; then a held rule as B | "Two rules, side by side" appears above the filters; the held rule's column is blank cells; the address keeps A and B. Faults: rows 1, 2, 4, 6 |
| The 90 days of changes filtered by state | The State filter (VA: 0; CA: 2), the five regions, a rule opened from a change | The counts are the buttons' (29, 17, 14, 19, 15: 94); a change's rule opens in the table above and the page moves to it. Faults: rows 8, 9 |
| The downloads opened | The six files of the tab and the three of `/policy` | CSV of the rules (122 rows, the 22 held as "license needed"), of the changes, of the laws (28 rows); each Python and Stata reader names its file and its columns. Fault: row 9 |
| Every hover read | 409 different hovers opened and their words kept; each of the 579 drawn at 1280 px, and the same at 390 px, measured | Before: rows 1 to 3. After: none cut at 1280 px; at 390 px one of 579 measured outside the window, and that one's trigger was itself outside the window when it was measured (the read's own doing). Words: row 11 |
| The held rows' blank cells and their "license needed" hover seen | The 22 held rules (120 blank cells drawn on the first page of 12), a held rule opened and set as B, the 4 held changes, Indiana's law, Texas S.B. 6 | Each cell is blank; its hover and its name to a screen reader say "license needed" (or, for S.B. 6, "not shown" with the reason) |
| No sideways scroll at 390 | The page's own width measured in every state above | The document is 390 px wide in every one; the wide tables scroll inside their own frames |
| axe run, no rule broken | Five states of the two pages, WCAG 2.0 to 2.2 A and AA, at both widths | Before: one rule (target size) broken on both pages. After: no rule broken, in all five, at both widths. Row 10 |
| Ten figures each found in its table row | 17 figures | 17 of 17 drawn and found in their rows (below) |

## The faults

Kinds: `site` (fixed on `wip/7600-large-load-read`, with a test), `data machine` (a request), `ruling` (a default taken). A row's test is in `site/scripts/test-large-load-read.mjs` under its number.

| # | Where | What a reader met | What it is now | Kind | State |
|---:|---|---|---|---|---|
| 1 | Every hover inside a table that scrolls sideways: the rules, A and B, the changes, the laws | A hover's box was drawn inside the table's frame, so a box near the frame's foot or right side was cut by it and the frame grew scroll bars. In A and B the last row's "source" showed a sliver of its box and no words | The open box is placed against the window, outside any frame: under its trigger where it fits, above it where there is more room, and no taller than its room | site | fixed (`placeTip` in `site/lib/largeloadrules.ts`, `site/components/largeload/TipPlace.tsx`) |
| 2 | The same hovers, and the hub table's "no large-load rule found" and "read" lines | A box opened from its trigger's left edge, 416 px wide: at 1280 px one whose trigger stood in the right third ran past the window (the table 9 of 147, the Austin Energy panel 1 of 68). At 390 px nearly all did: the table 144 of 147, A and B 23 of 27, the changes 29 of 38, the laws 176 of 227; the hub table's ran 28 to 35 px past the left edge | Never past an edge, at either width | site | fixed (the same placing; measured again: 0 of 579 at 1280 px) |
| 3 | A hover holding a long address or a file's path (the hub table's "no large-load rule found") | The box grew a sideways scroll bar of its own | The words break; the box scrolls only down | site | fixed (`site/app/tokens.css`) |
| 4 | The tables' first column, which stays in place while the rest scrolls | The cells scrolling under it were drawn over it: at 390 px "Northern Virginia Electric Cooperative" and "New or additional separately meterable load" stood printed on each other, and the heads "Utility and rule" and "Date" likewise | The column is above the cells that pass under it; a hover opened from the column is above the rows after it | site | fixed (`site/app/tokens.css`) |
| 5 | The panel a row opens: "The rule of a utility this row names (...)" | ERCOT LZ_AEN named Austin Energy twice and Oncor twice | Each utility once | site | fixed (`uniqueNames`) |
| 6 | A rule whose document prints no status date: the hub cells' link titles, the card's status line, A and B, a law's status | "Pacific Gas and Electric Company: in effect, not published", which reads as the rule not being published | "in effect, date not published" | site | fixed (`statusWords`, `statusDateWords`) |
| 7 | A rule's card with a long docket (Oncor's) | The docket took a line whole and left ". The ERW's notes" to open the next line with a period | The status, the docket, and the state law with the notes are a line each | site | fixed (`site/components/largeload/parts.tsx`) |
| 8 | "What changed in the last 90 days ... newest first" | The list opened with seven rows printed "2026-09" and "2026-10", above 13 November: their documents print a month, and the file dates them to the day they were read | A month is ordered as its month, at the head of that month's days; the first row is of 13 November | site | fixed (`orderChanges`) |
| 9 | The lines that count the rows under them, and the changes' file | `/policy`, every state: 29 rows under "28 of 28 shown" (Texas S.B. 6, read and not shown, is a row and was not counted); Texas alone: one row under "0 of 28 shown". The changes: 98 rows under "94 of 94 changes" (the 4 held), and their CSV left the 4 out where the rules' and the laws' files carry their held rows | "28 of 28 shown, and 1 read and not shown"; "94 of 94 changes, and 4 held"; the changes' file carries the 4 as their utility and "license needed" | site | fixed (`site/app/policy/StateLaws.tsx`, `LargeLoadRules.tsx`, `changesCsv`) |
| 10 | axe, target size (WCAG 2.2, 2.5.8) | Broken on the All grids tab by 78 elements, 57 of them new with this stack (the lines the hub cells draw for a row's rule, the A and B buttons, a rule's name) and 21 on production already (the hub table's utility names); on `/policy` by 15 to 20, 14 of them on production already (the links of the monitor's table of figures by month) and the rest the laws' documents | No rule broken on either page, at either width: the new ones and the ones production has | site | fixed (`site/app/tokens.css`: 24 px targets, and 24 px from one link to the next in the monitor's table) |
| 11 | The hovers "The ERW's notes" and two cites | The research's working words: "window A" (the data machine's old name) in 11 hovers and "the brief" in 4, beyond the six cells chain 302 named | Unchanged here: the words are the tables' | data machine | requested (row 8) |
| 12 | `/policy`, "Download the tables" | `state_large_load_laws` is drawn as a link "on Redivis", while chain 302's report says the three tables are out of release v1 | Unchanged here | data machine | requested (row 9) |
| 13 | A hover opened in a table's frame on a phone, in the second after the frame was scrolled | The frame's own scroll indicator (a bar 3 px high, which a phone lights for about a second after a scroll) is drawn across one line of the open box: 4 of 228 hovers of the laws were measured so | Unchanged | ruling | default: left as it is. The box is a child of the frame it describes, which is what lets a keyboard and a screen reader reach it from its trigger; drawing it outside the frame is a change to how every hover of the section is built |
| 14 | The site's shared "i" mark (`site/components/tool/ToolPage.tsx`, `Tip`), on every page that draws it: found while reading the old laptop's rows of `docs/state/browser_reads_wanted.md` | The mark's box is 288 px wide and opened from the mark's left edge. On production at 390 px, 62 of the 91 marks read on 19 pages ran past the screen (by up to 240 px) and the page scrolled sideways while the box was open: `/impact` 23 of 36, `/play/ev` 13 of 15, `/cost-of-power/battery` 5 of 9, and every "Decisions on this page" fold of the old laptop's four new pages. At 1280 px, 4 of 87 (a mark in a page's right column) | The same placing as rows 1 and 2, from the site's layout: 0 of 199 marks at 390 px and 0 of 195 at 1280 px on the same 19 pages, on a build of this branch with the old laptop's four | site | fixed (`TipPlace`, mounted once in `site/app/layout.tsx`) |

## The 17 figures, each in its table row

The tables were written from the committed research files by the connector, as `tests/test_session7200_large_load_rules_page.py` writes them (no request, no lock), and each figure the browser drew was looked for in its row.

| # | Drawn on | Figure | Table and row |
|---:|---|---|---|
| 1 | the section's first line | 122 rules | `utility_large_load_rules`: 100 rows written and 22 held, as its header says |
| 2 | the same line | 52 in effect | the rows whose status is in effect |
| 3 | the same line | 94 changes | `utility_large_load_rule_changes`: 94 rows |
| 4 | the laws' first line on `/policy` | 27 laws and bills | `state_large_load_laws`: 27 rows |
| 5 | the same line | 6 enacted | the rows whose status is enacted |
| 6 | the panel of ERCOT LZ_AEN | Austin Energy, in effect, 2026-03-09 | row `texas-06`, `x_status_date` |
| 7 | the panel of ERCOT HB_NORTH | 75 MW (the PUCT's rule) | row `texas-01`, `x_threshold_mw` and its cite |
| 8 to 10 | A and B, NOVEC's queue | 88 data center buildings; 1,750 MW; 15,794 MVA | row `dominion-04`, `x_queue_size` |
| 11 | the row opened in the table | Old Dominion Electric Cooperative, in effect | row `coops_public_power-03`, `status` |
| 12 | the table filtered to VA | Dominion's Schedule GS-5, 2025-11-25 | row `dominion-01`, `x_status_date` |
| 13 to 16 | the laws' table | Maryland 2026-05-12 and 2025-05-20; Vermont 2026-05-29; West Virginia 2025-07-11 | rows `laws_midwest_northeast-15`, `-14`, `-20`, `-21`, `x_status_date` or `x_effective_date` |
| 17 | the changes | Black Hills Energy's change, printed 2026-09 | row `west_changes-15`, `x_date` |

The State filter's counts were held to the table too: VA 8, NY 7 and CA 2 are the public rows naming each state; TX 11 is 8 public rows and 3 held.

## The measures, before and after

Hovers measured as cut or covered, of those drawn. "Before" is `wip/7200-large-load` at `d192de75c`; "after" is `wip/7600-large-load-read`.

| Where | 1280 px before | 1280 px after | 390 px before | 390 px after |
|---|---:|---:|---:|---:|
| The hub table's rule lines (8 rows) | 0 of 7 | 0 of 7 | 7 of 7 | 0 of 7 |
| The panels of five rows | 1 of 136 | 0 of 136 | 0 of 136 | 0 of 136 |
| Two rules, side by side | 12 of 27 | 0 of 27 | 23 of 27 | 0 of 27 |
| The rules table, Virginia's rows and one opened | 54 of 147 | 0 of 147 | 144 of 147 | 0 of 147 |
| The changes (the first 12 and the held) | 19 of 38 | 0 of 34 | 29 of 38 | 0 of 34 |
| The laws, every state | 132 of 227 | 0 of 228 | 176 of 227 | 1 of 228 |
| axe, rules broken (elements): the tab | 1 (78) | 0 | 1 (78) | 0 |
| axe, rules broken (elements): `/policy` | 1 (15 to 20) | 0 | 1 (5), with every state | 0 |
| The site's shared "i" mark, 19 pages (before: production; after: this branch with the old laptop's four) | 4 of 87 | 0 of 195 | 62 of 91 | 0 of 199 |
| The page's own width at 390 px | | | 390 | 390 |

The one of 228 at 390 px is a state's hover in the line "No row for 22 states": when it was measured its trigger stood below the window's foot (the read had scrolled it there), so its box, placed above it, was below the window too. With its trigger in the window the box is in the window (the test tries 5,563 places at the two widths).

## The screenshots

After the fixes, at both widths (`-1280` and `-390`), in this folder:

- `docs/reviews/large-load-on-site/allgrids-top-1280.png`, `docs/reviews/large-load-on-site/allgrids-top-390.png`: the tab as it opens.
- `docs/reviews/large-load-on-site/row-own-panel-cell0-1280.png`, `docs/reviews/large-load-on-site/row-own-panel-cell0-390.png`: the panel of ERCOT LZ_AEN (Austin Energy's rule, Oncor's, the PUCT's).
- `docs/reviews/large-load-on-site/row-own-panel-source-hover-1280.png`, `docs/reviews/large-load-on-site/row-own-panel-source-hover-390.png`: a "source" hover in that panel.
- `docs/reviews/large-load-on-site/row-state-panel-cell0-1280.png`, `docs/reviews/large-load-on-site/row-state-panel-cell0-390.png`: a state's rule alone (ERCOT HB_NORTH).
- `docs/reviews/large-load-on-site/row-found-cell1-hover-1280.png`, `docs/reviews/large-load-on-site/row-found-cell1-hover-390.png`: "no large-load rule found" and its hover (CAISO SP15).
- `docs/reviews/large-load-on-site/row-unread-cell1-hover-1280.png`, `docs/reviews/large-load-on-site/row-unread-cell1-hover-390.png`: "no large-load rule read" and its hover (ISO-NE Connecticut).
- `docs/reviews/large-load-on-site/row-pjm-panel-cell0-1280.png`, `docs/reviews/large-load-on-site/row-pjm-panel-cell0-390.png`: PJM's row.
- `docs/reviews/large-load-on-site/rules-table-1280.png`, `docs/reviews/large-load-on-site/rules-table-390.png`: the rules table.
- `docs/reviews/large-load-on-site/rules-va-1280.png`, `docs/reviews/large-load-on-site/rules-va-390.png`: filtered to Virginia.
- `docs/reviews/large-load-on-site/rules-ab-1280.png`, `docs/reviews/large-load-on-site/rules-ab-390.png`: two rules as A and B.
- `docs/reviews/large-load-on-site/rules-field-hover-1280.png`, `docs/reviews/large-load-on-site/rules-field-hover-390.png`: a field's hover in the table.
- `docs/reviews/large-load-on-site/rules-held-hover-1280.png`, `docs/reviews/large-load-on-site/rules-held-hover-390.png`: a held row's blank cell and "license needed".
- `docs/reviews/large-load-on-site/rules-held-open-1280.png`, `docs/reviews/large-load-on-site/rules-held-open-390.png`: a held rule opened.
- `docs/reviews/large-load-on-site/changes-open-rule-1280.png`, `docs/reviews/large-load-on-site/changes-open-rule-390.png`: a rule opened from a change.
- `docs/reviews/large-load-on-site/laws-va-1280.png`, `docs/reviews/large-load-on-site/laws-va-390.png`: `/policy` on Virginia's law.
- `docs/reviews/large-load-on-site/laws-all-1280.png`, `docs/reviews/large-load-on-site/laws-all-390.png`: every state.
- `docs/reviews/large-load-on-site/laws-topic-hover-1280.png`, `docs/reviews/large-load-on-site/laws-topic-hover-390.png`: a topic's hover.
- `docs/reviews/large-load-on-site/laws-held-hover-1280.png`, `docs/reviews/large-load-on-site/laws-held-hover-390.png`: Indiana's held law.

Before the fixes, four for the record:

- `docs/reviews/large-load-on-site/before-rules-field-hover-390.png`: rows 2 and 4 (the box past the window, the first column printed over).
- `docs/reviews/large-load-on-site/before-row-found-cell1-hover-390.png`: rows 2 and 3 (the box past the left edge, its own scroll bar).
- `docs/reviews/large-load-on-site/before-ab-last-source-1280.png`: row 1 (the box cut by the frame).
- `docs/reviews/large-load-on-site/before-row-own-panel-cell0-1280.png`: rows 5 and 7 (the names twice, the period at the head of a line).

## What only a person can still judge

- Whether 24 px lines for the hub cells' two rule lines read well beside the cells' other captions (they were 18 px; each hub row is about 12 px taller).
- The ruling of row 13.
