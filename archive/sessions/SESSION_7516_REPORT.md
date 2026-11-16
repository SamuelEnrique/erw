# Session 7516 report: the ERCOT peak premium explorer read as the reader it is for

Chain 304, part B, tool 7 of 9. samueloldlaptop (code role), unattended, 16 November 2026. Branch `wip/7507-peak-premium`, on top of session 7507's work, not pushed. Model spend: USD 0. The read: `docs/reviews/ercot-peak-premium-read-2026-11-16.md`.

## At the top

- **No figure the page shows was found wrong, and no two pages give a different figure for the same hub and period.** The one other page that draws these tables (the ERCOT tab of `/prices`) draws the same rows by the same rule.
- **No shared explore file and no other page's code was changed.** `site/components/explore/`, `site/lib/explore/index.ts` and `site/lib/explore/source.ts` are as they were. Changed: the page, its own library `site/lib/explore/peakpremium.ts`, its `Decisions.tsx`, the method note (a new section 9).
- **No site build and no type check was run** (this machine cannot). The page's figure writer was reshaped and one read added: a build of the merged commit is needed before landing.
- **The cases were read on this machine's copy of the tables** (built 29 September 2026): 2026 runs to 28 September here and to 21 October on the site. Every complete year and month is the same.
- **For the desktop's tool (`/prices`, the ERCOT tab):** the whole-dollar price part A suspected is not a fault there. `fmt` in `site/app/explorer/ercot-peak-premium/Explorer.tsx`, lines 35 to 38, writes every price with two decimals.
- Not meant and seen: nothing.

## The reader and the five cases

- **The reader:** a fund analyst sizing the evening premium a merchant battery or a peaker captures in ERCOT. The page holds six hubs and no node and compares years, so it answers an underwriter; the developer's two-node question is case 1, as far as hubs go.
- 1. HB_WEST against HB_NORTH: the peak block's median and spread in 2025, and in August 2025.
- 2. How the evening premium moved from 2019 to 2025 at HB_HUBAVG.
- 3. February 2021 (Winter Storm Uri) at HB_HOUSTON, and what it does to 2021's figures.
- 4. The worst interval of 2023 at HB_HUBAVG and its multiple of the median.
- 5. 2026 so far against 2025 at HB_HUBAVG: a comparison of like months?

## The rows by kind (14)

- **site, fixed with a test: 5** (rows 1 to 5).
- **data machine: 2** (rows 6 and 9; the ready rows are below).
- **browser: 1** (row 7, already asked by part A's browser row 4; three new browser rows for this session's changes are below).
- **ruling: 6** (rows 8 and 10 to 14).
- license: 0. key: 0.

## What was fixed

- **Row 1, two hubs side by side.** A fifth filter, "Beside hub" (`vs` in the address, none by default). With it the page draws "Two hubs side by side": 13 figures a hub and a period, each a row of the table with its source on hover. No difference is taken; a tip says why. With no second hub the page is as it was (64 figures).
- **Row 2, the mark of a period not yet over.** "2026 (partial)" wherever it heads a figure: the headline numbers, the period cells, the column heads. It was in the filters and one grey sentence only.
- **Row 3, the worst-interval multiple.** The decisions block now says it is the multiple of the 99.9th percentile (about 35 intervals of a year pass it), not of the highest interval, and where the highest interval is.
- **Row 4, HB_BUSAVG** is said in words in the decisions block.
- **Row 5, nodes.** One sentence says the page holds no node and names the battery page, where ERCOT's storage nodes are set against the hub average.
- The method note: section 9, what the read changed on the page.

## Tests

One file a process, `ERW_SPEND_CAP_USD=0`, `.venv\Scripts\python.exe -m pytest tests/<file> -q -p no:cacheprovider`; every exit code 0.

