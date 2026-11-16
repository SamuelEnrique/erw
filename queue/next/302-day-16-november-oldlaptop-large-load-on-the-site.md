# Chain of 16 November 2026: sessions 7200 to 7249, samueloldlaptop (code role), unattended: the large-load rules of 91 utilities put on the site, and the All grids tab read as an AI lab would read it

machine: samueloldlaptop

Written by Claude in chat with Samuel on 16 November 2026, from a read of origin/main at `f0360123` and of every branch. It is not a machine's successor file, and no machine writes a successor to it (rule 3). Folder: `C:\Users\lossa\Documents\erw`. Model: Fable, high effort. One Claude Code session. Sized for about 30 hours. The work here is judgment: what a person deciding where to put a gigawatt needs to see, and whether the page gives it.

## Why this chain

On 13 and 14 November the ERW read the large-load connection rules of 166 utilities: 122 rules from 91 utilities and statewide regimes, 98 changes of the last 90 days and 28 state laws, 1,699 cites, audited by five independent readers. The public rows are warehouse tables (`utility_large_load_rules`, `utility_large_load_rule_changes`, `state_large_load_laws`). No page of the site shows a row of them. This is the dataset an AI lab's energy team and a fund ask for first, and a reader cannot see it. This chain puts it on the pages that answer "where can a gigawatt go", then reads those pages as that reader would.

## The owner's rules of 16 November 2026 (they win over anything older, in this file or any file it names)

