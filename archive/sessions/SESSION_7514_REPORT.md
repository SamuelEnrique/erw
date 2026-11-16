# Session 7514 report: `/cost-of-power/battery/awards` read as the reader it is for (chain 304, part B)

16 November 2026, unattended, on samueloldlaptop (code role). Worktree `erw-7505`, branch `wip/7505-battery-awards`
(stacked on session 7505's part A), not pushed. Model spend USD 0. No table written, nothing loaded, nothing published.
The page stays in review. The read: `docs/reviews/battery-awards-read-2026-11-16.md`.

## At the top

- **No figure the page had is changed.** Every one of the 307 figures of part A's replication is still on the drawn
  page (held by the new test). Six things were added; nothing was dropped.
- **The page now makes a sixth read:** `storage_buildout_monthly` (`iso:ercot`, three variables, from December 2025),
  for one hover that sets the EIA's count of ERCOT's fleet beside this page's MW. If the live set does not answer it,
  the hover says so and no other line changes (tested).
- **Two pages agreed and did not look it.** The battery page says the model is "5.64 times" the awards; this page said
  the awards are "22%" of the model's. Both are right: the first is ancillary services alone per kW a month, the
  second energy and ancillary together over seven months. This page now draws the first as well, and a test holds the
  two pages to the fourth decimal.
- **Three figures of ERCOT's fleet differ between this page and `/storage`, each right for what it counts:** MW
  (21,365 against 18,070 in July 2026), hours (about 1.9 against 1.65) and MWh discharged (847,905 against 705,980 in
  July 2026). Two are now said on the page; the hours are a ruling (row 8).
- **All changes are in the tool's own files.** No other page's file was edited (`/storage`, `/supply`, `/shoulder`, the
  battery page).
- **Not finished:** `replication/battery_awards/replicate.py` does not yet recompute the added figures (45 by service,
  6 of the five together, 5 in the MW hover). They are held by the new test on the committed public rows, which is the
  page's own library, not an independent computation, except the five together, held to the battery page's file.
- **How it was read:** the whole page drawn by its own function, reads answered from the tables of this machine
  (`site/scripts/battery-awards-page.mjs`, new). No click, no chart, no browser, no live set.

## The reader and the five cases

- **Reader:** a lender's analyst testing a developer's revenue case against what the fleet was really awarded. Not
  the developer choosing between two nodes: the page has no input and names no settlement point.
- 1. July 2026: a kW awarded day-ahead (0.68: 0.53 energy, 0.15 ancillary), and the ancillary by service.
- 2. The 2-hour model against the award: July 2026 (2.87 against 0.68) and January to July 2026 (30.14 against 6.53;
  of the gap, offered and not awarded is the largest part, 14.53 of 23.61).
- 3. Two settlement points by ERCOT's names, `AZURE_RN` (the table's median point, USD 68.22 per MWh) and `KNAPP_RN`
  (its widest, 354.96), 28 September to 18 October 2026, against the hub's 57.60. Chosen by rule from the table.
- 4. January to July 2026: 8.0 percent of the energy offered day-ahead was priced at USD 100 or less.
- 5. A 4-hour battery: the page says nothing of its own (part A, row 7).

## The rows by kind (16)

- **Site, fixed with a test: 6** (rows 1 to 6).
- **Data machine: 3** (rows 11 to 13; ready rows below).
- **Browser: 3** (rows 14 to 16; ready rows below).
- **Ruling: 4** (rows 7 to 10).
- License: 0. Key: 0.
- Part A's rows 4 to 9 were met again and are cited in the read, not rewritten.

## What was fixed

- **Row 1.** `page.tsx`, `lib/storageawards.ts` (`servicesOf`): each month's ancillary cell in "By month" says its five
  services on hover, the ancillary share of the month and the source document.
- **Row 2.** `Offers.tsx`: the ancillary table ends with "The five together" (2.78, 15.66, 12.88) and one sentence
  gives the two per kW a month (0.40, 2.24, 5.64 times), says it is ancillary services alone, and links the battery
  page at 2 hours on the day-ahead schedule.
- **Row 3.** `Offers.tsx`, `RealTime.tsx`: "ECRS" carries its name on hover.
- **Row 4.** `RealTime.tsx`: the node part ends by saying it names no point, links the ERCOT node list of the All grids
  tab and the battery page, and names the table that holds each point's own days.
- **Row 5.** `page.tsx`, `lib/storageawards.ts` (`inventoryOf`): a hover on the MW line of "What is counted": the EIA's
  18,070 MW in 257 generators at 1.65 MWh per MW beside 21,365 MW in 332 resources, what each counts, both sources.
- **Row 6.** `RealTime.tsx`: under the MWh table, what this page's MWh count and what the storage page's daily cycle
  counts, with a link.
- The method note has a section 8 for the six. `replication/battery_awards/inventory_rows.csv`: the 27 public rows of
  the EIA's count, so the page draws on any copy.

## Tests

Each file in its own process, one at a time, its output under `runs/` and its exit code read.

