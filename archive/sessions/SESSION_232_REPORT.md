# Session 232 report: the daily chart in the Digest

13 October 2026, 04:20 to 04:55 UTC (the night of 12 October, Pacific), unattended, on lab-desktop (the data machine), the second session of the chain of 12 October, night. Branch `task/231-232-pipeline-daily-chart`, with session 231. Model spend USD 0: no model call, and none in what was built. Writes: one internal table created in Supabase under the data lock (migration 030) and one row in it; no warehouse table.

## Read these first

- **From today every weekday Digest carries one chart, chosen and drawn by code, with no model and no approval.** The section is "ERW's Chart of the Day", after "ERW's Numbers Today" and before the fun fact: the picture, the one-line fact, the table and the series it reads, a link to the table, and one sentence saying it was chosen by rule. The first Digest to carry it is today's (13 October, about 15:00 UTC), if this lands before the daily run.
- **The rule.** The day's strongest scanner flag (records and first negative prices first, then by how far past its threshold); never a chart a Digest has already shown; if the scanner has nothing new, the watch list's largest change of the latest period, in the same form; if neither, no section and the reason in the log.
- **Proved on today and the last five weekdays:** six pictures and their records in `docs/digest/charts/` (table below). All six are marked as proofs and are not counted as shown, so today's real Digest starts with the strongest flag.
- **The email's picture is fetched from GitHub, as the Roundup's chart is,** so it shows once the daily run has pushed its commit, a minute or two after the email is sent. A reader who opens the email in that minute sees the text and a missing picture. Two ways to close the gap are under "For Samuel's ruling"; I chose neither at night because one changes the daily run's git steps and the other needs a test send.
- **The first chart will be Wyoming's natural gas generation in July 2026, 1,028,747 MWh against a record of 765,381.** It is what EIA's table says, and it is a 34 percent jump over the old record. With no approval step, a publisher's error would be printed as a record. The ruling is yours; I only say what the first one is.
- **The launch ruling is written** in `docs/roadmap.md` (Status and Rulings) and at the top of `docs/state/launch_2026-10-20.md`. The ruling says "Monday 21 October"; 21 October 2026 is a Wednesday (Monday is the 19th). I wrote the date, 21 October, and the question is under "For Samuel's ruling".

## What was built

- **The candidates, on the data machine.** After every daily scan (the worker's and `run_data_machine.sh`'s) the day's flags are ranked, each with the finding card the scanner computes for it, then the watch list's changes of the latest period, each as a card of the same form. They are kept in `runs/scanner/<date>/daily_chart.json` and written as one row to the internal table `daily_chart_candidates` (migration 030: row-level security on, no policy, no page reads it). A scan is never failed by this step.
- **The choice and the picture, on the runner.** `brief.py` asks for the day's row, waits up to seven minutes for it (the worker takes the runner's request within a minute and scans for about two), uses the day before's when today's is not there, and with no row at all tries the watch list on the runner's own tables. It draws the chosen card to `docs/digest/charts/<date>.png` (1200 by 880 pixels, the house style, drawn by matplotlib) and keeps what it chose in `<date>.json`, which is also the memory of what has been shown.
- **The fact** is written by code from the flag's own numbers. A series is named in plain words where its codes are known (states, EIA's fuels and sectors, CAISO's reserve products); any other keeps the table's own name. The exact table and series key are printed under it.
- **The site** shows the same file on the Digest's page (`/digest-charts/<date>.png`, copied at build). **The email** shows it inline at 600 pixels.
- **Only public-licensed tables:** not a table whose license is not public, not one marked "license needed", and not NYISO's or SPP's (your ruling of 12 October holds them).

## The six proofs

Scans as of each past day over today's tables, chosen in date order with the rule's memory running across the five past days; today's from the row the data machine published at 04:38 UTC, read back as `brief.py` reads it.

| Day | Flags that day | Chosen | The fact |
|---|---|---|---|
| 6 October | 19 | rank 1, record | Net generation from natural gas in Wyoming: 1,028,747 MWh in July 2026, the highest monthly value held since January 2001. The record until now was 765,381 MWh, in July 2024. |
| 7 October | 20 | rank 2, record | iso:pjm battery_operating_mw_net_added_12m: 223.0 MW in July 2026, the highest monthly value held since January 2016. The record until now was 110.0 MW, in February 2016. |
| 8 October | 22 | rank 3, record | Retail electricity price in the District of Columbia, industrial: USD 321.5 per MWh in July 2026, the highest monthly value held since January 2001. The record until now was USD 272.6 per MWh, in June 2006. |
| 9 October | 15 | rank 3, record | Retail electricity sales in Utah, residential: 1,658,263 MWh in July 2026, the highest monthly value held since January 2001. The record until now was 1,484,757 MWh, in July 2024. |
| 12 October | 15 | rank 4, record | Retail electricity price in Iowa, industrial: USD 99.90 per MWh in July 2026, the highest monthly value held since January 2001. The record until now was USD 91.70 per MWh, in July 2022. |
| 13 October (today) | 15 | rank 1, record | the same as 6 October: the proofs are not counted as shown, so today's Digest starts at the top |

