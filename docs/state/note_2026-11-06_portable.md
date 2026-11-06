# The portable laptop's note of chain 152: Ask the warehouse, from 19 of 30 to 30 of 30 (written 6 November 2026, night)

Energy Research Warehouse (ERW), session 2228, for Samuel. Chain 152 (sessions 2220 to 2228, `queue/done/152-night-5-november-portable-ask-quality.md`), unattended on portable-laptop (the code role) from 00:52 to 03:10 UTC on 6 November 2026, one Claude Code window, Fable 5.1. Ask the warehouse had landed on main at 00:08 UTC (`task/1314-ask`); its evaluation stood at 19 of 30 and 8 of 8. This chain took the thirty to 30 of 30, added twenty questions a lab's energy team asks (20 of 20), proved the owner's rule by tests, and **did not land: the gate was stopped for memory at its suite, and the code waits whole on `wip/2226-ask` with the commands that remain** (session 2227's report).

## Read these first

- **The counts.** The thirty (`questions_s320.yaml`, asked through the Python loop, graded under the hold): 19 of 30 before (23 October); **26 of 30** after USD per kW on by default (session 2221); **29 of 30** after a figure is written as returned and a repeated call is not read (2222); **30 of 30** under the grader's two named rules for session 320's ruling 3 (2223). The eight (the second set's eight asked on 23 October) stand at 8 of 8; the whole second set's thirty, regraded from their stored answers under the rules: 29 of 30, from 24. The twenty (`questions_s2224.yaml`, new): 15 of 20 at the first asking, **20 of 20** after the fixes (2224). Each count, question by question, with its fault's class: `docs/reviews/ask-faults-2026-11-05.md`.
- **The three rulings of 23 October carried out as recommended** (`docs/reviews/ask-board-rulings-2026-10-23.md`, items 1 to 3): the tool hands back USD per kW beside USD per MW for the battery table by default (`ASK_PER_KW=off` the way back); a money figure is written to the cent, never "about 50,424"; a refusal is graded on refusing and stating no figure, and a key's table is met by the record's own evidence (`eval_s267.py` `RULES_2223`, named in every grading from 2223 on; the stored gradings keep their counts).
- **Both loops fixed alike.** A tool call repeated with the same arguments is answered with a note, read from nothing, counted toward the 12 and, when a turn only repeats, the next model call may not read (the site held this for Ask ERCOT since session 143; now every chat and the Python loop): 155 to 185 calls for the thirty against 205, none sent back. The Python loop reads the live set's review tables as the site does (`ERW_LIVE_REVIEW=on`, set by the chat's tools; the package's default unchanged). An en dash in an answer becomes a hyphen in both loops.
- **The rule proved** (`tests/test_session2225_ask.py`): every figure of 266 stored answers is fetched and the digits left after the strip are names; every table held whole is refused by name with "license needed" and no digit; MISO's rows with the pause's words; every "lacks" refusal says "not in the warehouse" first; every answered record lists what each query read; eleven kinds of answer give the same thing in both loops (session 1300's test, two scenarios added).
- **The chats seen** (`runs/s2226/shots/` in the main checkout, not in git, 21 images): `/ask`, the seven grids' chats and the board at 390 and 1280 in the internal view, a chart answer hovered with its value at both widths, the board's Ask answered.
- **The model's cost**: USD 9.72 of the chain's 15 (2221: 2.49; 2222: 1.96; 2223: 2.31; 2224: 2.60; 2225: 0; 2226: 0.36; 2227: 0; 2228: 0), every call's cost in the run files and the session reports; no ledger row on this machine (a code machine holds no data lock), said in each report.

## One line a session

| Session | What | USD |
|---|---|---|
| 2220 | The prompt saved (`queue/done/152-...md`, pushed to main); the machine (the desktop app stopped for memory); the eleven failures and ten refusals classed in `docs/reviews/ask-faults-2026-11-05.md` | 0 |
| 2221 | USD per kW on by default in both loops; rule 10; the two-loop scenario; `eval_loop.py` (the thirty through the Python loop under a cap). 26 of 30 | 2.49 |
| 2222 | A repeated call counted and not read, every chat, both loops; a figure as returned (rule 1). 29 of 30 | 1.96 |
| 2223 | Ruling 3 in the grader as two named rules; the second set regraded (29 of 30). 30 of 30 | 2.31 |
| 2224 | The twenty from `scripts/ask_eval/lab_questions.py`; review tables readable by the Python loop; keys fixed where the key was the fault. 20 of 20 | 2.60 |
| 2225 | The rule proved by nine tests; a held table and MISO's pause as two-loop scenarios | 0 |
| 2226 | The build (twice), the screenshots, the method note, `runs.json`; the en dash | 0.36 |
| 2227 | The gate, fifteen tries: the probe closed it fourteen times (3.1 to 3.5 s), main moved once; on the fifteenth it passed the probe and Claude Code stopped it at the suite for memory. Nothing landed | 0 |
| 2228 | This note | 0 |

## What landed, and what did not

- **Landed on main**: the queue file alone (`77f13b5bd`, session 2220) and this note.
- **Not landed, whole on origin**: `wip/2220-ask` to `wip/2226-ask` (each cut from the one before, origin/main merged into `wip/2226-ask` at `202508dec` at 03:00) and `wip/2227-ask` (its report). The gate (`scripts/land_check.py --ref wip/2226-ask --task 2220-2226-ask --port 3220`) passed `freeze`, `main_merged`, `task_branches`, `db_probe`, `build_lock` and `worktree` on its fifteenth try and was stopped by Claude Code at the suite because the machine was critically low on memory (2.49 GB free at the start of the suite, the owner's Chrome holding about 1.5 GB); its lock and worktree were released and removed. Not started again on my own, by the harness's own rule. The exact commands to finish are in `archive/sessions/SESSION_2227_ASK_REPORT.md` under "To finish": the gate again, then the snapshot before, the push to `task/2220-2226-ask`, the snapshot after and the comparison. No page changed for a visitor; nothing was sent or posted; no warehouse data was written.
- **The reports**: `archive/sessions/SESSION_2220_ASK_REPORT.md` to `SESSION_2227_ASK_REPORT.md`, on their branches (the plain names are chain 098's).

## Decisions made without you

- The Claude desktop app was stopped by PID at the start (0.5 GB free, "a stray claude process"); nothing else of yours was stopped for memory, before or after the gate.
- The reports, tests and files of this chain carry `_ASK`, `_ask` or the session's number in another place, since `SESSION_2220_REPORT.md` to `SESSION_2228_REPORT.md` and `tests/test_session222N.py` are chain 098's (the data machine, 24 October); the branches and the gate's task keep your numbers.
- Session 320's three rulings were taken as decided the chain's way, as the chain's prompt reads ("takes Ask from 19 of 30 to 30 of 30", "never by adding a number the loop did not fetch"); each is on by default and dated in `docs/methods/ask.md`.
- USD per kW: on by default, `ASK_PER_KW=off` the way back (before, `on` turned it on).
- The precision fix is the prompt's, not the check's (a stricter check would send back stored right answers); the grader's tolerance was not changed.
- A repeated call still counts toward the limit of 12, so a repeating model cannot loop without end.
- The grader's rules are named and dated; the stored gradings of 20 to 23 October keep their rules (none) and their counts, so `ask-history.md`'s old rows stand.
- "States no figure": a number with decimals, or a whole number of 1,000 or more that is not a year, is a figure; a year or a small count is not.
- The twenty's keys moved where the key was the fault (an incomplete month, a grid chat asked for a table no grid's, a held table given a figure key); the loop's answers to the first keys were right by the rule.
- The Python loop reads review tables; the package's default does not.
- The runner writes no ledger row (the data lock) and keeps every call's cost in the run file; its reserve is one question at the dearest cost, since its costs are exact.
- The first asking's files of the twenty are kept beside the worktrees in `Documents`, not in the repository.
- One build was tried at 1.75 GB free with the heap capped and failed on the cap; the second at 2.68 GB passed.
- The gate was run again each minute while the database probe closed it, up to fifteen times, and not again after Claude Code stopped it for memory.
- An en dash is turned into "-".
- The chain's worktrees (`erw-2220` to `erw-2228`) are removed at the end of this session, their branches being on origin; the queue step is not run (your rule: this machine runs at night only).

## For Samuel's ruling

1. The landing: run the commands of session 2227's "To finish" on a machine with memory free (the desktop, or this laptop with Chrome closed), or say that a night chain here may close Chrome before a landing.
2. `ASK_PER_KW` on Vercel: nothing need be set (the default is on); say if you want it off until you have seen an answer.
3. Whether the Python loop's evaluation runs should write the cost ledger through another path (a code machine's own file, or Supabase directly), so the precheck's day's spend sees them.
4. Whether the hold by grid should also hold an unprefixed entity in a single-grid table (`nyiso_rtm_zone_prices` with entity `N.Y.C.` in the general chat): no run of this chain read such rows, but the rule leaves the gap open.
5. Whether the grids' chats should see a table whose entities are `<table>:<grid>` (`grid_peak_vs_capacity:ercot`) and the tracker's tables (no grid's): the rule file admits neither; the general chat answers them.
6. `ERW_LIVE_REVIEW`: whether the package's default should be the site's (yes and review).
7. Whether `energy_deals` and the tracker's tables should stay held whole: a lab's team asks for PPA prices and datacenter MW first, and every such question is answered "license needed".
8. Whether the second set's 22 unasked questions should be asked in a session of their own (about USD 2).
9. The database probe's 3-second line, read on one probe (it opened on 2 of 20 tonight, at 2.6 and 2.9 s): whether the median of three should decide.
10. Whether the desktop app may be stopped at the start of every night chain.
11. The page screenshots at 1280 show the Ask panel beside the home page's content: say if a reviewer should see the panel alone.
