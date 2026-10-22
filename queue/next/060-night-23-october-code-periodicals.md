# Chain of the night of 23 October 2026: sessions 800 to 813, code machine (personal laptop), unattended: the Digest and the Roundup made better

machine: code

Fourteen sessions for the personal laptop (`portable-laptop`, $HOME\Documents\erw, user samen), written on the owner's instruction on the night of 22 October. Model: Fable 5.1, high effort (the worker is registered with `-Model fable`; a session states its model in its report). This machine runs at night only: the chain is sized for about ten hours and does not renew itself into the day (session 813). Goal: the Daily Digest and the Weekly Roundup are the platform's only two periodicals and must become excellent; the audits of 21 October (`docs/reviews/digest-audit-2026-10-21.md`, `roundup-audit-2026-10-21.md`, "State on 22 October") landed their mechanical fixes, and what is left to the audits waits for the owner's rulings, which no session makes. This chain goes past the audits to the four things a reader notices: which stories are chosen, what the why line says, the numbers section, and the charts. Read the issue of 21 October (`docs/digest/2026-10-21.md`) first and see what a sharp reader sees: why lines that restate the title in adjectives ("massive", "unprecedented", "significant"), the same figure twice in one item, three stories on one topic, sources that read "news.google.com", a numbers section that does not say what moved.

Session numbers 800 to 813 are this chain's; 814 to 849 are this machine's for later nights. The old laptop holds 700 to 749. A number found taken is skipped upward inside 800 to 849 and said so.

Files this chain owns: `warehouse/news/` (`brief.py`, `score.py`, `roundup.py`, `email_digest.py`, `funfact.py`, `rubric.md`, `eval/`), `warehouse/analysis/` (the chart templates, `findings/daily_chart.py`), `site/app/digest/`, `site/app/roundup/`, `docs/digest/checks/`, `docs/reviews/periodicals-*.md`. It does not touch `site/app/cost-of-power/`, `site/lib/cost.ts` or anything the old laptop's chain 050 names. No past issue is rewritten (every file under `docs/digest/` and `docs/roundup/` with a date stays byte for byte); no workflow's schedule, trigger or secret changes; nothing is sent or posted; the scheduled runs produce tomorrow's Digest and Sunday's Roundup as they do today unless a session's change has landed through the gate with its tests, and a landed change is default-neutral to the pages' figures. Every change is proved on the saved scored stories of past issues (`warehouse/news/index.py`'s store, the facts files, the fixtures under `tests/`), never on a live feed.

Model spend: most sessions USD 0 (fixtures and saved stories only; no test reaches the API). Sessions 807 and 808 may call the model, each under its own cap, through the same code the scheduled run uses, writing only under `runs/periodicals_dryrun/` (never under `docs/digest/` or `docs/roundup/`). Total for the chain: USD 8.

## Rules for every session

Every python command uses `.venv\Scripts\python.exe`. Precheck first (exit 1: stop). Unattended: never stop to ask, never wait for a time of day; any wait over 20 minutes is stopped and the step done directly or left under "To finish"; reversible choices under "Decisions made without you", irreversible ones under "For Samuel's ruling", undone, one item a line so `/internal/waits` lists it. One Claude Code session on this machine at a time; each in its own git worktree beside the main checkout, on its own `wip/<N>-periodicals` branch cut from origin/main, removed once landed. THE DATABASE: `python scripts/db_probe.py` before a build; exit 1: code, tests and documents first, probe again at the end. A build over 30 minutes is stopped. `python scripts/buildlock.py acquire <who>` and `release <who>`; `python scripts/duty.py beat` before each build. Landing through the full gate, `python scripts/land_check.py --ref wip/<N>-periodicals`, snapshot before, push to `task/`, snapshot after, `compare`, every difference listed; no landing between 14:00 and 16:15 UTC, and no landing between 15:00 and 16:00 UTC on any day touches `brief.py` or `email_digest.py` (the Digest is written at 15:45 UTC; a change to its code lands before 14:00 or after 16:15 and is proved on fixtures). No warehouse data written; no web request. Screenshots at 1280 and 390 for every page touched under `docs/brand/review-<N>/`. No em dashes anywhere. Reports as the chain of 20 October's, short bullets, "Read these first", "What to review" with addresses and clicks, checks with their exits, the landing, "Decisions made without you", "For Samuel's ruling".

## Session 800: what a sharp reader sees

Long end 1:30. Spend USD 0. Read `brief.py`, `score.py`, `rubric.md`, `roundup.py`, `email_digest.py`, `daily_chart.py`, the 13 Digest issues and W40 and W41, the two audits' state tables, session 498's `scripts/check_digest.py` and `check_roundup.py`. Write `docs/reviews/periodicals-plan-2026-10-23.md`: for the Digest and for the Roundup, the ten changes that would most improve each for a reader at a lab or a fund, ranked, each with the function it touches, whether it needs a ruling (then it is listed and not done), and the fixture that proves it. Count, over the 13 issues: why lines with an adjective from a list the session writes (massive, unprecedented, significant, major, critical, key, huge); items whose why line repeats a figure the title holds; days with three or more items on one topic in the top ten; sources shown as a Google News address. The counts go at the top. Sessions 801 to 806 take the plan's no-ruling items in order; a session that finds its item needs a ruling says so and takes the next.

## Session 801: the why line says the consequence

Long end 2:00. Spend USD 0. The why line's rule, in the prompt and in `brief.plain`'s check: one sentence, the consequence for the energy system or the market, no adjective of the list, no figure the title already gives, the stop before the figures (session 577) kept. Proved on fixtures of twenty saved items (the prompt's output cannot be tested without the model, so the check is the gate: a why line that fails the check is rewritten by the fallback the session writes, which is the title's own clause, never an invented fact). `rubric.md` gains the rule. Tests. Land.

## Session 802: one topic, one item, the rest below

Long end 2:00. Spend USD 0. In the selection: at most one item a topic cluster in "Top of the industry" (the cluster rule `brief.same_event` widened from one event to one topic, by the tags and the parties; the threshold in a constant with its reasoning), the others of the cluster folded under it as "also:" lines with their outlets, so no story is lost (fix 3's rule holds). Proved on the saved stories of the 13 issues: the top ten of each regenerated by selection alone, no model, and the difference listed issue by issue in the report. Tests. Land.

## Session 803: the sources say the outlet

Long end 1:30. Spend USD 0. Where the ingest's resolver fails (18,976 of 18,981, fix 7), the item shows the outlet's name from the feed's own field as the link text with "(via Google News)" after it, never the address; the email the same; an item whose outlet is in the "license needed" list of `docs/licenses.md` shows the outlet and the title only (fix 1's ruling stays his: the rule of session 470 is kept, not widened). Tests on the fixtures. Land.

## Session 804: the numbers section says what moved

Long end 2:00. Spend USD 0. The Digest's numbers section rebuilt from the warehouse through the same functions the price board uses: the five prices that moved most in the 24 hours (hubs, Henry Hub, WTI, Brent, TTF, JKM where held), each with its level, change and the one-line reason only when a scored story of the day names that price (else no reason); held prices under their rule; US48 demand's peak against the same weekday a year before. Every number through `scripts/check_digest.py`'s trace (131 of 131 stays 100 percent). Proved on a saved day's data. Tests. Land.

## Session 805: the chart of the day follows the day

Long end 2:00. Spend USD 0. `daily_chart.py` ranks the candidate charts by their relevance to the day's top stories (the tags and the series the story names) before the existing checks, so the chart is of the day, not of the warehouse (fix 10's caveat, floor and drafts stay his: listed, not done). Proved on the 13 issues: the chart chosen before and after, listed. Tests. Land.

