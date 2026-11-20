# Ruling alternatives: /deals, the deal tracker (17 November 2026)

Session 7627 (portable-laptop, code role). The five lines of `docs/reviews/ruling-impact-deals-2026-11-17.md`. Three are built, each on its own branch from origin/main with a test that pins it, in order of size of change; two are not, said below. **No branch asks to land; no default on main changed; no hold lifted.** Model spend USD 0.

**The tracker is held whole.** `energy_deals` is held ("license needed", since 21 October): `/deals` draws the hold and no row, in the internal view too, on origin/main and on every branch here. So no cell these choices move is drawn on any page: the screenshots show the hold standing, and each figure is pinned by its test through the page's own functions (`site/lib/deals2.ts`: `toDeal`, `fold`) on the repository's copy of the table (583 rows, 5 folded by `site/data/deal_duplicates.json`). Only counts and sums are written here, never a deal's parties or its own figures. The live set holds more deals than this copy (the rulings file: 590 deals, 43,119 MW), so the shares are the measure to carry over.

- **Build:** the worktree `erw-alt` (2,277 to 3,102 MB free before the three builds), served on port 3320 with the repository's `.env` and no model key, read with the internal cookie at 1280 px. The counting script, counts only: `runs/c7627_deals_counts.mjs`.

| # | Line | Branch | Figure before (origin/main) | Figure after (the other choice) | Files touched | Test | Screenshot |
|---|---|---|---|---|---|---|---|
| 1 | Open the deals table at a floor of the extraction's confidence ("Sure at least" 0.7, as the Roundup's tables use) | `wip/alt-deals-1` (`29b14e2c0`) | No floor: 578 deals, 40,297 MW stated by 35, 212 AI-power deals | At 0.7, each deal as folded by its kept row's confidence: **281 deals (-51.4 percent), 21,705 MW (-46.1 percent), 99 AI-power deals (-53.3 percent)**, the impact file's figures exactly. Every view (the tracker, the charts, the comparables, the AI view) reads its deals through `atFloor` | `site/lib/deals2.ts`, `site/app/deals/{ai,charts,comparables,v2}/view.tsx`, `tests/test_session7627_alt_deals_floor.py` | The counts above through the page's functions; the four views apply the floor | `docs/reviews/ruling-alternatives/deals-1-floor-held-1280.png` (the hold) |
| 3 | When two rows are folded into one deal, the kept row takes a figure only the folded row states | `wip/alt-deals-2` (`3613dc1e4`) | MW disclosed 40,297 by 35 deals | **40,730 MW by 36 (+433, +1.07 percent)**: one kept row lacked MW its folded row states (the impact file names it: the Energy Department's loan to Vistra); a figure a kept row states is never replaced. The same for MWh, dollars, price and term | `site/lib/deals2.ts`, `tests/test_session7627_alt_deals_carry.py` | 578 deals, 40,730 MW by 36, every kept row's own MW unchanged | `docs/reviews/ruling-alternatives/deals-2-folded-figure-held-1280.png` (the hold) |
| 4 | The tracker, the comparables and the AI view read a grid the story names before the state | `wip/alt-deals-3` (`08659cf2e`) | By grid: not stated 544, PJM 10 | **Not stated 543, PJM 11** (one deal; +10 percent of PJM's count) | `site/lib/deals2.ts`, `tests/test_session7627_alt_deals_grid.py` | 578 deals, 543 not stated, 11 PJM | `docs/reviews/ruling-alternatives/deals-3-grid-held-1280.png` (the hold) |

## Tests that pin the default, left failing on the branches

These tests hold the figures as origin/main computes them; under the other choice they would move with the ruling. They are named here, not rewritten, since the page draws none of the figures they pin.

- `wip/alt-deals-2`: `tests/test_session113.py` (`test_a_figure_not_stated_is_never_a_number`, `test_every_selection_against_the_table`), `tests/test_session2241_deals.py` (`test_the_stored_deals_trace`), `tests/test_session466.py` (`test_every_cell_of_every_dimension`), `tests/test_session7404_trackers.py` (`test_made_up_deals_key_by_key`: the replication, `replication/deals/replicate.py`, reads the kept row as extracted).
- `wip/alt-deals-3`: `tests/test_session113.py` (`test_every_selection_against_the_table`, `test_the_grid_is_only_a_state_one_operator_mostly_serves`), `tests/test_session466.py` (`test_every_cell_of_every_dimension`), `tests/test_session7404_trackers.py` (`test_the_two_readings_of_a_deals_grid_stand_as_they_were`, `test_made_up_deals_key_by_key`).
- `wip/alt-deals-1` passes every deals test (123 passed): the floor is applied in the views, and the library's `fold` is unchanged.

## Lines not built

- **Line 2, a sentence in the extraction's prompt and the older rows read again:** a model call for every row of the affected months (spend USD 0 until 1 December). Needs the key: about 51 rows (8.8 percent of the deals) would leave every count, by the faults file's count; the cost is one extraction call a row, not estimated here.
- **Line 5, the rows whose every source is public shown:** no figure moves (every one of the 578 deals rests on a source the registry marks internal), and the hold stands.

## Decisions made without you

- **Line 1 at 0.7, not 0.5:** the larger of the two floors the line names and the one the Roundup's tables use; at 0.5 the impact file counts 525 deals and every MW kept. The floor is one constant (`SURE_FLOOR`).
- **The floor is applied to each deal as folded**, by its kept row's confidence, as the impact file counted (applied to the rows before folding it gives 282 deals and 22,138 MW).
