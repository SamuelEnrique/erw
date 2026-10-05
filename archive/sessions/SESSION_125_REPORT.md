# Session 125 report: the contracts tracker, to useful

## To finish

**The freeze is on** (`REVIEW_FREEZE`, 5 to 6 October, merged at 15:07 UTC). From 15:00 this session pushed `wip/125-contracts` only. Four things are left, in this order. None changes a live page or a table a live page reads.

**1. The write steps the data lock kept me from.** The daily run took the lock at 14:03:53 UTC and still held it at 15:32, past its usual 86 minutes. Two waits of 15 minutes (15:01 and 15:16) ended without it. When `python warehouse/lock.py status` says free:

```bash
python warehouse/lock.py run --task "session 125: contracts history and terms" --minutes 45 --wait 15 -- bash runs/session125/finish_writes.sh
```

That script is on this machine (not in git) and runs, each with its own exit code read, stopping at the first that fails:

```bash
PY=C:/Users/lossa/Documents/erw/.venv/Scripts/python.exe
T='^ferc_eqr_(contracts_history|contract_terms|party_mw|quarter_changes)$'
git fetch -q origin && git merge -q --no-edit origin/main          # the daily run's commit
"$PY" warehouse/connectors/ferc_eqr_contracts.py --quarter 2025_Q4 --history --also 2026_Q1 2025_Q3   # from warehouse/raw; two requests, for the list
"$PY" warehouse/connectors/ferc_eqr_contracts.py --quarter 2025_Q3 --history --also 2026_Q1 2025_Q4
"$PY" warehouse/derived/eqr_terms.py
"$PY" warehouse/validate/erw_validate.py warehouse/output/ferc_eqr_contracts_history.csv warehouse/output/ferc_eqr_contract_terms.csv warehouse/output/ferc_eqr_party_mw.csv warehouse/output/ferc_eqr_quarter_changes.csv
"$PY" warehouse/metadata/build_coverage.py --only "$T"
"$PY" warehouse/archive/archive.py --tables "$T" write
"$PY" warehouse/redivis/upload.py --tables ferc_eqr_contracts_history ferc_eqr_contract_terms ferc_eqr_party_mw ferc_eqr_quarter_changes   # a draft, in the internal dataset
```

**2. Commit what step 1 changed, to the wip branch.**

```bash
git add docs/coverage.md warehouse/metadata && git commit -m "Session 125: coverage, registry and manifests of the four contract tables with all four quarters" && git push origin wip/125-contracts
```

**3. The page's stored summary, so `/contracts` shows four quarters and not two.** Internal, read only with the internal token; no live page reads it. Held because it is after 15:00:

```bash
python warehouse/lock.py run --task "session 125: the contracts page's summary" --minutes 8 --wait 15 -- C:/Users/lossa/Documents/erw/.venv/Scripts/python.exe warehouse/supabase/load.py --only '^ferc_eqr_contracts$' --no-vacuum --allow-older ferc_eqr_contracts
```

**4. Land the branch, after the freeze** (`python scripts/freeze.py status` exits 0). It holds the method's final numbers, one more test, the connector's handling of a cut-off filing, session 124's updated report and this one. Nothing a visitor sees.

```bash
node site/scripts/snapshot-live.mjs take before-125b
git fetch origin && git merge origin/main && git push origin wip/125-contracts && git push origin wip/125-contracts:task/125-contracts
python runs/session118/watch_run.py task/125-contracts 15      # checks, then the merge
node site/scripts/snapshot-live.mjs take after-125b && node site/scripts/snapshot-live.mjs compare before-125b after-125b
git push origin --delete wip/125-contracts wip/124-network-v3   # once both are on main
```

**And one thing to know before 16:00.** The daily run of 14:00 UTC was still running when this was written. Scheduled jobs do not read the freeze file: when it ends it will load its tables and push its commit to main, which deploys, as it does every day. The live pages were unchanged from 15:08 to 15:32 UTC (snapshot `at-1532`, 0 differences); what the daily run moves when it lands is not in this report.

## What was done

**Built, and its page deployed before the freeze.** `/contracts` (in review, internal) has two new views: "Ranked by megawatts stated" and "What the filings state". Three more quarters of FERC's Electric Quarterly Reports were pulled, a filing at a time: 574,005 contract rows of the 800,000 allowed, at no cost. No model call. No live page changed (snapshots below).

**Verdict: not ready to open, and the reason is not code.** The page is now useful to the person it was built for, and honest about how thin the record is. Two things keep it closed: the table is internal until a person has read FERC's own terms (its pages again refused this machine), and the page holds names of companies beside figures that rest on name rules a person has not yet reviewed (1,281 doubtful pairs). What is left is at the end.

