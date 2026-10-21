# Session 470 report: the Digest and the Roundup, the fixes the audits name

21 October 2026, about 09:06 to 11:00 UTC, unattended, on portable-laptop (the code machine; the chain file was written for samueloldlaptop), in the worktree `C:\Users\samen\Documents\erw-470` on `wip/470-periodicals` (from `origin/main` at `440a2c8f`). Chain `queue/done/019-night-21-october-code.md`, session 470. Model spend USD 0: no issue was written and no model was called; each change is shown on the audits' named days by rebuilding their selection from `warehouse/output/news_stories.csv` with the brief's own functions. No warehouse data written, no published issue rewritten, nothing posted or sent, no web request, no file under `site/` changed (so no build and no shots).

## Read these first

- **The two audits are tonight's sessions 442 and 444** (`docs/reviews/digest-audit-2026-10-21.md` and `roundup-audit-2026-10-21.md`, on `wip/441-450-third`). Of their 30 ranked fixes, **16 are made here**, each with its test in `tests/test_session470.py` (37 tests). The rest need a ruling, a site change after session 402 lands, or data this machine does not hold: the table below gives each its reason.
- **No issue is lost to a repeat any more.** 5 and 6 October had no Digest because `assert_unique` refused the whole issue: two policy actions of one title (5 October), and a DOE address printed under Policy and again under AI and power (6 October). `without_repeats` now also compares the new lines with each other, and `drop_repeated_items` drops a later repeat, names it in the log and numbers the top items again before the hard check, which still runs.
- **One event, once, and not yesterday's story again.** Rebuilt from the stories as the repository holds them: on 2 October Korea's USD 120 billion framework is one item, not top 1 and top 2; on 14 October the attack on Aramco's headquarters is one item, not top 6 and 7; on 9 October Voltus's USD 225 million (shown on 8 October), Devon's Eagle Ford sale (8 October) and Poland's AP1000 order are left out; on 28 September Sabine Pass's final environmental statement (shown 25 and 26 September) is left out and the AI section drops the four items the scorer rated 3 and 4. In the Roundup, W40 shows Korea once and W41 leaves out W40's Amazon and Constellation agreement. The rules are written to fail safe: two stories must name a party in common and be filed in one sector, so a day's gas futures report or a big name with a round sum (Firmus and d-Matrix, both "Nvidia" and "USD 5 billion" on 9 October) is not merged. **Not caught:** W40's two OPEC+ weekend items and 13 October's two Saudi items, which share no amount and too few title words.
- **Session 402's site work is not on this branch** (`wip/015-land`: the Digest's figures keyed, held figures read as held, a day without a Digest said, the method on `/about#digest`). This session changes only the Python that writes the issues, which 402 did not touch; the real-time line keeps the form 402's parser reads (`` `spp_rtm` `` after the frequency), and a test pins it.

## What to review

