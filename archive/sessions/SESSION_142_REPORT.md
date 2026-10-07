# Session 142 report: Thesis Builder, the unstable stage

Run on 7 October 2026 (UTC), unattended, in the chain 140 to 145. Landed out of order, before session 140, because
it was finished first and touches no page. An agent built it to a written brief; I checked its tests, its spend in
the ledger and the landing myself. Nothing here changes a page.

## Three things to know first

- **The target is only partly met.** Runs 1 and 2 of the geothermal niche give the same landscape and pipeline map
  in the same order. Run 3 adds one company (XGS Energy), and the cause is NOT a change of source: the page it rests
  on (renewablesnow.com) was held since 6 October, and the model reported that sentence from it for the first time in
  run 3. The rule reads only sentences the model quotes from the web, so what the model quotes still moves the set.
- **The landscape is much smaller: 3, 3 and 4 companies** (session 135: 8, 12, 9). The rule needs literal terms of a
  trend in a saved sentence. The model's own opinion would have named a trend for 20 of 24, 19 of 31 and 20 of 26
  organisations. Whether three or four companies is a useful map is yours to judge (thresholds below).
- **The figures are the three runs read through the FINAL rule.** The rule was corrected three times after seeing run
  data; the code stage was then re-applied to each run's saved, paid model answers from an empty store, with no model
  call. Run 3 as it executed printed landscape 5 and pipeline 3; the final rule gives 4 and 2.

## Verdict: not ready to open. What is left, exactly