- The watch list's fallback was drawn too (`runs/session232/watch_fallback/`, not in git): CAISO Regulation Up, 12.84 USD/MW in the week of 5 to 11 October, up 7.8 from 5.04, the largest week-to-week move of the last 105.
- A whole Digest was written by `brief.py` itself (`--no-model --out`, 273 stories) with the section in it, and rendered as the email: `runs/session232/digest_check/2026-10-13.md`, `runs/session232/email_check.html`. Neither is in git and no email was sent.

## Checks

| What | Exit | Notes |
|---|---|---|
| `python -m unittest tests.test_session232` | 0 | 29 tests |
| `python -m unittest discover -s tests` | 1 | 3,616 tests, 3 failures, none in what this chain touched: `test_session51` (a site snapshot against this machine's table, ERCOT September), `test_session125` (the contracts' row order), `test_session165` (a table's hash). Each compares a table on this machine with a committed file and is skipped on GitHub's runner, where the tables are not |
| `apply.py --only 030`, under `lock.py run` | 0 | applied 04:25 UTC |
| `verify_rls.py --catalog` | 0 | PASS, 0 mismatches; `daily_chart_candidates` blocked for the public key |
| `findings_scanner.py --daily` with the new step | 0 | 15 flags and 12 watch changes published for 13 October |
| `brief.py --no-model --date 2026-10-13 --out ...` | 0 | the section is in the check copy; `docs/digest/` untouched |
| `npm run build` (site) | 0 | |
| `node scripts/test-digest-chart.mjs`, `test-markdown-safe.mjs` | 0, 0 | the picture's address on the page; raw HTML still shown as text |
| `python scripts/freeze.py status` | 0 | no freeze |

## Decisions made without you

1. **A chart is never shown twice.** The rule you gave would print Wyoming's record every weekday for four months (a monthly record stays fresh to the scanner for 130 days). The Digest takes the strongest flag it has not shown.
2. **"Largest change" on the watch list** is the share of the measure's own earlier changes that the newest one exceeds, the same score the chart of the week uses, so a barrel and a megawatt can be ranked together.
3. **NYISO and SPP are held out** of the daily chart, on your ruling of 12 October about their tables; one line in `daily_chart.py` lifts it.
4. **The candidates cross between the machines in a new internal table** (migration 030, applied tonight under the data lock, with its rollback). The alternative, a field of the scan's queue row, would have changed what `/analysis` lists.
5. **The method is a section of the scanner's method document,** not a new page.
6. **The six proofs are in `docs/digest/charts/` as you asked, marked `"proof": true`,** and do not count as shown. The Digests of 7 to 12 October, already published, were not rewritten.
7. **The picture names its source and holds the card's three callouts,** not the long footnote; the footnote's content is in the method document.
8. **Session 231's report and this one share a landing.**

## For Samuel's ruling

1. **21 October 2026 is a Wednesday.** Did you mean Monday 19 October, or Wednesday 21 October? The documents say 21 October.
2. **The license rule's own date** (tables marked "license needed" from 20 October 2026, session 207) was not moved with the launch. Should it move to the public day?
3. **The email's picture in the first minute.** Either (a) the daily run commits `docs/digest/charts/` before it sends the email, as the Roundup's workflow does for its chart (a change to the daily run's git steps), or (b) the picture travels inside the email as an attachment shown inline (a change to the sender that needs one test send). Or leave it as it is.
4. **No approval means a publisher's error can be printed as a record.** If you want a guard, the simplest is a size limit: a record more than, say, 25 percent past the old one waits a day. Today's first chart would be held by that rule.
5. **Plain names.** Series outside the list keep their table names in the fact ("iso:pjm battery_operating_mw_net_added_12m"). A names file would fix that; it needs a person to write the names.

## Files

- New: `warehouse/analysis/findings/daily_chart.py`, `warehouse/analysis/findings/card_image.py`, `warehouse/supabase/migrations/030_daily_chart.sql`, `warehouse/supabase/rollbacks/030_daily_chart.sql`, `site/scripts/test-digest-chart.mjs`, `tests/test_session232.py`, `tests/fixtures/session232/candidates.json`, `docs/digest/charts/` (six pictures, six records).
- Changed: `warehouse/analysis/findings/findings_scanner.py` (the candidates after a scan), `warehouse/news/brief.py` (the section), `warehouse/news/email_digest.py` (the section in the email), `site/lib/markdown.ts` and `site/scripts/build-content.mjs` (the picture on the Digest's page), `site/.gitignore`, `warehouse/supabase/verify_rls.py`, `warehouse/supabase/README.md`, `docs/methods/automated_analysis_scanner.md`, `docs/roadmap.md`, `docs/state/launch_2026-10-20.md`.
- On this machine, not in git: `runs/session232/` (the backfill, the proofs' outputs, the check Digest and email).

## The landing

- Shared with session 231. The before snapshot, the push, the check run, the after snapshot and the comparison are in session 233's report. Expected: 0 differences on the 25 pages (the Digest's pages are in review; the three live pages read none of what changed).
