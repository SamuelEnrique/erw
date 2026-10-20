# Chain of 20 October 2026, night: sessions 351 to 356, code machine (samueloldlaptop), unattended

Taken from the queue after the chain of 19 to 20 October (sessions 328 to 335). The code for the four weaknesses the five packs rank first (section 6 of each): the years ahead, the node, credits and contracts, and Research's statistics. Every change is default-neutral: at default inputs every existing number is identical to before (check-values proves it); new inputs default to today's behaviour. Rulings: Samuel, 20 October, in chat; his answers to the six questions of review_2026-10-19_code_pm.md: /terms names the email a reader leaves and says Samuel answers within a week with no promise of an analysis; /prices keeps a day-ahead column whose cell says the newest hour; no range slider; heat maps one color for magnitudes and a two-hue diverging ramp where the figure is signed; the two maps stay as they are; the hunt's floor stays at one typical move.

## Rules for every session

Every python command uses .venv\Scripts\python.exe. Precheck first (exit 1: stop). Unattended; reversible choices under "Decisions made without you"; irreversible ones under "For Samuel's ruling", undone. A failed session stays on wip/ and the next starts. Landing on main when green: freeze status, snapshot before and after, check-values, pull and merge origin/main first (the data machine lands tonight; the third machine does not). NO LANDING 14:00 to 16:15 UTC or 22:30 to 23:45 UTC. No warehouse data written; pulls none; model spend USD 0. One heavy process at a time; python scripts/duty.py beat before each build. tokens.css and the shared components only; Impeccable once per page; screenshots at 1280 and 390. No em dashes. Reports as the chain of 18 October's. Read sessions 314 to 335's reports; do not redo their work. Where a table this chain reads has not landed from the data machine yet (price_years, node_basis_daily, ercot_4cp_intervals), build against the table's documented shape in its methods note, read it when present, and show "not yet held" otherwise; never a placeholder number. Last step of the last session: docs/state/review_2026-10-20_code.md, then python scripts/chain_queue.py next; exit 0 run the printed file; exit 3 say CHAIN DONE.

## Session 351: the six answers, and the words

Long end 1:15. /terms: the email line and the one-week answer; /prices: the day-ahead cells as ruled; the heat maps: the diverging ramp where the figure is signed (the day-ahead minus real-time maps, the capture spread), one color elsewhere, in the shared component; the hunt's floor documented as ruled. Land.

## Session 352: the price years

Long end 3:00. All three economics pages (/cost-of-power/battery, /cost-of-power/seller, /cost-of-power): a "Price years" setting in the Assumptions box: the last twelve months (default, unchanged), any held calendar year, the three-year and seven-year averages, or a reader's window, reading the data machine's price_years table (its shape: tool, grid, asset or configuration, window, revenue or cost per unit, the months counted). Scenario A and B, the results table and the sensitivity all follow the chosen window; the headline says which window prices it; a line under the results says what the same project earns under the best and worst held year. Pack section 6 item 1 of each tool rewritten to say what the page can now show. Land.

## Session 353: credits and contracts on the generator

Long end 2:30. /cost-of-power/seller: an investment tax credit and a production tax credit as inputs in Financing (default 0; the ITC at year 0 against equity as the battery's; the PTC per MWh for ten years; the hover names the credit and says to confirm it); a settlement-point choice beside the hub (the hub, or a load zone the tables hold, or, when node_basis_daily is held, a percentile of the node basis distribution: the median point, the 25th, the 75th), the figure saying which; the PPA's shape (flat, or the asset's own shape) as a scenario setting. Every default number identical. Land.

## Session 354: the datacenter's charges

Long end 2:30. /cost-of-power: the 4CP saving as a scenario toggle (a load off in ERCOT's four coincident-peak intervals, read from ercot_4cp_intervals, saves the transmission component the delivery table prices; the page says the intervals are known only after the fact); the node basis band from node_basis_daily when held; capacity charges outside ERCOT only where a public table holds them, "no public figure" otherwise. Every default number identical. Land.

## Session 355: the node basis on the battery, and Research's error bars

Long end 2:30. /cost-of-power/battery: the node basis as a band on the revenue chart and a line under the headline (what the median storage settlement point earned against the hub over the same months) when node_basis_daily is held. /research: every card's regression figure carries its Newey-West standard error from the engine (the data machine's session), a caveat line on multiple comparisons naming the count of claims tested that round, and the step-versus-trend flag where the engine sets it; the card page and the library both. Land.

## Session 356: the night note

Long end 0:45. docs/state/review_2026-10-20_code.md: one line a session with its URL, every screenshot folder, every decision made without Samuel, every item waiting for him; the third machine's branches wip/345-impact and wip/348-map named as the next landings with their "To finish" lines read from docs/state/review_2026-10-20_third.md. Push, then the queue step.
