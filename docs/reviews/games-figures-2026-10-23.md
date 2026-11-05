# The games' figures: each one, its key and where it says it comes from (23 October 2026)

Energy Research Warehouse (ERW), session 2402 (chain 088, `queue/done/088-day-23-october-portable-policy-games.md`), written on portable-laptop on 23 October 2026 at about 21:50 UTC. The four game and learning pages read for every figure a visitor sees: `/play/battery` (three modes), `/play/ev`, `/learn/bill`, `/learn/problems/<set>` (five sets). For each: whether it is a value of the live set or of a file the checker can read again (then a `Num` with its key, which `check-values.mjs` recomputes), or the page's own model's answer (then its source in words beside it or on hover, and no key). Then the open items of the battery game, from `docs/state/`, the accessibility review of 22 October and the feedback log, each fixed or listed.

## `/play/battery`

| Figure | Where | Key | Its source, in words |
|---|---|---|---|
| Today's level's lowest and highest real-time price | "The day and the battery" | `series\|iso_rtm_hub_prices\|ercot:HB_HUBAVG\|spp_rtm\|<ts>` (two keys, since session 38) | the sentence names ERCOT's hub average and the operating day; the paragraph under it, the table and the method |
| The game's fleet: MW, MWh | "The fleet: fictional and real" | `battery\|fleet_mw`, `battery\|fleet_mwh` | the cell's head says "fictional"; the line says "10,000 homes, each 5 kW and 13.5 kWh (an assumption)" |
| ERCOT's real fleet: MW, units, MWh, units with MWh | the same section | `storage\|iso_mw\|ERCOT\|operating`, `iso_n`, `iso_mwh`, `iso_n_mwh` | the cell's head: "ERCOT's real battery fleet, operating (EIA-860M)" |
| The ratio of the two | the line under them | `calc\|ratio\|storage~iso_mw~ERCOT~operating\|battery~fleet_mw` | the sentence |
| The price now, the day's lowest, average and highest before a play | the game's face | none: the level's prices, drawn in the browser (the same rows the two keys above check for today's level; the famous days are the frozen file `data/battery_levels.json`, every row a warehouse row with its source line) | the preview names the day; "The day and the battery" names the table; Hard's spiked price carries "game rule, not a real price" with the real price beside it |
| Your money, the fleet's money during the play | the HUD | none: the game's own model, moving with every quarter hour | **new hover** on the fleet line: a fictional fleet of 10,000 homes, your earnings times 10,000, a game rule |
| The end table: You, The perfect battery, No battery (earned, bought, sold, average prices) | the end screen | none: the model's answer to a play made in the browser | **new hovers** on the three row heads: the model (`simulate`, `optimum` of `lib/battery.ts`) under the mode's rules on the day's real prices; not a real battery's earnings; no battery is nothing bought or sold, or the roof's power alone |
| The fleet's figures at the end | the end screen | none | **new hover**: fictional, your score times 10,000 |
| The hour lost the most, the replay's figures, the leaderboard's scores | the end screen, the replay, the board | none: the model's, and the stored plays' | the words of each (session 66, 50, 290); the stored plays are the site's own table (`/play/battery`, "What is stored") |

## `/play/ev`

| Figure | Where | Key | Its source, in words |
|---|---|---|---|
| Electricity for homes, cents a kWh; regular gasoline, USD a gallon | the two cards, once a state is chosen | none: the page is a client component and shows no price until a state is chosen, so the server's page carries no figure for the checker; the prices are `data/ev_prices.json`, built from the warehouse's two EIA tables (not in the live set) by `scripts/build-ev-prices.mjs` | each card prints the table, the entity and the month or week beside the figure; the gasoline card says whether it is the state's own series or its region's, and why |
| Cost per 100 miles, a year's fuel, the saving, payback, net present value | "The verdict" | none: the game's arithmetic (`lib/ev.ts`) on the family's inputs | each figure's sentence says what it is; every default prints its source and "changed by you" when moved; the parents' table lists every number with where it comes from; the IRS line on the credit |

The EV game's figures carry their source in words beside them, not on hover: the page is for a child of about 12 to show their parents, and the brand's rule for that page (session 294) was that nothing is hidden behind a hover. No change here.

## `/learn/bill`

| Figure | Where | Key | Its source, in words |
|---|---|---|---|
| Each state's total, the wholesale share, the wholesale price | the worked bills | `bill\|<st>\|total`, `bill\|<st>\|wholesale\|<ts>`, `bill\|<st>\|share\|<ts>`, `series\|cost_of_power_monthly\|...` (session 52) | the sentence names the month and the table; the method note `bill.md` |
| The calculator's figures | `BillCalc.tsx` | none: the page's arithmetic on the reader's inputs | the rule's words beside each input (four hovers) |

## `/learn/problems/<set>`

| Figure | Where | Key | Its source, in words |
|---|---|---|---|
| Every figure of an answer and a worked solution | the questions | each figure a `Num` with its key (`series_*`, `fullday\|...`: session 369) | "Tables:" under each question names the tables with links; "Figures of <day>" names the day the figures belong to, keyed |

## The battery game's open items

| Item | From | What was done |
|---|---|---|
| The dimmed reason "Not available for <day>: ..." at 3 to 1 | session 583's report and `docs/reviews/accessibility-2026-10-22.md`; `docs/state/review_2026-10-23_code.md` item 5 | **fixed, choice (b)**: only the switch and its name are dimmed; the reason stays in the full muted grey. No ruling was found in `docs/state/rulings_*.md`; the choice is reversible and said in the method note |
| The demo note's figures against the page | `docs/battery_game_demo.md` | **checked**: `site/scripts/check-battery-demo.mjs` recomputes the ten figures the note quotes from `data/battery_levels.json` with the game's model; all ten match on 23 October 2026 (60.97, 48.36, 88.34, 34.32, 0.44; 24.90 at 08:45 and 3,842.89 at 15:30 Central). The note is unchanged |
| The license hold on `iso_rtm_hub_prices` and `iso_hub_prices_history` for their MISO partitions | `docs/state/launch_2026-10-20.md`, `licenses_2026-10-21.md` | not this chain's: a license flag; the game reads ERCOT's rows alone and shows "license needed" where the hold applies (session 215's rule). Listed, not changed |
| The feedback log | `docs/feedback/` (one file, 28 September 2026) | names no game or policy item |

## Checks

- `node --import ./scripts/alias-register.mjs scripts/test-battery.mjs`: exit 0 before and after (its Part B reads `Game.tsx` for a played price printed outside the library's labeled text: none).
- `scripts/test-ev.mjs`, `scripts/test-bill.mjs`, `scripts/test-bill-fixtures.mjs`: exit 0 (no file of theirs changed).
- `scripts/check-battery-demo.mjs` (new): exit 0, 10 of 10.
- `npx tsc --noEmit`: the same 15 generated-file errors as before this session; none in the games' files (one JSX comment placed wrongly was caught here and fixed before the commit).