| File | Result |
|---|---|
| `site/scripts/test-battery-awards-read.mjs` (new; run with `--import ./scripts/battery-awards-page-register.mjs`) | 39 of 39 passed |
| `site/scripts/test-battery-awards-render.mjs` | 25 of 25 passed |
| `site/scripts/battery-awards-figures.mjs` (on this machine's tables) | exit 0: 307 figures, 217 of 217 found |
| `site/scripts/test-usage.mjs` | 16 passed |
| `tests/test_session7505_battery_awards.py` | 12 passed |
| `tests/test_session115_page.py` | 12 passed, 1 skipped |
| `tests/test_session116_page.py` | 20 passed, 2 skipped |
| `tests/test_session120.py` | 30 passed, 3 skipped |
| `tests/test_session120_page.py` | 15 passed, 2 skipped |
| `tests/test_session178.py` | 30 passed, 4 skipped |
| `tests/test_session241a.py` | 17 passed, 199 subtests |
| `tests/test_session408.py` | 7 passed |
| `tests/test_session585.py` | 6 passed |
| `tests/test_session142.py`, `147`, `158`, `160` (the method notes) | 42, 65, 58 and 40 passed |
| `tsc` with the site's settings on the page's four files and all they import (a scratch project file, removed) | exit 0, no error |

The skips are tests that read a warehouse table the worktree does not hold. No failure. No site build, no full suite,
no landing gate, no `check-values`, `check-routes` or `check-390` (they need the built or live site).

## What to review

`https://erw-flame.vercel.app/cost-of-power/battery/awards` (in review; after the branch lands). The figures below are
those of this machine's tables; the live set's may be of a later build (part A, row 4).

1. The beige panel "What is counted", the line "MW.": a small "i" after it. Hover it: "The storage page (its
   build-out tab) counts this fleet another way ... For ERCOT in July 2026 it lists 18,070 MW in 257 generators,
   holding 1.65 MWh per MW. ERCOT's file lists 21,365 MW in 332 resources, 3,296 MW more ... 18 percent higher."
2. "By month", the row July 2026, the cell 0.15 (dotted underline). Hover it: "July 2026, USD per kW awarded
   day-ahead: Regulation Up 0.01, Regulation Down 0.01, Responsive Reserve 0.02, ECRS (ERCOT Contingency Reserve
   Service) 0.02, Non-Spin 0.09; ancillary services are 22 percent of the month's 0.68."
3. "Where the gap comes from", the table "Ancillary services": its last row, beige, "The five together", with 2.78,
   15.66 and 12.88 and the share cells empty. Under it: "The five together, over the 7 months: USD 2.78 per kW awarded
   against the model's USD 15.66. Per kW a month that is USD 0.40 against USD 2.24, the model's 5.64 times the awards."
   Hover "ECRS" in the table: "ERCOT Contingency Reserve Service".
4. "The real-time side", under the table of MWh by month: "The MWh here add up each resource's own discharge ... A net
   count is the smaller of the two, so that page's MWh for a month stand below these."
5. The last paragraph of the page's last part: "No settlement point is named on this page ...", with links to the
   ERCOT node list on the All grids tab and to the battery page.
6. The source line at the foot names six tables, the last `storage_buildout_monthly`.

## Data request rows

| Requested (UTC) | Session | Table or file | What, exactly | Source | State |
|---|---|---|---|---|---|
| 2026-11-16 12:50 | 7514 | `ercot_storage_node_basis` | On samueloldlaptop it holds 21 whole days (28 September to 18 October 2026, retrieved 19 October) and its header's Coverage line still says "this is the week listed when it was pulled", while `node_basis_summary` says real-time node prices are held to 20 October (23 days). Rebuild it on every day of real-time node prices held (no request to ERCOT), correct that header line, load it. And say whether the live set holds its rows by settlement point (293 entities, the variable `spread_node`) or the summary entity `ercot:esr_nodes` alone: the page now names the table as where each point's own figure is | `docs/reviews/battery-awards-read-2026-11-16.md`, row 13 | requested |
| 2026-11-16 12:50 | 7514 | a new monthly table of the fleet's real-time energy offers (the form of `ercot_storage_dam_offers_monthly`) | From the zips kept under `warehouse/raw/ercot_60d_sced/zips` (the file `60d_ESR_Data_in_SCED`, the 160 offer-curve columns `ercot_sced_esr_hourly` leaves out): what the fleet offered to sell in real time at USD 0, 25, 50, 100, 250 and 1,000 per MWh or less and at any price, by month from February 2026, in MWh per MW per day and as a share of all offered. No request to ERCOT. It lets the page answer its price-band question in the market where the fleet trades, beside the market monitor's 55 percent for 2025 | the same file, row 11 | requested |
| 2026-11-16 12:50 | 7514 | `ercot_storage_dam_awards_monthly` and `ercot_storage_rt_monthly`, by duration class | From `ercot_sced_esr_hourly`: each resource's highest `x_soc_max_mwh` over its highest `x_hsl_mw`, over the days held, is a floor on its hours. Class each resource (under 2 hours, 2 to 4, 4 and over, not seen in real time) and write the two tables' figures per MW by class and month as new entities, each with its MW and its count of resources. No request to ERCOT. The method line says it is a floor (the highest state of charge seen), not a nameplate | the same file, row 12 | requested |

