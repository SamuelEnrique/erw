# Session 158 report: Thesis Builder, the name rule

Run on 8 October 2026 (UTC), unattended, in the chain 155 to 159. An agent built it in a working copy of its own to
a written brief (`runs/session158/BRIEF.md`), in two phases; I landed the code between them and checked the spend
in the ledger. `/thesis` stays `review` and internal.

## Five things to know first

- **The overlap is 0.733, below last night's 0.889 and session 142's 0.833** (pairs 1.0, 0.6, 0.6). The two runs on
  the laptop give the same four companies in the same order; the runner's run differs by two.
- **Neither difference comes from your rulings; both come from where the run was made.** A page that answered the
  laptop (renewablesnow.com, 200 at 09:06 UTC) refused the runner (403 at 10:22 UTC), and a page that fails holds
  no sentence, so XGS Energy left the runner's landscape. And one search result's title returned to the runner's
  search and not to the laptop's put Teverra LLC on it. By the rule as it stood before tonight the same three runs
  read 0.619: the rulings worked on the runner too.
- **Your rulings alone, on the earlier paid answers:** session 147's 5, 5, 6 (0.889) become 4, 4, 4 (1.0); session
  142's 3, 5, 5 (0.733) become 3, 4, 4 (0.833).
- **Quaise Energy leaves the landscape in every reading of every night.** Its one remark, printed on two pages,
  counted once is 1 point, under the tie of 2. That is your ruling doing what it says; worth your eye.
- **A build fault of this session reached production's deploy, not its pages.** A type error in the provider file
  passed the agent's own build and GitHub's checks and failed Vercel's deployment of the first landing; production
  stayed on the deployment before it for 23 minutes, the live pages untouched. I fixed the line and landed it. Why
  GitHub's build did not catch it is not yet known.

## Verdict: not ready to open. What is left, exactly

1. **A page refused to one machine drops a company** (session 147's open point, now the largest cause of
   difference): keep a page's last good text when it later refuses, or not. Yours to rule.
2. **A search result's title counts as evidence** (2 points): whether it should.
3. **Whether a vendor page's sentence may tie a company** (4 such sentences scored on the runner).
4. One company stands under three names ("Terra AI"), and its first reading of its kind stands.
5. **The research stage's reserve**: 2 of the 6 research calls of sessions 147 and 158 passed USD 0.85.
6. The runner's log holds only the run's one summary line; that its store was the bucket and its pages were
   fetched is read from the state it kept, not from the log.
7. The "vendor page" mark has not yet appeared in a report a user holds.
8. Unchanged: the thresholds are yours; the PitchBook stage waits for your results; Crunchbase waits for your
   ruling on its terms.

## What was built

