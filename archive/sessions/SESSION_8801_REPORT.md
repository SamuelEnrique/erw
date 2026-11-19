# Session 8801 report: the morning's drafts finished, part C to 80, the sheet of forty, part E (chain 506)

Energy Research Warehouse (ERW). 19 November 2026, samueloldlaptop (code role), unattended, from about 12:25 PST. Chain file: https://github.com/SamuelEnrique/erw/blob/main/queue/done/506-day-19-november-oldlaptop-findings-audit-shortlist.md. Model spend: USD 0.00, no model call.

## At the top

- **Claude Code stopped the per-draft rebuild of the hourly EIA-930 tables** (regions, tie lines, supply) and France's grid because the machine ran critically low on memory. It is not restarted unattended. About 50 drafts stay "not checked" with "table not on this machine" in the audit; the 24 region drafts it finished were run, and the one table it was halfway through was deleted first.
- **The sheet:** https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/findings-shortlist-2026-11-19.md (forty, no family over six, each with its do-file's address for the Stata run).

## What was done

- Part B finished for all 549: every draft has a verdict (passed, passed after a fix, withdrawn, held, or not checked with its reason). The 23 events drafts that ran reproduce, and their comparisons (the other years held, their mean and the percent) were recomputed from the run: all agree.
- Part C: 80 drafts read against publishers. Pages opened only on www.eia.gov and www.census.gov, robots file and terms first (`hosts.csv`); the rest cite the search result's page, marked "seen in search results, page not opened".
- Part D: twenty, then forty.
- Part E: a second route for each of the forty (`route2.csv`). Six candidates lost their place where the routes differ by more than rounding: Far West Texas mean and 99th-percentile demand (ERCOT's own zone load differs from EIA-930 by 1.7 to 3.5 percent), the Mid-Atlantic June 2025 peak (1.1 percent from PJM's own), the US residential less industrial price (EIA table 5.3: 87.2 against 87.7 USD per MWh), Nebraska's interruption minutes (EIA table 11.3: 547.3 against 542.8), China's gas CO2 (another source by another method), and power construction (its 1993 base, 1.2 percent apart). The Texas January 2026 cold peak agrees with ERCOT's own load within 0.04 percent; US commercial sales equal EIA's table 5.1.
- Found on the way: EIA notes that 2023 to 2024 changes in commercial and industrial sales largely reflect better reporting of data centers and crypto mining; Omaha's commercial sales jump 42 percent in one year (2022 to 2023). Both are written as the risk of the commercial-sales findings.

## Decisions made without you

- A finding whose second route is a publisher's figure seen only in a search result counts as agreeing when the two match at the publisher's precision; each row says the page was not opened.
- Where the only second route differs in its base year but agrees in the latest (power construction), the finding left the sheet, reading the chain's rule strictly.

## For Samuel's ruling

- Whether a 1 percent difference between EIA's published annual price averages and the warehouse's annual figure (the residential and industrial prices) is a fault of the warehouse's annual method. Default: the draft stays a draft, off the sheet.
- Restarting the per-draft rebuild of the hourly EIA-930 tables when the machine has memory to spare (the command is `runs/c506_multi_restore.py`, one table at a time). Default: not restarted.

## Needs the key

- Nothing.
