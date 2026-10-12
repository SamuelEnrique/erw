# Session 205 report: the licensing sweep, on lab-desktop

lab-desktop (data role), 12 October 2026 from 09:49 UTC (02:49 Pacific). Unattended, second and last session of the night's chain. Branch `task/205-licenses`. Model spend USD 0, no model call. 39 reads of the 40 approved, each a publisher's terms page; no data request. No request to a paused publisher. Nothing deleted. No site page, test logic, run time or trigger, scanner or release gate touched. `coverage.csv` not changed.

## Read these first

- **Vercel has failed both deployments of this chain, and the reason is unread.** Both branches passed GitHub's check and are merged on `main` (session 204 as `30dd910b`, this session as `28e880da`). Each time Vercel said "Deployment has failed" within eleven seconds of the merge, too soon to be the site build. The live site is still the deployment of 03:44 UTC (`9687ca26`): 0 page differences at both landings. This machine has no Vercel sign-in. To read the logs: `npx vercel inspect dpl_UMxy7XZv7MQESf1mreTsxcZNzHwD --logs` and `npx vercel inspect dpl_78gwF1oMczCxgD8mPj4vgDFfUM6T --logs`. **Until it is fixed, nothing pushed to `main` reaches the site,** the code machine's landings of tonight and the daily run's files included. See the two landing sections.
- **`docs/licenses.md` holds a verdict for each of the 198 tables.** The flag in `coverage.csv` and the verdict agree on 132, disagree on 44, and 21 are not settled because a publisher was not read. One table is internal by the ERW's own choice.
- **42 tables are flagged public where a publisher's sentence asks for permission.** Three operators decide most of them: NYISO 29, ISO-NE 25, MISO 21 (a table can be under several). The rest are the news tables, the datacenter operators' table and two tables taken through FRED.
- **Most of the 42 are derived tables.** The ERW's own rule gives a derived table the strictest license of its inputs, so one zonal price of NYISO's in a comparison table makes the whole table NYISO's to permit.
- **FRED is new.** Its terms forbid storing FRED content in a database without the Bank's written consent. Two public tables come through FRED. The same series are public domain at EIA and at the Federal Reserve Board.
- **No page read states a price.** PJM's agreement prohibits a non-member from republishing data and names membership; the cost is not on the page. For the letter of intent, prices have to be asked for.

## What to review

- The document: https://github.com/SamuelEnrique/erw/blob/main/docs/licenses.md
  1. "Read these first": the counts.
  2. "The publishers: the sentence and the verdict": 40 rows. Check a sentence against its page if you doubt a verdict.
  3. "Where the flag and the verdict disagree": the 44, none changed.
  4. "Three lists": public now (117 tables), permission needed, paid.
- The ten drafts, none sent:
  - https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/nyiso-permission-email.md
  - https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/spp-permission-email.md
  - https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/pjm-permission-email.md
  - https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/miso-permission-email.md
  - https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/isone-permission-email.md
  - https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/fred-permission-email.md
  - https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/imf-permission-email.md
  - https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/rggi-permission-email.md
  - https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/news-outlets-permission-email.md
  - https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/datacenter-operators-permission-email.md
- The record of every read: https://github.com/SamuelEnrique/erw/blob/main/warehouse/metadata/license_reads.csv
- The sentences and verdicts: https://github.com/SamuelEnrique/erw/blob/main/warehouse/metadata/license_verdicts.csv
- Each table's publishers, and how they were found: https://github.com/SamuelEnrique/erw/blob/main/warehouse/metadata/license_tables.csv
- The two scripts: https://github.com/SamuelEnrique/erw/blob/main/scripts/license_read.py and https://github.com/SamuelEnrique/erw/blob/main/scripts/licenses.py
- The tests, 14: https://github.com/SamuelEnrique/erw/blob/main/tests/test_session205.py

## What was built

- **The reads.** One request a publisher, the ERW's own User-Agent, no second try. The publishers are those `coverage.csv` names in its source column: 40. MISO was not asked (paused): its line is in the record with no request.
- **The sentences.** Each is cut by code from the page as it was saved. None was typed.
- **Two verdicts a publisher:** as the ERW is today (it sells nothing), and if it sells anything. They differ for SPP, the IMF, the Railroad Commission of Texas, Natural Gas Intelligence and Dow Jones.
- **A table's verdict** is the strictest of its publishers'. A derived table takes the publishers of the tables its header names, kept to the grids its own coverage row lists.
- **The drafts.** One file each for NYISO, SPP, PJM, MISO, ISO-NE, FRED, the IMF and RGGI; one for the news outlets and one for the datacenter operators, each to be sent once per name. Each: who you are, what the ERW is, what is asked, what is offered, in short lines. Your surname, role and address stand in brackets.

