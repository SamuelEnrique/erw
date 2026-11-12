# Session 1853: the deal tracker's faults fixed, second batch (chain 213, 12 November 2026)

Energy Research Warehouse (ERW). Chain 213, session 1853, samueloldlaptop, unattended, Fable 5.1. 10:37 to 10:42 UTC (corrected by session 1856 from the commit times). Long end 1:30.

## What it did, with commits

- `wip/1853-deals` cut from `wip/1852-deals` in the same worktree (`C:\Users\lossa\Documents\erw-1852`).
- **`4f841a8ed`, rows 7 and 8 of `docs/reviews/deals-faults-2026-11-11.md`:** the tracker's "Deals by month" bars, the charts view's "MW stated, by quarter and kind of supply" stack and "The AI-power deals' share of the MW stated" bars are wrapped in `components/tool/BarsHover.tsx` (session 2201, the brand's card: fog with a rule-colored edge, the period in sans, each series named in its own color with its figure in mono, by pointer and by the arrow keys, Home, End and Escape). One card a month ("deals: 12") and one a quarter (each kind of supply with its deal count and MW in its own color, the MW stated, and in the sub line the deals that state no MW; the AI share, the AI-power MW and the MW stated). The SVGs are unchanged and keep their `<title>` for a reader with no script; the price points and the parties' bars keep their titles and their tables, as the faults file said.
- `tests/test_session1853.py` (3 tests) with 1852's and the deals tests: 53 passed, 1 skipped. `tsc --noEmit` on the branch: exit 0 in 47 s (the build itself is not run: the harness stopped 1852's for memory and asks that it not be restarted unattended).
- Both branches pushed to origin (`wip/1852-deals`, `wip/1853-deals`); rows 7 and 8 marked fixed on main.

## Decisions made without you

- The hover card is added by wrapping, not by redrawing the charts: `BarsHover` places the card by the pointer's share of the plot width, which fits bars by month and by quarter; the horizontal bars (the comparables' medians, the parties) carry their figure at the bar's end and their table, so they keep the title alone.
- No build on this branch: a type check stands in until a landing gate builds it (1856) or the owner allows the retry.

## For Samuel's ruling

- None new.
