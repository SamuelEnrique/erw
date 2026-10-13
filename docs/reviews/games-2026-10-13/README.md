# The Games tab, set up for review: 13 October 2026

Energy Research Warehouse (ERW), session 261. Four items, each played or read end to end as a first-time user, on a desktop (1280 px) and a phone (390 px), on a local production build of `origin/main` (`811328fe`). Nothing is landed: the work is on the branch `wip/261-games`.

| Item | Address | Review | Screens before | Screens after |
|---|---|---|---|---|
| The bill explainer | `/learn/bill` | [`bill.md`](bill.md) | `bill/before/` (20) | `bill/after/` (22) |
| The problem sets | `/learn/problems` and five sets | [`problems.md`](problems.md) | `problems/before/` (22) | `problems/after/` (22) |
| The tour | `/tour` | [`tour.md`](tour.md) | `tour/before/` (12) | `tour/after/` (12) |
| The home battery game | `/play/battery` | [`battery.md`](battery.md) | `battery/before/` (46) | `battery/after/` (46) |

In all four: **every number checked matches its table** (100 of 100, `check-values.mjs`, before and after the fixes), no page error in any screen, no dead link, and after the fixes no sideways scroll at 390 px. All four are in review (`site/lib/release.ts`): a visitor sees the "in review" page (`battery/before/00-visitor-sees-in-review-desktop.png`).

## Ranked by how close each is to real users

1. **The bill explainer: closest.** It wore the brand already, a first-time user finishes it, its 18 numbers match, and it now has a Reset. What stands between it and a reader: one ruling (the season of the California defaults), a date on which the tariffs are read again, and help beside three California fields.
2. **The problem sets: close for reading, not yet for a class.** 73 numbers match and every answer opens. Five answers or questions are worded wrongly or loosely (one lists seven hubs under "all six"), and the answers move every day, so a class cannot answer what its teacher prepared. Rulings first, then a session.
3. **The tour: small, now true, and not yet a tour.** Its words pointed at headings that are gone; that is fixed, and it takes the brand. It is still a list of five links with no way back from a stop, and it can open only when all five stops are open.
4. **The battery game: the most built and the furthest.** The simple page plays cleanly from start to end. But the game is the one item that does not wear the brand (and is far from it: green, 11 px canvas text, motion), a first play on Hard ends at minus $105 by following what the screen says, Henry's ten questions have no answer on file, and the leaderboard is empty.

## What was fixed on the branch (no ruling needed)