## The verdicts, by publisher

| Publisher | Today | If the ERW sells anything |
|---|---|---|
| EIA, ERCOT, CAISO, NWS, NOAA NCEI (U.S. stations), CARB (California's page), CFTC, NRC, Census Bureau | may be public | may be public |
| Berkeley Lab | may be public (not read today: HTTP 403; an earlier session's reading, CC BY 4.0) | the same |
| SPP | may be public, with citation | needs written permission |
| IMF | may be public, with attribution | needs written permission |
| Railroad Commission of Texas | may be public, noncommercial | needs written permission |
| NYISO, ISO-NE | needs written permission | the same |
| MISO | needs written permission (not asked: paused; the sentence of 4 October) | the same |
| FRED | needs written permission (to keep its content in a database) | the same |
| RGGI | needs written permission (no terms found on the page read) | the same |
| PJM | needs a paid license (membership; no price on the page) | the same |
| Bloomberg, Data Center Dynamics, Data Center Frontier, Data Center Knowledge, Heatmap News, Latitude Media, POWER Magazine | needs written permission | the same |
| Natural Gas Intelligence, WSJ | needs written permission | needs a paid license (no price on the page) |
| Financial Times, Hart Energy, Reuters | not read; permission by default | the same |
| Amazon Web Services, Google, Meta, Microsoft, Oracle, Vantage Data Centers | needs written permission | the same |
| Digital Realty, Equinix, Switch | not read; permission by default | the same |

- **Forbidden: none.** Every prohibition read names permission, consent or membership as the way.

## The reads against the ceiling

39 requests of 40. All on 12 October 2026, 09:53 to 09:55 UTC. Every address, time, status and byte count is in `warehouse/metadata/license_reads.csv` and in the document's table "The reads"; every sentence taken is in the document's table "The publishers".

| | Count | Which |
|---|---|---|
| Pages read, a sentence taken | 31 | the publishers of the table above not named below |
| Pages read, no sentence on reuse in them | 3 | RGGI (the home page: no terms page exists that a search found); Digital Realty and Switch (the bytes hold no terms: a browser's scripts load them, or the page is a list) |
| Could not be read | 5 | Berkeley Lab 403, Financial Times 404, Hart Energy 404, Reuters 401, Equinix 403 |
| Not asked | 1 | MISO, paused |

- **21 web searches** were made to find the right address before spending a publisher's one read. A search asks a search engine, not a publisher; no sentence in the document comes from a search result.
- No robots file was read: the ceiling is 40 and the approval is one page a publisher.

## Checks, with exit codes

None piped; outputs under `runs/s205/` in the session's worktree on lab-desktop.

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 205"` | 0 | 6 of 6, on duty |
| `scripts/duty.py beat`, before each batch of reads | 0, 0 | |
| `scripts/license_read.py --list ... --ceiling 40 --dry-run` | 0 | 14 lines; MISO "PAUSED: would not" |
| `scripts/license_read.py --list ... --ceiling 40`, twice | 0, 0 | 13 and 26 requests; "requests in the record: 39 of 40" |
| `scripts/licenses.py tables --headers <the tables>` | 0 | 198 tables |
| `scripts/licenses.py check` | 0 | "198 tables, 40 publishers with a verdict, 39 requests in the record; 0 problems" |
| `scripts/licenses.py write` | 0 | `docs/licenses.md`, 198 tables |
| `python -m unittest tests.test_session205` | 0 | 14 tests |
| The whole suite in the session's worktree, 10:04 UTC | 1 | 3,411 tests, 1 failure, 247 skipped: `test_planner`'s clock test, which fails from 05:00 to 13:00 UTC (session 204's report) |
| The whole suite again, after merging `main` with session 204 in it, 13:20 UTC | 0 | 3,445 tests, 247 skipped |
| `scripts/licenses.py check`, after the merge | 0 | the same line, 0 problems |
| `scripts/freeze.py status`, 13:20 UTC | 0 | no freeze |

- **Not verified:** no lawyer has read a verdict. No draft was sent. The addressees of five drafts (NYISO, PJM, MISO, the outlets, the operators) are not from a page read; each draft says so.

## The landing of session 204

Session 204's report was pushed with its branch, before its own result existed. The result, also added to that report by this branch:

- **Waited for 13:00 UTC.** One test of `tests/test_planner.py` reads the real clock and fails from 05:00 to 13:00 UTC, so GitHub's check refuses a branch in those hours. Not touched (rule 8). Session 204's work was done by about 09:45 UTC; this session's work was done while that push waited.
- At 13:01 UTC `origin/main` was still `9687ca26`: the code machine had landed nothing, so nothing was merged in.
- `take before204`: exit 0, 25 pages, 0 failed, 13:01:41 UTC. Push at 13:05:33 UTC. GitHub's check, run 38253279086: success. Merged on `main` as `30dd910b` at 13:12:43 UTC.
- **Vercel: "Deployment has failed" at 13:12:53 UTC,** four seconds after "Vercel is deploying your app" (deployment `dpl_UMxy7XZv7MQESf1mreTsxcZNzHwD`, https://vercel.com/erw6/erw/UMxy7XZv7MQESf1mreTsxcZNzHwD). The deployment before it took 92 seconds, so this is not the site build failing.
  - Checked: Vercel's status page ("All Systems Operational"); 15 Vercel deployments in the 24 hours before; the site build on this machine at the same site files, exit 0; the landing's 19 files under `site/` are all data, no code.
  - Not checked: the log. No Vercel sign-in on this machine.
- `take after204`: exit 0, 25 pages, 0 failed, 13:16:22 UTC. **`compare before204 after204`: exit 0, 0 differences on each of the 25 pages,** expected: every address is in review and the live site is still the deployment of `9687ca26`.
- The main checkout on lab-desktop went back to `main` at `30dd910b` at 13:17 UTC.

## The landing

- Merged `origin/main` (`30dd910b`, session 204) into `task/205-licenses`: no conflict. The suite after it: exit 0, 3,445 tests.
- `take before205`: exit 0, 25 pages, 0 failed, at 2026-10-12T13:20:21Z. Against `after204`: 0 differences.
- This branch changes no file under `site/`. Its merge still starts a Vercel deployment of the whole of `main`, session 204's site files with it.
- **The push, GitHub's check, Vercel's answer, the after snapshot and the comparison are added by the branch `task/205-report`,** below this line.

Added by `task/205-report`:

- **Push** of `task/205-licenses` (`10be5869`) at 13:20:53 UTC, exit 0. **GitHub's check** "code branch", run 38255054586: success. **Merged** on `main` as `28e880da` at 13:28:45 UTC.
- **Vercel failed again:** "Vercel is deploying your app" at 13:28:50 UTC, "Deployment has failed" at 13:28:56 UTC, deployment `dpl_78gwF1oMczCxgD8mPj4vgDFfUM6T` (https://vercel.com/erw6/erw/78gwF1oMczCxgD8mPj4vgDFfUM6T). Two failures in a row, 16 minutes apart, each within seconds: a standing fault, not a passing one.
  - What it is not, as far as this machine can tell: an incident Vercel has posted (status page "All Systems Operational" at 13:14 and 13:30 UTC); a known advisory on the site's packages (`npm audit --omit=dev` in `site/`: exit 0, 0 vulnerabilities; Next.js 16.3.8); a broken build of these files (the site build passed here on session 204's site files, and this session changed none).
  - What it may be, not verified: something on Vercel's side of the project (the account, the plan, the project's settings) since 03:44 UTC, when the last deployment completed. Session 204's merge is the first deployment after that hour, so I cannot rule out that something in it is the cause; I found nothing in it that could fail before a build starts.
  - Nothing was changed to get round it, and no deployment was tried for its own sake.
- `take after205`: exit 0, 25 pages, 0 failed, at 2026-10-12T13:29:51Z. **`compare before205 after205`: exit 0, 0 differences on each of the 25 pages.** Expected: no page changes were meant, and none could arrive.
- **This file's own push** (`task/205-report`): `take before205r` exit 0, 25 pages, 0 failed, at 13:30:30 UTC. Its check, Vercel's answer and the after comparison cannot be in the file they follow; they are in the chain's closing message and under `runs/s204/` on lab-desktop (`cmp_before205r_after205r.out`).
- The scratch copy used for the clean runs of the suite was removed with `git worktree remove`. The worktree `erw-205` stays, on `task/205-report`.

## Decisions made without you

- **This branch was pushed with Vercel's failure of session 204's deployment unexplained.** It changes nothing under `site/`, GitHub's check had passed, and the live pages had not moved. Its merge is also the next try at a deployment. Reversible: a failed deployment leaves the site where it was.
- **"Each publisher in coverage.csv" is read as the 40 its source column names.** 47 other publishers appear only in the source registry or in a table's own rows (FERC, the Public Utility Commission of Texas, state commissions, three Texas utilities, the Federal Register, the smaller outlets). They were not read: the ceiling is 40. Their tables are "not settled".
- **Two verdicts, not one.** The four words of the prompt are kept; the second column says what changes if the ERW sells anything. Reversible: delete the column.
- **A publisher not read gets "needs written permission" by default,** and its tables are never listed as public.
- **A derived table takes the strictest verdict of its inputs** (the ERW's own Decision 23), kept to the grids its coverage row lists. Where the header names no input, the table is named by hand in `scripts/licenses.py` with the reason (13 tables).
- **The rule errs strict.** A derived table can be listed under an operator whose rows it barely uses.
- **MISO's sentence is the one in `paused_sources.csv`,** read on 4 October. Reading its page today would be a request to a paused publisher.
- **One page a publisher, also where the first address failed.** Five failed; none was tried again.
- **For RGGI the home page was read,** because no terms page could be found. For Data Center Frontier and Data Center Knowledge the page is the parent company's (Endeavor Business Media; Informa TechTarget).
- **For NOAA the database's readme was read,** which states the one restriction (non-U.S. stations). It names no license for the U.S. data.
- **Web searches before the reads** (above). If a search counts as a read, the ceiling was passed.
- **Three new files in `warehouse/metadata/`** and two scripts under `scripts/`. They read; none writes a table or `coverage.csv`.
- **The saved pages stay on this machine** (`runs/license_reads/`, not in git): they are the publishers' own text.
- **Ten drafts, not one per name.** The twelve outlets and nine operators share a draft each, with the names listed in it.
- **No personal email address is in a draft.** The signature has brackets.
- **The session's tests read none of the day's files** (`coverage.csv` moves daily; the document is of 12 October).

## For Samuel's ruling

- Vercel has failed every deployment since 13:12 UTC on 12 October. Will you read the log (the two commands at the top) and say what it needs, or sign this machine in to Vercel so a session can read it?
- 42 tables are flagged public where the publisher's sentence asks for permission (29 under NYISO, 25 under ISO-NE, 21 under MISO). Flag them internal until permission comes, or leave them while the letters are out?
- Should a derived table still take the strictest license of its inputs when only a few rows come from that input, or may those rows be dropped to keep the table public?
- FRED forbids keeping its content in a database without consent. Take the two series from EIA and the Federal Reserve Board directly, and retire the FRED route?
- Two tables are flagged internal where the page allows them: `carb_auction_allowance_prices` (California's page: public domain) and `rrc_lease_production_monthly` (noncommercial). Make them public?
- `datacenter_operator_sites` is public and holds facts from nine operators' pages; six pages read restrict automated collection or reproduction. Keep it public as facts, or ask first?
- The news tables that are public hold links and the ERW's own fields, no outlet text; Bloomberg's terms name linking itself. Keep them public, or ask the outlets?
- 47 publishers were not read (FERC, the Texas commission and utilities, the state commissions, the Federal Register, the smaller outlets). Approve a second sweep of 40?
- Is the ERW "noncommercial" for these letters? SPP, the IMF and the Railroad Commission allow that today and want a letter before anything is sold.
- Which of the ten drafts go out, and to whom at NYISO, PJM and MISO (their pages name nobody)?
- PJM: ask for the price of an Associate Membership, or leave PJM out of the product?

## The prompt

"Chain of 12 October (night): sessions 204 and 205, the data machine", pasted on 12 October 2026 at about 02:00 Pacific: the ten rules of the chain, and for 205: reads of each publisher's terms, license or data-use page, one page each, ceiling 40, no data request; for every one of the 198 tables the publisher, the page read, the sentence and the verdict, compared with `coverage.csv`'s flag and none changed; `docs/licenses.md` with the table and three lists; draft permission emails under `docs/reviews/`, not sent; a landing with snapshots; then rule 10.
