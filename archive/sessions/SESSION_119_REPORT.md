# Session 119 report: the news products. Sunday's Roundup, the digests of ten days, the weekly chart's chooser, the sending domain

**Done, with one thing I did not do because it had already happened.** Sunday's Roundup was delivered to your address at 23:05:46 UTC on 4 October; the run failed afterwards, on a git step. I did not send it again: the send-once guard refuses, and you have it. The cause is fixed in three places. The weekly chart's chooser is rebuilt. One deploy (run 37288670943, merged as `6354b9b`), with the snapshot of the live pages before and after: 34 differences, every one the home page's latest prices or `/network`'s hourly refresh. Model spend USD 0.0073 of a cap of USD 3.

## Read these first

1. **The Roundup of 4 October reached you.** Resend holds it as "delivered", from `onboarding@resend.dev` to your Stanford address, subject "ERW's Roundup, 2026-W40", at 23:05:46 UTC. The guard's table has one row for it: sent, 1 recipient, run 37242113598. What failed was the step after the send.
2. **Two things failed, in both runs, and neither is in `erw_health`.**
   - **The rendered copy's commit.** After the email, the step committed `docs/digest/email/` and ran `git pull --rebase` with the run's other files still modified: "cannot pull with rebase: You have unstaged changes", exit 128.
   - **The cost ledger.** The Roundup's model calls add rows to `api_cost_ledger`. Coverage came with the checkout and said 1,110 rows; the file held 1,113. Since session 65 the loader refuses a table coverage does not describe, so the load failed and the Redivis upload after it never ran.
   - `erw_health` says "ok" for all three recorded steps of both runs: the two commands that failed ran outside `health.py`. "No scheduled job fails on GitHub" was not true of this workflow.
3. **The failure cost a second run.** The gate asks whether a run succeeded today. None had, so GitHub's own schedule started again at 01:23 UTC on Monday. That run wrote the whole Roundup a second time (the model was paid twice: USD 0.0117 for the Roundup's text each time, and the chart's note besides), overwrote the Roundup on the site with different wording, and then its email was refused by the guard. It failed on the same two steps.
4. **What you read on Sunday and what the site showed were not the same text.** Four headlines and the chart's note differed. I put back the Roundup as it was emailed (commit `85b972b`) and wrote the rendered copy the failed step never committed.
5. **Of six weekday digests due in the last ten days, one was delivered: Monday 28 September.** Of two Roundups, one: 4 October. The table is below. The largest single cause: your address was on the unsubscribe list from 29 September 00:32 UTC until session 59 restored it on 2 October.
6. **The two causes you named for the daily run were already mended,** by sessions 77 (a table uploaded before main knows it: it passes on its own header's license) and 113 (ERCOT's yearly reserve price file in both forms). I added tests that hold both in place, and what was missing: a failed step is now one line by email the same day.
7. **Last Sunday's chart of the week was a count of the ERW's own reading:** "Energy deals in the news, by month", 59 in September, the most ever, because the ERW began reading in late September. The new rule would have chosen a real change (below).
8. **The chooser does not draw on every public table.** It reads 38 of 117. For the other 79 `docs/analysis/tables.json` gives a stated reason each; for 9 the reason is the plain one, that no line reads it yet.
9. **No sending domain is verified,** which is why nobody but you can be emailed. The steps are in `docs/email_domain.md` and under "The sending domain" below.

## Sunday's Roundup: what happened, by the clock

| UTC | What |
|---|---|
| Sun 4 Oct, 23:00 | The database's schedule dispatches the run (37242113598) at `9aa7921` |
| 23:05:28 | The Roundup is written: 1,692 stories, 1,489 clusters; headlines USD 0.0075, summary USD 0.0042 |
| 23:05:43 | Committed and pushed as `85b972b` |
| 23:05:45 | The guard's row is claimed; the email goes out; Resend records it delivered at 23:05:46 |
| 23:05 | The rendered copy is committed locally; `git pull --rebase` refuses: exit 128. **The run fails** |
| 23:06 | "Keep the cost ledger": archived (3 rows), then the loader refuses on coverage: exit 1. The Redivis upload does not run |
| Mon 5 Oct, 01:23 | GitHub's own schedule starts a run (37251227726) at `6d1a85b`. The gate finds no successful run "today" and lets it through |
| 01:28:10 | The Roundup is written again; committed as `cce5278`, over the first |
| 01:28 | "news_email roundup SKIPPED: roundup already sent: issue 2026-W40 on 2026-10-04 (sent, 1 recipients, run 37242113598 ...)". The guard held |
| 01:28 | The same two failures. **The run fails** |

