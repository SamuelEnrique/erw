# Session 3760 report: the large-load tariff registry from the research file, with 3761 to 3763

Energy Research Warehouse (ERW). Chain 211, sessions 11 to 14 of 24, data machine (lab-desktop), 12 November 2026. Opus 5.5. Model spend USD 0. Requests: 3760 35 (22 robots, 13 documents), 3761 8 documents, 3762 7 (1 robots, 6 documents); each a single GET through a capped probe, every host's robots read first, none naming an AI agent.

- **3760, adopted tariffs** (`acf82eb12`): 14 schedules verified in the documents the research file cites, each figure with its page and printed words.
  - Evergy Missouri Metro and West LLPS: 75 MW, 80 percent, ramp plus 12 years, two years of minimum bills as collateral, seasonal demand and grid charges.
  - Ameren Missouri LLCS: 75 MW at 115 kV, 80 percent, $22.43 and $10.66, 4.06 and 3.71 cents.
  - Entergy Louisiana LLHLFPS-L and LPHLF-G, Entergy Texas LIPS, Georgia Power TOU-SC-15 (100 MW, no per-kW charge), SRP E-67 (20 MW, 80 percent), APS XHLF, Alabama Power LPL.
  - Oncor Transmission Service and Rider TCRF ($6.260839 per 4CP kW from 4 October 2026), CenterPoint Houston Transmission Service (per kVA, in notes).
  - **AEP Ohio Schedule DCT held internal** (ruling 4: aepohio.com's terms; PUCO's copy behind a reCAPTCHA).
- **The connector** takes seasonal and voltage variables, `x_status`, `x_license` and `x_notes`. An internal file is kept in the registry but written nowhere public; the header names it.
- **3761, ordered, proposed and framework** (`4a7349559`): Dominion GS-4 (2027 minimums 85 and 60 percent, 25 MW), Duke Energy Carolinas's Large Load Tariff (proposed), Xcel Colorado TL (proposed, 50 MW), NV Energy LGS-X (closed) and LLESA (framework), Alabama Act 2026-610 (framework, 150 MW).
- **3762, connection rules** (`6b9a86691`): PJM's Board letter and EIT, PJM's show-cause proposal, CAISO's straw proposal, ERCOT's batch study cadence, PUCT Project 58000's proposed 25.252.
- **The tables written** under the data lock with the locked script:
  - `utility_large_load_tariffs`: 83 rows, 24 schedules, 18 utilities; written again whole for its new columns; archive `20261112T113024Z-local`.
  - `large_load_connection_rules`: 59 rows, 8 documents; archive `20261112T112956Z-local`.
- **3763, the method notes** (`31c63f598`): the verification rule, the status vocabulary, the row-level license, what waits and why.
  - The cross-check, LLPS or LLCS all-in at 80 percent against EIA-861's 2025 industrial average: Evergy Metro 67.39 against 74.31 USD/MWh; Evergy West 63.90 against 62.63; Ameren 63.24 against 81.92 (its fuel clause outside the printed energy charge).
- **What waits:**
  - Dominion GS-5: its order is on the paused SCC host and no sheet is published.
  - Duke Energy Progress's own leaf.
  - Utah's statute.
  - Evergy Kansas: bot check.
  - The adopted 16 TAC 25.194.
  - MISO ERAS and FERC's orders: only secondhand copies named.

## Decisions made without you

- **AEP Ohio is held, not published:** its rows are kept out of the public table, rather than marked internal inside it. This follows ruling 4 ("the cell blanked with a footnote") without putting a held figure in a public copy. The standard's mixed-license rule (decision 28) stays whole.
- **A figure printed in another unit (per kVA) or in blocks is in notes, not converted.** The registry converts only between units.
- **Each status is written as the document reads:**
  - A closed schedule (LGS-X) is written as adopted, with "closed" in its sector and notes.
  - A utility's fact sheet (LLESA) and a statute (Alabama) are frameworks.
  - A rule for every TSP (PUCT 58000) goes in the rules table, not the tariff table.
- **SRP and the intervenors' copies are public.** SRP's price plan, published by a public power district that no state commission regulates, is treated as public. So are the intervenors' posted copies of filings (SELC for Duke, Earthjustice for Colorado), the mirrors the research file names.

## For Samuel's ruling

- **AEP Ohio's DCT:** recommendation, ask AEP Ohio for written permission or use PUCO's docket copy when a reader can pass its check. Default: held internal.
- **The intervenors' copies (SELC, Earthjustice) as the filed record for public rows:** recommendation, keep them public, since each is a verbatim copy of a public filing. Default: public.
