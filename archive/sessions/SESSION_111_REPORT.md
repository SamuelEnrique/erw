# Session 111 report: the battery game, checked for a demonstration

**The game is ready to demonstrate, after one real fault was found on production and fixed.** It was played on production in the internal view ten times after the fix, five at a phone's width (390 by 844, by touch) and five at a laptop's (1366 by 768, by the keys): the simple page, Easy, Normal, Hard, and Hard with the rooftop add-on. **91 of 91 checks pass at each width.** The same fault was then found in the end screen's replay and fixed too; that last fix goes out with session 112's push and is checked on production there. The guide is `docs/battery_game_demo.md`, one page, five minutes. Two deploys of this session's own; the live pages did not change in either, the home page's 15-minute prices aside.

## Read these first

1. **The game could stop dead on pressing Start, and this was found only on production.** On the first production run the fifth play at a laptop's width (Hard with rooftop solar) never ended: the page threw an error on the play's first frame and the board stayed on the day's first interval. Nine other plays in the same two runs were fine, and all ten had passed on this machine. The cause: a browser can stamp a play's first frame a little earlier than the press of the button that started it; the game then computed a negative elapsed time, looked up the price of the interval before the day's first one, and stopped. It is a matter of timing, so it would have shown up now and then, on any difficulty, with a reload as the only way out: the worst kind of fault for a demonstration. **Fixed** (the elapsed time is never below zero), and the check now forces the case in one play each run: on production before the fix that play stops with the same error; after it, it plays to its end. **The end screen's replay had the same fault** ("Play the replay" could take the whole page down, error "Invalid time value"): forced on production, it failed; fixed the same way; on the fixed build on this machine it runs. That fix is committed with this report and deploys with session 112's push.
2. **Hard's emergency did not say how much charge to keep.** The announcement said "keep charge for the house" and no number, and the line on the charge bar looked like the answer. It is not: the default backup reserve holds 2.70 kWh and the two-hour outage takes 3.16 kWh, so a player who sells down to the line goes dark late in the outage, at a cost of USD 105. The announcement now says "It will need 3.16 kWh from the battery; the backup reserve is 2.70 kWh, which is not enough by itself". With the rooftop add-on the house needs nothing from the battery on the demonstration day, and the announcement now says "Today the roof carries the house through it" where it used to tell the player to keep charge all the same.
3. **If it freezes tomorrow all the same: reload.** The guide says so. The prices are part of the page; a reload costs ten seconds.
4. **A day takes 90 seconds whatever you do,** so two plays fit in five minutes, not three. The guide is built around two: the simple page, then Hard.

## What was checked, and how

`site/scripts/check-battery-game.mjs <address> <phone|laptop>` drives a real browser. For each of the five plays it opens the page in the internal view, picks the day 2023-08-10 and the difficulty, starts, and follows the perfect battery's own plan interval by interval, by a phone's touch on the two buttons or a laptop's C and S keys. Every request carries `x-erw-check`, so the plays stay off the leaderboard. A play is the real 90 seconds.

| Asked for | What the check holds it to | Result on production, each width |
|---|---|---|
| Every difficulty | Easy, Normal and Hard can be chosen; the start button names the day and the difficulty; the day plays to its end | pass |
| A phone-width screen and a laptop | nothing is wider than the screen before, during and after the play; the two buttons are on the screen and at least 44 px tall | pass (phone 390 px wide, laptop 1366) |
| The simple page | one sentence, a day to pick and Start; no settings and no leaderboard; "Play again" and "More" after | pass |
| The end screen's three lines | what you earned; the perfect battery's figure for that day and those rules, equal to the model's (USD 60.97 Easy and Normal, 49.01 Hard, 89.17 Hard with the roof); the hour you lost the most, or that none was lost | pass |
| Hard's emergency and its labels | the announcement with its label "game rule, not a real price" and what comes next; how many kWh the house will need; the outage announced with both buttons off; wear shown beside the money | pass |
| The rooftop add-on | offered on Hard only; the title says "with rooftop solar"; the roof's power shows; in the outage the notice says the house takes the roof's power first | pass |
| The controls | following the perfect plan by touch or by keys earned 100 percent of the perfect score in all ten plays | pass |
| No error in the page | none thrown in ten plays, one of them started with its first three frames stamped early | pass |