Source: the two runs' logs (kept on this machine, `runs/session119/`), `erw_health`, the table `digest_sends`, and Resend's own list of the account's emails.

## Fixed for good

| What | Before | Now |
|---|---|---|
| The rendered copy's commit | `git commit`, then `git pull --rebase` over a dirty tree | `warehouse/news/commit_paths.sh`: stages only the paths named, commits, sets every other change aside, pulls and pushes (once more if main moved), puts the changes back. Never a force push. It runs under `health.py`: a failure is a row of `erw_health` and never the run's |
| The ledger's load | refused: coverage older than the table | `build_coverage.py --only '^api_cost_ledger$'` first: that one row is rebuilt, every other row carried word for word. Each of the four ledger steps runs under `health.py`: one that fails no longer stops the next |
| A second run writing the Roundup again | nothing stopped it | A scheduled start first asks the guard's table (`email_digest.py --roundup --sent-check`): already sent is a skip with its reason, before anything is restored or written. A person's run still writes again; the guard still refuses a second email |
| Nobody told | a failed run on GitHub, or nothing | `warehouse/health.py alert`: the last step of the daily run and of the Roundup. A step recorded as failed is one line by email the same day, to the fixed recipients; no failed step, no email. It cannot fail the job |
| The Roundup on the site | the second run's wording | the Roundup as emailed, and `docs/digest/email/2026-W40-roundup.html` and `.txt` |

- **The commit script is tested in real repositories** made for the test: a tracked file changed by the restore, an untracked log, main moved by someone else. The commit holds only the email's file; the other changes are still in the tree afterwards.
- **`--only` was tried on this machine** on a table that had not changed: coverage came back identical, byte for byte. A pattern that matches nothing exits 1.
- **The alert was dry-run on yesterday's real rows.** It would have said: "1 step of daily prices failed on 2026-10-04 UTC (run 37207629600): ercot_as_prices: ... NP4-181-ER zip holds ['...DAMASMCPC_2026.xlsx'], expected one CSV". For today so far it finds no failed step and sends nothing.
- **A YAML fault of my own, caught before the push.** My first edit put a colon and a space inside an unquoted `run:` line; the workflow no longer parsed. A test now reads every workflow file as YAML.

