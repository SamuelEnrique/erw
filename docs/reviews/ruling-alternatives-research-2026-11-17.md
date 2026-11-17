# Ruling alternatives: /research (17 November 2026)

Session 7629 (portable-laptop, code role). The two lines of `docs/reviews/ruling-impact-research-2026-11-17.md`, both built, each on its own branch from origin/main with a test that pins it, in order of size of change. **No branch asks to land; no default on main changed; no Digest touched.** Model spend USD 0; no card was run again.

- **Build:** the worktree `erw-alt` (3,030 and 3,323 MB free before the two builds), served on port 3320 with the repository's `.env` and no model key, read with the internal cookie at 1280 px.
- **Tests:** the new test of each branch and every test file that names a changed file: 1,004 passed and 6 skipped (`wip/alt-research-1`, after moving test 5171's pin of the card loader's line to the other choice); 235 passed and 3 skipped (`wip/alt-research-2`).

| # | Line | Branch | Figure before (origin/main) | Figure after (the other choice) | Files touched | Test | Screenshot |
|---|---|---|---|---|---|---|---|
| 1 | Three findings cards are built from internal tables (`gas_sets_price` from ISO-NE's prices; `siting_flexible` and `siting_gigawatt` from the PUCT's transmission matrices) and served by address: withdraw them? | `wip/alt-research-1` (`135b8310a`) | The library: 14 card files; the card index 12 of 12 (14 less the 2 superseded, by the page's rule); each of the three cards at its own address | **Card index "9 of 9"; the library 11 card files (-21.4 percent)**; the three cards' 9 callouts, 49 numbers, 6 chart series of 96 points and 9 downloads leave the library (-100 percent each); `/research/card/gas_sets_price`, `siting_flexible` and `siting_gigawatt` answer 404 (read: `queue_divorce` 200); the catalogue a reader may ask from 11 to 10 entries | `site/lib/findings.ts`, `tests/test_session5171.py`, `tests/test_session7629_alt_research_withdrawn.py` | 14 files, 11 kept, the catalogue 11 to 10, the files still on disk; the loader drops the three and their addresses | `docs/reviews/ruling-alternatives/research-1-cards-withdrawn-1280.png` |
| 2 | Today's chart of 12 November says Wyoming's August gas generation broke July 2024's record, where July 2026 broke it first: correct the stored chart record | `wip/alt-research-2` (`da337da8f`) | "The record until now was 765,381 MWh, in July 2024"; August above it by 295,122 MWh | A correction line under the stored record: **"the record until now was 1,034,451 MWh, in July 2026 (+269,070, +35.2 percent), ... August 2026 was above it by 26,053 MWh (2.5 percent), not by 295,122"**; the stored fact, picture and numbers are left as stored, and the headline ("the highest monthly value held since January 2001") stands | `site/app/research/page.tsx`, `tests/test_session7629_alt_research_correction.py` | The correction's arithmetic and its line under the record of its date alone | `docs/reviews/ruling-alternatives/research-2-chart-correction-1280.png` |

## What the builds showed

- **Line 1: the downloads stay reachable by address.** The three cards' files under `site/public/findings/` (their do-files, Python files, pictures and CSVs) are served as static files; withdrawing them from the address would mean deleting them, which this repository's rule 3 forbids on a branch as anywhere. The ruling would say whether they go.
- **Line 1: the requests table still names a withdrawn card.** "Requests" lists the reader's past asks, among them "Gas sets the price less often?", whose "show the card" link now leads to a 404 on the branch. A ruling to withdraw would also say how a past request of a withdrawn card is drawn.
- **Line 2: July 2026's figure is the data machine's copy** (1,034,451 MWh); Redivis's draft of 10 October reads 1,028,747 (then the record cell moves +263,366, +34.4 percent, and August is above it by 31,757, 3.1 percent). The Digest of 12 November, which shows the same chart, is not touched (no Digest work this week).
- **The browser's cache:** `/research` is a static page; the first read of the second build showed the first build's copy until reloaded without the cache. Every figure above is from a cache-free read.

## Decisions made without you

- **Line 2 as a correction line, the stored record left as it was:** a stored chart is the record of what was said that day; the line says what was wrong and what is right, beside it.
