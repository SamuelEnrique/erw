# Session 249 report: how it works, five tools

13 October 2026, 09:00 to 09:27 UTC, unattended, on lab-desktop (the data machine), the seventh session of the chain of 12 to 13 October. Branch `task/249-how-it-works`. Model spend USD 0: no model call by any script of the repository. No pull, no request to any publisher, no warehouse table written, no data lock taken. No page edited.

## Read these first

- **Added by session 250: this session's own push failed its check and it lands with session 250.** Run 38376287516, step "Site build and check-routes", failed at 09:35 UTC. The cause was not in these files: the emissions page's read of the hourly carbon table was being cancelled since session 245's load (`archive/sessions/SESSION_250_REPORT.md`, "Read these first"). Nothing below was changed.
- **`docs/howitworks/` holds five documents, one a tool, each with the seven parts asked for and a last part that names the file every number was read in.** `battery.md`, `generator.md`, `datacenter.md`, `grid.md`, `research.md`; `README.md` is the index. 1,414 lines in all.
- **Sessions 235 and 236 landed while I wrote: `aa3addbc`, 09:14:02 UTC (the generator and the datacenter pages, together). Sessions 237 and 238 had not.** When the session began none of the four was on `main`, so four documents were written from the branches. The generator's page files as landed are the same as the branch's; the datacenter's landed with two sentences reworded, and its document gives both wordings. The Grid tool and Research are written from `origin/wip/237-grid` (`13dfe385`) and `origin/wip/238-research` (`f95bb129`), and say so in their first lines.
- **No demo path was clicked through in a browser.** Each was written from the page's code, its check scripts and its data, and says so in one line. Every page is in review, so each path starts by opening the internal view. A person, or a browser session on the code machine, owes each path one run.
- **Every number is one the repository already holds, with one marked exception.** I searched the cited files for about 330 of the documents' figures and found each. The exception: a dozen figures of the battery document, marked **[c]**, are printed in no method or report. They were computed with the page's own library from this morning's table; the script and its output are committed beside the document (`docs/howitworks/computed/`). The same run reproduced every headline figure of the battery's methods note.
- **Writing them found six things that are wrong or unsettled in other files.** They are under "What the writing found", and the ones that need you are under "For Samuel's ruling". The first: four of the nine Research cards are filed under NYISO and three under ISO-NE, their numbers are in committed files, and nothing replaces them on 21 October.
- **The 21 October license table was written again,** because the datacenter page that landed reads four more tables (all public: `caiso_grid_emergencies`, `carbon_intensity_hourly`, `carbon_intensity_monthly`, `large_load_rules`). The counts did not move: 197 tables, 124 public, 40 "license needed", 33 internal; 3 pages dark, 24 partly.
- **Session 248 landed:** see "The landing of session 248".

## The five documents, and the one line of each to know

| Tool | Document | The honest line |
|---|---|---|
| What a battery earns | `battery.md` (267 lines) | An upper bound. ERCOT, 4 hours, 100 MW: USD 81.40 per kW over the last twelve months, NPV USD -69.78 million at 12 percent. The model takes USD 2.25 per kW a month of ancillary income where ERCOT's storage fleet was awarded 0.40. In California the model takes 42.25 of regulation where the real fleet was paid 9 |
| What a generator earns | `generator.md` (267 lines) | A fleet at a hub, merchant, no tax credit. 100 MW of ERCOT solar: USD 59.85 per kW, paid USD 23.27 per MWh against a hub average of 32.17, debt covered 0.67 times, NPV USD -74.16 million. It needs USD 58.36 per MWh for an NPV of zero. The finance repeats the newest twelve months, lower than every full year held but 2024 (59.46) |
| What a datacenter pays | `datacenter.md` (296 lines) | Wholesale energy alone: USD 33.73 per MWh at `LZ_NORTH`. Texas industrial customers paid USD 70.70 in July 2026 by EIA's count, against the tool's 30.59 that month. Delivery is itemized for Texas only (USD 7.10 to 8.81); no wait is estimated for any grid |
| The Grid tool | `grid.md` (288 lines) | Measurement, not real time. The exchange was 53 hours behind the clock at 07:57 UTC today, and that is EIA's lag. For CAISO, MISO, PJM and SPP the ties do not close EIA's own balance (mean gaps of 978 to 3,199 MW). Four browser checks are owed on the branch |
| Research | `research.md` (267 lines) | Eleven cards, nine in the library; 16 drafts wait and 0 are approved. No card claims cause. No Stata do-file has been run. A language model writes two sentences a week and nothing else |