**Not fixed, and said:** the three ledger rows of the two Roundup runs (and one of this session's trial, USD 0.0073) are in the archive or a trial folder and not in the Redivis draft's ledger. Session 121 spends on the model and keeps the ledger; it will carry these with its own.

## Every digest and Roundup due in the last ten days

Friday 25 September to Sunday 4 October. The digest is a weekday email since session 23 (28 September); the Roundup is Sunday's.

| Day | Due | Written | Delivered | Why not |
|---|---|---|---|---|
| Fri 25 Sep | digest | yes, by sessions 6 to 8 on this machine | no | the email tool did not exist until 27 September (session 19) |
| Sat 26 Sep | none (a digest was still written: the weekday rule came on 28 September) | yes | no | as above |
| Sun 27 Sep | Roundup 2026-W39 | yes | **no** | "not sent: RESEND_API_KEY, DIGEST_RECIPIENTS not set": the secrets were not in the repository yet. A digest was also written that day and not sent, for the same reason |
| Mon 28 Sep | digest | yes | **yes, 23:52:18 UTC** | the 21:10 run could not send (secrets); the 23:52 run did |
| Tue 29 Sep | digest | not on main | no | your address had been on the unsubscribe list since 00:32 UTC (session 58 found it; no report says why). Only the shadow digest reached you, at 10:51 |
| Wed 30 Sep | digest | **no** | no | five runs. Two failed at the merge tests (a chat test). In the three that reached the digest, `news_brief` failed on a date it could not read (pandas, mixed formats); one of those also met the database's 400 MB limit, and the last ended green without a digest. The email step sent Monday's issue again each time, "to 0 recipients" |
| Thu 1 Oct | digest | **no** under its own date | no | two runs failed (19:06 in the first minute; 22:48, which ran past midnight). The late run wrote the digest dated 2 October at 00:23 UTC and sent it "to 0 recipients" |
| Fri 2 Oct | digest | yes, at 00:23 UTC, by Thursday's late run | **no** | all three starts on Friday were skipped: "the day's work is done: ... 1 'Daily prices 2026-10-02' commits on main". Thursday's run, finishing after midnight, had taken Friday's turn. Your address was restored that day (session 59), after the send |
| Sat 3 Oct | none | | | |
| Sun 4 Oct | Roundup 2026-W40 | yes, twice | **yes, 23:05:46 UTC** | |

- **Counted against Resend, not against the logs.** Resend holds 53 emails for the account, all to your address. Two are a digest or a Roundup proper; three are shadow issues ("SHADOW HAIKU"); the rest are session and alert lines.
- **Today, Monday 5 October,** a digest is due from the 14:00 UTC run. Your address is not suppressed (the list is empty) and there are no subscribers. I will read the run after 14:00.
- **One cause still open:** a daily run that crosses midnight commits under the next day's date and the gate then counts the next day as done. It happened once (1 to 2 October). I did not change the gate: it is the daily run's own, hours before a run that matters. For Samuel, 3.

## The weekly chart's chooser

### What was wrong

- The rule compared a headline's level with its own history. Anything that grows with the warehouse wins.
- 4 October's pick: deals in the news, 59 in September against 11 the month before. True, and a fact about the ERW.
- The caption: "... with a robust z of 2.73 against its own history." A statistic, not a finding.
- Ten templates read 8 public tables.

### The rule now

Stated in `warehouse/analysis/run.py` and `docs/methods/automated_analysis.md`.

1. **Real.** Only a measurement of the energy system competes. A count of what the ERW collected is run, shown, and never chosen.
2. **A change.** The headline's change from the week before (weekly figures) or from the same month a year earlier (monthly figures with a season).
3. **Notable against its own recent past.** The change is ranked by size among the measure's last 104 weekly, or 36 monthly, changes. The score is the share that were smaller. At least 8 are needed.
4. **This week's.** The period must be new: not this measure's headline in an earlier week's run. And it must have ended within 100 days.
5. Highest score wins; ties go to the higher z of the change, then to the order of the list.

If nothing new passes, the largest change among periods already seen is chosen and the chart says so. With too little past, the old level rule is used and the chart says so.

**I changed the statistic after its first trial.** My first version scored a robust z of the change over the whole history. It chose US battery storage: 743 MW added in August 2026, z 9.32. Of 138 earlier months, 29 had added as much. Most of that history is years with nothing added. The rank over a recent window is what the caption can honestly say.

### The watch list

`warehouse/analysis/watch.py`. A measure is one line: a table, an entity, a variable, how a period is made, what it is compared with. 31 lines today. The four you named are there:

- **Storage build-out:** US and ERCOT operating battery MW, by month.
- **The shoulder hours:** California and Texas, hours needed, by month.
- **The day-ahead awards:** ERCOT's storage fleet, USD per MW, whole months only.
- **Curtailment:** California wind and solar by month; SPP wind by week (beside the existing California midday template).

The others: Henry Hub, WTI, Brent, gasoline and diesel at the pump, New York Harbor diesel, crude stocks, imports and exports; ERCOT's day-ahead price, load-weighted price and the battery model; regulation prices in ERCOT, CAISO, NYISO and SPP; retail price and sales; battery discharge; California solar; ERCOT wind held back; large load approved; solar's and gas's share of US generation.

- A week needs its rows (4 of 5 business days, 7 of 7, or 160 of 168 hours). The week and month under way are not shown. Nothing is filled.
- **No line reads a carbon table:** they are behind session 118's hold.
- On GitHub's runner the Roundup's job now restores the lines' tables. One it cannot restore is skipped and named.

### What the rule gives for last week (a trial, not published)

39 public templates and lines ran (9 templates, 30 lines) and 1 line was skipped (ERCOT wind held back: one complete week held, three needed).

**Picked:** "CAISO Regulation Up day-ahead price, weekly mean: 5.04 USD/MW in the week of 2026-09-28 to 2026-10-04, up 1.73 from 3.31 the week before. Of the 104 week-to-week moves before it, 7 were as large."

**Also moved, next by the same rule:**

- WTI spot price at Cushing, weekly mean: 93.57 USD/bbl in the week of 2026-09-21 to 2026-09-27, down 9.97 from 103.54 the week before. Of the 104 moves before it, 7 were as large. (The same rank as the pick; the pick's move stands further from its own usual.)
- New York Harbor diesel: 4.75 USD/gal, down 0.28 from 5.03; 12 of 104 as large.
- SPP Regulation Up: 10.78 USD/MW, down 4.11 from 14.89; 12 of 104.
- NYISO regulation: 19.46 USD/MW, up 7.74 from 11.72; 17 of 104.
- Brent: 117.08 USD/bbl, down 7.07 from 124.15; 18 of 104.

Deals in the news, 11 to 59: run, shown, not a candidate.

- **You may think WTI is the better chart.** By the rule the two are tied on rank and the tie goes to z. If oil falling USD 10 should beat a regulation price rising USD 1.73, the rule needs a notion of weight, and that is a judgment I did not make. For Samuel, 2.
- **The caption is the finding and code writes it.** The model still drafts the two-sentence note under the number check, and is told to name no statistic. Tried once on the trial: it passed on the first attempt, USD 0.0073.
- **I did not rerun last week's chart for real.** It went out with the Roundup. The new rule takes effect on Sunday 11 October.

### Which public tables it reads

`docs/analysis/tables.json`, written on every run. Today, of 117 public tables:

| | Tables |
|---|---|
| Read by a template or a line | 38 |
| A list of things or events, not a series | 21 |
| The latest values or a short window only | 10 |
| An input of a table that is read | 9 |
| **No template or line reads it yet** | **9** |
| Behind a fix held for approval | 8 |
| A study of past events or a fitted model | 8 |
| Yearly figures | 5 |
| By hour of the day or by owner, not one series | 5 |
| EIA's daily sums, which can hold a faulty value | 4 |

The 9: `battery_stack_review_monthly`, `eia_crude_first_purchase_prices`, `eia_lng_exports_monthly`, `eia_padd_crude_pipeline_flows`, `eia_sector_energy_consumption_monthly`, `eia_state_generation_monthly`, `ercot_peak_premium_monthly`, `ercot_storage_dam_offers_monthly`, `merchant_revenue_monthly`. Each is one line away.

## The five stories ranked highest, for your judgment

Only five digests exist. For the three weekdays with none I give the scorer's five highest for the UTC day, ranked as the digest ranks (significance, then AI and power relevance, then the number of stories); the headline is the scorer's, since no digest was written.

**2026-09-25**, as the digest printed them
1. Oracle invokes force majeure on data center project amid power delays (significance 8, datacenter_power)
2. Applied Digital reveals $3.2bn Delta Forge 2 AI data center planned for Alabama (significance 8, datacenter_power)
3. Anthropic strikes multi-billion dollar cloud computing deal with Akamai (significance 8, deal)
4. DOE unveils funding for 31 grid upgrade projects to speed data center connections (significance 8, transmission)
5. Fervo Energy achieves first power at Utah geothermal plant (significance 8, generation)

**2026-09-26**, as the digest printed them
1. Applied Digital plans $3.2bn AI data center in Alabama (significance 8, datacenter_power)
2. Problems emerge in Oracle's New Mexico AI data center project (significance 8, datacenter_power)
3. DOE funds 31 grid upgrade projects to speed data center connections (significance 8, transmission)
4. Anthropic signs $12 billion computing deal with Akamai (significance 8, deal)
5. Fervo Energy achieves first power at Utah geothermal plant (significance 8, generation)

**2026-09-27**, as the digest printed them
1. EPA rollback of power plant rules seen adding 123 million tons of CO2 (significance 8, policy)
2. Tight global natural gas supply could persist through next summer (significance 7, gas)
3. US moves to finalize lower vehicle fuel economy standards (significance 7, policy)
4. US natural gas futures fall as weather cools (significance 6, gas)
5. Trump rejects Iranian proposal to reopen Hormuz Strait (significance 6, geopolitics)

**2026-09-28**, as the digest printed them
1. UK PM Burnham to launch state-owned GB Grid to cut energy costs and speed connections (policy)
2. Qatar extends LNG force majeure notices as Hormuz disruptions continue; Edison says until early December (lng)
3. NGPL asks FERC to approve 550,000 Dth/d Texas Panhandle pipeline expansion to serve a planned Google data center (datacenter power)
4. Fervo Energy sells power to the grid from a 33 MW unit at Cape Station in Utah (renewables)
5. EIA: renewables and storage to add about 82.7 GW in the next 12 months (generation)

**2026-09-30**, no digest written: the scorer's five highest of 591 stories published that day
1. Senators release bipartisan omnibus permitting package to streamline approvals (significance 8, policy; Canary Media, Hart Energy, Heatmap News)
2. FERC partially approves PJM backstop procurement; PJM delays power auction (significance 8, policy; Utility Dive)
3. Constellation and Amazon sign 20-year power deal for Maryland nuclear plant (significance 8, ppa; Reuters)
4. FERC accepts PJM reliability backstop procurement, suspends it to Feb. 28, 2027 (significance 8, policy; PJM newsroom)
5. 617 projects totaling nearly 169 GW enter PJM's new interconnection Phase 1 (significance 8, interconnection; PJM newsroom)

**2026-10-01**, no digest written: the scorer's five highest of 428 stories published that day
1. South Korea to invest $120 billion in US nuclear, including eight large reactors (significance 9, nuclear; ANS Nuclear Newswire)
2. US and South Korea outline $120 billion framework for six AP1000 and two APR1400 units (significance 9, nuclear; World Nuclear News)
3. Amazon signs 20-year PPA with Constellation for Calvert Cliffs nuclear capacity (significance 8, nuclear; ANS Nuclear Newswire, Data Center Dynamics, OilPrice.com)
4. Senate permitting bill gives FERC transmission siting authority, ends NIETCs (significance 8, policy; Heatmap News, Rigzone, Utility Dive)
5. Oil jumps 4% on reports China halts fuel exports, US troops head to Middle East (significance 8, oil; Reuters)

**2026-10-02**, as the digest printed them
1. South Korea to invest $120 billion in U.S. nuclear projects, including eight large reactors (nuclear)
2. US Commerce outlines USD120 billion framework for six AP1000 and two APR1400 units (nuclear)
3. Amazon and Constellation sign 20-year deal adding 190 MW at Calvert Cliffs (nuclear)
4. Bipartisan Senate permitting bill would let FERC issue transmission permits in the public interest (policy)
5. Oil jumps 4% on reports China halts fuel exports and US troops head to Middle East (oil)
**2026-09-29**, no digest written: the scorer's five highest of 188 stories published that day
1. NRC approves TVA construction permit for BWRX-300 at Clinch River (significance 8, nuclear; ANS Nuclear Newswire, Heatmap News, Reuters)
2. Trump to promote $54 billion Korean-backed Alaska LNG plan (significance 8, lng; Bloomberg.com, Hart Energy, Reuters)
3. Shell approves project to double LNG Canada capacity with Phase 2 (significance 8, lng; Hart Energy, Rigzone)
4. Trump holds talks on possible diesel export ban (significance 7, oil; Financial Times)
5. PJM starts annual vetting of large load requests for 2027 forecast (significance 6, datacenter_power; PJM newsroom)

Two things I noticed, which are yours to judge:

- **25 and 26 September carry the same five stories in a different order.** Both digests covered overlapping 24 hours.
- **1 October's first two are one event** (South Korea's USD 120 billion for US nuclear), from two outlets, and the digest of 2 October printed both. The digest drops a repeat by its normalized headline or its first link; these differ in both.

## The sending domain

`docs/email_domain.md` has the steps in full. In short:

1. You need a domain whose DNS you control. `erw-flame.vercel.app` will not do.
2. In Resend: Domains, "Add Domain", a subdomain such as `mail.<your domain>`, a US region.
3. Paste the DNS records Resend shows (SPF, DKIM, an MX for bounces) at your DNS host. Do not proxy them.
4. Wait for "Verified": usually within 15 minutes, up to 72 hours.
5. Set the GitHub secret `DIGEST_FROM` to `ERW Energy Digest <digest@mail.<your domain>>`, and the same line in `.env` on each machine.
6. Test with `python scripts/alert.py send ...`, which goes to you only. Then subscribe a second address of your own on `/subscribe`.

Checked today: Resend lists no domain for the account, and all 53 emails it holds were sent from `onboarding@resend.dev`. Steps 2 to 4 are Resend's own guide, read today and quoted in the document.

## Tests and checks

- `tests/test_session119.py`, 43 tests. Real rows of four public tables are kept in `tests/fixtures/session119/` (1,130 rows, every column, unaltered):
  - **the workflows:** every workflow file reads as YAML; the send step no longer pulls over a dirty tree and commits through the script, under `health.py`; the ledger's coverage row is rebuilt before its load and each of its four steps is recorded; a scheduled start asks the guard before writing; the watch list's tables are restored, and a failed restore does not stop the Roundup;
  - **the sent check:** the guard's row as it stood on 5 October is a skip (exit 75) with its reason; no row is a go; a start at 01:23 UTC on Monday still asks about Sunday; the check claims nothing;
  - **the commit script, in real repositories made for the test:** it commits only the paths named with a changed tracked file and an untracked log in the tree, and puts both back; it pulls when main has moved under it; nothing under the paths is nothing to commit; it never forces;
  - **the chooser on real rows:** WTI in the week of 21 September 2026 (93.57, down 9.97 from 103.54; 7 of the 104 moves before it as large), to the sentence; an ordinary month of battery additions scores 27.8, where the first version's z was 9.32; a monthly figure is set beside the same month a year earlier; no period to compare with is no change; "largest", "unchanged" and "1 was" read right; no statistic is named to the reader;
  - **the pick, with measures made for the test:** a count of what the ERW collected is never chosen, however large its move; the larger move against its own past wins over the larger number; a month already shown is not this week's news; with nothing new, or too little past, the chart says which fallback it used;
  - **the watch list on real rows:** a week with three of its five days is left out, never estimated; the week and month under way are not shown; a month counts only when every day is held (the awards table: January to July 2026); EIA's "not itemized" counts as zero where named optional; a line is a template to the engine; every line reads a public table; no line reads a table behind a held fix; the registry accounts for every public table;
  - **the failure alert, on yesterday's real rows:** one line within 300 characters; a run with no failed step sends nothing; nine failures still fit; a database that does not answer cannot fail the job; the step is last in both workflows, `if: always()`, `continue-on-error`;
  - **what sessions 77 and 113 mended** is held in place; MISO is still paused; no em dash.
- **Every session's tests on this machine: 1,101 ran, 19 skipped, 1 error, mine.** My test imported `build_coverage` by name; another test had put `warehouse/validate` first on the path, where a shim of that name runs the builder. It stopped on its arguments and wrote nothing (I checked: the working tree was clean). The test now loads the builder by its path. Rerun with that other test first: passes.
- The route check and the site build: below.

## Deploy and snapshots

One push, to `task/119-news-products` at 09:13 UTC. `python scripts/freeze.py status` before it: exit 0, no freeze. Run 37288670943 passed (tests, site build, route check, the no-request check) and merged as `6354b9b` at 09:20; production served the new pages by 09:21. Two snapshots of the 25 live pages: `before-119` (09:08 UTC) and `after-119` (09:21, after the deploy). No table was loaded in this session.

`before-119` against `after-119`: **34 differences.**

| Page | Differences | What | Expected |
|---|---|---|---|
| `/` | 28 | the latest real-time prices of five hubs: 10 numbers (5 keys gone, 5 new) and 18 lines of text, each a price or its interval line | yes: the 15-minute refresh. Not this session's |
| `/network` | 6 | "refreshed 08:05 UTC" became "09:05 UTC"; demand's newest hour 06:00 became 07:00 (two lines); the source line's build stamp | yes: the hourly refresh. Not this session's |
| `/cost-of-power/battery` and its 12 variants | 0 | | |
| `/about`, `/storage`, the three seller pages, `/terms`, the four methods pages | 0 | | |

No difference was unexpected. The home page's five digest headlines did not move: they come from `docs/digest/latest.md`, which this session did not touch (it restored the Roundup's `latest.md`, a different file). They will move today when the 14:00 UTC run writes Monday's digest, as on any weekday.

