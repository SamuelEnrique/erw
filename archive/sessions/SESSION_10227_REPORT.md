# Session 10227 report: the games under /play audited

Chain 710 part D, 26 November 2026, the old laptop, worktree `erw-c710-c`. The audit: `docs/reviews/play-model-audit-2026-11-26.md`, its evidence in `docs/reviews/play-model-audit-2026-11-26/`.

## What was done

- The battery game (`/play/battery`) and the EV game (`/play/ev`) read as a battery trader, an EV fleet manager and a teacher would.
- The arithmetic is right: 693 of 693 battery figures (8 levels, 3 modes, 6 plays) and 312 of 312 EV figures agree between an independent restatement and the site's own code; the perfect battery is the exact optimum of the game's three moves (a second dynamic programme agrees on 16 cases; any power earns at most 2.7 percent more).
- Eight findings: 1, 2, 4, 5, 6 words-only, each on its branch with a test, drawn with the site's own code and read again (pass), merged as `wip/audit-play-words`; 3 and 7 figure tests for a ruling; 8 to confirm.
- No table written, no lock, no model call, no live service, no play written, no default changed, no web read.

## Decisions made without you

- Today's level is read from the live set, which this machine does not read: the newest complete ERCOT day in the main copy (2026-11-12) stood in for the default game.
- The end table is drawn only after a play: to draw it with the site's own component, a loader hook under `runs/` adds one export to `Game.tsx` at load time; the repository is unchanged.
- Finding 8 (the cap's year) has no branch: the warehouse's prices show the cap at 5,000 in 2022, but the Commission's date is not in the repository and no web read was allowed.
- The EV game's 52-week gasoline mean ends 2 November (this machine's copy), a week before the file's newest week.

## For Samuel's ruling

- Finding 3: make the battery end the day at least as full as it began? Default: left as it is. Effect: the perfect score falls 15 percent on the newest ERCOT day, 24 on Uri's, 31 on the calm day; every share of perfect moves.
- Finding 7: price the EV game's gasoline at its 52-week mean (and electricity at its 12-month mean)? Default: left as it is. Effect: US net present value 3,887 to 2,946; four states (MA, NH, NY, RI) turn below zero.
- Finding 8: confirm the year ERCOT's USD 5,000 offer cap began (the page says 2023; the warehouse's highest prices say 2022). Default: left as it is.

## Needs the key

- Nothing.

## Rows returned to the chain

- Landing (words): `wip/audit-play-words` `b049745f7`, or `wip/audit-play-1` `b07de2fb7`, `-2` `4f12d4559`, `-4` `01bf977ea`, `-5` `bb95cfdc7`, `-6` `0c175118f`.
- Not for landing: `wip/audit-play-3` `a7863f750`, `wip/audit-play-7` `881d7fbde`.
- Data requests (a) CAISO SP15 day-ahead for 2026-04-27 and 2026-07-24; (b) the EV file's 52 gasoline cells of 9 November and their 52-week means; (c) a count of posted scores matchable to a research record (level, preset, score, within 120 seconds).
