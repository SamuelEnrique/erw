# Session 157 report: the policy monitor

Run on 8 October 2026 (UTC), unattended, in the chain 155 to 159. Two agents worked in one working copy to written
briefs (`runs/session157/BRIEF_DATA.md`, `BRIEF_PAGE.md`): one on the reads, the tags and the daily refresh, one on
the page's new view. I ran the locked writes, the merged build and the landing. Scope held: federal regulators,
state commissions and grid operators; nothing municipal. `/policy` stays `review`.

## Six things to know first

- **The Federal Register answered HTTP 429 to 170 requests in a row, and that was the agent's fault.** Its first
  pull of the printed texts kept its pace through a rate limit. It was stopped and fixed (wait, halve the pace, one
  retry, then stop); the remaining 795 texts came with no 429. No row was made from a refused answer.
- **Up to 5 model calls were paid for and are not in the ledger: at most USD 0.11.** One was a fault of the ledger's
  writer under threads (fixed in `warehouse/llm.py`); four were in flight when the batch was stopped. The ledger
  holds USD 5.3003; with the bound, at most 5.41 of the 6.00 cap.
- **The next daily run will spend about USD 2 on its own.** Rescoring moved 123 actions to a rating of 5 or more,
  so 124 actions now have no impact read, and the daily reader reads them once (under its own cap of USD 3).
- **The derived fields were as weak in the second fifty as in the first.** On all 100: `states` wrong or missing
  in 40, the tags in 47. The copied fields stay sound. Both are now fixed from each document's printed text.
- **Treasury and the IRS are now in the Federal Register listing** (my reading of "the monitor refreshes"; say if
  not): 8 rows, all the IRS's, 5 tagged tax credit.
- **900 scores were not rechecked, and each row says so**: 662 Register actions the money did not reach and 238
  news releases whose text is not held.

## Verdict: the monitor refreshes itself and its reads are checked against the text; not ready to open

What is left, exactly:

1. **The live set shows the rechecked rows after today's daily run**, not before: the tables are in the Redivis
   drafts, which the runner restores at 14:00 UTC; I loaded nothing. Until then the new view reads the rows as
   loaded on 7 October, and a federal row's hover is its title where the Register holds no summary (100 of 136 in
   the last 30 days).
2. **No tagged action falls in either window tonight** (the newest of the 22 tagged is of 4 September), so a tag
   chip on a federal row was proven by unit tests only, not seen in the browser.
3. **Ohio and Illinois are never refreshed**: Ohio's docketing system answers a reCAPTCHA, Illinois's docket page
   says "no robots". Each is named in the agency filter with its reason on hover. FERC, Indiana and Arizona are
   refreshed in part.
4. **Virginia's terms were read for the first time**: "Permission is granted to make fair use..." (the sentence in
   full is in the Method note). Its class (sentences shown or withheld) is left for you with session 154's.
5. Three Indiana rows are about a MISO utility: listed when no grid is chosen, under no grid's filter.
6. The first view of `/policy` keeps its method paragraph on the face, since nothing it shows was to be dropped;
   the rule of no method prose would move it to a hover. Yours to say.
7. The daily refresh found 0 new rows in its trial; its first day with a row is untested on the runner.

## The hundred, against their source documents

