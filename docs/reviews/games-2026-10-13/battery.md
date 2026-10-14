# The home battery game (`/play/battery`): review of 13 October 2026

Energy Research Warehouse (ERW), session 261. Played end to end on a local production build of `origin/main` (`811328fe`), at 1280 px with the keys and at 390 px with touch. Screens: `battery/before/` (46) and `battery/after/` (the same list after the fixes). Every play here carried `x-erw-check: 1`, so none is on a leaderboard or in the research data.

## What it is, and for whom

- A 90-second game: one home battery, one real day of 15-minute prices (ERCOT's hub average, or CAISO SP15 on two days). Hold to charge, hold to sell, let go to wait.
- Two pages. The simple page (the default): one sentence, the day, Start, two big buttons, three lines at the end. The full game (`?more=1`): Easy, Normal and Hard, the battery's settings, the fleet call, Hard's grid emergency and outage, the replay, a share card, the leaderboard, and about 1,100 words of rules (the page is 1,900 words in all).
- For whom: a student first (the simple page was built for a class, session 63). The full game's rules page reads for an investor or an operator who wants the assumptions, not for a player.
- **What it teaches, in one line:** a battery earns the spread between cheap and dear hours, and even perfect foresight earns very little of it on a calm day.

## Can a first-time user finish it without help?

- **The simple page: yes.** Start, hold a button, read three lines. No dead end. The play on today's level (2026-10-12) ended at $0.13 earned against $0.87 for the perfect battery.
- **Normal and Easy on the full page: yes**, after scrolling past two paragraphs and the settings to find the Play button.
- **Hard: no, not the first time.** Where they get stuck:
  1. The battery will not sell below the backup reserve, and the screen says "Held: the battery is at its backup reserve", so the reserve reads as the safe floor. It is not: the default reserve holds 2.70 kWh and the outage needs 3.16 kWh. The play here sold to the reserve by 21:00, the lights went out at 23:30 and the round ended at **-$105.63** (`before/17-hard-done-desktop.png`).
  2. The warning that says so (3.16 against 2.70) appears only when the emergency has started, with the price already at USD 1,291/MWh (`before/16-hard-status-2-desktop.png`).
  3. Fifteen minutes before, the screen says "Fleet call in 15 minutes ... Keep charge to sell then". On Hard the call hour is the emergency hour, and the next line says "keep charge for the house". Two instructions that pull opposite ways, one interval apart. On Hard the "Fleet call: discharge now" line never shows at all: the emergency's line replaces it.
- **On the simple page the fleet call arrives unexplained**: the opening sentence says nothing of it, then "Fleet call in 15 minutes" appears near the end of the day.
- **The money is cents.** A first play earns $0.13; perfect is $0.87. The full page multiplies by 10,000 homes; the simple page does not, so a student sees thirteen cents and no reason to care.
- The tutorial (four cards) moves on by itself every 7.5 seconds. A slow reader loses a card; Next and Skip are there, Back is not.

## Bugs, dead ends, numbers, layout

Numbers: `check-values.mjs` on `/play/battery` and `/play/battery?more=1`: **9 of 9 match Supabase** (today's level's low and high, the fleet's MW and MWh, ERCOT's operating fleet, the ratio). By hand: 10,000 homes x 5 kW = 50 MW and x 13.5 kWh = 135 MWh; the lights-out charge 35,000 x 1.5 kW x 2 h / 1,000 = USD 105.00; the degradation cost 721 x 25 / 158,000 = 0.114. All as the page says. No stale number found. The ADER document's date and the 500 MW limit were not read again (no pull in this session).

| # | What | Where | Fixed here |
|---|---|---|---|
| 1 | **The chart at the end of a play was empty.** When a play ended the canvas was drawn again from the day's first interval: no price line, the first interval's price at the now line (19.46), and the marks of the player's moves out of place at the right. On both pages, both widths | `before/04-simple-done-desktop.png`, `before/17-hard-done-desktop.png` | yes |
| 2 | **The simple page scrolled sideways on a phone**: the list of days was 30 px wider than a 390 px screen (420 against 390) | `before/01-simple-pick-390.png` | yes |
| 3 | "see the rules below" on the simple page, where no rules are below | `before/03-simple-status-2-desktop.png` | yes |
| 4 | The end screen of the simple page said "29.93 USD/MWh now" beside "end of day" | `before/04-simple-done-desktop.png` | yes |
| 5 | The end screen writes "you made -357 percent of the perfect battery's earnings" and "Your fleet of 10,000 homes: -$1,056,251.19" after a lights-out. True arithmetic, odd reading | `before/17-hard-done-desktop.png` | no: words |
| 6 | The header says "end of day" when a play ended early (out of money, lights out) | the same | no: words |
| 7 | "Keys: C or the down arrow ..." is shown on a phone, where there are no keys | `before/16-easy-playing-390.png` | no: small |
| 8 | On Easy at 390 px the price label sits on the price line, left of the now line | the same | no: small |
| 9 | The default reserve (2.70 kWh) is smaller than the outage's need (3.16 kWh): the "safe" line loses the round | above | no: a rule |
| 10 | The leaderboard is empty on today's level for the three presets tried ("No scores yet") | `before/10-full-first-visit-desktop.png` | no: needs players |

Not broken: no page error in any play, no dead link (the 10 links to the site's own pages all answer, `/grid/ercot` by redirect at `/grid?grid=ercot`; the 4 links to ERCOT's, the Commission's and Brattle's documents were not requested: no pull in this session), a setting outside its range is refused with a plain line and Play is disabled, "Reset to the defaults" works, "Play again" returns to the day's list, the server verified every score, touch holds work at 390 px, no sideways scroll on the full page.

## Against the brand (`docs/brand.md`)

It is the one item of the four that does not wear the brand, and the furthest from it.

- The page is the old look: cream paper, the old text face, no `<Brand>` wrapper.
- Green for charging (`--color-down`) on the button, the battery, the wire and the bar. The brand has no green and says a series is never told by color alone.
- The canvas draws its own text at 11 px in the system font and its fills as written colors (`rgba(140, 21, 21, 0.08)` and two more), where the brand says 12 px at the least and tokens only. The house drawing has 9 and 10 px labels.
- Motion: the flowing wire. The brand says no motion (it does stop for a reader who asks for less).
- The battery has a 4 px corner, the fleet map round dots; the brand's corners are square.
- The full page's opening paragraphs and its rules run about twice the brand's measure of 68 characters a line.
- Not wrapped in this session: the canvas, the drawing and the buttons carry their own colors, so the wrapper alone would leave a half-branded game. It is a session of its own (number 3 below).

## Henry's review and Kelsey's conversation

**Henry** (`docs/reviews/henry-questions.md`, session 50): ten questions for a former Tesla battery engineer. **No answer is written anywhere in the repository**: the file holds the questions only, and the method never cites him. The game moved on without them (versions 3 and 4).

| Q | Asks | Status |
|---|---|---|
| 1 | Energy and power defaults and bounds; cap the power-to-energy ratio? | open: waits for Henry |
| 2 | Even split of round-trip losses; efficiency by power or state of charge? | open |
| 3 | Is capital over lifetime throughput a fair degradation cost? | open; the method itself says the proxy overstates one cycle |
| 4 | Wear per kWh discharged, flat, or by depth and power? | open |
| 5 | Does a fleet call override the backup reserve? Is 20 percent typical? | **built without him**: version 3 lets the outage use the reserve and the call never does. Bug 9 above is this question |
| 6 | Start half full every day? | open |
| 7 | How much notice, how long a call? | open: still 15 minutes and one hour |
| 8 | How is a home paid in a real Texas VPP? | open: the bonus is still a labelled stand-in |
| 9 | Does an inverter taper near full and empty? | open |
| 10 | What does the game leave out: home load, rooftop solar, time-of-use rates? | **part built without him**: version 4 added rooftop solar (Hard's add-on) and a 1.5 kW house load in the outage; retail rates are still left out |

Needs Samuel's answer: has Henry answered at all (by voice or mail), and if so where are the answers; if not, is the game to wait for him.

**Kelsey's conversation of 5 October:** nothing of it is in the repository (no file, report, prompt or queue entry names it; searched tracked and untracked files). I cannot say what it asked for, or mark any of it done or open. Needs Samuel: the asks, in a few lines, written to `docs/reviews/`.

## Done for real users

| # | What | Effort |
|---|---|---|
| 1 | Samuel's rulings on the reserve against the outage, the two opposite instructions on Hard, and the cents (README, questions 1 to 3) | S |
| 2 | Henry's answers written under his questions, then the defaults and the method changed to cite him | M |
| 3 | The brand: wrapper, the canvas's colors and type from tokens, no green, 12 px text, the rules at 68 characters | M |
| 4 | The simple page tells the whole game in its first screen: the fleet call in one clause, and what the cents mean at fleet scale | S |
| 5 | The rules split from the game: play first, the 1,100 words behind a link or below the leaderboard | S |
| 6 | A first-play path on Hard: the outage's need shown beside the reserve before the day starts, not when the emergency begins | S |
| 7 | End-screen words for a lost round (bugs 5 and 6) and the phone's key hint (bug 7) | S |
| 8 | A browser check of its own in the workflow at 390 px (the list of days, the end chart), so bugs 1 and 2 cannot return | S |
| 9 | Real plays on the leaderboard before it opens (a class, or the owner's own), or the board hidden while it is empty | S |
| 10 | The release line in `site/lib/release.ts` set to `live`, with rule 8's snapshot | S |

## Fixes made on the branch

1. The chart keeps the day's end when a play ends (`Game.tsx`: the redraw at position 0 on every phase but play is now a redraw at the play's last interval, on done only).
2. The list of days is no wider than its screen (`max-w-full`).
3. On the simple page the fleet call's line says "the rules are under More, below".
4. The price on the end screen says "when the play ended", not "now".

No rule of the game is changed: `site/lib/battery.ts` is untouched, and so are the scorer and the presets.
