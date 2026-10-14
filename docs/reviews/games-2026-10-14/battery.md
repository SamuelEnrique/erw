# The home battery game (`/play/battery`): review of 14 October 2026

Energy Research Warehouse (ERW), session 279. Played end to end on a local production build of `wip/279-games` (session 261's fixes merged with `origin/main` at `eb64c7a5`), at 1280 px with the keys and at 390 px with touch. Screens: `battery/before/` (46) and `battery/after/` (46). Every play carried `x-erw-check: 1`, so none is on a leaderboard or in the research data. Session 261's review of 13 October (`docs/reviews/games-2026-10-13/battery.md`, on `wip/261-games`) is the base: this one says what still holds, what moved, and what this session fixed.

## What it is, and for whom

- A 90-second game: one home battery, one real day of 15-minute prices (ERCOT's hub average, or CAISO SP15 on two days). Hold to charge, hold to sell, let go to wait.
- Two pages. The simple page (the default): one sentence, the day, Start, two big buttons, three lines at the end. The full game (`?more=1`): Easy, Normal and Hard, the settings, the fleet call, Hard's emergency and outage, the replay, a share card, the leaderboard and about 1,100 words of rules.
- For whom: a student first (the simple page was built for a class). The full page's rules read as a method, for an investor or an operator who wants the assumptions.
- **What it teaches, in one line:** a battery earns the spread between cheap and dear hours, and even perfect foresight earns very little of it on a calm day.

## Can a first-time user finish it without help?

- **The simple page: yes.** Today's level (2026-10-13, ERCOT) ended at **$0.24** earned against **$1.34** for the perfect battery, on both widths (`after/04-simple-done-desktop.png`).
- **Easy and Normal on the full page: yes**, after scrolling past two paragraphs and the settings to find Play.
- **Hard: no, not the first time. Unchanged since 13 October.** The play sold down to the reserve, the lights went out at 19:30 and the round ended at **-$105.95**; the perfect battery earned $29.66 (`after/17-hard-done-desktop.png`). The default reserve holds 2.70 kWh, the outage needs 3.16 kWh, and the screen says so only once the emergency has begun. Fifteen minutes before, it says "Keep charge to sell then"; one interval later, "keep charge for the house".
- The fleet call still arrives on the simple page unexplained by its opening sentence.
- The money is still cents on the simple page (24 cents against 134).
- The tutorial still moves on by itself every 7.5 seconds, with Next and Skip but no Back.

## Bugs, dead ends, numbers, layout

Numbers: `check-values.mjs` on the Games pages, before and after the fixes: **100 of 100 match Supabase** (the game's share: today's level's low and high, 27.67 and 99.99 USD/MWh, the fleet's 50 MW and 135 MWh, ERCOT's operating fleet of 18,204.50 MW in 259 units, the ratio 364.09). By hand: 10,000 x 5 kW = 50 MW; 10,000 x 13.5 kWh = 135 MWh; 18,204.50 / 50 = 364.09; the lights-out charge 3.00 kWh x USD 35,000 / 1,000 = USD 105.00. No stale number. The ADER document (read 2026-10-01) and the Commission's value of lost load were not requested again: no pull in this session.

| # | What | Where | Status |
|---|---|---|---|
| 1 | The chart at the end of a play was empty | 13 Oct `before/04-simple-done-desktop.png` | fixed by 261, holds (`after/04-simple-done-desktop.png`) |
| 2 | The simple page scrolled sideways on a phone | 13 Oct `before/01-simple-pick-390.png` | fixed by 261, holds: page width 390 at 390 |
| 3 | "see the rules below" on the simple page | | fixed by 261, holds: "the rules are under More, below" |
| 4 | "now" beside the price after the play ended | | fixed by 261, holds |
| 5 | **The header said "end of day" when the play ended at 19:30** (lights out or out of money) | `before/17-hard-done-desktop.png` | **fixed here**: "ended at 19:30" (`after/17-hard-done-desktop.png`) |
| 6 | **"Keys: C or the down arrow ..." shown on a phone** | `before/16-easy-playing-390.png` | **fixed here**: a touch screen reads "Hold a button down; let go to idle." (`after/16-easy-playing-390.png`) |
| 7 | The end screen writes "-357 percent of the perfect battery's earnings" and a fleet total of "-$1,059,465.91" after a lights-out. True arithmetic, odd reading | `after/17-hard-done-desktop.png` | open: words |
| 8 | On Easy at 390 px the price label sits on the price line, left of the now line | `after/16-easy-playing-390.png` | open: small |
| 9 | The default reserve (2.70 kWh) is smaller than the outage's need (3.16 kWh) | above | open: a rule (README question 1) |
| 10 | The leaderboard is empty on today's level for the presets tried | `after/10-full-first-visit-desktop.png` | open: needs players |
| 11 | The site menu's closed dropdown measures 418 to 423 px wide at 390 px (an `ul.absolute` in the header). The page itself does not scroll sideways (scroll width 390) | every 390 px screen | not the Games tab's files: noted for the menu's owner |

Not broken: no page error in eight plays (four before, four after), no dead link (14 of the page's own links answer, `/grid/ercot` by redirect), a setting of 100 kWh is refused with a plain line and Play disabled, "Reset to the defaults" puts 13.5 back, "Play again" returns to the list of days, every score verified by the server, touch holds work at 390 px.

## Against the brand (`docs/brand.md`)

The game is the one item of the four that does not wear the brand. Unchanged since 13 October: the old cream paper and text face, green for charging, 11 px canvas text in the system font, written colors in the canvas, the flowing wire (motion), a round-cornered battery and round fleet dots, rules about twice the measure of 68 characters. The header and footer are the site's, so the page reads half new, half old (`after/17-hard-done-desktop.png`). A restyle is its own session (README, order of sessions, number 2).

## Henry's review (`docs/reviews/henry-questions.md`)

Ten questions for a former Tesla battery engineer, written in session 50. **No answer is on file anywhere in the repository on 14 October** (searched `origin/main` and this branch). The game has moved on without him through versions 3 and 4.

| Q | Asks | Status |
|---|---|---|
| 1 | Energy and power defaults and bounds; cap the power-to-energy ratio? | open: waits for Henry |
| 2 | Even split of round-trip losses; efficiency by power or state of charge? | open |
| 3 | Is capital over lifetime throughput a fair degradation cost? | open |
| 4 | Wear per kWh discharged, flat, or by depth and power? | open |
| 5 | Does a fleet call override the backup reserve? Is 20 percent typical? | built without him (the outage uses the reserve, the call never does); bug 9 is this question. Needs Samuel or Henry |
| 6 | Start half full every day? | open |
| 7 | How much notice, how long a call? | open: still 15 minutes and one hour |
| 8 | How is a home paid in a real Texas VPP? | open: the bonus is a labelled stand-in |
| 9 | Does an inverter taper near full and empty? | open |
| 10 | What does the game leave out? | part built without him: rooftop solar and a 1.5 kW house in the outage; retail rates still left out |

Done: none answered. Open: all ten. Needs Samuel: whether Henry has answered by voice or mail, and whether the game waits for him (README question 12).

## Done for real users

| # | What | Effort |
|---|---|---|
| 1 | Samuel's rulings on the reserve against the outage, Hard's two opposite instructions, and the cents (README questions 1 to 3) | S |
| 2 | Henry's answers written under his questions, then the defaults and the method changed to cite him | M |
| 3 | The brand: wrapper, canvas colors and type from tokens, no green, 12 px text, no motion, rules at 68 characters | M |
| 4 | The simple page tells the whole game on its first screen: the fleet call in one clause, and what the cents mean at fleet scale | S |
| 5 | Play first, rules after: the 1,100 words behind a link or below the leaderboard | S |
| 6 | Hard's first play: the outage's need beside the reserve before the day starts | S |
| 7 | End-screen words for a lost round (bug 7) and the price label at 390 px (bug 8) | S |
| 8 | A browser check of its own at 390 px (the list of days, the end chart, the key hint), so bugs 1, 2 and 6 cannot return | S |
| 9 | Real plays on the leaderboard before it opens, or the board hidden while empty | S |
| 10 | The release line in `site/lib/release.ts` set to `live`, with rule 8's snapshot | S |

## Fixes made on the branch in this session

1. The header says "ended at HH:MM" when a play ended early, "end of day" when it ran to the end (`Game.tsx`).
2. The key hint shows only on a screen with a fine pointer; a touch screen reads "Hold a button down; let go to idle." (`Game.tsx`, a media query on `pointer: coarse`).

No rule of the game changed: `site/lib/battery.ts`, the scorer and the presets are untouched.