On production after the deploy (`site/scripts/check-review-pages.mjs`, 09:21 UTC), in the internal view: `/analysis`, `/analysis/2026-W40`, `/roundup`, `/digest` and the method note answer 200 with figures; a visitor gets the in-review page for all five.

This machine's build of the site: exit 0. The route check on it: exit 0, 114 of 114 pages in the internal view, 16 live pages and 98 in review as a visitor.

## Errors and decisions

1. **I did not send the Roundup again.** The prompt asked for it to be sent to the owner's address, believing it had not gone out, and said the guard stays on. It had gone out, to that address, and the guard refuses a second. Sending it would have meant taking the guard off.
2. **I restored five files to an earlier commit:** the Roundup of W40, `latest.md`, the week's chart record and results, and the social caption, as they were when the email went out. The rule is not to overwrite; here an unattended second run had overwritten the record of what was sent. The second run's text is in git at `cce5278`.
3. **The watch list is curated, not a scan.** A scan of every series in every public table would have chosen a data fault within a week: session 118 found a day of interchange of 429,515,551 MWh. A line is a person's (here a session's) statement that a measure means something.
4. **Two more chart templates now use session 118's rule:** the forecast error and the evening peak read hourly demand, and New York's hours of zero were in it.
5. **The share of California's potential curtailed is not on the list.** The monthly table holds no California generation after December 2025 (EIA's series changed), so the line would have stood at 2025-12 for good.
6. **`build_coverage.py` now exits with its own code.** It called `main()` without passing the result to the shell. Its normal path returns nothing, as before.
7. **I added a step to the daily workflow on the day of a review.** One step, last, `if: always()`, `continue-on-error`, and the command itself never raises. The file parses and a test holds that. The 14:00 UTC run is its first.
8. **Model spend: USD 0.0073,** one note draft in a trial, against a cap of USD 3. No pull. MISO was not requested. No force push. The data lock was not taken: no warehouse table was written.
9. **I began this session's reading while session 118's checks ran on GitHub** (about eight minutes), and its branch before 118's report was pushed. Nothing of 119 reached main until 118 was merged.

