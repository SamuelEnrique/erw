# What main's Digest still writes: the issue of 23 October 2026, counted against the dry run

Energy Research Warehouse (ERW), session 2103 (chain `queue/done/084-day-23-october-portable-deals-4.md`, portable-laptop). The periodicals' code of sessions 801 to 817 sits on `wip/818-periodicals` and is not on main (session 2100: the landing is blocked by a data branch in flight, by rulings item 7 and by this machine's memory). So the Digest the daily run wrote on 23 October at 15:45 UTC (`docs/digest/2026-10-23.md`, 276 scored stories) is main's code's. This review counts it the way `docs/reviews/periodicals-dryrun-2026-10-23.md` (session 807) counted the stored issue of 21 October and the dry run, so the owner sees what the landing changes in tomorrow's issue. The counter is the branch's own `why_check` and `figures_of` of `warehouse/news/brief.py` (`erw-818`), run read-only over the stored issues; no model call, no build, no request. The issue of 22 October is counted beside it.

## Read these first

- **The adjectives are already gone from main's issues, the links are not.** Sessions 470 and 577 reached main after the stored issue of 21 October was written (the dry run's note says that issue was "written by the code before sessions 470 and 577"), and main's `brief.py` now cuts the why lines' adjectives (`HYPE`, line 440). The issues of 22 and 23 October carry 4 and 1 such adjectives against 11 on 21 October. What main still does that the branch does not: it links every item to its outlet, 32 links on 23 October, 15 of them Google News addresses and 31 to outlets whose terms ask for permission (Reuters, Bloomberg, WSJ, Natural Gas Intelligence, OilPrice.com, Rigzone, Hart Energy, Data Center Dynamics, Heatmap News, ANS Nuclear Newswire). The dry run names a held outlet with no link (3 links, 0 Google addresses).
- **The figures are still said twice on four items**, each a top-ten item whose figures line repeats the headline's sum (Kinder Morgan's USD 14.4 billion, SK's USD 350 billion, Welspun's USD 580 million, Westinghouse's USD 1 billion); the dry run's rule leaves 2 of 30.
- **The top ten reads as ten topics today** (no sector with three items: geopolitics and gas have two each), where 21 and 22 October each had three datacenter-power items. The branch's fold ("also" lines under one topic) would have put the two Brent items (top 2 and top 10, both the Saudi attacks) under one line.
- **What the landing changes in tomorrow's issue, in one line:** the held outlets lose their links and are named instead (about 30 links fewer, every Google address gone), the repeated figures fall from about 4 to about 2, two items on one event fold into one with an "also" line, and the movers and the week's numbers appear; the adjectives it would also cut are already cut by main.

## The counts, side by side

| | Main, 23 October (this review) | Main, 22 October (this review) | Stored, 21 October (this review; the dry run's count) | Dry run, 21 October (session 807) |
|---|---|---|---|---|
| Items (top ten, By sector, AI and power) | 30 | 30 | 30 (33 with the three policy actions, which this counter does not read) | 30 |
| Why lines with an adjective of the list | 1 | 4 | 11 (11) | 0 |
| Items whose figures line repeats a headline figure | 4 | 4 | 9 (9) | 2 |
| Why lines of two sentences | 0 | 3 | 2 | not counted |
| Top-ten sectors with three or more items | none (ten sectors: geopolitics 2, gas 2, the rest 1) | datacenter power 3 | datacenter power 3 (the same) | none |
| Links, and Google News addresses among them | 32, 15 | 37, 15 | 36, 17 (39, 17 with the policy actions' three) | 3, 0 |
| Links to outlets whose terms ask for permission or are not read | 31 | 35 | 35 | 0 (named, not linked) |

The counter reproduces the dry run's counts for the stored issue of 21 October on the adjectives (11) and the repeated figures (9); its links are three fewer because the three policy actions of "By sector" are written in another shape and are not read as items.

## The worst lines of each kind, 23 October

- **An adjective** (1): By sector, "Trade restriction threatens renewable energy supply chains and could raise deployment costs significantly." ("significantly" is in main's own `HYPE` list, and was not cut: main's `why_line` reads the list on the scorer's line; the branch's `why_check` is the gate that rewrites such a line.)
- **A figure said twice** (4): top 1, headline "Kinder Morgan's project backlog reaches $14.4 billion ..." and the figures line "USD 14.4 billion"; top 5, "$350 Billion" and "USD 350 billion"; top 6, "$580 million" and "USD 580 million"; top 7, "$1 billion" and "USD 1 billion".
- **One event twice in the top ten**: top 2, "Brent climbed above $113 amid Saudi attacks and renewed Iran tensions" (Rigzone), and top 10, "Brent crude reaches more than a five-month high on Houthi-Saudi attacks and a UAE oil spill" (Reuters); By sector adds two more Brent lines (OilPrice.com, Bloomberg). The branch folds a cluster's items under one line.
- **Held outlets linked** (31 of 32): every Reuters, Bloomberg and WSJ item through a Google News address (15), the rest through the outlet's own address.

The same for 22 October: 4 adjectives ("critical" three times, "significantly" once); 4 repeated figures (Google and Voltus's 1 GW, SpaceX's 13 GW, Nebius's 50 MW, New England Wind's 2 GW); 3 why lines of two sentences (the figures line run on from the why line: "1 GW VPP to support data center power demand in constrained PJM grid. 1,000 MW;").

## Decisions made without you (session 2103)

- The counter is this session's script over the stored Markdown (the branch's `why_check` and `figures_of` imported from `erw-818`, the issue's items parsed from the three sections); the dry run's own numbers are quoted from its review, not re-run (a run would be a model call).
- The three "By sector" policy actions are not counted as items (their shape differs); the table says so.
- "Links to held outlets" uses `license_verdicts.csv`'s verdict for each link's outlet name through `scripts/licenses.py`'s `canon`, as `public_rows.py` does.

## For Samuel's ruling

- None new. The landing of `wip/818-periodicals` waits on rulings item 7 (`docs/reviews/deals-rulings-2026-10-23.md`); this review says what it changes.
