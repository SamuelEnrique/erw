# The Energy Digest and the Sunday Roundup: the published issues audited as a hostile editor would

Session 10235, 26 November 2026, chain 710 part D, on the old laptop. Read as an editor at an energy publication who has to stand behind every number of the ten newest Digests (9 October to 12 November 2026) and the three newest Roundups (W43, W44, W45) and wants to find them wrong. Platform tools 1 (the Energy Digest), 14 (the Roundup) and 25 (the fun fact and the chart of the day inside them), `docs/platform-tools.md`. The findings file of 5 November (`docs/reviews/periodicals-faults-2026-11-05.md`, 190 rows) is not repeated: a fault it already holds is cited by its row.

- Nothing changed on main but this file and its evidence folder. No issue's words changed (the owner's rule: no change to what the Digest or Roundup say), no table written, no lock taken, no default moved, no model called (spend USD 0, `ERW_SPEND_CAP_USD=0` on every run), no script under `warehouse/news/` that writes or calls a model run, no request to any live service, no web read.
- Each finding has its own branch `wip/audit-digest-<n>` from origin/main. Branches 1 and 2 change page code only and are returned for landing. Branches 3 to 7 hold a test that shows the finding, not for landing; the fix is Samuel's ruling.
- Evidence: `docs/reviews/digest-model-audit-2026-11-26/`: the scripts `r1` to `r5` and their outputs, the drawing script and its stand-ins, the drawn words of the pages on main and on branches 1 and 2, each test run. All run on this machine from the main checkout's tables, read and never written.

## In short