## To finish

Nothing is owed for what this session changed. What is next is on a clock or is yours.

- **Today, 14:00 UTC:** the daily run is the first to carry the new last step (`health.py alert`). After it I read the run: whether the digest of 5 October was written and delivered, and whether the new step ran and stayed quiet or said what failed. The result is in session 120's report or the next one written after 14:00.
- **Sunday 11 October, 23:00 UTC:** the first Roundup with the new steps and the new chooser. To look for in its log: "Was this week's Roundup already sent" as "roundup: not sent yet"; the watch list's tables restored; `chart_of_the_week.json` with a `finding`; "commit_paths: \"Energy Roundup email rendered\" is on main"; four `ledger:` steps in `erw_health`.
- **The ledger rows not yet in the Redivis draft** (three of the two Roundup runs, in the archive; one of this session's trial, USD 0.0073, in `runs/session119/analysis_trial/_out/api_cost_ledger.csv`): session 121 keeps the ledger and carries them.

To see what the chooser would pick on any day, without publishing:

```bash
python runs/session119/trial_chooser.py --fresh            # this machine's tables; writes under runs/session119/analysis_trial/ only
python warehouse/analysis/run.py --tables-only             # rewrites docs/analysis/tables.json alone
python warehouse/health.py alert --day 2026-10-04 --dry-run   # the line a day's failures would have sent
```

## For Samuel

1. **Verify a sending domain** (`docs/email_domain.md`). It is the one thing between the news products and a reader.
2. **Whether the chart of the week needs a notion of weight** (WTI against a regulation price, tied on rank).
3. **A daily run that crosses midnight takes the next day's turn** (1 to 2 October). The gate counts a commit named for today. A fix is to count only a commit made today after the scheduled hour; it is the daily run's gate, so I left it for a day that is not a review day.
4. **The W39 Roundup of 27 September was never emailed.** It is on the site. Say if you want it sent to you; the guard has no row for it.
5. **The digest repeats one event from two outlets** when their headlines differ (2 October, items 1 and 2).
6. **The 9 public tables no line reads yet** are listed above.

## Verdict

**The Roundup and the digest: ready to open to readers the day a sending domain is verified, not before.** The pipeline writes, guards and sends; Sunday's failure was after the send, and the three places it could recur are closed and tested. What is left, exactly:
- the domain (yours);
- one clean scheduled Roundup on Sunday 11 October with the new steps, which nothing but a real run can show;
- your judgment of the rankings above.

**The chart of the week: ready for its next Sunday.** The rule is stated, tested on real rows and tried on last week. What is left: your ruling on weight (2), and nine tables.

**`/analysis`, `/roundup`, `/digest`: stay in review.** They show what the news products wrote; they open with them.

Energy Research Warehouse (ERW), session 119, on the old laptop (`samueloldlaptop`, data role), 2026-10-05 from about 08:30 UTC to about 09:25 UTC, unattended.
