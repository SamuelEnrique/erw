# Roadmap item 2, its state for the Sunday review (written 6 November 2026, session 1507, chain 158)

A draft for Samuel; `docs/roadmap.md` is not edited (only a person writes there). Item 2's `done:` line: "each of the five has a method note signed by Samuel, a replication a reader can run, a cross-check table against published figures, and a decisions block; Automated Analysis in its final form; the Grid tool one page".

| Tool | Method note | Signed | Replication a reader can run | Cross-check table | Decisions block |
|---|---|---|---|---|---|
| What a battery earns (`/cost-of-power/battery`) | `docs/methods/battery_earns_algorithm.md` | **no**: its "Sign-off" block is empty (added by session 1527) | **yes**: `replication/battery/` (`replicate.py`, 22 of 22 of the page's figures; `replicate.do`, not yet run in Stata) | **yes**: the note's "Cross-checks" (Lazard, the ATB, Modo Energy's ERCOT 2025 nowcast, ERCOT's fleet) | the shared scenario block (section 11.1, `components/decisions/ScenarioBlock.tsx`); no "decisions on the page" section of its own |
| What a generator earns (`/cost-of-power/seller`) | `docs/methods/generator_earns_algorithm.md` | **no**: its "Sign-off" block is empty | **yes**: `replication/generator/` (13 of 13; `replicate.do` not yet run) | **yes**: the note's "Cross-checks" | **yes**: section 13 |
| What a datacenter pays (`/cost-of-power`) | `docs/methods/datacenter_pays_algorithm.md` | **no**: its "Sign-off" block is empty | **yes**: `replication/datacenter/` (14 of 14 since session 1523: the one difference was the live set's moving window, the page's own code giving 309.84 on the file); `replicate.do` not yet run | **yes**: the note's "Cross-checks" | **yes**: section 12 |
| Automated Analysis (`/analysis`, now `/research`) | `docs/methods/automated_analysis.md` and the scanner's and findings' notes | **no**: the findings note's "Sign-off" block is empty (added by session 1744) | **yes**: `site/public/findings/erw_2026_research_replication.py` (session 381) and each card's do-file; ten cards, 363 of 363 figures equal the cards' JSON on 6 November (session 1744; the findings note's "Replication"); the do-files not yet run in Stata | **yes**: `automated_analysis_findings.md`'s "Cross-checks" (session 381; two of its four rows are against the thesis) | **no** (a page change; its "final form" is item 2's own clause) |
| Grid (`/grid`; `/network`, `/mix` and `/ask` redirect to it) | `docs/methods/grid_network.md` | **no**: its "Sign-off" block is empty (added by session 1743) | **yes**: `site/public/grid/erw_2026_grid_replication.{csv,do,py}` (session 266); the mirror on the committed CSV prints the do-file's expected values on 6 November (session 1743; the note's "Replication"); the do-file not yet run in Stata | **yes**: the note's "Cross-checks" table (session 381: eleven rows, EIA-930 against Form EIA-923, the operators' own figures and the ties' two sides; session 1528 corrected this cell, which said "no table") | **yes**: "Decisions on this page" on `/grid` (`data-decisions="299"`, the rulings of 18 October). The page is one page since session 299; its brand waits for the mockups (the roadmap's hold) |
| (also) the explorers (`/explore/*`, platform tool 5) | `docs/methods/explorers.md` (session 1496) and the tables' notes | no | the figures are rows of tables; the peak premium's thesis reproduced to the cent; each table downloadable, the rows drawn too | no table | not a decision tool |

**What would close the first three, in order:**

1. Your Stata run of the three `replication/<tool>/replicate.do`, from their folders. Their closing lines print the differences.
2. Your signature in the three notes' "Sign-off" blocks (the battery's added by session 1527).

**What item 2 still asks beyond the three:** Automated Analysis's final form, and the Grid tool as one page, which waits on the brand's mockups.

**Corrected by sessions 1743 to 1745 (chain 195, 6 November 2026).** The Grid and Automated Analysis rows said "no" for a replication, a cross-check table and the Grid's decisions block. All three were in the repository: the Grid's replication since session 266, Research's since session 381, the Grid's decisions block since session 299. They were named only in the review packs (`docs/reviews/packs/grid.md` and `research.md`, "Against roadmap item 2"), not in the method notes. Sessions 1743 and 1744 added a "Replication" section and an empty "Sign-off" block to `grid_network.md` and `automated_analysis_findings.md`; session 1745 corrected the two rows above. What would close those two rows, beside the first three:

1. Your Stata run of `site/public/grid/erw_2026_grid_replication.do` and of the cards' do-files in `site/public/findings/`.
2. Your signature in the two notes' new "Sign-off" blocks.
3. For Research, a decisions block on the page (a page change) and your word on its form and on the cards' `.py` downloads.
4. For the Grid, your word on whether the one page of session 299 closes "the Grid tool one page" before the brand's mockups.
