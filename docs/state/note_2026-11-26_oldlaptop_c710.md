# Note of 26 November 2026: chain 710 on the old laptop (sessions 10200 to 10208)

Energy Research Warehouse (ERW). Chain file: `queue/done/710-night-26-november-oldlaptop-weekend-page-model-audits.md`. Progress: `docs/state/progress_c710.md`. Written at about 12:20 UTC by session 10201.

## How the chain ran

- Session 10200 (the chain worker's) took the file and wrote resume file 711, then was stopped by Samuel at about 11:00 UTC. Its one unpushed commit is on `wip/c710-stray-2026-11-26` and was re-applied on main.
- Session 10201 took resume file 711 by Samuel's word, wrote 712, and ran parts A to D with agents in three worktrees: sessions 10202 (weekend page), 10203 (datacenter), 10204 (Automated Analysis), 10205 (Grid), 10206 (board, and the datacenter words branches drawn), 10207 (severance), 10208 (weekend page kept current).
- No model was called. No site build. Nothing landed from this machine; no warehouse table written.

## The weekend page

- https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/weekend-2026-11-28.md
- Tier 1, 30 minutes: a first item (held grids' figures in public files) and ten decisions.
- Tier 2, 132 minutes more: the ranked list's groups, the five audits of tonight, the two of 20 November, the week's smaller rulings, security.
- Tier 3, about 5 hours more: findings (Stata, then approve), signatures, licenses, 31 pages to look at.
- Words to paste: about 5 minutes. To be kept current until Saturday 28 November 10:00 PST.

## The five audits (each: arithmetic, three worst, fixes)

- **What a datacenter pays** (`docs/reviews/datacenter-model-audit-2026-11-26.md`): arithmetic right, 131 figures to the digit.
  - Worst: "All-in power per GPU-hour" holds no delivery, ancillary or loss charge (high); 20-year scenarios discount flat prices at a rate that holds inflation (USD 261.19 million against 299.42 at 2 percent); California priced at generator hubs, not the load's aggregation point.
  - 5 word fixes requested (rows 59 to 63); 3 wait for a ruling.
- **Automated Analysis** (`docs/reviews/analysis-model-audit-2026-11-26.md`): the code computes what the notes say, to the digit.
  - Worst: held and paused grids' figures in public files (the impact CSV, 190 gallery charts, weekly results); no-trend series pass the five tests 12 to 83 percent of the time and no draft says how many were tried; tight hours picked by net load make solar's share fall by construction.
  - Draft findings 3 and 6 shown wrong, states untouched. 3 word fixes requested, 1 waiting on `wip/audit-battery-6`; 9 wait for a ruling.
- **The Grid tool** (`docs/reviews/grid-model-audit-2026-11-26.md`): arithmetic right.
  - Worst: the Lower 48 is not the sum of the seven grids; a grid's net export reads each tie from the authority first in the alphabet (PJM moves 990 MW in the median hour if read from its own report); carbon is an average with imports at EIA's estimate.
  - 4 word fixes requested (rows 68 to 71); 3 wait for a ruling.
- **The price board** (`docs/reviews/board-model-audit-2026-11-26.md`): arithmetic right.
  - Worst: the page keeper keeps an older row when a new build is shorter (98 rows stale; ERCOT's day-ahead tile 16.18 for 20 November beside 46.31 for 25 November); NYISO and ISO-NE rows written after the hold sit in `site/data/board.json`; CAISO's week uses Monday to Friday against the group's Monday to Saturday, unsaid.
  - 3 word fixes requested (rows 76 to 78; 76 and 77 after window E's board group); 1 waits for a ruling; the builder fixes are data requests 13 and 14.
- **The severance tool** (`docs/reviews/severance-model-audit-2026-11-26.md`): arithmetic right, 907 figures to the cent.
  - Worst: the Lease tab taxes every month back to 2023 at today's rates; Louisiana's posted-price floor is said but not applied; New Mexico's district levy left out puts a total 13.6 to 19.5 percent low.
  - 4 word fixes requested (rows 72 to 75); 1 waits for a ruling.
- In all: 19 word fixes requested, 1 waiting on another branch; 17 for Samuel's ruling, each with its measured effect; 10 data requests (rows 6 to 15 of `docs/state/data_requests_five_tools.md`).

## Part D goes on: more audits in the same form (sessions 10209 onward)

- Each found the arithmetic right. Each words fix is a requested row in `docs/state/landing_request_oldlaptop.md`; each figure fix is a test on its own branch, for Samuel's ruling; each measurement this machine cannot make is a row in `docs/state/data_requests_five_tools.md`.
- The trader view (`docs/reviews/trader-model-audit-2026-11-26.md`): 6 findings; rows 89 to 93; SPP's real-time table is held but never read; heat rate against the next day's gas; off-peak week by days, not hours.
- The curtailment tracker (`curtailment-model-audit-2026-11-26.md`): 7 findings; rows 85 to 88; held grids' hour counts printed; "What it is worth" is a hub price while 81 percent was local congestion.
- The datacenter power tracker (`tracker-model-audit-2026-11-26.md`): 6 findings; rows 79 to 84; a third of the MW is one Utah row joined from two stories.
- The storage page (`storage-model-audit-2026-11-26.md`): 7 findings; row 99; "US Lower 48" leaves out CAISO, NYISO and PJM.
- The interconnection queues (`queues-model-audit-2026-11-26.md`): 6 findings; rows 94 to 98; CAISO's hybrids counted at both parts (32.1 percent above a like count).
- The consumption page (`demand-model-audit-2026-11-26.md`): 7 findings; rows 100 to 104; from 2018, CAISO's and MISO's growth is negative.
- The deal tracker (`deals-model-audit-2026-11-26.md`): 6 findings; rows 105 to 110; the held deals CSV and its evidence file are tracked in the public repository.
- The project map (`map-model-audit-2026-11-26.md`): 6 findings; row 111; 50 datacenters with 25,158 MW have no point.
- The policy monitor (`policy-model-audit-2026-11-26.md`): 8 findings; row 112; a held table shown in the monitor view; 15 large-load orders dropped on 20 November.
- Congestion (`congestion-model-audit-2026-11-26.md`): 7 findings; row 113; SPP and CAISO places ranked in one list across different references.
- Grid conditions (`conditions-model-audit-2026-11-26.md`): 11 findings; row 114; no screen for impossible hours (PJM peak 215,682 MW against 108,513).
- The prices pages and map (`prices-model-audit-2026-11-26.md`): 6 findings; row 115; ERCOT load zones called hubs; SPP October "not held" though held.
- AI's energy (`ai-energy-model-audit-2026-11-26.md`): 8 findings; row 116; 5 of 23 rows are a company's whole consumption.
- The states page (`states-model-audit-2026-11-26.md`): 8 findings; row 117; the trade row's sign label is backwards (Virginia imports 45 TWh net, the page reads as exports).
- The industry page (`industry-model-audit-2026-11-26.md`): 8 findings; row 118; the whole industrial sector set beside manufacturing fuel, half of it.
- The supply page (`supply-model-audit-2026-11-26.md`): 5 findings; row 119; California's gas burn compared across a change of source (-22.8 percent against +0.8 like for like).
- The events pages (`events-model-audit-2026-11-26.md`): 9 findings; row 120; the weather share fitted on the event days too (Uri's effect changes sign fitted on the baseline alone); the paper's columns untouched.
- The same held-rows-in-public question gathered in the weekend page's tier 1 first item.

## What waits for Samuel, in plain words

- Whether to take held and paused grids' figures out of the public analysis files and the board file (tier 1, first item).
- The ten decisions of tier 1, and the rulings of tier 2 (the 17 from tonight's audits each say what moves and by how much; leaving them as they are is the default).
- Whether to stop any of tonight's 19 word fixes before window A lands them ("hold").
- The battery game branch `wip/7535-play-battery` (row 33 of the old laptop's landing file) was never requested: request it or not.

## Decisions made without you

- Parts A to D were run side by side by agents instead of one after another; the progress file was written by session 10201 alone.
- Word fixes that change no page (rows 64, 65, 67, 78) were requested without a drawing, as there is no page to draw.
- Documents pushed to main without a before and after snapshot: they change no file a page reads, there was no freeze, and this machine may not build or read the live site tonight.

## Problems

- Agent rule slips, reported by the agents themselves: in session 10204, one commit message went through a heredoc and one `python -c` ran; in session 10202, a push with `--force-with-lease` was refused by the permission check and never ran. Nothing was forced.
- `docs/state/note_2026-11-21_data.md` to `note_2026-11-29_data.md` hold October notes under future dates.
- Two tests fail on clean origin/main on this machine once `node_modules` is present (`tests/test_session1898.py`, `tests/test_session137.py`); `tests/test_session705.py` fails on clean main too. None is caused by tonight's work.
- The worktrees `erw-c710-a`, `-b` and `-c` each carry a junction `site/node_modules` to the main copy's; remove the junctions before removing the worktrees.
