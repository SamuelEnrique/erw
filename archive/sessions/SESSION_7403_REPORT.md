# Session 7403 report: the datacenter tracker's cross-check, its do-file and its faults

Energy Research Warehouse (ERW). Chain 303, portable-laptop, 16 November 2026, about 09:39 to 09:55 UTC. Model spend: USD 0.

## What was done

- **The cross-check** (`docs/methods/crosschecks/datacenter_tracker.md`): ten rows, ours beside the publisher's figure, the gap, and why they differ. No figure adjusted.
  - Berkeley Lab's report of 19 December 2024 (176 TWh in 2023; 74 to 132 GW in 2028): the tracker states 75 MW as operating and 28,254 MW in all.
  - EIA's outlook of November 2026 (4,390 billion kWh generated in 2026): EIA publishes no count or megawatts of datacenters, so this is a scale check.
  - ERCOT's own large-load totals (8,927 MW approved, 3,900 observed, 19 June 2026), its preliminary forecast of 15 April 2026 (367,790 MW by 2032) and its 140,000 MW of submissions: the tracker's Texas is 47 sites and 457 MW.
  - PJM's load report of 14 January 2026 (65,733 MW of summer peak growth in ten years): the tracker's PJM is 11,618 MW from 3 facilities.
  - Dominion (29 September 2026: about 54 GW under contract, a 4.8 GW billing peak): the tracker's Virginia is 33 facilities and no megawatt.
  - AEP (28 October 2026: 84 GW of incremental contracted load by 2031): three times every megawatt the tracker's news stated.
- **What the table says:** the tracker is a list of named sites, not a measure of megawatts. That is now said in the note, the decisions and the table.
- **Web reads** (rule 9): each host's robots file first, 09:40 to 09:43 UTC; every figure read from the publisher's own file, none from a news summary. Facts with links, no quoted text. Not requested: MISO (paused); the SEC's EDGAR (it asks for a contact address).
- **The do-file** (`replication/datacenter_tracker/replicate.do`): the five headline figures, expected values at its top (458; 274; 28,254; 21; ERCOT 8,927). Not run: Stata is not on this machine. Its Python mirror, `replicate.py --headline`, prints the same five lines.
- **The faults file** (`docs/reviews/datacenter-faults-2026-11-11.md`), rows 15 to 21: one site fault fixed with a test (15), one ruling (17), five for the data machine (16, 18 to 21). The four `ruling` rows restated in plain words with their defaults.
- **Tests:** `tests/test_session7403_trackers.py`, 7 pass; with the chain's other two files, 23 pass.

## Needs the key

- **The four megawatt rows found wrong against their stories' own words** (faults rows 18 to 21: a tenant named as operator, 1,000 MW; a fuel-cell plant's 702 MW; a turbine project's 1,200 MW; the Utah join, 9,400 MW). Correcting them is a re-extraction of those facilities' stories, or `--reextract` of the news table. Estimated cost: under USD 1 for the four rows' stories (about ten stories at the extraction's batch price); the whole table's rebuild is the data machine's to price from `api_cost_ledger`, which this machine did not read. Not run.

## For Samuel's ruling

- **PJM's two figures.** PJM's data license forbids a non-member to republish its data feed. The two figures in the table are from a report PJM marks "For Public Use" and from Dominion's presentation on PJM's committee page, stated as facts with links. Default taken: kept. If you rule they count as PJM's data, the two rows come out.
- The four rulings of the faults read and the one of row 17, each with its default, are in the method note's section 13.

## Decisions made without you

- Two utilities stand for "the largest utilities" (AEP and Dominion): each states its figure in a file this machine could read. FirstEnergy's is on EDGAR only as far as this session found.
- The gap column says "not a gap" where the two figures measure different things, and gives the ratio.

## Commit

- `wip/7400-trackers`: this session's commit, named in the progress file.
