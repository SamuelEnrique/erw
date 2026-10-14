# The Games tab, set up for review: 14 October 2026

Energy Research Warehouse (ERW), session 279. Four items, each played or read end to end as a first-time user, at 1280 px (keys) and 390 px (touch), on a local production build of `wip/279-games`: session 261's branch of 13 October (`wip/261-games`, never landed) merged with `origin/main` at `eb64c7a5`. Nothing is landed. This folder replaces `docs/reviews/games-2026-10-13/` as the one to read; that one stays on the branch as the record of the first pass.

| Item | Address | Review | Screens before | Screens after |
|---|---|---|---|---|
| The bill explainer | `/learn/bill` | [`bill.md`](bill.md) | `bill/before/` (22) | `bill/after/` (22) |
| The problem sets | `/learn/problems` and five sets | [`problems.md`](problems.md) | `problems/before/` (22) | `problems/after/` (22) |
| The tour | `/tour` | [`tour.md`](tour.md) | `tour/before/` (12) | `tour/after/` (12) |
| The home battery game | `/play/battery` | [`battery.md`](battery.md) | `battery/before/` (46) | `battery/after/` (46) |

"Before" here is the branch as session 261 left it, today's data; "after" is with this session's three fixes. In all four: **100 of 100 checked numbers match Supabase** (`check-values.mjs`, before and after), no page error in 204 screens, no dead link. All four are in review (`site/lib/release.ts`): a visitor sees the "in review" page (`battery/before/00-visitor-sees-in-review-desktop.png`).

## Ranked by how close each is to real users

1. **The bill explainer: closest.** In the brand, finished without help, its numbers match, Reset works. Between it and a reader: the season ruling (question 9), a date for reading the tariffs again, help beside three California fields.
2. **The problem sets: close for reading, not yet for a class.** Every answer opens and every number matches, but five answers or questions are loosely worded, and the answers moved overnight (set A question 1: 2.56 times on 13 October, 2.92 today), so a class cannot answer what its teacher prepared.
3. **The tour: small and true, not yet a tour.** Its words match the pages; it is still five links with no way back from a stop, two of whose pages scroll sideways on a phone.
4. **The battery game: the most built and the furthest.** The simple page plays cleanly. It does not wear the brand, Hard's first play still ends at -$105.95 by following the screen, and Henry's ten questions are still unanswered.

## What was fixed on the branch

Session 261's eleven fixes (13 October) all still hold. This session added three:

| # | Item | Fix |
|---|---|---|
| 1 | Game | The header said "end of day" when a play ended at 19:30; it says "ended at 19:30" |
| 2 | Game | "Keys: C or the down arrow ..." was shown on a phone; a touch screen reads "Hold a button down; let go to idle." |
| 3 | Bill | A credit's rate read "$-0.00857"; it reads "-$0.00857" |

No rule of the game, no answer or question of a problem set, no rate or default of a bill and no stop of the tour changed. Commit `a27ba856`.

## Questions only Samuel can answer

Session 261's sixteen, still open on 14 October (no ruling on file), with what changed since:

1. **The game, Hard: the reserve (2.70 kWh) is smaller than the outage's need (3.16 kWh).** (a) Raise the default reserve to 25 percent (3.38 kWh). (b) Shorten the outage or lower the house's draw. (c) Keep both and say it before the day starts. (d) Ask Henry first (his question 5).
2. **The game, Hard: "Keep charge to sell then" is followed one interval later by "keep charge for the house".** (a) On Hard the notice names the emergency. (b) Move Hard's emergency off the call's hour. (c) Leave it: the conflict is the lesson.
3. **The game: a first play earns cents (today $0.24 against $1.34).** (a) Show the fleet of 10,000 homes on the simple page. (b) Open on a famous day. (c) Leave it, with a sentence on the end screen.
4. **Problem set B question 2: "all six ISO hubs" lists seven, two named "CAISO".** (a) Name the zones, say seven, take the latest complete month. (b) Keep one CAISO zone. (c) Keep the partial month and say how many days it holds.
5. **Sets B (question 5) and D (question 3) use a partial month without saying so.** (a) The latest complete month. (b) The latest month, with "(14 days so far)".
6. **Set E question 5 compares 18 storm days with one normal week (201.95 times; about 79 day for day).** (a) 18 days against 18. (b) A mean day against a mean day. (c) Leave it and say "18 days against 7".
7. **The ratio questions' word order.** (a) "ERCOT's peak was how many times CAISO's?" (b) Leave them.
8. **The answers move every day** (2.56 yesterday, 2.92 today). (a) A dated edition beside the live one. (b) Live only, with the build day at the top. (c) Frozen, rebuilt on request.
9. **The bill: PG&E and SDG&E default to summer, SCE to winter.** (a) All in the season of the day the tariffs were read (winter). (b) All in summer. (c) Leave them, the season in each card's first line.
10. **The bill: shares past 100 percent are billed all the same.** (a) Refuse. (b) Clamp. (c) Leave the warning.
11. **The tour: a list of links, or a guided path?** (a) Guided, with a bar on each stop. (b) A list, stops opening in a new tab. (c) Fold it into the home page and retire `/tour`.
12. **Henry's review: ten questions, no answer on file today either.** Has he answered? If not, does the game wait for him, or do questions 1 and 2 go ahead on your ruling?
13. **Kelsey's conversation of 5 October: still nothing in the repository.** What did it ask for, item by item?
14. **The menu: four of the five problem sets, no index; the bill explainer under Economics.** (a) Games: the game, the tour, the bill, "Problem sets". (b) Add the fifth set. (c) Leave it. (The menu was not touched: today's chain prompt keeps it for your roadmap review.)
15. **The brand wrapper on the tour and the problem sets** (`46fd7338`): keep it or drop it? Is the game's restyle the next brand session?
16. **Who is each item for?** Read as: the bill and the sets for a student and a teacher, the tour for any first visit, the game's simple page for a class and its full page for nobody yet.
17. **New: the fifth game (below).** (a) Build it as proposed, after the incentive source is ruled. (b) Build the EV half first (every price is already in the tables), solar after a yield source. (c) Not now.

## Proposed order of sessions

One session each; none needs a pull except number 6 and the fifth game's sources.

| # | Session | What it does | Needs | Effort |
|---|---|---|---|---|
| 1 | The words and the menu | Problem sets: questions 4 to 7 as ruled, with tests; the bill's season (9) and shares (10), the 10 px chip; the menu (14); check-values on every Games page | rulings 4 to 7, 9, 10, 14 | S |
| 2 | The game takes the brand | Wrapper; canvas, drawing and buttons from tokens, no green, 12 px, no motion; rules at 68 characters and after the play; end-screen words for a lost round; a 390 px browser check | ruling 15 | M |
| 3 | The game's rules, version 5 | Questions 1 to 3 as ruled, Henry's answers where there are any; presets carry "-v5" | rulings 1 to 3, 12, 16 | M |
| 4 | The tour, as ruled | Guided: the bar as one shared component, stops at today's addresses, a heading check. A list: the last two only | ruling 11 | M (S for a list) |
| 5 | The problem sets for a class | Dated editions, the rows a question needs, a teacher's copy | ruling 8 | M |
| 6 | The bill's tariffs | The five tariffs read again and dated; help beside the California fields; SDG&E's allowance by zone. Robots files and terms first | approval of the five pulls | M |
| 7 | Kelsey's asks | Whatever question 13 turns up | answer 13 | unknown |
| 8 | The fifth game | As designed below, EV half first if 17(b) | ruling 17, the sources ruled | M to L |
| 9 | Opening | Release lines to `live`, one landing an item with rule 8's snapshot: the bill, the sets, the game, the tour last | approval of each | S each |

Sessions 2 and 3 touch the same file (`site/app/play/battery/Game.tsx`): one after the other.

## A fifth game, proposed: "Should your family get an EV or solar panels?"

Ben Domingue's ask. A proposal only: nothing is built.

**For whom and why.** A middle-schooler, about 12, who will show it to their parents at the kitchen table. The child drives; the parents check the numbers. It teaches one idea: **what a choice saves depends on where you live, because power and gasoline cost different amounts in different states**, and it shows the child where each number comes from so that the parents can trust it.

**The play, five screens, about five minutes.**

1. **Where do you live?** A list of states. The game reads that state's home electricity price and its gasoline price, and shows both with their dates and sources: "Electricity for homes in your state: 33.61 cents a kWh (July 2026, EIA)."
2. **Your car.** Three questions with plain defaults the family can change: miles a year, the car's miles per gallon, and the EV's kWh per mile. Each default says where it comes from; a slider, never a blank field; a Reset.
3. **The EV card.** Cost to drive 100 miles on gasoline and on electricity, side by side as two bars, then a year of driving. One sentence on what it leaves out (the car's price, insurance, charging at work or at a public charger, which costs more).
4. **The solar card.** The family's monthly power use (default from their state's average home), panel size, and what the panels would make in their state. What the power would have cost at their rate. One sentence on how their utility pays for power sent back, which differs by state and changes the answer.
5. **The verdict card, to show the parents.** "In California, driving an EV instead of a 30 mpg car saves about $1,281 a year at today's prices." A list of every number used, each with its table and date, and "What would change the answer": a gasoline price slider, a power price slider. A "Print for my parents" view.

**Real prices from the tables (read 14 October 2026), a worked example.** Example inputs a family would type (not data): 12,000 miles a year, a car of 30 miles per gallon, an EV of 0.30 kWh per mile.

| State | Gasoline, regular, USD a gallon (week of 2026-10-05) | Homes' electricity, USD/MWh (2026-07) | Gasoline, 100 miles | EV, 100 miles | A year, saved |
|---|---|---|---|---|---|
| California | 6.227 | 336.1 | $20.76 | $10.08 | $1,280.84 |
| Washington | 5.424 | 147.1 | $18.08 | $4.41 | $1,640.04 |
| Texas | 3.874 | 158.8 | $12.91 | $4.76 | $977.92 |
| Florida | 3.970 | 150.3 | $13.23 | $4.51 | $1,046.92 |
| Massachusetts | 4.302 | 304.9 | $14.34 | $9.15 | $623.16 |
| United States | 4.354 | 183.1 | $14.51 | $5.49 | $1,082.44 |

Sources: gasoline from `eia_regional_retail_fuel_prices` (entities `eia:EMM_EPMR_PTE_S<state>_DPG` and `eia:EMM_EPMR_PTE_NUS_DPG`, EIA's weekly retail gasoline survey); electricity from `eia_retail_electricity_prices` (entity `eia:retail_price:<state>:RES`, EIA's monthly retail sales). The lesson shows itself in the table: Massachusetts has dear power and middling gasoline, so an EV saves least there; Washington has cheap power and dear gasoline, so it saves most.

**What the tables hold and what they do not.**

| Input | Held? | Where, or what is needed |
|---|---|---|
| Home electricity price by state | yes | `eia_retail_electricity_prices`, monthly, all 50 states and DC, to 2026-07 |
| Gasoline price | partly | `eia_regional_retail_fuel_prices`: 9 states (CA, CO, FL, MA, MN, NY, OH, TX, WA), the regions (PADD) and 10 cities, weekly. Other states would use their region, and the card must say so |
| A state's average home use | partly | `eia_retail_sales_monthly` holds residential sales; customer counts would be needed for use per home. To check |
| Car mpg and EV kWh per mile | no | defaults from the federal fuel economy site (fueleconomy.gov), as labelled assumptions the family changes |
| Solar output by state | no | a source to rule: NREL's PVWatts (an API: terms and key to read first), or a published table of yield by state |
| How a utility pays for exported solar | no | varies by state and utility (California's net billing since 2023, others net metering): a short table written by hand from the commissions' orders, each cited, or the game says "ask your utility" |
| **State incentives** | **no** | Not in the warehouse. DSIRE (NC State) is the usual source; its terms need reading before any automated use. A hand-written table of the few largest programs, each cited to the state's own page, is the smaller first step |
| **Federal tax credits** | no | **To confirm before any page says it:** the 2025 budget law ended the federal credit for new EVs (for cars acquired after 30 September 2025) and the homeowner's solar credit (for spending after 31 December 2025). If the IRS's pages confirm it, the game says "no federal credit today" with the IRS page cited, not a number |

**The brand and the rules.** Inside `<Brand>`; numbers in the mono face, each with its table on hover; inputs with sourced defaults and a Reset (brand section 7); no green and no motion; 12 px at the least. Every number traces to a table or is labelled an assumption the family set. It never says "you should": the verdict says what each choice saves at today's prices and what would change it.

**Effort.** The EV half: M (every price is held; the defaults need their citations). The solar half: M once a yield source is ruled. Incentives: S for a hand-written cited table of a few states, L for all states. A method note `docs/methods/ev_or_solar.md` and tests that hand-compute the worked example above.

**Needs from Samuel.** Question 17; the solar yield source; whether incentives are hand-written or a licensed source; and whether Ben wants the parents' view printed or shared as a link.

## How this was made

- `runs/session279/shots.mjs` (not in git), session 261's script pointed at this worktree, drove the machine's Chrome through `site/scripts/browser.mjs`: every screen at both widths, each play with a plain rule (charge in the cheap third of the prices seen so far, sell in the dear quarter), keys on the desktop and touch on the phone. Every request carried `x-erw-check: 1`.
- The screenshots are 128-color PNGs (17 MB for 204 files; 46 MB as taken).
- AccessLint and Impeccable were not run: an accessibility audit and a design critique of the four items each belong with session 2 above.