| Field | New 50 | All 100 |
|---|---|---|
| type, RIN, document number, source, address, status | 0 each | 0 each |
| date, title | 0 each | 1 each |
| agency, abstract | 1 each | 2 each |
| docket | 1 | 1 |
| **states** | **20** | **40** |
| **sector tags** (the keyword rule, as held on 3 October) | **28** | **47** |
| sector (a model's) | 5 | 8 |
| why (a model's) | 4 | 8 |
| the read's price direction | 1 of 6 | 2 of 15 |

- The new 50 were drawn by a stated seed from the actions not in session 154's sample, saved before any fetch.
- **Fixed:** the place is now right in 85 of the 87 audited Register rows (54 before); 683 rows of the table
  change. Two titles the Register cuts short are completed from the print. Every one of the 1,637 Register rows
  has its printed text, kept by document number so it is never asked twice.

## The reruns, under the cap

| Step | Rechecked | USD |
|---|---|---|
| Impact reads | 226 of 234 (8 are on a site not requested) | 3.06 |
| Scores made on a title alone | all 853 | 2.00 |
| Other Register scores | 100 of 762 | 0.24 |
| **In the ledger** (273 calls, session 157) | | **5.3003** of 6.00; stop 5.50, lowered to 5.35 |

- `what_changes` blank fell from 55 reads to 12.
- Every row carries whether its model fields were rechecked against the source text in this session, and when.
- The measurement came first and the plan was written before each batch.

## The tags, across the whole table

- 14 actions and 30 tag rows before; **22 actions and 38 rows after**, the rule now also reading the first
  paragraph of the printed text. Tax credit: 0 before, 5 now.
- The page applies the same rule file to the rows it reads, so an action is tagged the day it arrives: on all
  1,875 actions held, 22 tagged, 0 differ from the Python rule.

## The daily refresh, under `health.py`

- One soft step asks, by plain request, each regulator's own open list for what is new: **9 of the 11 are
  refreshed** (FERC through the Federal Register and govinfo; Texas, Virginia, Pennsylvania, Indiana, Georgia,
  Arizona, Oregon, California); **Ohio and Illinois are never requested**. At most 120 requests a day, one a
  second to a host. Where a list gives only a filing's title line, that line is the row's sentence, marked as cut
  from the docket list; no model.
- A second soft step rebuilds the page's site files after it (the agent's addition; two lines to remove).
- The trial: 55 of 120 requests, 0 new rows.

## "What changed this week" on `/policy`

- A second view of the page (`/policy?view=week`); everything `/policy` showed is its first view, unchanged.
- **Seven days: 28 rows** (24 federal actions, 4 docket rows), all with a model's read. FERC 11, DOE 6, NRC 6,
  Indiana 3, EPA 1, Texas 1. **Thirty days: 146 rows** (136 and 10); 145 with a read, 1 "no read yet".
- Filters in the address: agency (18 choices), topic, grid, large-load relevance. MISO shows "paused while terms
  are reviewed" and no row. A small chart of counts by agency and topic answers the mouse.
- A state row of a regulator whose terms restrict copying shows its facts, link and read, not its sentence, as on
  `/cost-of-power`.

## Every pull against its ceiling

| Pull | Ceiling | Read |
|---|---|---|
| The Federal Register's printed texts | 5,000 requests, 2 GB | **1,886 requests**, 109 MB (170 of them refused with 429) |
| The second fifty's source documents | 200 requests, 200 MB | 94 requests |
| Releases for the reads | within the same | 44 |
| The daily refresh's trial | 120 requests a day | 55 |

- **Contact string where one is required: exactly "ERW research project, github.com/SamuelEnrique/erw". No address
  sent.** No request to misoenergy.org; no PJM Data Miner or API; Ohio's and Illinois's systems not requested.
- Terms: each regulator's as session 154 quoted them; Virginia's added. The Federal Register's records are the
  table's registered source, as before.

## The landing

- **Added after the landing.** Pushed with sessions 156, 157 and 159 as `task/156-157-159` (`bc1fba0`): checks passed (run
  37764344933), merged as `a161ec5`. **Vercel built it:** "Deployment has completed" at 10:43:19 UTC on 8 October.
- **Snapshot before** (`157_before`, 10:34:04 UTC) **and after** (`157_after`, 10:43:32 UTC): **0 differences** on the
  25 live addresses, 3,357 checked number keys. Nothing was reverted.
- **On production, in the internal view:** the policy page's check 45 of 45, the resource map's 97 of 97, the Ask
  panel's 13 of 13 (recorded answers).
- Under the lock, nothing released and nothing loaded. I first restored the three policy tables from Redivis (the
  runner's newer copies: 1,855 actions, 239 reads), so no row of 4 to 7 October was lost; then the writes:
  `policy_actions` 1,877 rows, `policy_reads` 239 (226 rechecked, 8 not, 5 newer kept as they are),
  `policy_reads_evidence` 1,999, `policy_action_tags` 38. Validators, coverage, the archive, the Redivis drafts:
  exit 0 each. No live page reads any of them.

## Checks

- On the merged build: `check-policy` 45 of 45; `check-routes` 0 failed (8 live pages and 141 in review asked as a
  visitor); `check-values` 7,006 of 7,006. The whole suite in a clean copy of the merged commit: 2,440 tests,
  passed.

## Decisions made without you

1. Treasury and the IRS added to the listing.
2. The second daily step (the site files).
3. The stop lowered from USD 5.50 to 5.35 after the lost calls.
4. The tables are not loaded by me: the daily run loads them.
5. A regulator that refuses is never requested by the daily step.

## The five most interesting numbers

1. **40 of 100 and 47 of 100**: actions whose `states` and whose tags were wrong or missing, before the fix.
2. **853**: scores that had been made on a title alone, all now made on the document's first paragraph.
3. **55 to 12**: reads whose `what_changes` was blank.
4. **170**: requests the Federal Register refused in a row before the pull was stopped.
5. **28 rows in seven days, 146 in thirty**: what the new view shows tonight; FERC is 75 of the 146.