Runs: on this machine before the first deploy, 88 of 88 at each width. On production after the first deploy, 78 of 86 at a laptop's width (the stopped play, item 1) and 89 of 90 at a phone's (the one failure was the check's own: it expected a figure the announcement rightly does not give with the roof). The forced case on production before the fix: 9 of 14, the same error. On production after the fix: **91 of 91 and 91 of 91** (`runs/111b_game_prod_laptop.out`, `runs/111b_game_prod_phone.out`). The replay, forced: on production before its fix 12 of 15 (the page went down); on the fixed build on this machine 19 of 19.

## The guide

`docs/battery_game_demo.md`, under 800 words: how to open the internal view; what to say first; the controls; minute 0 to 2 on the simple page with the day's lowest and highest price and the perfect battery's USD 60.97; minute 2 to 5 on Hard with the emergency at 15:00, the outage from 16:00 to 18:00 and the 3.16 kWh to keep; a sixth minute with the roof; four questions a room asks, with answers; what to do if something goes wrong. Its figures are tested against the game's own model (`tests/test_session111.py`), so a change to the game that moves one fails a test.

## Deploys and snapshots

| Deploy | Workflow run | Merged as | Snapshots | Differences |
|---|---|---|---|---|
| The announcement's figure, the check, the guide | 37242659788 | `413cfc2` | `before-111`, `after-111` | 0 |
| The first-frame fix, the roof's sentence | 37245085943 | `19790e9` | `before-111b` (23:48 UTC), `after-111b` (23:55) | 26, all the home page's latest real-time prices (five hubs moved to their next interval): expected. The other 24 pages: 0 |

The game is in review; no live page reads anything this session changed.

## Tests

- `tests/test_session111.py`, 8 tests (the replay's fix inside the first-frame test): the guide's figures are the model's; the reserve alone does not carry the house, and the guide says so; the guide is one page and says how to open the internal view; the announcement gives the kWh; the board carries the marks the check reads; the first-frame fix and the check that forces it; the roof's sentence; no em dash.
- Every session's tests on this machine: 802 ran; one fails and is not this session's (the interchange ceiling of session 49, which is not run on GitHub).
- Both workflow runs passed (tests, site build, route check) and Vercel accepted both deployments.

## Errors and decisions

1. **The first production run found what ten local plays had not.** Recorded as it happened above. The lesson for later sessions: a check that passes on this machine is not a check of production, and a fault of timing needs the case forced, not waited for.
2. **The check was wrong once:** it held the announcement to "It will need 0.00 kWh" with the roof. The game was right. Corrected.
3. **The local server outlived the tool that started it** and went on answering on port 3111 during a rebuild; it was stopped by its process number before the rebuilt site was served.
4. **Not changed:** a day's 90 seconds; the default reserve of 2.70 kWh (raising it above 3.16 would make Hard's line safe, and would also make the emergency a non-event; the number in the announcement is the smaller change). Both are yours.
5. **No model call, no pull, no table, no load. Model spend USD 0.00.**

## For Samuel

1. **Before the demonstration, on the machine you will use:** open the unlock address, then `/play/battery`, and play the simple page once. Two minutes, and it settles the one thing a check cannot: your browser.
2. **The replay's fix is on production only after session 112's push.** Its report gives the check's result there.
3. **Whether Hard's default reserve should cover the outage** (decision 4).

Energy Research Warehouse (ERW), session 111, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from about 22:50 UTC to 2026-10-05 00:15 UTC, unattended.