## Session 806: the Roundup's five numbers and its chart

Long end 2:00. Spend USD 0. The Roundup opens with the week in five numbers (the week's biggest price move, the US48 peak, the week's largest deal by MW or USD from the tracker, the week's largest queue or policy figure, one from the week's chart), each traced; the chart of the week ranked by the week's top stories as session 805 does for the day (fix 3's division rule stays his). Proved on W40 and W41 regenerated without the model, the difference listed. Tests. Land.

## Session 807: tomorrow's Digest, dry run

Long end 1:30. Spend cap USD 3. If sessions 801 to 805 have landed: run the Digest's code as the schedule runs it, on the stories scored by the last scheduled run, into `runs/periodicals_dryrun/digest_<date>.md` (and the email's HTML beside it), with the model, under the cap, checked before each call. Beside it the issue the scheduled run actually produced for the same day. `docs/reviews/periodicals-dryrun-2026-10-23.md`: the two side by side, the counts of session 800 for each, every number traced, every difference, and the three the owner should read. If the sessions have not landed: the dry run on the branch's code, said so.

## Session 808: this week's Roundup, dry run

Long end 1:30. Spend cap USD 5. The Roundup's code on the current week's saved stories and the warehouse's week, into `runs/periodicals_dryrun/roundup_<week>.md`, with the model under the cap; beside it W41. The same review file extended. Nothing under `docs/roundup/`.

## Session 809: the regression suite

Long end 1:30. Spend USD 0. One test file a periodical that holds every rule the chain and the audits set (the adjectives, the figures, one topic one item, the outlet, the numbers traced, the chart's relevance, the stop, the money style, the named days), run on the fixtures, so a later change that breaks a rule fails a test and the gate. `tests/test_periodicals.py`. Land.

## Session 810: the pages and the email at 390

Long end 2:00. Spend USD 0. `/digest`, `/digest/<date>`, `/roundup`, `/roundup/<week>` and the email's HTML at 390 by 844 and 1280: tables in their scroll containers, the numbers section readable, the chart's labels whole, links reachable; `docs/brand.md` tokens only; AccessLint's unattended scan; screenshots before and after. No issue's text changes. Land.

## Session 811: the method on the page

Long end 1:00. Spend USD 0. `/about#digest` and the Roundup's method line updated for the rules sessions 801 to 806 landed, in the brand's words; `rubric.md` and `docs/digest/checks/` consistent with them. Land.

## Session 812: the rulings the periodicals wait for, in plain words

Long end 1:00. Spend USD 0. `docs/reviews/periodicals-rulings-2026-10-23.md`: every item of both audits and of this chain that waits for the owner, one a line, in plain words (what the choice is, what each answer changes, the session's recommendation and why), no codes without their meaning. This file is what the owner reads at the next review evening. Push to main (a document only).

## Session 813: the note and the queue

Long end 0:45. Spend USD 0. `docs/state/review_2026-10-24_portable.md`: one line a session with its branch, every decision made without the owner, every item waiting for him, the dry runs' paths. Push. Then `python scripts/chain_queue.py list`. If the time on this machine is before 07:00 Pacific and nothing waits for it, write one more file for this machine, at most six sessions numbered 814 on, from the open items of this chain's reports, push it to main, and take it with `python scripts/chain_queue.py next`. Otherwise run `python scripts/chain_queue.py next` and, at exit 3, say "CHAIN DONE" and stop: this machine does not run in the day.
