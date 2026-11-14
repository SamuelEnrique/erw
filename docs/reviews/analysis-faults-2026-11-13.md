# Automated Analysis (Research, `/research`): faults of 13 November 2026

Energy Research Warehouse (ERW). Chain 233, window P1 of the portable laptop, session 5004. Read on the local production build of session 5001 in the internal view at 1280 and 390, the fix read again on session 5004's build, and its done line for roadmap item 2 read against the method note, the replication and the cross-check table. `/analysis` redirects to `/research` (session 238). States as in `battery-faults-2026-11-13.md`.

| # | Where | Fault | Fix | State |
|---:|---|---|---|---|
| 1 | The page at 390, "Chart archive" | The page is 563 px wide at a 390 px window: one daily chart's entry holds a word of 95 characters (an entity id), and a grid item is as wide as its longest word | `.brand-a .chart-archive li` may shrink (`min-width: 0`) and break a long word (`overflow-wrap: anywhere`); `tests/test_session5004.py` | fixed (session 5004) |
| 2 | The daily chart of 2026-11-06 in the archive (the Digest's chart of the day) | Its fact line opens with a raw entity id, `onrr_revenue:federal:onshore:22081_red_river:other_revenues:oil_gas:oil_gas_pre_production:none`, where a reader expects words | Not this window's: the daily chart is written by the Digest's chart of the day (`warehouse/analysis/findings/daily_chart.py`), the old laptop's. Recommendation: the fact names the entity's label, never its id | other window (the old laptop) |
| 3 | Method note, first paragraph | "on the site's `/analysis`": the page is `/research` since session 238 | The paragraph names `/research` and says `/analysis` redirects | fixed (session 5004) |
| 4 | Method note | No sign-off block, which the three economics notes and the Grid tool's have; roadmap item 2 asks for a signed note | A "Sign-off" block ends the note, naming what a signature accepts | fixed (session 5004) |
| 5 | Method note | Nothing says which parts of the page run by themselves and on which clock, which "the final form" needs | A section "Final form" before "Replication": each part, what makes it, its clock, the last one made, and what waits for a person by ruling (a finding's publication) | fixed (session 5004) |
| 6 | `docs/methods/crosschecks/automated_analysis.md` (found in session 5402, reading the cards against it) | The cross-check table quoted the cards of 6 November where the page prints those of 12 November: least all-in 40.99 for 41.04, the gigawatt's years, the curtailment estimates (8,539 for 8,426 and five more), the flexible load's hub figures, the queue's 3,509 GW for 3,591 and its best technology's 52 percent for 53. Session 5073 held only the three decision tools' tables to their page figures | Every figure set to `replication/analysis/page_figures.json` of 12 November, the gaps recomputed (-25.98; +90 GW); `tests/test_session5073.py` holds every card figure the page prints to the table | fixed (session 5402) |

## The read

| View | 1280: width, keys, errors | 390: width, keys, errors |
|---|---|---|
| `/research`, session 5001's build | 1265, 138, 0 | **563**, 138, 0 |

## The done line after session 5004

| Item | State |
|---|---|
| Method note | complete for signature (with `automated_analysis_findings.md` and `automated_analysis_scanner.md`); unsigned: the owner signs |
| Replication | `replication/analysis/replicate.py`: 66 of 66 computed figures inside the tolerance, 10 license needed, 2 not in a download; the do-file never run |
| Cross-check table | `docs/methods/crosschecks/automated_analysis.md` |
| Decisions block | the note's "Decisions" (35 assumptions, `replication/analysis/assumptions.json`) |
| Final form | every part made on a clock with no person (the note's "Final form"); a finding is published after the owner's approval, by ruling; whether it is final is the owner's word |

## The fresh read (session 5077, chain 243)

Read on production (`https://erw-flame.vercel.app`, main as deployed on 13 November 2026 between 19:59 and 20:12 UTC) in the internal view, the token posted as the site's form does, at 1280 by 900 and at 390 by 844 as a phone, with the site's own browser helper (`site/scripts/browser.mjs`): each page's end address, its scroll width against the window, the exceptions it threw, the words that betray a broken value (NaN, undefined, [object Object], Infinity), its text and a picture of the window and of the whole page (four looked at: the Grid's Ask flag and Network at 1280, Gravity at 390, the battery's CAISO view at 390; the others read by their measures and text). Not on a local build: the build of `wip/5072-analysis` was stopped by Claude Code when the laptop ran low on memory (three windows on 16 GB), and the stack changes no page's code.

- `/research` and the archive's newest week, `/research/2026-W45`, at both widths: no sideways scroll, no exception, no broken word.
- **No new fault.** The week's chart of 2026-W46 is made on Sunday 15 November; this chain's dry run of it (session 5075) chose Brent's weekly mean.