1. **The web tier depends on what the model quotes.** For the same set each time, the run must hold the page text
   itself (fetch each result's address in code, saved with hash and date) so the rule reads the sentences. That is a
   data pull and needs your approval.
2. **The evidence store is a local file.** On the GitHub runner the page's runs use, it is discarded, and
   `energy_companies` and `energy_deals` are absent there, so the warehouse tier is empty. It needs a table or a
   bucket object (a migration). Not built.
3. **The thresholds are yours.** On the final store: as built, 4 companies on the landscape; tied at 1 point instead
   of 2: 5; one term enough to support: 8; both loosened: 13.
4. **A full run of the page writes its trends anew.** Stability was measured with the five trends held fixed.
5. **Facts are still the model's reading**: "USA" against "United States" is on record 17 times as a disagreement.
6. **A full run's stage reserves now sum to USD 2.08 against the run's stop of USD 2.00**: if every stage hit its
   reserve, the last would be refused. Left for your ruling.
7. **Two matching gaps:** "modelling" does not match "modeling"; an acronym is not joined to its full name ("NREL"
   and "National Renewable Energy Laboratory (NREL)" count as two).
8. **The PitchBook stage: untouched**, still pending your results.

## The rule as built (`warehouse/thesis/tie.py`: code only, no model, no network)

- **Order of evidence.** Warehouse first (the company's `energy_companies` row and the `energy_deals` rows naming it,
  read fresh each run); then the sources fetched (the title of a search result or a cited passage that names the
  company; a reported sentence found word for word in its source's held text); then the web (a sentence the research
  reported from a page, with the page's address, not held as text).
- **A trend's terms.** Words of its title and its two search phrases, four letters or more, or capitals of two or
  more (AI, DAS, DOE); lower case, final "s" dropped; stop words, the niche's own name words and four general words
  (system, method, public, high) removed. A word of the company's own name is not a term for it.
- **Scoring a person can redo.** A sentence supports a trend with 2 or more distinct terms, or every word of one
  phrase. Points: warehouse 3, fetched 2, web 1; plus 1 if strong (a whole phrase, or 3 or more terms). A trend's
  score is the sum of the best sentence per address, at most 3 addresses; the same sentence on two addresses counts
  once. Tied at 2 or more.
- **Tie-break.** Total score over tied trends, then best tier (warehouse, fetched, web), then the normalized name.
  The pipeline map still takes confidence 60 or more, the first ten.
- **Dedupe.** The same core name, or one core name the leading words of the other ("Eden", "Eden GeoPower") with
  website domains that do not differ; a short name leading two different companies merges with none; the longest name
  is kept.
- **Saved evidence.** One store per niche, stage and geography: every source by address with the hash of its text
  and the date fetched, every reported sentence, every row. A run reads the store and what it newly fetched, and its
  record names the difference from the run before by company and source. The first value saved for a fact stands; a
  later different reading changes nothing and is listed as a disagreement.

## The three runs side by side

The niche "geothermal mapping and sensing", startups, United States, session 135's five trends held fixed.

| | Run 1 | Run 2 | Run 3 | In all | In any | Mean overlap | Session 135 |
|---|---|---|---|---|---|---|---|
| Found | 24 | 34 | 35 | 23 | 37 | 0.738 | 27, 32, 24; 0.697 |
| Private | 19 | 22 | 22 | | | | |
| Fits stage and geography | 14 | 16 | 16 | | | | |
| On the landscape | 3 | 3 | 4 | 3 | 4 | **0.833** | 8, 12, 9; 5 of 17; 0.429 |
| On the pipeline map | 1 | 1 | 2 | 1 | 2 | 0.667 | 5, 7, 6; 3 of 11; 0.402 |

- **Landscapes, in order.** Run 1: Zanskar Geothermal & Minerals; Geothermal Radar; Thermofilic. Run 2: the same.
  Run 3: Zanskar Geothermal & Minerals; XGS Energy; Geothermal Radar; Thermofilic.
- **Pipeline maps.** Zanskar; Zanskar; Zanskar and XGS Energy.
- **The rule alone does not stabilise; the saved evidence does.** On each run's own evidence with no store, the
  landscapes are 3, 1 and 4 companies and overlap 0.444, the same as session 135's 0.43.
- Session 135's pipeline overlap, 0.402, was computed today from its saved states; its report gave none.

## Every difference between runs, with its explanation

- **XGS Energy** (run 3, onto the landscape and the pipeline, score 3): 2 points from a sentence of renewablesnow.com
  holding "DOE geothermal field tests" (the page was held since 6 October; the sentence was first reported in run 3);
  1 point from a sentence of energycapitalhtx.com saved since run 1.
- **Mazama Energy** (run 2, private to fits, below the landscape): its country and location were first stated by the
  model in run 2, from three sources already held. Not a source change.
- **Geothermal Strategy Partners** (run 3, private to fits): country first stated in run 3 from sources already held;
  its one new sentence repeats one already saved on another address, so it counts once: score 1, not tied.
- **Zonge International** (run 3, fits to private): its stage fit "no" was first stated in run 3; two of its three
  sources were first fetched in run 3.
- **Found, run 2:** ten organisations first named. **Found, run 3:** one, a duplicate of "NREL" under its full name.
- So 1 of the 4 moves is explained by sources newly fetched; 3 are the model stating something for the first time
  from sources already held. Each is on record by address and hash.

## What a user receives

- "Why it is here" is now a saved source sentence in quotation marks with its publisher's domain, or "(ERW companies
  and deals tables)".
- Kept: the caption above the landscape, and the stop reason "no fetched source ties it to one of the five trends".
  Reworded: "its confidence is too low for the pipeline map"; "the pipeline map is full".
- **None of it states the order of evidence, the points, the thresholds or the tie-break.** Checked by a script that
  read every key and string of the three real reports and nine page and note files (0 found), and by a test.
- No site file, no Method note and nothing of the PitchBook request changed.
- **One thing for you to weigh:** the rule itself is in `warehouse/thesis/tie.py` and its test, and this repository
  is public. A user of the tool is not shown it; a reader of the repository can read it.

## Every pull against its ceiling

- **No data pull.** The tool's own web search and fetch by the model, as in any run. No MISO request, no PJM request.
- **Run `20261006T193517Z-50a8be` and its PitchBook request: untouched.** The three runs made no database connection.

## Model spend: USD 2.9046 of the USD 6.00 cap (stop at 5.50)

| Run | Research | Structure | Total |
|---|---|---|---|
| 1 | 0.7262 | 0.2199 | 0.9461 |
| 2 | 0.7876 | 0.2371 | 1.0247 |
| 3 | 0.6992 | 0.2346 | 0.9339 |
| **All** (6 calls, session 142 in the ledger: 2.904603) | | | **2.9046** |

- **Nothing was refused.** Two stops stood before every stage: the run's own guard at USD 5.50 and the ledger's cap.
- Run 1 was the measurement: its research cost 0.7262, above the 0.66 reserve, so the reserves were raised before
  run 2 (landscape 0.66 to 0.85, its structure 0.26 to 0.34).
- A landscape stage now costs USD 0.93 to 1.02 against 0.72 in session 135: the notes carry whole quoted sentences.

## The landing

- **Freeze: on** (`python scripts/freeze.py status` exited 1; it ends today, 7 October). The chain's prompt names
  these landings; nothing a live page shows or reads was touched.
- **The first push failed its checks and nothing merged** (run 37605982726): session 30's cost ledger test recorded
  nothing, because the new test file switched the ledger off at import and it stayed off for the whole suite. Fixed
  (the switch now lasts only while that file's tests run), the whole suite run in a clean copy (1,566 tests, passed),
  a new before snapshot taken, pushed again.
- **Second push: checks passed** (run 37607190601), merged as `1e8beb8`.
- **Vercel built it:** "Deployment has completed" for `1e8beb8` at 10:32:39 UTC.
- **Snapshot before** (`142_before2`, 10:24:09 UTC) **and after** (`142_after`, 10:33:04 UTC): **0 differences** on the
  25 live addresses, 3,357 checked number keys. No number moved on `/cost-of-power/battery`, `/network` or `/storage`.
  Nothing was reverted.
- This report is pushed on `wip/142-thesis` and reaches main with the next session's landing.

## Checks

- `tests/test_session142.py`: 41 tests on saved real evidence (seven companies scored by hand, the tie-break, the
  same evidence giving the same landscape twice and under six shuffles, the dedupe, the difference between runs, what
  a reader sees, a stage refused before it starts, paid research kept).
- `tests/test_session135.py`: 29 tests; three assertions changed on purpose (the two reworded stop reasons; the
  guard's example, because the landscape reserve rose).
- The whole suite in a clean copy of the branch: 1,566 tests, passed, before the second push.

## Decisions made without you

1. Landed before session 140, out of order, because it was ready and touches no page.
2. The three runs kept their state under `runs/session142/`, not in the tool's store, through new flags; the store
   to keep is `runs/session142/final/evidence/`.
3. The first value saved for a fact stands ("most sources wins" had moved a company when the model called a spinout
   a university).
4. A sentence the model attributes to a warehouse row is dropped: the rule reads the warehouse itself.
5. Research already paid for is saved when a later stage is refused.
6. `docs/methods/thesis_builder.md` (internal) still describes the old selection. Not changed.

## The five most interesting numbers

1. **0.833 against 0.429**: the landscape's overlap across three runs, now and in session 135.
2. **0.444**: the same rule on each run's own evidence. The saved evidence, not the rule, is what stabilises.
3. **3 of 14**: the fitting companies the rule ties to a trend in run 1, where the model's opinion named a trend for
   20 of 24 organisations.
4. **6 against 20 and 21**: the sentences the same prompt saved in run 2 against runs 1 and 3.
5. **1 sentence**: the whole difference among the three landscapes, from a page held since 6 October.
