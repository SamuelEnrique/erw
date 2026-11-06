# Roadmap item 2: the five tools' four items, after chain 208 (rewritten 6 November 2026, about 23:25 UTC, session 3710)

Energy Research Warehouse (ERW). Chain 208 (`queue/done/208-night-6-november-portable-sellable.md`), the portable laptop. For the owner's Sunday review. `docs/roadmap.md` is not edited (only a person writes there).

Item 2's `done:` line: "each of the five has a method note signed by Samuel, a replication a reader can run, a cross-check table against published figures, and a decisions block; Automated Analysis in its final form; the Grid tool one page".

- **The before state** is the first version of this file (session 3700, commit `902be2878`) and chain 158's `docs/state/roadmap_item2_state_2026-11-07.md`.
- **Where the work is:**
  - sessions 3701 to 3705 are on `wip/3701-sellable` at `f61920f88`, whose gate ran in session 3706 (its result is in session 3706's report);
  - sessions 3707 to 3709's cross-check files are on the same branch, after it.

What each column means:

- **Method note:** a note under `docs/methods/` that states the method. "Signed" is a filled "Sign-off" block, which only the owner writes.
- **Replication:** a package a reader runs from the tool's public files (and, for the Grid tool, the warehouse's tables), which prints each figure beside the page's with the difference: `replication/<tool>/`, Python (`replicate.py`) and Stata (`replicate.do`).
- **Cross-check table:** each headline figure against a figure a named publisher states, the gap and its reason, or said to have none: `docs/methods/crosschecks/<tool>.md`, besides the notes' own "Cross-checks".
- **Decisions block:** every assumption, its default, its source and how to change it.

## The five tools

| Tool | Method note | Signed | Replication (Python; Stata) | Cross-check table | Decisions block |
|---|---|---|---|---|---|
| What a battery earns (`/cost-of-power/battery`) | present: `docs/methods/battery_earns_algorithm.md` | **no** | present: `replication/battery/`, 22 of 22 (chain 158); the do-file not yet run in Stata | present: `docs/methods/crosschecks/battery.md` (22 figures, 8 with a counterpart) and the note's "Cross-checks" | present: the note's section 6 (each assumption, its value, its source and whether and where the reader can change it) and the scenario block on the page; the page has no list of its decisions as the other two pages have |
| What a generator earns (`/cost-of-power/seller`) | present: `docs/methods/generator_earns_algorithm.md` | **no** | present: `replication/generator/`, 13 of 13; the do-file not yet run | present: `docs/methods/crosschecks/generator.md` (13 figures, 4 with a counterpart) and the note's | present: the note's section 13, `GENERATOR_DECISIONS` on the page |
| What a datacenter pays (`/cost-of-power`) | present: `docs/methods/datacenter_pays_algorithm.md` | **no** | present: `replication/datacenter/`, 14 of 14; the do-file not yet run | present: `docs/methods/crosschecks/datacenter.md` (14 figures, 1 with a counterpart, two rows) and the note's | present: the note's section 12, `DATACENTER_DECISIONS` on the page |
| Automated Analysis (`/research`) | present: `docs/methods/automated_analysis.md` (with `automated_analysis_findings.md`, `automated_analysis_scanner.md`); its new sections "Replication", "Cross-checks", "Decisions" (sessions 3701 and 3702) | **no** | **present (new):** `replication/analysis/`, 78 figures of the page; 65 of 66 computed inside the tolerance, 1 known difference (the weekly score: the chart file holds 102 of the 104 changes ranked), 10 "license needed", 2 not in a download; `replicate.do` covers the cards' figures, not yet run | **present (new):** `docs/methods/crosschecks/automated_analysis.md` (9 rows with a counterpart: ERCOT's market monitor's 2025 report, EIA-860M, EIA's retail prices, CDC, the owner's thesis; every other callout named with none) | **present (new):** 35 assumptions in the note and `replication/analysis/assumptions.json`, held to each other by `tests/test_session3702.py` |
| The Grid tool (`/grid`) | present: `docs/methods/grid_network.md` (with `generation_mix_hourly.md`, `emissions.md`, `clean_energy.md`, `ask.md`); its new "Replication" and "Decisions" sections (sessions 3703 to 3705) | **no** | **present (new):** `replication/grid/`, 188 figures; 147 of 158 computed met (Network and Gravity 85 of 85, the Clean tab's carbon months 14 of 14, the Ask panel's stored answers 48 of 59 and 11 a known difference: copies of their tables older than the answers), 22 "license needed"; `replicate.do` and `replicate_ask.do` (24 plain queries), not yet run; the Mix tab's latest hour is a live read and is not in the comparison | **present (new):** `docs/methods/crosschecks/grid.md` (the network against EIA-930's balance, Form EIA-923, carbon intensity in 2023 against eGRID2023 and EIA, the Ask panel against the monitor's report) and the note's eleven rows | **present (new):** 25 assumptions in the note and `replication/grid/assumptions.json` (with the owner's rulings 1a, 2c, 4b and 6a), held to each other by `tests/test_session3705.py`; the page's own block of rulings as before |

## The rest of item 2's line

- **Signed by Samuel:** none of the five notes. Signing is the owner's act.
- **Automated Analysis in its final form:** the owner's clause; no session can say it is met.
- **The Grid tool one page:** one page of four tabs and the Ask panel since session 299. Its design waits for the brand's mockups (the roadmap's hold).

## What waits for the owner, in order

1. The Stata runs of the five do-files: `replication/<tool>/replicate.do`, and `replication/grid/replicate_ask.do` through `replicate.do`.
2. The five signatures.
3. Whether Berkeley Lab's public data files may be read (session 253's open ruling). They would give the generator's price received, capture rate and breakeven PPA, and Research's queue card, a published counterpart.
4. Whether the Mix tab's latest-hour figures may be replicated against the live set. The code is `replication/grid/replicate.py` `mix_now()`; this chain read no row of the live set.