## What the writing found

1. **Research cards and the licenses.** `docs/state/licenses_2026-10-21.md` lists `/analysis` among "the pages no license touches": the page reads no table when it is drawn. But its cards hold numbers computed from `iso_zone_prices_history`, `iso_hub_prices_history` and `nyiso_rtm_zone_prices`, which are held by grid. Four of the nine library cards are filed under NYISO, three under ISO-NE. No code replaces those numbers on 21 October. My table of session 248 reads pages, not committed files, so it could not see this. Ruling 1.
2. **Stata.** No session report records a run of any of the 11 do-files; sessions 178, 182 and 233 say their machine had no Stata. Six of the 11 read the column names from line 1, and line 1 of each CSV is a comment (there are four). Ruling 2.
3. **No file records your sign-off on the 11 committed cards.** They did not pass through the review list. Ruling 3.
4. **Four methods notes carry a stale line each** (the code is right in each case):
   - `battery_earns_algorithm.md`, section 11: capital cost is listed as the first row of "What matters most" and cycles second with "USD 11.14 million up". The library sorts cycles first, and 11.14 is the move down to 0.5 cycles; the move up to 1.5 cycles is 1.40 **[c]**. The note also keeps a contract-share row that session 211 removed at the defaults, and its Lazard row uses the toll of before session 208 (8.90).
   - `generator_earns_algorithm.md`, section 11.1: the hurdle rate's default reads 9.6; the code and the note's own opening say 12.
   - `datacenter_cost.md` and section 7 of `datacenter_pays_algorithm.md`: the hurdle rate reads 8 percent; the code says 9.6 since session 196.
   - `grid_network.md`: the newest complete hour is "the median hour"; `network_hourly.py` uses the 90th percentile of the hours' counts since session 61. And the floor of the day rule reads "500 MWh" in one note and "5,000 MWh" in another; `impossible_hours.md` holds the sentence that reconciles them.
5. **Two defaults have no cited source:** the coverage target of 1.25 (the battery's breakeven toll, the generator's contract price), and the datacenter's hurdle rate of 9.6 percent, which is a power plant builder's cost of capital (Lazard), not a datacenter's.
6. **The battery page prints the fleet's line for ERCOT and none for CAISO** (session 246's ruling 4 asks the same): the document says it aloud in the demo.

## How they were written

- Five writers in parallel, one a tool, each a sub-session of this session with the same brief: the seven parts, the sources to read, real numbers only, no file changed but its own. Each sent back its twelve most important numbers with the file and line.
- I read each document whole and searched the cited files for its figures: the branch's methods note and number files for the generator (69 figures) and the datacenter (80), the cards' own JSON for Research (47), the methods notes and the branch's data files for the Grid tool (60), the six methods notes for the battery (78). All found. Six of the generator's sensitivity figures are in their source at full precision (USD 8,208,909.55 for 8.21 million).
- Then the edits that were mine: the landing of 235 and 236 in the two documents and the index; the two reworded sentences of the datacenter page; the battery's computed figures moved from an untracked folder to `docs/howitworks/computed/`.
- `tests/test_session249.py` (9 tests) holds the form: the five files, the eight headings in order, the model numbered from one, ten questions numbered one to ten, the three tables, the demo's two sentences, no em dash. It holds no number.

## Checks

| What | Exit | Notes |
|---|---|---|
| `python scripts/precheck.py` | 0 | six of six |
| `python -m unittest tests.test_session249` | 0 | 9 tests |
| `node docs/howitworks/computed/battery_headline.mjs` | 0 | its output equals the writer's first run, line for line |
| `python scripts/license_state.py --check`, after main was merged | 1 | "is not what the four sources give today": the datacenter page's reads moved |
| `python scripts/licenses.py state`, then `--check` | 0, 0 | 197 tables, 56 pages, 0 problems |
| `python -m unittest discover -s tests` | 1 | 3,779 tests, 3 failures, 61 skipped: the three this machine always has (`test_session51`, `test_session125`, `test_session165`), run on `main` at `aa3addbc` with this session's files |
| `python scripts/freeze.py status` | 0 | no freeze |