- The branch: `https://github.com/SamuelEnrique/erw/tree/wip/470-periodicals` (commits `63dcc2e3`, `239e78cf`, `a8afc37c`, and this report).
- The code: `warehouse/news/brief.py` (`same_event`, `one_per_event`, `issue_items`, `repeat_of`, `not_shown_before`, `select`, `drop_repeated_items`, `money_style`, `plain`, `rt_label`, `paused_row`), `warehouse/news/roundup.py` (`fuel_change`, `policy_title`, `dockets`, `dated`, `DEAL_LABEL`), `warehouse/news/email_digest.py` (`live`, `gate_links`, the opening line), `warehouse/news/funfact.py` (`GRAVE`), `warehouse/analysis/templates/peak_premium_block.py` (`BLOCK_HOURS`).
- The rebuilds, before (origin/main's `brief.py`) and after, in `runs/chain_019/s470/` (git ignores `runs/`): `before_<day>.txt`, `after_<day>.txt` for 28 September and 2, 9 and 14 October (and after only for 12, 13 and 20 October), `roundup_W40_W41.txt`; the script `rebuild.py`.

## Every fix of the two audits

| Audit, rank | Fix | State | Commit, test |
|---|---|---|---|
| Digest 1 | Held NYISO and ISO-NE prices printed as held in the issue and the email | **not made: a ruling** (Samuel's, in both audits; the page holds them since session 402) | |
| Digest 2 | The window opens at the previous issue's end; a missed weekday caught up | **not made: a ruling** (it changes what a Monday covers) | |
| Digest 3 | Never lose an issue to a repeat | made | `63dcc2e3`; `NoIssueLostToARepeat` |
| Digest 4 | Do not reprint an earlier issue's story (seven days), unless it brings a new sum of money | made | `63dcc2e3`; `NotTheDayBeforeAgain`, `TheNamedDays` |
| Digest 5 | One event, one item (the scorer's clusters joined across batches) | made in the selection, not in `score.py` | `63dcc2e3`; `OneEventOneItem`, `TheNamedDays` |
| Digest 6 | The AI tie-break | **not made: a ruling** (the Roundup audit asks Samuel) | |
| Digest 7 | Google News links | made as the audit's no-ruling form: "(via Google News)" beside the link, on the page and in the email | `63dcc2e3`, `239e78cf`; `Wording`, `TheEmail` |
| Digest 8 | The why lines in the voice | made at print: "major", "massive", "significant(ly)", "huge" cut, "a" and "an" set; "signals" and "boom" left (a verb and a noun: cutting them breaks a sentence) | `63dcc2e3`; `Wording` |
| Digest 9 | One money style | made in `detail()`: "USD 45 billion", "CAD 14.3 billion" | `63dcc2e3`; `Wording` |
| Digest 10 | The chart of the day: preliminary caveat, strength floor, no ruled draft | **not made**: the caveat needs EIA's statement that the newest state month is preliminary, which no file of the repository holds; the floor is a number to choose; the ruled drafts are the three rulings no person made (Samuel's) and need a database read | |
| Digest 11 | No deaths or disasters in the fun fact | made: `check_record` refuses them; the 14 October item fails it now; the bank's 43 rows all pass. The 14 October issue itself is not corrected (a ruling) | `a8afc37c`; `TheFunFactAndTheChart` |
| Digest 12 | The real-time price named; MISO's absence said | made: "ERCOT's real-time settlement point price" after the code; MISO's row "not requested: paused by the ERW since 2026-10-04 (MISO's terms forbid automated access)", read from `paused_sources.csv` | `63dcc2e3`; `Wording` |
| Digest 13 | The archive lists a missed weekday | **done by session 402** (`wip/015-land`, `site/lib/markdown.ts`) | |
| Digest 14 | The schedule line | **done by session 402** (`site/app/about/page.tsx`) | |
| Digest 15 | Two minutes: what stays above the fold | **not made: a ruling** | |
| Digest 16 | The AI section takes significance 5 or more | made (`AI_MIN_SIG`) | `63dcc2e3`; `TheAISection` |
| Digest 17 | The email links no page in review | made: the issue's page only when `release.ts` says it is live, else its markdown on GitHub; "How this is made" only when `/about` is live; a site link in a section written as its text | `239e78cf`; `TheEmail` |
| Roundup 1 | One event once, not the previous Roundup's story | made (the Digest's functions; the previous ISO week's file as the ledger) | `239e78cf`; `TheNamedDays`, rebuild of W40 and W41 |
| Roundup 2 | The fuel change a week, not two trading days; an outlying close flagged | made: the newest close against the newest close seven or more days before it, both dated; a close that moved over 8 percent in a day while the other crude moved under 5 is flagged "to be confirmed against EIA's page". W40's WTI row would compare 29 with 22 September (USD 96.16 and 96.41), not with 25 September's 85.23 | `239e78cf`; `TheRoundup` |
| Roundup 3 | The chart of the week's eligibility | **not made: a ruling** | |
| Roundup 4 | Google News links | made (Digest 7) | `63dcc2e3` |
| Roundup 5 | The email carries the page's disclosures | made: the line under the title (the period, the story count, the model line), and no single-star emphasis in the text part | `239e78cf`; `TheEmail` |
| Roundup 6 | A missed week said | **not made: a ruling** (week 42: one of the options Samuel is asked to choose from) | |
| Roundup 7 | Deals and datacenters: a floor, US first | **not made: a ruling** | |
| Roundup 8 | Deal rows extracted twice | **not made here**: `warehouse/deals/extract.py` is the deal tracker's (session 465 of this chain) | |
| Roundup 9 | Policy wording | made: a title over 160 characters as its subject (the parties kept when short); "docket" once; one date, "published" or "released" | `239e78cf`; `TheRoundup` |
| Roundup 10 | Codes as words | made: every `DEAL_TYPES` code as words ("acquisition" for `m_and_a`, as `site/lib/deals2.ts` labels it) | `239e78cf`; `TheRoundup` |
| Roundup 11 | The chart shows the number it calls notable | **not made**: a new chart form for a template the analysis engine and its card share; for the code machine with a design pass | |
| Roundup 12 | One definition of midday | made in the template's fact: each block's hours, local time; the finding's own 10:00 to 15:59 is left as it is (it is that card's method) | `a8afc37c`; `TheFunFactAndTheChart` |
| Roundup 13 | Trace W40 and W41 | **not made: data**: this machine's tables end on 22 September (fuels) and early October | |

16 made (Digest 3, 4, 5, 7, 8, 9, 11, 12, 16, 17; Roundup 1, 2, 5, 9, 10, 12), with Roundup 4 the same change as Digest 7; 2 done by session 402; 7 a ruling (Digest 1, 2, 6, 15; Roundup 3, 6, 7); 3 not made for the reasons above (Digest 10, Roundup 8, 11) and 1 for data (Roundup 13).

## Checks

Every gate redirected to a file under `runs/chain_019/s470/` in the worktree, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 470"` | 0 | every check passed; the duty mark was not taken again (the main checkout holds it) |
| `tests.test_session470` | 0 | 37 tests OK, among them the 2 and 9 October rebuilds from the repository's stories |
| The 52 tests that read the brief or the Digest | 1 | 1,112 tests; the errors are `test_session170`, `182` and `67`, the same as on origin/main's `brief.py` (`near_base.out`) apart from `67`, which passes alone (a scipy import that fails only after other modules in one process) |
| The 24 tests that read the Roundup or the email | 1 | 492 tests; the errors are in `test_session170`, `181` and `233` (analysis findings), all of which pass alone with these changes and on the code before them: the same scipy import |
| The email's tests (`119`, `206`, `232`, `34`, `63`) | 0 | |
| The fun fact's tests (`176`, `202`) and `test_session182_flow` (the template) | 0, 0 | 101 and 19 tests |
| The whole suite (`ERW_LOCK_EXEMPT=1 ... unittest discover -s tests`, under the build lock) | 1 | 4,829 tests, 11 failures, 268 skipped, in 1,689 s (`suite.out`). Every failure is a site Node test (`test_session121`, `137`, `143`, `148`, `153`, `156`, `161`, `168_ask`, three of `92`) that stops on "alias-loader: nothing at @/content/docs.json", a file the site writes at its build and a new worktree does not hold; none reads a file this session changed |
| Build, snapshot, browser checks, Impeccable, shots | none | no `site/` change; `db_probe.py` not needed |

## Decisions made without you

1. **Each change is shown on the named days by rebuilding the selection from `news_stories.csv`, not by writing the issue again**: rewriting an issue needs the model (its headlines), which this chain may not call. The rebuild matches the published top 10 of 2 October in 9 of 10 places; the stories table holds more stories than the run saw (344 against 326), ingested later with earlier publish times.
2. **One event is joined in the issue's selection, not in the scorer**: the scorer's clusters are the model's (`score.py`); the brief's rule is code and reads only the clusters' own fields.
3. **The rules prefer a repeat to a lost story.** Two clusters are one event only with a party in common and one sector; an earlier issue's story is one only with a link, or a party and an amount, or a party and five title words in common. The first version, tried on the seven named days, also merged a day's gas futures columns, two CAISO notices of one month and two unrelated Nvidia stories; it was tightened until those stayed apart, and the tests keep them apart.
4. **A cluster an earlier issue printed comes back when it brings a sum of money none of those issues printed** (a price disclosed after the deal), the audit's "unless the cluster has a new figure", narrowed to sums: a new MW or percentage in a later story of the same deal is a detail.
5. **The hype words are cut at print, not refused at scoring**: refusing them would send the scorer back to the model; "signals" and "boom" stay.
6. **The fuel change looks back seven days from the newest close held**, not to "the latest complete trading week": EIA's lag makes the week's end the newest close in practice, and the rule needs no calendar of trading days.
7. **A long Federal Register title becomes its subject**, the part after the last semicolon, not the part before the first (the audit's wording), since the part before is the list of companies.
8. **The email names the issue's markdown on GitHub while every page is in review**, rather than no link at all: the repository is public and the file is the issue as written.
9. **Session 402's branch was not merged into this one**: none of the files this session changes is changed there.

## For Samuel's ruling

- The Digest audit's and the Roundup audit's rulings, unchanged: the held prices in the issue and the email, and the email while `news_index` is held; the window and a missed weekday; the AI tie-break; the two-minute form; the chart of the week's eligibility; week 42; US first in the deals and datacenter sections; the 14 October fun fact as published.
- The chart of the day's strength floor (1.01 robust standard deviations chose 20 October's chart): a number.
- A source for "the newest month of EIA's state data is preliminary", so the chart of the day can say it.

## To finish

- Land `wip/470-periodicals` with the chain's landing (session 461's second part or 474): merge origin/main (and `wip/015-land` if it has landed by then; no file in common), `tests.test_session470`, the suite, then the usual gate. No page changes, so the snapshot comparison should read 0 differences; the next Digest written after the landing is the first to carry the changes.
- After session 402 lands: `/about#digest` (the method on the site) should say what the brief now does (one event once; an earlier issue's story left out for seven days; the AI section at 5 or more; Google News links named). It is a `site/` change, so it was not made here.
- On the data machine: Roundup fix 13 (trace W40 and W41), and the side finding that `ercot_rtm` rows carry `variable` = `spp_rtm`.

## Files

- `warehouse/news/brief.py`, `warehouse/news/roundup.py`, `warehouse/news/email_digest.py`, `warehouse/news/funfact.py`, `warehouse/analysis/templates/peak_premium_block.py` (changed).
- `tests/test_session470.py` (new).
- This report.
- Not in git: `runs/chain_019/s470/` (the audits as read, the rebuilds before and after, the test and suite outputs, the scripts).
