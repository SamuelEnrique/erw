# Note: the large-load rules on the site, 16 November 2026 (old laptop, chain 302)

Energy Research Warehouse (ERW). Sessions 7200 to 7204, 16 November 2026, unattended, one Claude Code session, samueloldlaptop (code role). Chain file: `queue/done/302-day-16-november-oldlaptop-large-load-on-the-site.md`. Progress: `docs/state/progress_c302.md`. Model spend: USD 0.00; no model call was made. Nothing is landed: two branches wait on the desk (`docs/state/landing_request_oldlaptop.md`, rows 15 and 16). Reports: `archive/sessions/SESSION_7201_REPORT.md`, `SESSION_7203_REPORT.md` and `SESSION_7204_REPORT.md` on `wip/7200-large-load`; `SESSION_7202_REPORT.md` on `wip/7202-key-refusal`.

## First

- **Nothing was built or seen in a browser on this machine.** A site build needs 2.5 GB of memory free (the chain's rule); the most free all day was 2.0 GB. No screenshot at 1280 or 390 exists, no hover or A and B was exercised in a browser, axe was not run. In their place: the pages' components drawn to HTML with the site's own code and files, read and tested (`site/scripts/tsx-loader.mjs`; 58 checks on the new sections, 25 on the whole tab). The desk's landing gate builds the site.
- **Row 16 should land first.** The key is at its limit until 1 December. Until row 16 lands, each daily run records the news scoring, the policy scoring and the Digest's step as failed. Nothing wrong is published either way: no Digest is written and none is sent.
- **One test fails on clean main on this machine and is not this chain's:** `tests/test_session705.py` (`connect.json` against its table).

## What a reader can now do that they could not (after row 15 lands; both pages are in review)

- **Open a utility's large-load rule from a row of the tab.** `https://erw-flame.vercel.app/cost-of-power?view=allgrids`: each row's Utility cell and Time to connect cell draw a line that opens the rule. Of 48 rows: 21 open a utility's own rule, 10 the state's rule alone, 5 say "no large-load rule found", 11 "no large-load rule read", and PJM's one row opens the 22 rules read in PJM by state.
- **Read any of 122 rules in full, and compare two.** Under the tab, "Large-load rules by utility": the smallest load, the contract's length, the minimum bill, the collateral, the exit fee, the study time, the time to energize and the queue, each as the document prints it with its cite on hover; filters by state, grid, status and name; A and B; CSV, Python and Stata of the rows shown.
- **See what changed in 90 days.** 94 changes, newest first, by region and by the rules' State filter, each with its document and the rule it changed.
- **Reach the state's law.** `https://erw-flame.vercel.app/policy?view=monitor&state=VA#large-load-laws`: 27 laws and bills and 1 held under the monitor's records, following its State filter. A state with no row says what the research found or did not reach, never "no law".
- **Held rows are drawn, not left off.** 22 held rules, 4 held changes and 1 held law are named with every other cell blank and "license needed" on hover: 228 blank cells in the rules table, 16 in the changes, 4 in the laws.
- **On the tab itself (the read of five cases):** the energy cell names its market ("da 37.21 rt 35.35"); the all-in hover says the load's own effect on prices is not modelled; a Texas row's transmission hover names the four wires utilities' own lines.

## What the scheduled jobs now do when the key refuses (after row 16 lands)

- A model step the API refuses for the key's usage limit ends as skipped: one row of `erw_health` a step, "the key's limit" with the date access returns, no retry, no email.
- No Digest and no Roundup is written or sent on a day the scoring was refused.

## Needs the key (USD 4.80 in all)

- **Whether `/ask` answers from the three large-load tables:** about USD 4.80 to ask the 58 questions written for them (58 at about USD 0.082). Known without it: the tables are not in the live set, and on 15 November the site's chat refused all 58 rightly, by the table's name.

## Waits for Samuel, each with the default taken

- **The three tables and the live set.** Default: they stay out (their license verdict is unsettled, as the two registry tables'); the pages draw the public rows from a site file.
- **The blank cell.** The new sections draw a held value blank with "license needed" on hover, as your page rule says; the tab's older cells print the words in place. Default: left as two forms.
- **A bill withheld for a robots file (Texas S.B. 6)** is drawn blank and called "not shown", not "license needed". Default: so.
- **Which transmission figure a Texas row's all-in counts:** the Commission's rate for all wires utilities, or the row's own utility's lines. Default: the Commission's, as now.
- **Evergy Kansas South and Evergy's Kansas rule.** Default: not matched; the SPP North hub says "no large-load rule read, 3 in KS".
- **PJM-wide records under a state** in the monitor. Default: left; the State filter's hover says to use Grid.
- **Michigan's law row** (a sales tax exemption for data centers). Default: left as the table has it.
- **Whether a day under the key's limit sends you one line.** Default: nothing is sent.

## Asked of the data machine (`docs/state/data_requests_large_load.md`, rows 18 to 29, all "requested")

- 18: the three tables into the live set, if they may be. 19: the page file's rebuild when the tables change.
- 20: ERCOT's load zones' wires utilities. 21: ERCOT's 2030 peak forecast revision of +0.4 MW, to check. 22: a later ERCOT large-load report than 19 June. 23: PJM's one row and its county. 24: the rates of Dominion's GS-5, AEP Ohio's DCT and Georgia Power's schedules. 25: rows for the balancing authorities outside the seven grids (39 of the 122 rules are theirs).
- 26: Texas S.B. 6 from an allowed copy. 27: eight states with no row. 28: FERC's large-load orders as monitor records. 29: the research's working words in six cells and 45 notes.

## Waits for a build (this machine with 2.5 GB free, or the desk's gate)

- `check-values` on the two pages added to its list; `check-390` and axe on them; screenshots at 1280 and 390 into `docs/reviews/large-load-on-site/`; a hover, A and B, a filter and a rule opened from a change, in a browser.
