# Session 2239 (chain 156, deals and datacenters) report: the comparables

6 November 2026, about 09:21 to 09:45 UTC, portable-laptop (code role), unattended. Worktree `erw-2239` on `wip/2239-deals`, cut from `wip/2238-deals`. Model spend **USD 0**. Nothing deployed (`/deals` stays `review`); no warehouse data written.

- **`site/lib/deals2.ts`**: the disclosed prices of PPAs and offtakes (`priced`, `priceCells`): by technology, grid or year, the count always, and the median, lowest and highest where three or more state a price (the comparables' rule of session 466); each cell's records kept for its hover; `place()`, a reader's price against the first scope with three prices (its technology in its grid, else its technology, else every priced deal), as how many are below, equal and above, with their median; `priceKey` (`deals|price_<count|median|low|high>|<dimension>|<value>`).
- **`site/app/deals/comparables/view.tsx`**: the section "Disclosed prices" (`#prices`, `?pby=technology|grid|year`), each figure keyed and its hover the deals it is of (date, parties, price); with no priced deal it says so and links the method. **`PlaceDeal.tsx`** (new, client): technology, grid, MW and price typed in, one line out; nothing stored or sent (no storage, no request, `autoComplete="off"`); the line places the price among the stated prices and judges nothing.
- **`site/scripts/check-values.mjs`**: recomputes every new key with the page's own functions on every row of `energy_deals`, folded pairs once, as for the comparables.
- **The figure "6 of 18,358 stories"** was taken off the page and the table's tip (a number on a page carries a key or is not shown); it stays in the audit file.
- **`tests/test_session2239_deals.py`** (8 tests); with 466 and 2238: 25 passed, 1 skipped. The type check: no error in the deals files (the 15 of a build's generated files, as on main; `node_modules` linked from `erw-2238`).

## What the page will show today

No stored deal states a price in US dollars per MWh (the audit's ground: 0 of 529), so the section says that no PPA or offtake held states one, and the placement says there is nothing to place a price against. The section fills as the extraction finds prices; the stories the ERW reads rarely state one (the audit's "What the extraction cannot see").

## Decisions made without you

1. **The scope widens** (technology in grid, then technology, then every priced deal) to the first with three prices, and the line names the scope it used; a narrower scope with fewer than three is never used.
2. **The MW typed narrows nothing**: with almost no priced deal, a size band would leave none; it is shown beside the line.
3. **The lowest and the highest follow the median's rule** (three or more), so a cell of one or two deals shows no single deal's price as a range; its count is shown and its deals are in the hover only when there are three.

## For Samuel's ruling

- None new.
