# What a generator earns (`/cost-of-power/seller`): faults of 13 November 2026

Energy Research Warehouse (ERW). Chain 233, window P1 of the portable laptop, session 5002. Read on the local production build of session 5001 (`wip/5000-battery`, the generator page unchanged from main) in the internal view at 1280 and 390, and its done line for roadmap item 2 read against the method note, the replication and the cross-check table. States as in `battery-faults-2026-11-13.md`.

| # | Where | Fault | Fix | State |
|---:|---|---|---|---|
| 1 | Method note, section 10, item 3 | "No builder of this page is scheduled ... Open": session 204 made the model, the hub files, the hybrid and the download daily steps of the data machine (`warehouse/scheduled.py`), so the item the sign-off leaves open is already closed | The row reads "Closed by session 204", names the four steps and the capture file's builder, and keeps session 183's text after it | fixed (session 5002) |
| 2 | The page's figures, and the battery page's | The last twelve months end September 2026 on both pages on 13 November; the generator's snapshot (`site/data/merchant_snapshot.json`) was built 4 October 2026, and the battery page draws 2026 as nine months. October 2026 is not yet a held month for either model | Not the code machine's: the daily builders exist (row 1); why October is not held (a month under 90 percent of its days or hours, or a builder refusing) is the data machine's to read in its run log | data machine |
| 3 | The page's foot | The decisions block starts closed | Not a fault: the generator page is not under the battery's "nothing collapsed" ruling, and the block is session 463's form | not a fault |
| 4 | "What did it earn?", the spans table (found in session 5501, on production, ERCOT's solar, 1280 and 390) | Two capture prices for the same twelve months stand on the face with nothing to say why: the headline's price received 23.27 against 32.17, the spans table's capture price 23.20 against 32.10 (the note's section 9, item 1: "the page face does not") | A line under the spans table, for solar and wind, names the two weighings (the model's: output per MW of the month's nameplate, each month alike; the price received: the generation itself, every hour alike) and gives the four figures with the keys they already carry; the note's section 9 says so; `tests/test_session5501.py` | fixed (session 5501) |

## The read (session 5001's build)

| View | 1280: width, keys, errors | 390: width, keys, errors | Decisions block |
|---|---|---|---|
| `/cost-of-power/seller` | 1265, 180, 0 | 390, 180, 0 | `463`, closed, 23 lines |

No broken text ("NaN", "undefined", "null%", "license needed%"). Nothing scrolls sideways at 390.

## The done line after session 5002

| Item | State |
|---|---|
| Method note | complete for signature (sections 1 to 13, the sign-off block); unsigned: the owner signs; section 10 holds the items it leaves open, item 3 now closed |
| Replication | `replication/generator/replicate.py` from the public CSV, 13 of 13; the do-file never run (no Stata on this laptop) |
| Cross-check table | `docs/methods/crosschecks/generator.md`, current |
| Decisions block | `GENERATOR_DECISIONS` on the page and the note's section 13, word for word (`tests/test_session463.py`) |

## The wider read (session 5008)

Session 5004's build, internal view, 1280 and 390: every grid (ERCOT, CAISO, NYISO, SPP, ISO-NE) with every technology (solar, wind, battery, gas peaker), 40 views. No console error, no broken text, nothing scrolls sideways at 390. Five views draw no checked figure (NYISO's solar, battery and peaker; ISO-NE's battery and peaker): each says why above its first section ("No month of ... is held for ...", NYISO's solar adding that EIA-930 itemizes no solar generation for New York) or in its summary ("ISO-NE holds no twelve months of battery in a row"). Not a fault.

## The fresh read (session 5077, chain 243)

Read on production (`https://erw-flame.vercel.app`, main as deployed on 13 November 2026 between 19:59 and 20:12 UTC) in the internal view, the token posted as the site's form does, at 1280 by 900 and at 390 by 844 as a phone, with the site's own browser helper (`site/scripts/browser.mjs`): each page's end address, its scroll width against the window, the exceptions it threw, the words that betray a broken value (NaN, undefined, [object Object], Infinity), its text and a picture of the window and of the whole page (four looked at: the Grid's Ask flag and Network at 1280, Gravity at 390, the battery's CAISO view at 390; the others read by their measures and text). Not on a local build: the build of `wip/5072-analysis` was stopped by Claude Code when the laptop ran low on memory (three windows on 16 GB), and the stack changes no page's code.

- ERCOT's solar (the default) and CAISO's wind, at both widths: no sideways scroll, no exception, no broken word. The "Price years" default (59.85) is the headline's: the snapshot and the table are both of early October (row 2).
- **No new fault.**
- **Session 5404, about 20:55 UTC:** SPP's wind at both widths: no sideways scroll, no exception, no broken word. No new fault.
- **Session 5406:** CAISO's gas peaker at both widths: no sideways scroll, no exception, no broken word. No new fault.

## The read of 14 November (session 5501, chain 269)

Read on production (`https://erw-flame.vercel.app`, main at `85e5b2eeb` as deployed at 08:28 UTC on 14 November 2026, the tree this chain's stack was cut from) in the internal view, the token posted as the site's form does, at 1280 by 900 and at 390 by 844 as a phone, with the site's own browser helper (`site/scripts/browser.mjs`): each page's words, its headings, its closed folds, its links, its width and its exceptions. A local build was not used for this read: 1.0 GB was free at 08:26 UTC, under the chain's 2 GB rule.

- ERCOT's solar (the default) and CAISO's solar, at both widths: no sideways scroll, no exception, no broken word; axe at 390 on the default: 0 rules broken.
- Against the done line: the method notes are linked, the replication (CSV, do-file, Python mirror), "Checked against: 34 published figures" and the decisions block (closed, row 3) are on the face. Unsigned.
- The plant with a battery beside it reads "Nov 2025 to Oct 2026" beside the model's "Oct 2025 to Sep 2026": the hybrid file was built on 12 November and the model on 4 October (row 2, data request row 2); each says its months.
- **Row 4, new**, fixed in session 5501.
- **The last fresh read (session 5505):** ERCOT's wind and gas peaker, at both widths: no sideways scroll, no exception. The source line names EIA-930's workbook by its file name (`20261109T173953.668221Z_00004_ERCO.xlsx`): the provenance, by design. No new fault.