## Decisions made without you

1. **Four documents were written from branches,** as the prompt allows, and two were corrected when their branches landed 14 minutes into the writing. I did not wait for 237 and 238: nothing on `origin` says when they land.
2. **Five parallel writers, then my own check of their numbers.** The cap of USD 0 is on the repository's model calls (the ledger); none was made. The writing is this session's own work, as the whole chain is.
3. **The battery's computed figures stay, marked [c], with the script and its output committed under `docs/`.** The alternative was to strike them: the demo's second and third minutes would then have no number for the day-ahead schedule's coverage or for CAISO's share. The script reads; it writes nothing; it is not a gate.
4. **The form is held by a test; the numbers are not.** A pin on 81.40 or 33.73 would fail the first session that rebuilds a table.
5. **Both doors to the internal view are named** (`/internal/open` and `/internal/unlock?token=`): the reports differ on which to give, and both exist on `main`.
6. **The stale lines of the four methods notes are listed, not corrected.** Three of the notes are files the code machine edited tonight; a second hand in them the same night invites a conflict.
7. **The license table was written again in this session** (session 248's ruling 4 asked the code machine to do it after its pages land). It needs one more run after 237 and 238 land: `python scripts/licenses.py state`.
8. **An index, `docs/howitworks/README.md`,** not asked for: it says which document was written from what, and how to read a number that has moved.

## For Samuel's ruling

1. **The Research cards built on NYISO's and ISO-NE's prices: may they show those numbers after 21 October?** Four cards filed under NYISO and three under ISO-NE, of nine (a card can be filed under both). If not, the cards need a rule (the grid's panel reads "license needed") before that day; today nothing does it.
2. **Stata: who runs the 11 do-files once?** And the six that read `varnames(1)` want their import line corrected first (the code machine or this one, on your word).
3. **The 11 committed cards: do you sign them off, and where is that recorded?**
4. **The four stale lines in the methods notes** ("What the writing found", 4): correct them in the next session on each machine?
5. **A cost of capital for a datacenter,** and a source for the coverage target of 1.25, or the words "ERW's choice" on the page beside each.
6. **The battery's [c] figures:** enter them in the methods note and the check script (so they are checked on every build), or leave them in `docs/howitworks/computed/`?
7. **The five demo paths: one run each in a browser** before any is shown. The Grid tool's and Research's can only be run from a local build until their branches land.

## Files

- New: `docs/howitworks/README.md`, `battery.md`, `generator.md`, `datacenter.md`, `grid.md`, `research.md`; `docs/howitworks/computed/battery_headline.mjs`, `battery_headline.txt`; `tests/test_session249.py`.
- Changed: `docs/state/licenses_2026-10-21.md`, `site/data/license_status.json` (written again by `licenses.py state`: `/cost-of-power` reads four more public tables).
- On this machine, not in git: `runs/session249/` (each writer's scratch files, the branches' reports, the checks' outputs).

## The landing of session 248

- Pushed 08:59:16 UTC (`task/248-license-table`, `0b596738`). Checks passed (run 38373093624); merged to `main` 09:07:22 UTC (`9700198f`); the deployment succeeded 09:09:56 UTC.
- Snapshots: before `s247-after` (08:50:36 UTC), after `s248-after` (09:11:08 UTC). `compare`: 25 pages, 0 differences in all. Expected: every page is in review, and the day in the status file changes nothing before 21 October.

## The landing

- Freeze: `python scripts/freeze.py status` exit 0, no freeze. Main pulled and merged before the push (it holds `aa3addbc`, the code machine's landing of 235 and 236).
- The code machine's landing of 235 and 236 (`aa3addbc`, deployed 09:17:02 UTC) is between session 248's after snapshot and this one's before: `compare s248-after s249-before` gives 0 differences on the 25 pages, as expected of pages in review.
- The before snapshot is `s249-before` (09:25:38 UTC); the push of `task/249-how-it-works` followed within the minute.
- The check run, the merge, the deployment's time, the after snapshot and the comparison are in session 250's note and report. Expected: 0 differences on the 25 pages (documents, a test and the license file's three review keys; no page reads anything new).