1. **Model spend USD 0.** The owner's Anthropic API key is at its limit until 1 December and he is not raising it. No session runs any script that calls a model: no chat asking, no evaluation, no scoring, no Digest or Roundup run with the model, no Thesis Builder. Set `ERW_SPEND_CAP_USD=0` in the session's environment. A step that cannot be done without a model call is not run: it goes under "Needs the key" in the report and the progress file, with one line on what it would do and its estimated cost in US dollars. No other key or route is tried.
2. **No waiting.** Never wait on a time of day, a scheduled run, a landing, the data machine or Samuel. A step that needs something not yet here is marked waiting in the progress file and skipped; the session takes the next step at once. A commit that says only "waiting" is a fault of this chain. Never stop to ask: a reversible choice goes under "Decisions made without you", the rest under "For Samuel's ruling", each with the default taken, in plain words (no item codes without their meaning).
3. **No machine writes a chain.** No session writes a successor file, a "continued" file or any new goals. The goals are in this file alone. The one file a session may put in `queue/next/` is the resume pointer of the section "Restart safety", with its text exactly as given there.
4. **No redundant work.** Before each step, check whether it is already on origin/main, and say what was checked. Not in this chain: the forecast page (its 23 faults are fixed; it waits for Samuel's own review); a new page where an existing page can carry the work; a second version of any page; a session whose only output is a note or a record.
5. **Paused or out of bounds.** No LinkedIn work of any kind. No change to what the Digest or the Roundup say (the news is paused this week; goal 3 is the one exception and changes no issue's words). Nothing is sent, posted or published. `site/lib/release.ts` is not touched and no page opens to visitors. A license hold is never lifted or worked around.
6. **This machine does not land and writes no warehouse table.** No landing gate and no full suite here: the test files a change touches (every test file that imports or names the changed module, found by grep), then a row in `docs/state/landing_request_oldlaptop.md` for the data machine's desk. A site build only in the foreground and only with 2.5 GB of memory free. What only the data machine can do (a table loaded to the live set, a builder run under the data lock) is one row in `docs/state/data_requests_large_load.md`, marked requested, and the work goes on without it.
7. **Procedures by reference, goals from here.** How a code chain works on this machine is as in `CLAUDE.md` and `queue/done/280-day-14-november-oldlaptop-ask.md` (its rules on spend are replaced by rule 1). Where they differ from this file, this file wins. Never force a push. Before removing a worktree, list its ignored files.
8. **The worker's clock.** The chain worker closes a session that shows no commit for 30 minutes. Commit real partial work at least every 25 minutes; an empty commit is allowed only while a named long step (a build, a test sweep) is running, and its message names that step.
9. **The page standard (Samuel's standing rules).** An upgrade is made to the page itself and drops nothing the page had. Explanations, defaults and sources appear as hover tips only, never as grey text. Charts and tables answer to the mouse. The tool states facts and takes no view: no "so what" box, no advice. Two cases side by side (A and B) wherever a reader would compare. Menu and column names are plain nouns. A held or internal value is not left off: its cell is drawn blank with "license needed" on hover. Every figure carries its source document. Real numbers only, never a placeholder. No sideways scroll at 390 px. Not "AI slop": dense, informative, usable.
10. **Reports.** One report a session, `archive/sessions/SESSION_<N>_REPORT.md`, short bullets; "What to review" gives the full address of each changed page (`https://erw-flame.vercel.app/...`) with click-by-click steps and what Samuel should see; screenshots at 1280 and 390 under `docs/reviews/large-load-on-site/`. "Needs the key", "Decisions made without you", "For Samuel's ruling". No em dashes anywhere.
11. **Session numbers.** 7200 to 7249, each checked free on origin/main and every branch before it is used; a taken one is skipped upward and said so.

## Restart safety

- Session 7200 writes `queue/next/320-resume-chain-302.md`, commits it alone and pushes it. Its whole text is the block below, unchanged.
- A session started by the chain worker that takes a resume file first writes the same block again under the next number up (321, then 322, to 329), commits and pushes it, then does what the block says.
- The chain's last session removes the resume file from `queue/next/` (one commit) before its queue step.

```
# Resume of chain 302

machine: samueloldlaptop

Chain 302 was interrupted. First put this same text back in queue/next/ as the next number up to 329, named NNN-resume-chain-302.md, committed alone and pushed. Then read queue/done/302-day-16-november-oldlaptop-large-load-on-the-site.md whole and docs/state/progress_c302.md, and continue chain 302 from the first step not marked done, under that file's rules, with the next free session number in its range. Write no other queue file.
```

## The progress file

`docs/state/progress_c302.md`, started by session 7200 and pushed after every step: one line a step, with its state (`done` with the commit, `needs the key` with the cost, `ruling` with the default taken, `waiting` with what for) and the session.

Read first: `CLAUDE.md`, `docs/state/note_2026-11-14_portable_p4.md`, `docs/methods/large_load_research.md`, `docs/methods/siting.md`, `docs/research/large_load/` (the three CSVs and the audit), `docs/reviews/siting-gaps.md` (its table only), `site/app/cost-of-power/AllGridsView.tsx`, `site/app/cost-of-power/LoadAnswers.tsx`, `site/lib/siting.ts`.

## Session 7200: the ground (long end 0:30)

- Precheck; `git fetch`; memory and disk; worktrees of landed branches removed (ignored files listed first).
- If `queue/next/` still holds `284-day-18-november-oldlaptop-ask-continued.md` or `300-day-26-november-oldlaptop-periodicals-continued.md`, move them to `queue/parked/` (one commit, pushed). Remove any `*-resume-chain-*` file of this machine from `queue/next/`.
- The resume file and the progress file. Then goal 1 at once, in the same session.

## Goal 1: the large-load rules on the site (the main work; about twelve sessions)

Where, and no new page: the All grids tab (`/cost-of-power?view=allgrids`) and the policy monitor (`/policy`).

- **First, the reader's questions, written down** (`docs/reviews/large-load-on-site/questions.md`, one page): what the energy lead of an AI lab, a developer and a fund analyst each need from a utility's large-load rule before choosing a site (the smallest load the rule covers, the contract's length, the minimum bill or take-or-pay share, the collateral, the exit fee, who pays for the upgrades, every timed step, the rule's status and date). Which of the tables' 463 field values answer each. The design below follows from this page, and the page is short.
- **On the All grids tab:** each row's Utility cell and its Time to connect cell open that utility's rule: its status and date, the fields above as the document prints them, each with its cite. A row whose utility has no rule read says so in the same place.
- **Under the tab, one table: "Large-load rules by utility"**: one row a rule, sortable, filtered by state, grid and status (in effect, approved, proposed, ordered, denied), the fields above as columns, the document linked. Two rules side by side as A and B. Downloads of the public rows (CSV, Python, Stata).
- **"What changed in the last 90 days"**: the 94 public changes, newest first, by region, each with the rule it changed and its document.
- **On `/policy`:** the 27 state laws in the monitor's state view, each with its status (in effect, enacted, passed, introduced, vetoed, died) and its text's cite, linked from the rule's state on the tab.
- **Internal rows and internal fields** are never printed: their cells are drawn blank with "license needed" on hover (rule 9), counted in a test.
- **The data's route:** the page files are written by a builder (`warehouse/derived/`), with tests, from the tables as committed on main. If the three tables are not in the live set or the page files cannot be built on this machine, one row in `docs/state/data_requests_large_load.md` for the data machine, and the pages are built and tested against files made here from the committed tables until it answers.
- **Held to the tables by tests:** every figure the pages print is found in its table row (a test reads the page file against the CSV); the counts by status equal the tables'; no internal value in any page file; `check-values` entries for the new sections; the hover and the A and B exercised; 390 px and 1280 px read, no sideways scroll; an accessibility read (axe) with no rule broken.
- **The method note** (`docs/methods/siting.md` and `docs/methods/large_load_research.md`) says what the pages now show and from where.
- **The chat over the warehouse** cannot be asked (rule 1): whether `/ask` reads the three tables is written under "Needs the key" with the cost of asking the 58 questions already written for them.

Done when a reader on the tab can open any utility's rule, compare two, see what changed in 90 days and reach the state's law, every figure cited and tested, and the stack has a landing request row with its screenshots.

## Goal 2: the site side of the data machine's fixes (at the start of each session, as rows appear)

The desktop's chain 301 is closing the faults files' rows marked `data machine` and writes `docs/state/data_ready_c301.md` when a fix needs a site change (a hover naming the document a read is of, a column the page must now read). At the start of each session read that file; each new row is done before goal 1 continues, with a test, on its own branch with its own landing request row. Nothing there: two lines of the report, no more.

## Goal 3: the scheduled model steps fail soft when the key refuses (one session)

On 15 November the Roundup's step ended in `anthropic.BadRequestError` ("You have reached your specified API usage limits") and its job skipped the commit and the email; the news scoring and the policy scoring were refused the same way. The code already knows a daily cap (`warehouse/health.py budget`, `--no-model`); it does not know the key's own refusal.

- When the API answers with its usage-limit refusal, a scheduled model step ends as skipped, not failed: one row of `erw_health` saying "the key's limit" and the date access returns (read from the error), no retry, no second email beyond what the cap's rule already sends.
- No issue is written or sent on a day the scoring was refused: a Digest or a Roundup with no ranked stories is not an issue.
- Tests with a stubbed client that raises the error; dry runs only; nothing sent; no issue's words changed.

## Goal 4: the All grids tab read as the reader it is for (about six sessions, after goal 1)

Five real cases, each read on the built pages as the energy lead of an AI lab would, start to finish: 1 GW in ERCOT West; 500 MW in Dominion's Virginia territory; 300 MW in Arizona (APS); 1 GW in Ohio (AEP); 500 MW in Georgia (Georgia Power).

- For each case: can the reader get the cost of power, the time to connect, the headroom, the carbon, the utility and its rule, without leaving the tab and without a figure that contradicts another page? Each gap is a numbered row in `docs/reviews/allgrids-read-2026-11-16.md` with the cell or click it faults.
- A site fault is fixed with a test. A data fault is a row marked `data machine` in that file and a row in `docs/state/data_requests_large_load.md`. A gap only a license or a ruling closes is written as such, with the default.
- Then the same five cases on `/cost-of-power` (the datacenter cost tool's default view): the two pages must agree on every figure they share; each disagreement is a row and is fixed at its cause.

Done when the five cases are read on both pages, every row is fixed, requested from the data machine or written for Samuel, and the report says in five bullets what a lab's reader still cannot get from the tab and why.

## If goals 1 to 4 are done and no new file waits

Read `/policy` (the monitor's state view and the new laws) as a utility regulator's staffer would, for the same five states, the same way as goal 4: rows, fixes, requests. Then the same for the next five states by announced datacenter load. Never a waiting commit, never a file of new goals.

## The last session

- The progress file complete; `docs/state/note_2026-11-17_oldlaptop_c302.md` in short bullets: what a reader can now do that they could not, with the pages' full addresses; what needs the key, with the costs summed; what waits for Samuel, each with its default.
- The landing request row for the final stack.
- The resume file removed from `queue/next/`; then `.venv\Scripts\python.exe scripts\chain_queue.py next`, and the file it prints run the same way. Exit 3: run the precheck again (the queue step takes the machine off duty), continue with the section above, and run the queue step again at the end of each state.