| File | Result |
|---|---|
| `site/scripts/test-peak-premium-read.mjs` (new; the page drawn on the fixture's real rows) | 122 checks passed, 0 failed |
| `tests/test_session7516_peak_premium_read.py` (new; runs the script above) | 5 passed |
| `tests/test_session7507_peak_premium.py` | 14 passed |
| `tests/test_session403.py` | 12 passed, 1 skipped (it failed once: it holds the figure writer's two lines word for word; the writer was reshaped to keep them, and the test is unchanged) |
| `tests/test_session170.py` | 27 passed, 2 skipped |
| `tests/test_session538.py` | 14 passed |
| `tests/test_session328.py` | 11 passed |
| `tests/test_session416.py` | 9 passed |
| `tests/test_session2200.py` | 8 passed |
| `tests/test_session1496.py`, `test_session2203.py` | 6 passed each |
| `tests/test_session2204.py` | 5 passed |
| `tests/test_session417.py`, `test_session472.py` | 4 passed each |

Thirteen python files: 125 passed, 3 skipped. Not run: a build, a type check, `check-values`, `check-explorers`, `check-routes` (they need the built site), the full suite.

## What to review

All in review, as before.

1. `https://erw-flame.vercel.app/explore/ercot-peak-premium?hub=ercot:HB_WEST&vs=ercot:HB_NORTH&from=2025&to=2025`. The filters hold a fifth menu, "Beside hub", on HB_NORTH. Under "The thesis's figures" a new section, "Two hubs side by side: HB_WEST and HB_NORTH". First row, peak median: 39.03 and 34.82. Peak-block IQR: 42.37 and 35.17. Point at a figure: its table, hub, variable, year and source. Point at the "i" after "The same rows for each hub, 2025.": why no difference is taken.
2. In "Period" choose August. The same table for August 2025: 47.05 and 40.10; IQR 40.99 and 41.85.
3. In "Beside hub" choose None. The section goes; everything else is as it was.
4. `https://erw-flame.vercel.app/explore/ercot-peak-premium?from=2025&to=2026`. The three headline labels end "2026 (partial)". In the first table the four period cells of 2026 read "2026 (partial)"; the second table's head too. 2025 carries no mark.
5. `https://erw-flame.vercel.app/explore/ercot-peak-premium`. Open "Decisions on this page". Point at the "i" of the line on scarcity: it now says the multiple is not of the single highest interval. The "i" of the hub line says what HB_BUSAVG is.
6. Above that fold, the line with the link to the ERCOT tab now ends: "It holds the six hubs and no node: ERCOT's storage nodes are set against the hub average, month by month, on the battery page (ERCOT, HB_HUBAVG)."

## Data request rows

| Requested (UTC) | Session | Table or file | What, exactly | Source | State |
|---|---|---|---|---|---|
| 2026-11-16 12:51 | 7516 | `ercot_peak_premium_monthly` (new rows) or a new table of the same shape for nodes | The metrics of `docs/methods/ercot_peak_premium.md` ("Metrics") for each node of `ercot_rtm_node_prices` (312 nodes, 15-minute real-time prices, held from 2026-09-28T04:45Z), by calendar month from October 2026, the first complete month, by the builder's own rules (blocks, percentiles, completeness). So that a named node's 16:00 to 21:00 median and spread can be set beside a hub's. Nothing is wrong in a row today | ERCOT NP6-905-CD, through `ercot_rtm_node_prices` | requested |
| 2026-11-16 12:51 | 7516 | `ercot_peak_premium_annual` (new rows) or a table beside it | For each hub and each year before the newest: the same metrics over the intervals from 1 January 00:00 local to the local day and time of year of the newest year's "Last input interval", so that the partial year has a like figure beside it (today 2026's 25,916 intervals stand beside 2025's 35,040). New variables or a second table, the builder's choice; the page draws them once they exist | ERCOT NP6-785-ER and NP6-905-CD, through `ercot_all_hub_prices_history` and `iso_rtm_hub_prices` | requested |

## Browser read rows

| Asked (UTC) | Session | Branch | Address | What to look at | What should be seen | State |
|---|---|---|---|---|---|---|
| 2026-11-16 12:51 | 7516 | `wip/7507-peak-premium` | `/explore/ercot-peak-premium?hub=ercot:HB_WEST&vs=ercot:HB_NORTH&from=2024&to=2025` | The five filters and the section "Two hubs side by side", at 1280 and at 390 px; the "i" beside "The same rows for each hub" | The filters wrap with no sideways scroll of the page; the table (four columns of figures) scrolls inside its own frame at 390 px; 39.03 and 34.82 in the 2025 columns of the first row; the tip opens inside the page; changing "Hub" to HB_NORTH sets "Beside hub" to None and removes the section | wanted |
| 2026-11-16 12:51 | 7516 | `wip/7507-peak-premium` | `/explore/ercot-peak-premium?from=2025&to=2026` | The three headline labels, the first table's period cells, the second table's head | "2026 (partial)" in each (the label in its capitals), on one line at 1280 and wrapping cleanly at 390 px; no "2025 (partial)" | wanted |
| 2026-11-16 12:51 | 7516 | `wip/7507-peak-premium` | `/explore/ercot-peak-premium` | The fold "Decisions on this page": the "i" of the line on scarcity (now the longest tip) and of the hub line; the sentence on nodes above the fold | Each tip stays inside the page at 390 px and can be read whole; the battery page link opens `/cost-of-power/battery` for a signed-in reviewer | wanted |

## Landing request

- **Head:** the commit that holds this report, on `wip/7507-peak-premium` (stacked on session 7507's `b35e64e9a`). The work is `2bec866f5` and `b096ca5d5`.
- **Tests:** the 13 python files above (125 passed, 3 skipped) and the Node check (122 checks).
- **What changes:** `/explore/ercot-peak-premium` only: a fifth filter and, when it is used, one more section; "(partial)" beside a period not yet over; two longer hover tips in the decisions block; one sentence with a link to the battery page. New: `docs/reviews/ercot-peak-premium-read-2026-11-16.md`, `site/scripts/test-peak-premium-read.mjs`, `tests/test_session7516_peak_premium_read.py`; the method note is longer.
- **What does not:** no table, no builder, no shared explore file, no other page, `site/lib/release.ts`.
- **A snapshot would differ on:** none of the 25 pages it reads (the page is in review).
- **Before landing:** a site build of the merged commit (types: the figure writer is now made once a hub, `page.tsx`); `check-values` (the default views draw the same keys as before; a view with `vs` is not in its list and could be added once a build exists).

## Needs the key

Nothing.

## Decisions made without you

- The reader is the fund analyst, not the developer: the page holds hubs and compares years.
- The second hub is a filter and one table, not a second set of charts, and no "B less A" column: a difference of two medians is not the median of the hubs' price difference, and the page computes nothing.
- "(partial)" is written as a mark beside the period, as the filters already do, not as a tip.
- The name "Worst-interval multiple" stays (the table's variable, the thesis's term); the decisions block explains it.
- The filters' reset line keeps its words; no second hub is the default.
- Session 403's test was kept unchanged by keeping the figure writer's two lines word for word.
- No address was added to `check-values`' list: it cannot be run here.
- The method note got a section 9 rather than edits to sections 1 to 8.

## For Samuel's ruling

1. **The day and hour of a year's highest price** are in no table; the page takes a reader to the month only. Default: not built.
2. **A year beside one of its own months** (2021 beside February 2021) takes two views. Default: not built.
3. **"The thesis".** The page says "the thesis chart" and "the thesis's figures" and never says whose thesis or what it claims; `/thesis` is another tool. Default: the words stay. Smallest change: a hover tip on the first chart's title, in your words.
4. **The name "Worst-interval multiple"** for a figure that is the 99.9th percentile over the median. Default: the name stays, explained on hover. Smallest change: the label "99.9th percentile over the median".
5. **The download "The rows drawn here"** holds the first hub only when a second is chosen; the frame the three explorers share takes one download (`site/components/explore/Explore.tsx`, line 29). Default: not changed. Smallest change: the frame takes a list.
6. **"Peak" means two things on the site.** On `/grid`, "Day-ahead peak" is the mean of the 16 weekday hours ending 7 to 22; here it is the median of 16:00 to 21:00 every day. No period is on both pages, so no two figures disagree. Default: both stay. Smallest change: "Day-ahead on-peak" on `/grid` (`site/components/grid/YourGrid.tsx`, lines 282 and 283), as `/board` says.

## Added after the hand-back

The coordinator's ask: the replication must cover what the read added to the page (the second hub and the "(partial)" mark). Done on the same branch; no shared explore file touched.

- **The note:** `docs/methods/ercot_peak_premium.md`, a new section 10: the second hub's rules, the section's title, line and head, the 13 figures with their table and variable in order, how each is written, and when and where a period is marked partial. Section 7 gained one sentence pointing to it.
- **The page's figures:** `site/scripts/peak-premium-figures.mjs` draws 124 more views with `vs`: every ordered pair of the six hubs (30); HB_WEST beside HB_NORTH for each month with no year named (12) and for the whole year and each month with every pair of years (78); four more (the same hub twice, a hub not held, one year alone, a month the newest year does not hold). It also keeps each view's headline labels, tables' heads and period cells, and the section's title, line and keys.
- **The replication:** `replicate.py` computes the section and the marks from the two tables by the note's words (its own list of 13; it does not read the page's library). Run with `--in-dir C:/Users/lossa/Documents/erw/warehouse/output --write`, exit 0, as printed:
  - `674 of 674 views open as the note says (the hub, the period, the two years, the years marked, the rows' download, the freshness line)`
  - `24786 of 24786 figures inside the tolerance, with the same text; 0 drawn by the page and not expected; 0 drawn two ways`
  - `6214 of 6214 figures of the section of two hubs, in 122 views with a second hub, are the rows the note names, in its order, inside the tolerance and with the same text`
  - `12172 of 12172 periods that head a figure are written as the note says (the headline numbers, the first table's period cells, the tables' heads, the two-hub line; '(partial)' where the period is not over)`
- The distinct figures stay 24,786: the section draws rows the hub's own views already draw. `page_figures.csv` did not change; `page_figures.json` carries the new counts.
- **The replication was shown to fail when it should:** on a page file with two of the section's figures swapped, and with "(partial)" added to a head, a period cell and a headline label, it exits 1 and names the view (a scratch check under `runs/`, not committed).
- **Tests,** one file a process, every exit code 0: `tests/test_session7516_peak_premium_read.py` 8 passed (three new: the replication on all 282 views of the fixture, one list of 13 in the note, the replication and the page, the committed counts are the note's); `tests/test_session7507_peak_premium.py` 14 passed (its pinned counts updated: 48 views with `--opening`, 780 of 780 two-hub figures in 16 views, 894 of 894 periods); the eleven other files as before. Thirteen files: 128 passed, 3 skipped.
- **Not done:** `replicate.do` is unchanged (its five headline figures do not move). No build, no type check, no browser read, as above. The data machine's request row of session 7507 (run the replication on the current tables and commit the two figure files) now also writes the new counts.
- **The new head:** the commit that holds this section, on `wip/7507-peak-premium`; the work is `992d320a5`. The landing request's test counts become 128 passed, 3 skipped.