- **The tables' numbers are right.** 152 warehouse figures of the ten Digests and 98 of the three Roundups were re-done by code that imports nothing of the ERW. Every figure this copy can re-do equals the issue to the digit as of its writing: 4 differ only by a publisher's revision after the issue (EIA's WTI of 14 October and US48 demand of 11 November, both already noted on the page), and the rest that differ are NYISO and ISO-NE rows this copy does not hold (data request below). Every fuel close, hub mean, change, percent, chart value re-done from its table and warehouse fun fact is right; the one chart record that is not (12 November's "record until now") is row 87, fixed in the scanner since.
- **Three model-written figures stand in no story, and one is wrong by ten times (finding 4).** The line under a story is the scorer's own sentence, printed with no number check against the story: "adds ~2% to nuclear fleet" under PSEG's 200 MW Salem uprate (6 November; 200 MW of a fleet near 97,000 MW is about 0.2 percent), "USD 25 billion AI spending commitment" under Meta's credit gauge (23 October), "an October 20 decision" on a FERC notice (20 October); and on 12 November the line made Heatmap's "could add ... a third" of gas capacity into "will require ... one-third" of all generation capacity. The headline check also counts that line as a source. For ruling.
- **The literal-number check stops a number that is in no source, and reads nothing else (finding 3).** Tested on crafted text: it passes "USD 74 million" against "$74 billion", "580 MW" against "580 homes", a day or month of a date as a figure, a list marker, the opposite direction and a number in words. On these thirteen issues no printed number is wrong through these holes; they are open doors. For ruling.
- **The Roundup's index page drew a licence-held grid's prices (finding 1, fixed).** `/roundup` drew W45 with `render`, not `renderRoundup`, so NYISO's 40.90 and ISO-NE's 40.28, held on `/roundup/2026-W45` since rows 94 and 108, stood on the index. Branch 1 draws it as the week page does; drawn and read.
- **The news index hold stops at the Digest's story sections (finding 6).** While news_index is held whole, the Digest's opening number (Bloomberg's USD 74 billion on 12 November) and its two story rows are drawn, and no story of any Roundup page is held: eight items and six Google News links on W45. For ruling.
- **Two dates moved to another outlet (finding 7).** "As Bloomberg.com reported on 2026-11-11" and "JPT Homepage, 2026-11-11": both stories are of 12 November; the 11th is Hart Energy's earlier story that the scorer joined to each cluster. For ruling.
- **"Highest real-time price, yesterday" never says which grids had no row (finding 5)** (9, 13, 20 and 23 October; on 9 October SPP's 1,027.12 came the next day). For ruling. And the weekend pages promised the Roundups of W46 and W47 as "not written yet" days after their Sundays (finding 2, fixed in words).
- **Issues found wrong, their files untouched:** 12 November (four faults, rows 79, 80, 82 and 87, and finding 7), 6 November (held grids' prices printed two weeks into the hold, by an old writer; finding 4), 21, 22 and 23 October (held grids' prices; finding 4 on the 23rd), 20 October (finding 4), 14 October (the colliery fun fact, already noted on its page), and W43, W44 and W45 (held grids, rows 69, 93 and 108). Listed below with the reason.

## The ground: each file and what it does

| File | What it does |
|---|---|
| `docs/digest/<date>.md` (ten issues, 2026-10-09 to 2026-11-12) | The issues as published; the email and the page are made from them. Read, never written |
| `docs/roundup/2026-W43.md`, `-W44.md`, `-W45.md` | The three newest Roundups as published |
| `docs/digest/charts/<date>.json` | Each day's chart record: the fact, the scanner's flag, the figures, the plotted points |
| `warehouse/news/facts/items/<date>.json`, `facts/raw/` | Each fun fact with its sources, each part's quoted span and the stored raw text it was quoted from |
| `warehouse/news/brief.py` (read only) | Writes the Digest: the numbers (`numbers_today`, `dam_mean`, `day_move`, `demand_lines`), the opening number (`opening_number`, `opening_lines`), the block (`numbers_block`, `story_row`), the headlines (`headlines`, model, checked), the why line (`why_line`, `why_check`, no model of its own: it prints the scorer's line) |
| `warehouse/news/roundup.py` (read only) | Writes the Roundup: the weekly means, the fuel table, the week's highest real-time price, US48's peak, the five numbers |
| `warehouse/news/score.py` (read only) | The scorer (a model): significance, sector, MW, price, parties, a headline and the why line, per the rubric `warehouse/news/rubric.md` |
| `warehouse/chat/ask.py` `numbers`, `unverified` | The literal-number check: every number of a model's sentence must stand in a source at the same or a coarser precision (finding 3) |
| `warehouse/news/funfact.py` (read only) | The fun fact: a fact quoted from a stored source, checked by the same literal check and against its span |
| `site/app/digest/page.tsx`, `site/app/digest/[date]/page.tsx` | `/digest` (today's issue or one line saying none) and `/digest/<date>` (an issue, a weekend day, a missed weekday) |
| `site/app/roundup/page.tsx`, `site/app/roundup/[week]/page.tsx` | `/roundup` (the newest Roundup and the archive) and `/roundup/<week>` |
| `site/lib/digest.ts` | The Digest's figures with their keys (`digestFigures`, `digestMarkdown`), the licence hold on a Digest (held tables' figures, the summary, the story sections while news_index is held) and on a Roundup (`holdRoundupGrids`: a held grid's cells, real-time line and summary), the archive's days |
| `site/lib/digestLive.ts` | The revision notes: an EIA close or US48 peak the warehouse now holds at another value |
| `site/lib/markdown.ts` `renderDigest`, `renderRoundup`, `render` | How a stored issue becomes the page |
| `site/data/license_status.json`, `site/lib/license.ts` | The holds: news_index "license needed", whole, from 21 October 2026; NYISO, ISO-NE and MISO tables held by grid |

## How the numbers were re-done

- **The tables' figures** (`r1_tables.py`, `r1b_rt_when.py`, `r3_roundup.py`): each hub's mean of the 24 hours of its local operating day (or the 168 or 169 of its local week), half-up to the cent as the writer rounds; the day or week before, the change and the percent; each fuel close on its printed day, the close before it and the move; the highest real-time interval of the day or week over the grids read, with each row's retrieval time, so a row the issue could not have seen is told from one it missed; US48's peak hour of the UTC day or of the week and the hours held.
- **The story numbers** (`r2_stories.py`): every number of every story item, matched by its link to `warehouse/output/news_stories.csv` (or `policy_actions.csv`), read with its unit and scale and looked for in the stored title and summary (the story's text as the feed gave it), then in the scorer's fields (a model's words), then nowhere; each date beside an outlet against the stored dates. The ones not found in the story text were read by hand with the stored rows (`r2b_show*.out`).
- **The charts** (`r5_charts.py`): each printed figure against its record, the record against its own plotted points, and, where this copy holds the table, against the table. **The fun facts** (`r4_funfacts.py`, `r4b_warehouse_facts.py`): each quoted span looked for word for word in its stored raw source; the two warehouse facts re-done.
- **The pages** (`draw.mjs` with `register.mjs` and `stubs.mjs`): drawn to HTML with the site's own code through react-dom/server, no build, no server, no browser; every network read refused and listed (the revision notes' reads: refused, the page shows no note, as when a read fails).
- **The limit.** The main checkout's NYISO and ISO-NE tables end on 9 October 2026; three chart tables are not on this machine. Both are data requests; the audit goes on without them.

| Set | Figures | Re-done here | Equal | The rest |
|---|---:|---:|---:|---|
| Digests, warehouse tables (10 issues) | 152 | 126 | 122 | 4 revised by EIA after the issue (noted on the page); 26 rest on NYISO and ISO-NE rows not in this copy |
| Roundups, warehouse tables (3 issues) | 98 | 78 | 77 (67 to the digit; 10 equal in substance: 3 weeks complete since, 3 a format, 4 the copy grew, EIA moved W44's peak by 7 MW, or a retrieval time was overwritten) | 20 rest on NYISO and ISO-NE rows not in this copy or are held grids' real-time lines; 1 is row 69 |
| Story numbers (13 issues, 349 items) | 361 | 361 | 341 in the stored story text (13 of them in another written form, "50-MW", "580 megawatts", "62.89%" for "over 62%", read by hand) | 3 in no story text, only in the scorer's why line (finding 4); 17 are the Roundup's own counts of stories |
| Charts of the day (8 printed) | 16 | 10 from their tables | 8 | 12 November's "record until now" is false (row 87); 13 October's 1,028,747 MWh is revised to 1,034,451 since, unsaid; 3 charts (6 figures) rest on their records alone |
| Fun facts (10 printed) | every number | every number | all | every quoted span stands word for word in its stored source; the two warehouse facts re-done equal |

## Findings, most urgent first

| # | Finding | Severity | Measured | Branch | Fix |
|---|---|---|---|---|---|
| 4 | The why line is printed with no number check against its story, and lends its numbers to the headline check | high | 3 figures in no story text in 10 issues; PSEG's "~2%" is about 0.2% | `wip/audit-digest-4` | for ruling |
| 1 | `/roundup` drew the newest Roundup without the licence hold its week page applies | high | W45's NYISO 40.90 and ISO-NE 40.28 drawn | `wip/audit-digest-1` | page code: landing |
| 6 | The news index hold stops at the Digest's story sections | high | 12 Nov: the opening's Bloomberg figure and 2 story rows drawn; W45: 8 items, 6 Google News links, no word of the hold | `wip/audit-digest-6` | for ruling |
| 3 | The literal-number check reads a number's magnitude alone | medium | 8 crafted passes; 0 printed numbers wrong through them in 13 issues | `wip/audit-digest-3` | for ruling |
| 7 | Beside a story's figure, one outlet named with another outlet's earlier date | medium | 2 in the issue of 12 November | `wip/audit-digest-7` | for ruling |
| 5 | "Highest real-time price, yesterday" names no grid whose table held no row of the day | medium | 4 of the 9 issues with the line | `wip/audit-digest-5` | for ruling |
| 2 | A weekend day promised a Roundup "not written yet" days after its Sunday | low | W46 and W47 on 26 November | `wip/audit-digest-2` | words: landing |

### 4. The why line is printed with no number check against its story

- `brief.why_line` prints the scorer's `why` after its rules (no hype word, one sentence, no figure the headline gives); `why_check` has no rule that reads a number against the story's title or summary, and the scorer's prompt asks for "one fact the story gives", a prompt and not a check. `brief.headlines` checks each headline against `[*titles, summary, why, *figures(r)]`, the why line and the figures drawn from it among the sources, so a number the scorer wrote verifies a headline.
- In the ten Digests, by the stored rows: 6 November, By sector, "Capacity addition at dual-unit facility adds ~2% to nuclear fleet." under "PSEG executives say Salem nuclear plant expects a 200 MW uprate" (the story gives no share; 200 MW against a US fleet near 97,000 MW is about 0.2 percent, so the printed share is ten times too large); 23 October, By sector, "USD 25 billion AI spending commitment raises default risk" under Meta's credit gauge (title and summary give no sum); 20 October, Policy, a FERC notice "Five storage projects face an October 20 decision" (no date in the title, no summary stored).
- The same line restates its story's claims unchecked: 12 November, "Electricity demand from data centers will require enough new gas plants to expand generation capacity by one-third", where Heatmap's stored text says "could add enough natural gas power plants to expand America's gas power generation capacity by a third".
- `tests/test_audit_digest_4.py`, 3 passed on main: today's `why_line` still prints the PSEG line as the issue did, the literal check run against the story stops each figure, a headline carrying the why line's USD 25 billion passes the headline check.
- For Samuel's ruling: check every number of a why line against the cluster's titles and summaries (a line that fails is dropped, as `why_line` already drops one), and leave the why line out of the headline check's sources. Measured: 3 lines of the ten issues would not have printed. Default: left as it is.

### 1. The Roundup's index drew a held grid's prices (fixed, page code)

- `site/app/roundup/page.tsx` drew `DOCS.weeklies[newest]` with `render`; `/roundup/<week>` draws with `renderRoundup`, which holds a held grid's cells, its real-time line and a summary naming it (`holdRoundupGrids`, rows 94 and 108), adds the source trail and the fold. Drawn on main: `/roundup` printed "40.90" and "40.28" (W45's week-before means of NYISO and ISO-NE), `/roundup/2026-W45` did not.
- Fix (`wip/audit-digest-1`): the index draws with `renderRoundup`. No figure's value changes; the owner's standing hold reaches one more page. Drawn and read: the index's article is word for word the week page's, "license needed" in both cells, the source trail and the fold present. `tests/test_audit_digest_1.py`: fails on main, 3 passed on the branch.

### 6. The news index hold stops at the Digest's story sections

- `licenseNeeded("news_index")` is true from 21 October 2026, "hold": "whole". `digestMarkdown` holds the sections in `STORY_SECTIONS`; the opening number and the numbers block are not among them, and `holdRoundupGrids` holds grids, not stories.
- Drawn on 26 November through the site's library: the Digest of 12 November holds 4 story sections and draws "USD 74 billion: SpaceX plans USD 74 billion ..., as Bloomberg.com reported" and its two story rows (pv magazine USA's 580 MW, JPT's USD 2.1 billion), each a story of the same index. The Roundup of W45 draws 8 story items and 6 Google News links and says nothing of the hold.
- `tests/test_audit_digest_6.py` (with `site/scripts/test-audit-digest-6.mjs`), passes on main. For Samuel's ruling: hold the opening's story figure and the block's story rows while news_index is held, and the Roundup's story sections (What mattered, Weekend, The five stories) as the Digest's are. It changes what visitors see of the issues; item 2 of his rulings set the Digest's hold. Default: left as it is.

### 3. The literal-number check reads a number's magnitude alone

- `ask.unverified` takes every number of the sources into one pool and passes a number of the sentence when any number of the pool has its magnitude at its precision. It stops a number in no source, and one written finer than its source (both tested).
- On crafted text it passes: "USD 74 million" against "$74 billion" (scale); "580 MW" against "580 homes" (unit); "26 percent" against "Published 2026-11-26" and "11 GW" against "2026-11-04" (a date's day or month); "Oil rose 2 percent" under a list marked "2." (the marker rule passes any number equal to a marker, wherever it stands); "fell 5.0%" against "rose 5.0%" (direction); "by one-third" (a number in words); "USD 3 higher" against another source's "3 tankers" (the pool is shared).
- `tests/test_audit_digest_3.py`, 10 passed on main. On the thirteen issues the independent unit-aware trace found no printed number wrong through these holes. For Samuel's ruling: make the check read the unit and the scale after a number, leave dates and list markers out of the pool, and keep each source's numbers with their source. It changes what the check passes. Default: left as it is.

### 7. One outlet named with another outlet's date

- `opening_lines` and `story_row` print the outlet of the cluster's first link and `r["first"]`, the earliest story of the cluster. When the scorer has joined an earlier story of another outlet to the cluster, the named outlet is given that story's day.
- The Digest of 12 November: "as Bloomberg.com reported on 2026-11-11" (Bloomberg's story: 2026-11-12 17:28 UTC; the 11th is Hart Energy's "SpaceX Plans $24B Texas Power Project", another figure); "Deal value: USD 2.1 billion (Strathcona, Greenfire; JPT Homepage, 2026-11-11)" (JPT's story: 2026-11-12 18:01 UTC; the 11th is Hart Energy's "$2B" story).
- `tests/test_audit_digest_7.py`, 2 passed on main (both clusters rebuilt from the stored rows with `build_clusters`, the lines written with the brief's own functions). For Samuel's ruling: print the named outlet's own story date. Measured: 2 dates in the issue of 12 November. Default: left as it is.

### 5. The highest real-time price names no grid that had no row

- `numbers_today` takes the highest interval among the rows held when the issue is written; the line adds "Not read:" for the held grids only. By the retrieval times of the main checkout's rows: 9 October, N.Y.C. (NYISO) 726.09 printed while no ERCOT or SPP row of 8 October was held at 15:34 UTC (SPP's 1,027.12 at SPPNORTH_HUB came on 10 October); 13 October, no SPP row; 20 October, written at 06:55 UTC, no SPP and no CAISO row; 23 October, no ERCOT row (retrieved 25 October). 6 November said the true case ("no real-time table covers yesterday").
- `tests/test_audit_digest_5.py`, 2 passed on main: the stored lines, and `numbers_today` on stand-in tables (three grids read, two empty, neither named). For Samuel's ruling: name the grids whose table holds no row of the day. Measured: 4 of 9 issues with the line. Default: left as it is.

### 2. A weekend day promised a Roundup never written (fixed in words)

- `/digest/<Saturday or Sunday>` said the day's stories "open ERW's Roundup for <week>, written and sent on Sunday at 23:00 UTC (not written yet ...)" whatever the date. On 26 November, `/digest/2026-11-14` and `/digest/2026-11-21` promised W46 and W47, whose Sundays had passed with no Roundup.
- Fix (`wip/audit-digest-2`): `roundupDue(week)` in `site/lib/digest.ts` (the week's Sunday 23:00 UTC passed); a due week with no Roundup reads "No Roundup was written for 2026-W47, the week that holds this day (all Roundups)." Drawn and read on both days: pass. `tests/test_audit_digest_2.py` fails on main, passes on the branch; every test importing `lib/digest.ts` run on the branch: 86 passed (sessions 177, 402, 470, 2207, 4010 and this), `tests/test_periodicals.py` 131 passed and 1 skipped, `site/scripts/test-digest-numbers.mjs` 17 passed.

## Each claim set against its source

| The brief's question | Answer |
|---|---|
| A figure from a story stated as the ERW's own | None: every story figure carries "the outlet's figure, not a table's" or sits in a story item; the Roundup's deal line names its table (`energy_deals`, extracted from the story) |
| A number in no source | Three, all the scorer's why line (finding 4) |
| A date that moved | Two outlets given another outlet's date (finding 7); EIA's two revisions after issues (noted on the pages); 13 October's chart figure revised by EIA since, with no note (the revision notes cover the fuel closes and US48 demand only) |
| A held grid's figure | Printed in the issues of 21, 22 and 23 October (NYISO and ISO-NE means; LONGIL's 1,165.64 on the 22nd, 129.51 on the 23rd), of 6 November (NYISO 38.55, ISO-NE 41.55, two weeks into the hold, by a writer older than the hold's rule) and W43, W44 and W45 (rows 93, 94, 108). Held on the pages, except `/roundup` until branch 1 |
| A fun fact with no source | None: every printed part has a source whose quoted span stands word for word in its stored raw text. 14 October's colliery is kept with its note; W45 printed the fun fact of 6 November again |
| A correlation worded as a cause | 12 November, the rest of the top ten 4: the why line "Electricity demand from data centers will require enough new gas plants to expand generation capacity by one-third, raising customer bills." where Heatmap's stored text says the boom "could add enough natural gas power plants to expand America's gas power generation capacity by a third": a possibility made a certainty, a third of gas capacity made a third of all capacity, and the number in words, which the check does not read (findings 3 and 4). 9 October's "tightens supply and lifts prices" is the scorer's reasoning, not the story's. No numbers summary states a cause |
| An outlet whose terms forbid reuse | The outlets are held on the Digest's page as news_index ("ask for permission"); the opening number and every Roundup story are not (finding 6). pv magazine USA's own hover says its page asks for permission, beside its figure drawn in the block |
| The literal-number check: does it stop a number in no source | Yes (tested); and passes the eight forms of finding 3 |

## Issues found wrong (their files untouched)

| Issue | What is wrong | Where it is found |
|---|---|---|
| Digest 2026-11-12 | "No price moved enough to lead" beside SPP's 39.1% fall; Henry Hub "up 0.00 USD/MMBtu (0.0%)" as the market price; "Storage capacity, USA: 580 MW", power dispatched; the chart's "record until now", July 2024's 765,381 MWh, beaten by July 2026's 1,034,451, drawn on the same chart and printed as a record by the Digest of 13 October; "(1 days before this issue)"; Bloomberg and JPT given Hart Energy's date; a why line that makes Heatmap's "could add ... a third of gas power capacity" into "will require ... one-third of generation capacity" | rows 79, 80, 82, 87, 81; findings 7 and 4 |
| Digest 2026-11-06 | NYISO 38.55 and ISO-NE 41.55 printed (held); "adds ~2% to nuclear fleet" (about 0.2%, in no story text) | this audit; finding 4 |
| Digest 2026-10-23 | NYISO and ISO-NE means and LONGIL's 129.51 printed (held); "USD 25 billion" in no story text; ERCOT absent from the real-time maximum, unsaid | rulings item 1; findings 4, 5 |
| Digest 2026-10-22 | NYISO and ISO-NE means and LONGIL's 1,165.64 printed (held) | rulings item 1 |
| Digest 2026-10-21 | NYISO and ISO-NE means printed (held) | rulings item 1 |
| Digest 2026-10-20 | "an October 20 decision" in no stored text; SPP and CAISO absent from the real-time maximum, unsaid | findings 4, 5 |
| Digest 2026-10-14 | The fun fact's second half is a colliery disaster (the page says so) | `ISSUE_NOTES` |
| Digests 2026-10-09 and 2026-10-13 | The real-time maximum without the grids that had no row, unsaid | finding 5 |
| Roundup W45 | NYISO 40.90 and ISO-NE 40.28 printed (held); "US48 peak demand: 502,100 MW" as the week's, from 72 of 168 hours | rows 93, 94, 69 |
| Roundups W44 and W43 | A held grid's real-time maximum (CAPITL 588.05; LONGIL 1,165.64) and, in W43, a summary naming NYISO's price | row 108 |

Right as printed: the Digests of 12 October (no model; no summary, no fun fact) and every fuel close, hub mean, change and US48 peak the copy holds.

## Data requests (for `docs/state/data_requests_five_tools.md`, rows for window A)

- NYISO and ISO-NE: for each of the 16 day-ahead figures the Digests of 12 October to 6 November printed (N.Y.C. and .H.INTERNAL_HUB, operating days 11, 12, 13, 19, 20, 21, 22 October and 5 November), the mean of the 24 hourly `lmp_dam` of the local day from `nyiso_dam_zone_prices` and `isone_dam_zone_prices`, half-up to the cent; the `lmp_rtm_15m_mean` of `nyiso_rtm_zone_prices` at N.Y.C. 2026-10-08 12:00 UTC, LONGIL 2026-10-12 21:30, N.Y.C. 2026-10-19 12:00, LONGIL 2026-10-22 00:00, LONGIL 2026-10-23 01:00 and CAPITL 2026-10-29 21:30; the weekly means of W42 to W45 at both nodes. The copy here ends on 9 October.
- The charts of 22 October, 23 October and 6 November: from `eia861m_utility_sales_monthly` (`eia861m:4911:NE`, `industrial_sales`), `eia_padd_rail_barge_movements_monthly` (`eia_padd_movements:MGAMT1XP31`, `tanker_barge_receipts`) and `onrr_revenue_monthly` (the Red River series), the month's value, the highest (lowest) earlier value and its month, the first month and the count of months. None of the three tables is on this machine.

## Not covered

- No build, no browser, no email read; the pages were drawn with the site's code. `scripts/check_digest.py` and `check-values.mjs` were not run (both read the live set).
- The Roundup's "(n stories)" counts against the clusters' sizes; the deals and datacenter tables of W43 to W45 beyond the deal of the week (their own audit: `docs/reviews/deals-model-audit-2026-11-26.md`). The deal of the week of W45 (USD 938 million) stands in its story; the table names the lending banks as its buyer.
- The chart records of 9 and 12 October exist under `docs/digest/charts/` with no chart in those issues; their facts are the charts of 20 and 21 October.

## The branches

Every branch is from origin/main of 26 November and pushed: `wip/audit-digest-1` `4d7025411` (page code, landing), `-2` `b2b3f0035` (words, landing), `-3` `8d5b26fc4`, `-4` `bbffcaa9e`, `-5` `a58da8aae`, `-6` `ecbe76075`, `-7` `faaabdb96` (each a test, not for landing).