- **The name rule.** A company whose name is made only of the niche's own words matches a sentence only as a proper
  noun: capitalized as the company writes it and not part of a longer capitalized name ("Geothermal Technologies
  Office" is not the company), or with the company's domain, or in a list of companies. Every other company's
  matching is unchanged.
- **The same remark counts once**; the higher-tier copy is kept; the count of merged pairs is in the run's record.
- **Vendor pages are read and labeled**; a "Why it is here" sentence from one carries a short mark with a hover.
- **A Crunchbase answer is refused and nothing of it is stored**; the choice on `/thesis` shows Crunchbase as not
  yet available, with the reason on hover. PitchBook and Harmonic are as they were.
- **No point, threshold, tie or tie-break changed** (a test asserts the constants and the nine scoring lines).
- **For the runner** (the agent's additions, in the workflow): optional inputs for a like-for-like landscape run
  (with none given the workflow does what it did), and a run whose store is the bucket keeps its paid answers and
  ledger rows there (before, the runner lost them).

## The three runs side by side

Geothermal mapping and sensing, startups, United States; the five trends held fixed; from an empty store.

| | Run 1, laptop | Run 2, laptop | Run 3, the runner |
|---|---|---|---|
| Landscape | Zanskar Geothermal & Minerals; Thermofilic; Geothermal Radar; XGS Energy | the same four | Zanskar; Thermofilic; Teverra LLC; Geothermal Radar |
| Research, USD (reserve 0.85) | 0.7387 | 0.8512 | 0.7839 |
| Structure, USD (reserve 0.34) | 0.2431 | 0.2523 | 0.2142 |
| Total | 0.9818 | 1.1035 | 0.9980 |

- Overlap by session 142's definition (the mean of the three pairwise overlaps of the landscape sets): **0.733**,
  against 0.833 (session 142), 0.889 (session 147), 0.429 (session 135).
- **The reserves actually used:** research 87, 100.1 and 92 percent of 0.85 (passed once, by USD 0.0012);
  structure 72, 74 and 63 percent of 0.34.
- The runner's run: workflow run 37762358624 on main at `8614540`, 10:16 to 10:25 UTC, started by one dispatch
  through GitHub's API; its store was the bucket; 76 addresses requested, 65 holding text. It added one finished row
  to the runs table (in the internal list). **Run `20261006T193517Z-50a8be` and its PitchBook request: untouched.**

## Every pull against its ceiling

| Pull | Ceiling | Read |
|---|---|---|
| The pages the runs cite (the laptop's two runs) | 450 addresses a session, 150 a run | 58 addresses, 111 requests, 12.0 MB |
| The runner's run | 150 a run | 76 addresses |

- The fetcher's User-Agent is exactly "ERW research project, github.com/SamuelEnrique/erw"; robots.txt honoured.
- No request to misoenergy.org, PJM, pitchbook.com, crunchbase.com or harmonic.ai on either machine (4 crunchbase
  addresses were refused before any request). No connector was called.
- Vendor pages: the runner cited 12, 6 holding text; the laptop 7, 2 holding text.

## Model spend: USD 3.0834 of the USD 4.00 cap (stop at 3.70)

- Six calls, three runs; the plan was written before the first call; the stop stood before every stage; the
  runner's run had its own stop of USD 1.61. Nothing refused; no paid answer discarded.
- The six rows are in the main ledger (session 158: 3.083365).

## The landing

- **Phase 1** landed with session 155 as `task/155-158` (`22b1c34`): checks passed (run 37758726757), merged as
  `41c3115`. **Vercel's deployment of it failed** (the type error). The fix, `task/155-typefix` (`e715868`): checks
  passed (run 37761190030), merged as `8614540`; **Vercel: "Deployment has completed" at 10:14:56 UTC.**
- **Snapshot before the first push** (`155_before`, 09:43:57 UTC) **and after the fixed deployment** (`155b_after`,
  10:15:15 UTC): **6 differences, all on `/network`, all its own hourly refresh at 10:05 UTC**; no checked number
  moved (3,357 keys). Nothing was reverted.
- On production, in the internal view, the page's check passes 31 of 31.
- Phase 2 changed one internal method note; it lands with the chain's last landing.

## Checks

- `tests/test_session158.py` 58; the thesis tests 226; the whole suite in a clean copy of the phase 1 landing:
  2,292 tests, passed. Three assertions of `tests/test_session147.py` changed on purpose (Quaise Energy).

## Decisions made without you

1. The workflow's optional inputs and the run's state kept in the bucket.
2. The third run was the runner's, so that all three fit under the cap.
3. "A list of companies" is an enumeration of three or more capitalized names, or a list item that is the name alone.
4. Two remarks are the same when one's words are at least 90 percent the other's after the speaker's words are
   taken off (the measure is in the method note).

## The five most interesting numbers

1. **0.733, against 0.889 and 0.833**: lower, and for reasons outside the rule.
2. **0.889 to 1.0 and 0.733 to 0.833**: what your rulings alone do to the two earlier nights' answers.
3. **200 at 09:06, 403 at 10:22**: one publisher's answer to two machines, and a company's place on the map with it.
4. **1 point**: what Quaise Energy's one remark is worth once it is counted once.
5. **USD 0.0012**: by how much the research stage passed its reserve, once in three.