## Read these first

1. **A price can be read from the words in 23 of 104,952 rows.** That is the whole answer to "read a price from the words". 104,929 remain unread, and are counted by reason:

   | What the words hold | Rows |
   |---|---|
   | No dollar amount at all ("Market Based", "No Rates in this Contract", a tariff's name) | 101,781 |
   | A dollar amount with no unit after it (a deposit, a facilities charge) | 1,739 |
   | One amount with its unit, and a condition (escalating, plus other charges, a cap, an if, a year) | 766 |
   | More than one dollar amount (a schedule by year, peak and off-peak, tiers) | 636 |
   | A unit in the words that is not the unit the filing's own field names | 5 |
   | Another number beside it that is not a quantity | 2 |
   | **Exactly one amount, its unit, nothing else: read** | **23** |

   - For energy, capacity and tolling alone: 42,246 rates in words, 21 read.
   - Of the 23, 9 are in dollars per megawatt-hour and fill `price`. The other 14 are capacity prices per kW or MW and month or day; they are kept in their own unit and never turned into dollars per megawatt-hour.
   - I read all 23, and the commonest rows of each reason. The rule's first version accepted a cap ("in no case more than"), a price that applies "if" something happens, and a formula with a time-of-day factor. Those are now unread.
   - 47 rows hold a figure with a unit and no dollar sign ("2.50 per MWH"). They are not read: no currency is stated and most are one part of a charge. Counted so the size of that gap is known.
2. **Megawatts are stated for very few contracts, so the ranking is of what is stated.** In force in 2026 Q2:

   | Product | Contracts in force | State a quantity in MW | MW stated, in all |
   |---|---|---|---|
   | Energy | 22,808 | 356 | 31,402 |
   | Capacity | 12,598 | 382 | 40,617 |
   | Tolling | 216 | 3 | 525 |

   The page ranks buyers and sellers by megawatts, shows each one's place by contracts beside it, and says in its first sentence that this is not a ranking of the market. The two orders differ widely: a party first by megawatts can stand hundreds of places down by contracts.
3. **Some "megawatts" are not megawatts.** Some rows file figures in the hundreds of thousands under MW. A contract cannot be for more than the largest power station operating in the country, which the warehouse holds: 6,809 MW (EIA's generator inventory, August 2026). 45 rows of 17 contracts state more; they keep their figure as filed and are left out of the ranking, counted on the page. A figure under the ceiling can be mislabelled too, and nothing in the filing can tell: the page says so.
4. **No storage tag can be made from the product fields.** FERC's product list has no storage product: 0 rows. The words storage, battery or BESS do stand in 1,095 rows, in other fields: the seller's name (715), the rate description (266), the agreement's identifier (163), the tariff reference (68). The table records where (`x_storage_words_in`) and tags nothing.
5. **Tolling: 382 rows of 217 contracts** carry the product name Tolling Energy.
6. **Buyer merges marked certain are applied; the 1,281 doubtful pairs are untouched and still listed.** "Certain" is a merge a rule makes (`x_merged` yes in `ferc_eqr_buyer_names`). 128,962 of the 186,873 rows carry a buyer name counted with at least one other spelling.
7. **About one contract in six is new each quarter, and about as many leave.**

   | Filed for | Contracts in force | New | Gone | Kept |
   |---|---|---|---|---|
   | 2025 Q3 | 67,680 | | | |
   | 2025 Q4 | 67,914 | 11,863 | 11,629 | 56,051 |
   | 2026 Q1 | 68,981 | 12,201 | 11,134 | 56,780 |
   | 2026 Q2 | 70,277 | 13,561 | 12,265 | 56,716 |

   - Three in four have stood for a year: 52,994 of the 70,277 in force in 2026 Q2 are filed in all four quarters. For energy, 16,739 of 22,808.
   - A contract is the filer's identifier and its own contract identifier. A filer that renumbers makes one gone and one new, so both counts are ceilings on real change.
   - By product (energy, capacity, tolling) the table is in `docs/methods/eqr_terms.md`.
8. **Two filings of 2025 Q4 are cut off at the source.** The zip FERC serves for each ends inside its transactions file and has no directory (read twice, the same bytes). Their contracts files come first and are whole by the zip's own checksum (102 and 323 rows), but the file naming the filer comes after the break. So the rows cannot be given a company identifier, and are left out: 425 of 191,557 rows. The connector now asks twice for such a filing, then leaves it out, names it in the log and counts it in the table's header.
9. **FERC's terms, quoted.** Two passages of the Federal Register say the filings are public ("while making data available to the public", 91 FR 7278 at 7279; "available for public inspection in a convenient form and place", 91 FR 14306 at 14310). Neither states terms for republishing. FERC's own pages (disclaimers, privacy policy, the Electric Quarterly Reports page) answered this machine with HTTP 403 again; that was not worked around. The page and the method quote the passages whole and say what was not reached. The tables stay internal.

## The pull

| Quarter | Filings read | Contract rows | Requests | Read |
|---|---|---|---|---|
| 2026 Q1 | 4,016 | 191,996 | 4,018 | 3.74 GB |
| 2025 Q4 | 3,912 of 3,914 | 191,132 | more than 3,720, in two runs | more than 3.4 GB |
| 2025 Q3 | 3,768 | 190,877 | 3,770 | 3.95 GB |
| | | **574,005** of 800,000 | | |

- A filing at a time, with a pause between two (`--fetch-only`), no data lock held while fetching. A filing's zip holds its transactions too; only its contracts file is kept (about 200 MB for the three quarters, in `warehouse/raw`, not in git).
- The earlier quarters go to their own table, `ferc_eqr_contracts_history`. `ferc_eqr_contracts` stays one quarter: every agreement in force is filed again each quarter, so one table of four would hold most contracts four times.
- The registry's row for FERC, which the live `/terms` page lists, kept its words and its document; a test holds them.

**What is on the machine now, and what is not.**

| | State at 15:32 UTC |
|---|---|
| Raw contract files of all three quarters | on disk (`warehouse/raw/ferc_eqr_contracts/`), with each quarter's index |
| `ferc_eqr_contracts_history` | 190,816 rows: 2026 Q1 only. 2025 Q4 (190,249 rows) and 2025 Q3 (190,050) wait for the lock |
| `ferc_eqr_contract_terms`, `ferc_eqr_party_mw`, `ferc_eqr_quarter_changes` | built with two quarters held (186,873, 812 and 28 rows); validator pass; coverage built |
| Archive and Redivis draft of the four tables | **not done**: both are write steps |
| The page's stored summary | stored at 13:16 UTC, with two quarters |

- Every figure above for 2026 Q2 (prices, megawatts, tags, merges) is from the tables as built and will not change: it does not depend on the earlier quarters.
- **The four-quarter figures of point 7 are from a trial**, not from the table: the same code over the same raw files, written to `runs/` without the lock (`--limit`, which writes no table). Step 1 of "To finish" writes them to the table; a difference would be a fault.
- Until step 1 and its Redivis draft, the four tables exist only on this machine. The raw files rebuild them.

## The live pages

**One push, before the freeze.** `task/125-contracts`: run 37318355869, checks passed, merged to main as `b2f09c5` at 13:45 UTC; Vercel built it at 13:46. It carried session 124's code too, which Vercel had not built on its own.

| Snapshots | Pages | Differences |
|---|---|---|
| `before-125` 13:38:03 to `after-125` 13:47:09, around the deploy | 25 | **0** |
| `before-125load` 13:15:12 to `after-125load` 13:16:26, around the loader | 25 | 6, all on `/network`: "refreshed 12:05 UTC" to "13:05 UTC" and the demand's newest hour 10:00 to 11:00 UTC. Expected: the hourly refresh |

- The loader stored the page's summary with the contract table (internal, read only with the internal token). It did not load the catalogue. The registry gained one held source (`erw:eqr_terms`); `/terms` reads the registry from the build, with the hold, and did not move.
- On production the six contract views and `/network/v3` render in the internal view; a visitor finds them closed. Route check on the local build: 16 live pages and 107 in review, 0 failed.

## The freeze

`REVIEW_FREEZE` was created at 15:00:07 UTC on a branch from main, with `start: 2026-10-05` and `end: 2026-10-06` and one note line. `python scripts/freeze.py status` read it as a freeze (exit 1). Pushed as `task/freeze-2026-10-05`: run 37329344949, checks passed, merged as `c0bab7d`; Vercel built it at 15:07.

- `before-freeze` 15:00:21 to `after-freeze` 15:08:15, 25 pages: **35 differences, all on `/`, all the clock.** The price board's newest real-time price of five hubs (ERCOT 43.02 to 23.39, California 52.18 to 42.54, New York 29.66 to 32.41, SPP 23.62 to 57.12, New England 20.40 to 23.82 USD/MWh), their interval lines, and four lines giving a table's age in days (each a tenth lower). Expected: the 15-minute prices. The other 24 pages: 0.
- `after-freeze` to `at-1532` (15:32:15): **0 differences.**
- After 15:00 this session pushed `wip/` branches only and loaded nothing.

## The daily run of 14:00 UTC

Run 37321169760 started at 14:00:02, took the data lock at 14:03:53, and was still in its step "Pull, validate, rebuild coverage" at 15:40, when the chain ended. The two daily runs before it took 86.2 minutes each. Its commit had not landed, so it is not merged here (step 1 of "To finish" merges it).

**Not read, because the run had not finished:** whether Monday's digest was written and delivered, whether the new `health.py alert` step ran, and whether `network_daily.py --daily` passed with session 124's builder. Its log is `python runs/session118/gh.py log 37321169760 runs/daily.zip` once it ends.

## Decisions made without you

- **The megawatt ceiling.** Leaving out a figure is a judgment; I tied it to a number the warehouse holds and counted what it removes, in place of ranking a year's megawatt-hours as megawatts.
- **`--allow-older` on the loader.** It refused the contract table: 18,989 rows here against 19,009 live. The 20 are exactly the rows executed on 8 January 2024, the day the live set's 1,000-day window passed overnight. Checked, then allowed. The loader reads a shorter events file as an older one; it will refuse again each day until it knows the window (in "What is left").
- **A conditional price is not read**, even where number and unit are plain ("$50/MWh, escalating at 2 percent"). The prompt's test is number and unit; I added "and it is the price", since a first-year price or a cap ranked as the price would mislead.
- **The two cut-off filings are left out**, though their contracts files are whole. Giving them a company identifier would mean matching the seller's name to another quarter's filing: an inference, and yours to allow.
- **Nothing more was loaded after 15:00.** See "To finish".
- **An older test was changed** (session 90): it passed the whole stored summary on node's command line, which Windows refuses once the summary holds this session's lists. It now passes the two fields it reads.

## Errors, and what caught them

| What | Caught by | Now |
|---|---|---|
| The rule read a cap, an "if" price and a formula with a factor as prices | reading all 31 rows it first accepted | 8 of them unread; the words are in the rule and the tests |
| A year's megawatt-hours ranked first as megawatts | looking at the first ranking's top figures | the ceiling, read from the warehouse |
| A quantity of zero counted as megawatts stated | the same | not a quantity |
| The 2025 Q4 fetch stopped on a zip with no directory | the run's own failure (exit 1, "File is not a zip file") | asked twice, left out, counted; a test holds the handling |
| The page's words "could not be read" tripped the review-page check, which reads them as a failed read | the check (5 of 6) | reworded; 6 of 6 |
| Session 90's test failed in the full run (command line too long) | the full suite | fixed as above |
| A heredoc holding an apostrophe failed in this shell | the shell | the script written to a file |

## Tests

`tests/test_session125.py`, 27 tests: every reading and every reason of the price rule on made-up words; megawatts (units, zero, the ceiling, a contract counted once); the tags and the words elsewhere; rule merges only; new, gone and kept, and no change written across a gap; the loader's summary from made tables; the pull's ceiling and modes; the unreadable filing; the registry row `/terms` shows; that the four tables are internal, unloaded, held and out of git; that no name of the real tables is in a doc, a test, the page or this report; the tables as built; the page's views and words.

Full suite before the deploying push: 1,258 passed, 19 skipped, exit 0. Site build exit 0. Route check exit 0. On `wip/125-contracts` as it stands, with this report in place: 1,259 passed, 19 skipped, exit 0.

## What is left

1. **A person reads FERC's terms** (ferc.gov, in a browser) and rules on the license. Everything here is internal until then.
2. **A person rules on the 1,281 doubtful pairs** and on the rule `suffix_left_off` (session 99's open point). The ranking's names rest on them.
3. **The two cut-off filings of 2025 Q4**: allow the match by seller name, or ask FERC for whole files.
4. **The loader and the 1,000-day window**: compare an events table with a window by its newest rows, not its count, so the daily refusal ends.
5. **The 766 conditional rows** are the next prices worth reading, by hand or by a rule per kind (a first-year price with an escalator is the commonest). Each kind needs its own column: a base price is not a price.
6. **The quarter-signed view still reads one quarter's filings.** With four quarters held it could show a contract's first appearance; `x_first_quarter` is in the table for it.
7. **Technology.** Still no column says what a contract is for. The 1,095 rows naming storage outside the product fields are where a person would start.
