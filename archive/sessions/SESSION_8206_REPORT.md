# Session 8206 report (chain 502, lab-desktop second window)

19 November 2026, 11:47 to 11:58 UTC. Opus 5.5. Model spend: USD 0. Parts B and C checked at the start: both still waiting.

## Family 6, large loads: 15 drafts

- `docs/findings/large_load/`, loaded in state draft; second pass 15 of 15 reproduce; 15 of 15 do-files hold (all 291 of the hunt's do-files hold).
- The tables are filings, not series, so a claim is a figure across the filings that state it, with its own five tests (`deep/large_load.py`).
- Three from `utility_large_load_tariffs` (public):
  - The minimum contract term: 10 years at the median of 13 filings, from 1 year (Niagara Mohawk Power, New York) to 15 years (Santee Cooper, South Carolina).
  - The minimum bill: 80 percent of contracted demand at the median of 11 filings, from 75 to 100 percent.
  - The size from which a tariff applies: 47.5 MW at the median of 20 filings, from 0.5 MW (NYSEG) to 150 MW (Alabama Power).
- Twelve from `large_load_wait_summary` (internal; every sentence opens with "License needed" and names the table): the bounds of the median wait at Alberta's operator, Bonneville and the New York ISO. The strongest: at Bonneville the median time from request to energized for 248 requests was at least 67.5 and at most 128.5 months.

## Not drafted, and why

- `utility_large_load_rules` and `state_large_load_laws` hold their sizes and terms as free text; a read found a pattern would misread them ("Not stated as a size in the letter ... 25 MW" read as 25 MW; "5,000 kW" not read). No figure is drafted from free text.
- `utility_large_load_queue_totals` holds its figures as printed text; its `mw` column is empty. The claim is written and runs when the column is filled.

## Code

- `warehouse/analysis/findings/deep/large_load.py`; `check.py` reads a claim's named figures ("Expected figures:") and `check_do.py` accepts a do-file that ends by displaying them; on `wip/8202-findings` (`5d98357ac`).

## For the data machine

- `utility_large_load_queue_totals.mw` is empty in all 34 rows; the figures are in `x_figure` as text.

## Needs the key

- Nothing.