| # | Item | Fix |
|---|---|---|
| 1 | Game | The chart at the end of a play was empty (drawn again from the day's first interval). It now keeps the day's end |
| 2 | Game | The simple page scrolled sideways on a phone (the list of days: 420 px on a 390 px screen) |
| 3 | Game | "see the rules below" on the simple page, where no rules are below |
| 4 | Game | "now" beside the price after the day had ended |
| 5 | Bill | No Reset: "Reset this bill to its defaults" |
| 6 | Bill | The PG&E note named sessions 48 and 49 to the reader |
| 7 | Bill | "Both tariffs" in the glossary, where there are five |
| 8 | Tour | Stop 2's headings are the ones the page has |
| 9 | Tour | Stop 5's headings are the ones the page has |
| 10 | Tour | Stop 3 no longer counts six hubs (five hold a real-time price) |
| 11 | Tour, problem sets | The pages draw inside `<Brand>` (its own commit, `46fd7338`: it can be dropped) |

No rule of the game, no answer or question of a problem set, no rate or default of a bill and no stop of the tour was changed.

## Questions only Samuel can answer

1. **The game, Hard: the backup reserve is smaller than the outage's need** (2.70 kWh against 3.16 kWh at the defaults), so selling down to the line the game holds you at loses the round.
   - (a) Raise the default reserve to cover the outage (25 percent is 3.38 kWh).
   - (b) Shorten the outage or lower the house's draw so that 20 percent covers it.
   - (c) Keep both and say it before the day starts, beside the reserve.
   - (d) Ask Henry first (his question 5).
2. **The game, Hard: "Keep charge to sell then" is followed one interval later by "keep charge for the house".**
   - (a) On Hard the 15-minute notice says the emergency is coming, not the fleet call.
   - (b) Move Hard's emergency off the fleet call's hour.
   - (c) Leave it: the conflict is the lesson.
3. **The game: a first play earns $0.13 and perfect is $0.87.**
   - (a) The simple page also shows the fleet of 10,000 homes (as the full page does).
   - (b) The simple page opens on a famous day (the 2023 heat, Uri), not today's level.
   - (c) Leave it: thirteen cents is the lesson, and the end screen says so in a sentence.
4. **Problem set B, question 2: "all six ISO hubs" lists seven, two named "CAISO", in a month thirteen days old.**
   - (a) Name the zones (CAISO NP15, CAISO SP15), say seven, and take the latest complete month.
   - (b) Keep one CAISO zone (which?), six in all, and take the latest complete month.
   - (c) Keep the partial month and say how many days it holds.
5. **Problem sets B (question 5) and D (question 3) use October's hour-of-day profile without saying it is a partial month.**
   - (a) Take the latest complete month, as question 1 of set B does.
   - (b) Keep the latest month and write "(13 days so far)".
6. **Problem set E, question 5 compares 18 days of Winter Storm Uri with one normal week** (201.95 times; day for day about 79).
   - (a) Compare the storm's 18 days with 18 normal days.
   - (b) Compare a mean storm day with a mean normal day.
   - (c) Leave it, and add "18 days against 7" to the answer.
7. **The ratio questions' word order** ("how many times CAISO's was ERCOT's?", four questions).
   - (a) Reword to "ERCOT's peak was how many times CAISO's?".
   - (b) Leave them.
8. **The problem sets' answers move every day.**
   - (a) A dated edition of each set at its own address, beside the live one.
   - (b) Live only, with the day the page was built printed at the top.
   - (c) Frozen only: the sets are rebuilt when a person asks.
9. **The bill: PG&E and SDG&E default to summer, SCE to winter, and they stand side by side in October.**
   - (a) All three in the season of the day the tariffs were read (winter now).
   - (b) All three in summer.
   - (c) Leave them and print the season in each card's first line.
   - Either change moves the PG&E total and the two problems that quote it.
10. **The bill: two shares that add to more than 100 percent are warned about and billed all the same.**
    - (a) Refuse: no total until they add to 100 or less.
    - (b) Clamp the second share to what is left.
    - (c) Leave the warning as it is.
11. **The tour: a list of links, or a guided path?**
    - (a) Guided: a bar on each stop when it is opened from the tour (stop 2 of 5, what to look at, Next, Back to the tour).
    - (b) A list, as now, with the stops opening in a new tab so that the tour stays open.
    - (c) Fold it into the home page's "start here" and retire `/tour`.
12. **Henry's review:** ten questions, no answer on file. Has he answered (by voice or mail)? If so, where; if not, does the game wait for him, or do questions 1 and 2 above go ahead on your ruling?
13. **Kelsey's conversation of 5 October:** nothing of it is in the repository. What did it ask for, item by item? Until it is written down, no session can mark it done or open.
14. **The menu:** Games lists four of the five problem sets (storage and taxes is missing) and not their index; the bill explainer is under Economics.
    - (a) Games: the game, the tour, the bill explainer, and one line "Problem sets" that opens the index.
    - (b) Add the fifth set and leave the rest.
    - (c) Leave it.
15. **The brand wrapper on the tour and the problem sets** (commit `46fd7338`): keep it, or drop it until those pages have their own restyle? And is the game's restyle (green, canvas text, motion) the next brand session?
16. **Who is each item for?** The reviews read them as: the bill and the problem sets for a student and a teacher, the tour for any first visit, the game's simple page for a class and its full page for nobody yet (its 1,100 words of rules read as a method). Is that the intent, or is the game also meant for an investor or an operator?

## Proposed order of sessions

Each is one session. Sessions 1 and 2 need no pull; all need the rulings named.

| # | Session | What it does | Needs | Effort |
|---|---|---|---|---|
| 1 | The words and the menu | Problem sets: the changes ruled in questions 4 to 7, with their tests and check keys. Bill: the season (9), shares past 100 (10), the 10 px chip, defaults and resets by field. Menu: question 14. Check-values on every Games page | rulings 4 to 7, 9, 10, 14 | S |
| 2 | The game takes the brand | The wrapper; the canvas, the house drawing and the buttons from tokens (no green, 12 px, no written color); no motion; the rules at 68 characters and below the play; the end screen's words for a lost round; no key hint on a phone; a browser check at 390 px for the list of days and the end chart | ruling 15 | M |
| 3 | The game's rules, version 5 | Questions 1 to 3 as ruled, and Henry's answers where there are any: the reserve against the outage, Hard's notice, what the simple page says of the fleet call and of the cents. The method cites the source of each change; the presets carry "-v5" so old boards stay apart | rulings 1 to 3, 12, 16 | M |
| 4 | The tour, as ruled | If guided: the tour bar as one shared component, each stop opening at the thing to look at, stops 1 and 2 at today's addresses, and a check that fails when a quoted heading is gone. If a list: the last three only | ruling 11 | M (S for a list) |
| 5 | The problem sets for a class | Dated editions (question 8); under each question the rows it needs, not the whole table's download; a teacher's copy; the notes for teachers at today's addresses | ruling 8 | M |
| 6 | The bill's tariffs | The five tariffs read again and dated, the next reading written on the page; help beside the California fields; SDG&E's allowances by climate zone. Robots files and terms first | approval of the five pulls | M |
| 7 | Kelsey's asks | Whatever question 13 turns up that sessions 1 to 6 do not cover | answer 13 | unknown |
| 8 | Opening | The release lines set to `live`, one landing an item, each with rule 8's snapshot before and after: the bill, the problem sets, the game, and the tour last (it needs its five stops open) | Samuel's approval of each | S each |

Sessions 2 and 3 touch the same file (`site/app/play/battery/Game.tsx`): one after the other, never side by side.

## How this was made

- `runs/session261/shots.mjs` (not in git) drove the machine's own Chrome through `site/scripts/browser.mjs`: every screen at both widths, each play with a plain rule (charge in the cheap third of the prices seen so far, sell in the dear quarter), with the keys on the desktop and touch on the phone. Every request carried `x-erw-check: 1`.
- The screenshots are 128-color PNGs (17 MB for 202 files; 47 MB as taken).
- Tools of `docs/tooling.md` used: none of the six. The site's own browser helper and `check-values.mjs` did the work; AccessLint and Impeccable were not run (an accessibility audit and a design critique of the four items are a session's worth each and belong with session 2 above).