## Browser read rows

| Asked (UTC) | Session | Branch | Address | What to look at | What should be seen | State |
|---|---|---|---|---|---|---|
| 2026-11-16 12:50 | 7514 | `wip/7505-battery-awards` | `https://erw-flame.vercel.app/cost-of-power/battery/awards` | "By month": rest the mouse on the ancillary figure of July 2026. Then "What is counted": hover, then tab to, the "i" after "MW." | The figure has a dotted underline and the hover lists the month's five services with "22 percent". The tip opens on hover and on focus, names 18,070 MW and 21,365 MW (or the live set's figures for its newest whole month), and stays inside the page at 1280 and at 390 px | wanted |
| 2026-11-16 12:50 | 7514 | `wip/7505-battery-awards` | `https://erw-flame.vercel.app/cost-of-power/battery/awards#offers` | The ancillary services table and the page at 390 px | The table's last row is "The five together", beige, its four share cells and its last cell empty; the table scrolls inside its own frame and the page has no sideways scroll | wanted |
| 2026-11-16 12:50 | 7514 | `wip/7505-battery-awards` | `https://erw-flame.vercel.app/cost-of-power/battery/awards#real-time` | The last paragraph: click "the ERCOT node list on the All grids tab", type KNAPP_RN in its name filter. Back; in the offers section click "The battery page" in the sentence that begins "The five together" | The All grids tab opens on its ERCOT nodes and the filter leaves one row, `KNAPP_RN`, class storage. The battery page opens on a 2-hour battery on the day-ahead schedule and its line "Day-ahead ancillary services" reads the same two figures per kW a month and the same ratio as the sentence left behind | wanted |

## Landing request

- **Head:** the commit of this report on `wip/7505-battery-awards` (the reply gives its hash), on top of session 7505's
  `73837e331`, itself stacked on `wip/7500-done-line`.
- **Test files:** `site/scripts/test-battery-awards-read.mjs` (39, new) with the files under "Tests".
- **What changes:** `site/app/cost-of-power/battery/awards/page.tsx`, `Offers.tsx`, `RealTime.tsx`;
  `site/lib/storageawards.ts` (three exports added, none changed); three new scripts (`battery-awards-page.mjs`, its
  loader and its register) and the test; `replication/battery_awards/inventory_rows.csv`; the method note's section 8;
  the read; this report.
- **What does not:** `storagerealtime.ts`, `Decisions.tsx`, any shared component or loader, any table, any builder,
  `release.ts`, `check-values.mjs`, any other page.
- **A snapshot would differ on:** no page a visitor sees (the page is in review). Behind the review gate: this one
  page, in the six places under "What to review".
- **For the desk:** the page asks the live set for `storage_buildout_monthly` (`iso:ercot`); the storage page's
  build-out tab already reads that table there.

## Needs the key

- None. No step of this read calls a model, and none was run.

## Decisions made without you

- The reader is the lender's analyst, since the page is the fleet's and has no input.
- The two points of case 3 were taken by rule (the table's median point and its widest), and are named only as
  ERCOT names them. No view of either is taken.
- Row 1's hover is the cell's own `title` with a dotted underline, not the tip component: a tip inside a table's
  scroll frame can be cut by the frame, and no browser was here to see it.
- Row 5 reads the EIA's figure from its table when the page is drawn; it is not typed into the page.
- No link stands inside a hover; the links are in the page's own sentences.
- The stand-in for `next/font/google` is a new small loader beside the page's script, not a change to the shared
  loader, which other branches edit.
- What was added is the page's own text, hovers and one table row; no grey note was added.
- `replicate.py` was not extended in this session (see "At the top").
- `/supply` draws no figure of the battery fleet, so nothing there was compared; `/shoulder` was compared on its
  table, not on its drawn page.

## For Samuel's ruling

1. **Point from the lead to the real-time section?** The lead says "day-ahead awards only" and the page's last
   section adds real time at the hub's price. Default: the lead unchanged. The other choice: one closing sentence
   with a link.
2. **Which hours for the fleet in the decisions block?** It says "about 1.9 hours" from the market monitor; the
   storage page says 1.65 from the EIA. Default: unchanged, with the EIA's figure now in the MW hover.
3. **The gap's three parts by month?** Default: over the months together, as now. The other choice: one more table,
   from rows the page already reads.
4. **Two settlement points side by side on this page?** Default: no input added; the page links the node list. The
   other choice: an A and B of two points from `ercot_storage_node_basis` (293 points, 21 days of real time).
5. **Row 1's hover:** keep the five services on hover, or draw them as five columns of "By month"? Default: hover.

## Seen in another tool (one line)

- The battery page's paragraph "At its own node" and its fold are small grey text, which the page standard of 16
  November forbids; not touched here.
