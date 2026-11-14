# What a datacenter pays (`/cost-of-power`): faults of 13 November 2026

Energy Research Warehouse (ERW). Chain 233, window P1 of the portable laptop, session 5003. Read on the local production build of session 5001 (the page unchanged from main) in the internal view at 1280 and 390, and its done line for roadmap item 2 read against the method note, the replication and the cross-check table. The file is named `datacenter-cost-` so that it is not taken for the datacenter tracker's (`datacenter-faults-2026-11-11.md`). States as in `battery-faults-2026-11-13.md`.

| # | Where | Fault | Fix | State |
|---:|---|---|---|---|
| 1 | `site/lib/datacenter.ts`, `weights()`; the decisions line "foreseen"; the note's section 10, item 15 | The owner ruled on 12 October 2026 that "if perfectly foreseen" takes the rule's hour budget in a partial year (`docs/roadmap.md`, "Rulings"); the code still pro-rated it (a load of 100 hours got 76 in 2026 against the rule's 100), and the page's decisions block still said "waits for a ruling" | `k = min(hours held, shedBudget(x, hours of the year))`, the recommendation the ruling took; the decisions line and the note's line 7 state the ruling; item 15 closed; the note's worked example recomputed on its frozen inputs (foreseen 29.29, 4.44 less, "the rule kept 51 percent"; day-ahead 30.19), each old figure kept beside it; the test mirror in `test_session190_replication.py` follows. New: `site/scripts/test-foreseen-5003.mjs` and `tests/test_session5003.py`. No default figure moves: the default load is flat | fixed (session 5003) |
| 2 | Method note, section 10, item 4 | "ERCOT's load zones stop on 3 October 2026 ... `run_data_machine.sh` is registered nowhere": the page's last twelve months now run to October 2026 (`replication/datacenter/replicate.py`: 2025-11 to 2026-10), and `price_compare` is a daily step of the data machine since session 204 | The row reads closed by session 204, session 190's text kept after it | fixed (session 5003) |
| 3 | The page's foot | The decisions block starts closed | Not a fault: the datacenter page is not under the battery's "nothing collapsed" ruling | not a fault |
| 4 | The "Price years" choice (found in session 5077, on production, 1280 and 390) | "The last twelve months (default): 33.73 USD per MWh" and "2026, 9 months held" stand beside the headline's USD 34.07 for November 2025 to October 2026: the choice reads `price_years_by_window`, built once (retrieved 2026-10-20T09:08:39Z), before the daily files reached October | Not the code machine's: a trial build here on 13 November 2026 (`python warehouse/derived/price_years.py --out-dir <scratch>`, the live set read with the anon key; 2,754 rows, 33 proofs equal) gives CAISO's 4-hour foresight default 79.80 from November 2025 and LZ_NORTH's 34.07, the headlines' figures; the build and its load are window A's (`docs/state/data_requests_five_tools.md`, row 4) | data machine |
| 5 | The source line (found in session 5501, on production, ERCOT's default, 1280) | `ercot_large_load_status` is named twice in "Source: ERW tables ...", and two of the line's spans carry one key | The second entry dropped from the page's list; `SourceLine` (`site/components/tool/ToolPage.tsx`) names each table once, in its first place; `tests/test_session5501.py` | fixed (session 5501) |

## The read (session 5001's build)

| View | 1280: width, keys, errors | 390: width, keys, errors | Decisions block |
|---|---|---|---|
| `/cost-of-power` | 1265, 249, 0 | 390, 249, 0 | `462`, closed, 21 lines |

No broken text. Nothing scrolls sideways at 390. The default headline (USD 34.07 per MWh, November 2025 to October 2026) equals the replication's.

## The done line after session 5003

| Item | State |
|---|---|
| Method note | complete for signature (sections 1 to 12, the sign-off block); unsigned: the owner signs; section 10's open items are his, item 15 now closed by his ruling |
| Replication | `replication/datacenter/replicate.py` from the public CSV, 14 of 14; the do-file never run (no Stata on this laptop) |
| Cross-check table | `docs/methods/crosschecks/datacenter.md`, current |
| Decisions block | `DATACENTER_DECISIONS` on the page and the note's section 12, word for word |

## The wider read (session 5008)

Session 5004's build (which holds row 1's fix), internal view, 1280 and 390: each of the seven grids (ERCOT, CAISO, PJM, NYISO, ISO-NE, MISO, SPP) in the load view and the grids view, and the all-grids view, 30 views; and the load turned off in 100 hours a year. No console error, no broken text, nothing scrolls sideways at 390, a checked figure on every view. `check-values` restricted to `/cost-of-power` and `/research`: 2,873 of 2,873 values match Supabase.

## The fresh read (session 5077, chain 243)

Read on production (`https://erw-flame.vercel.app`, main as deployed on 13 November 2026 between 19:59 and 20:12 UTC) in the internal view, the token posted as the site's form does, at 1280 by 900 and at 390 by 844 as a phone, with the site's own browser helper (`site/scripts/browser.mjs`): each page's end address, its scroll width against the window, the exceptions it threw, the words that betray a broken value (NaN, undefined, [object Object], Infinity), its text and a picture of the window and of the whole page (four looked at: the Grid's Ask flag and Network at 1280, Gravity at 390, the battery's CAISO view at 390; the others read by their measures and text). Not on a local build: the build of `wip/5072-analysis` was stopped by Claude Code when the laptop ran low on memory (three windows on 16 GB), and the stack changes no page's code.

- The default (`LZ_NORTH`, a flat load, real time) and bought day-ahead, at both widths: no sideways scroll, no exception, no broken word.
- **Row 4, new:** the "Price years" choice is of 20 October (33.73 beside the headline's 34.07). The data machine's (data request row 4).
- **Second batch (session 5079), the same way, about 20:25 UTC:** CAISO's and SPP's load views, the all-grids view, the hours view (`run=hours`) and the all-grids view of a flexible load, at both widths: no sideways scroll, no exception, no broken word. CAISO's "Price years" default is 28.58 beside its headline's 29.72 for November 2025 to October 2026: row 4's cause, on another grid. SPP's agree (30.80, October 2025 to September 2026: its months have not moved).
- **Third batch (session 5404), the same way, about 20:55 UTC:** the load view of PJM, MISO, NYISO and ISO-NE at both widths: no sideways scroll, no exception, no broken word. PJM and MISO say "Grid: ... is not held here, so ERCOT is shown." and show ERCOT; NYISO and ISO-NE draw in the internal view, their price years "None is held for this case" and delivery charges "not held yet". No new fault.

## The read of 14 November (session 5501, chain 269)

Read on production (`https://erw-flame.vercel.app`, main at `85e5b2eeb` as deployed at 08:28 UTC on 14 November 2026, the tree this chain's stack was cut from) in the internal view, the token posted as the site's form does, at 1280 by 900 and at 390 by 844 as a phone, with the site's own browser helper (`site/scripts/browser.mjs`): each page's words, its headings, its closed folds, its links, its width and its exceptions. A local build was not used for this read: 1.0 GB was free at 08:26 UTC, under the chain's 2 GB rule.

- The default (`LZ_NORTH`, a flat load, real time) and the all-grids view, at both widths: no sideways scroll, no exception, no broken word; axe at 390 on the default: 0 rules broken.
- Against the done line: the method note, the replication (CSV, do-file, Python mirror), "Checked against: 8 published figures" and the decisions block (closed, row 3) are on the face. Unsigned.
- The "Price years" default is still 33.73 beside the headline's 34.07 (row 4, the data machine's).
- **Row 5, new**, fixed in session 5501.
- **The last fresh read (session 5505):** CAISO's load view and ERCOT's hours view (`run=hours`), at both widths: no sideways scroll, no exception. "USD 68.547301 per kW of four-peak demand" is the Commission's rate as filed. No new fault.
