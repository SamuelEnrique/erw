# Session 147 report: Thesis Builder, the evidence pages

Run on 7 October 2026 (UTC), unattended, in the chain 146 to 149. An agent built it in a working copy of its own to a
written brief (`runs/session147/BRIEF.md`); I checked its spend in the ledger and the landing myself. No page changed.

## Four things to know first

- **The overlap is 0.889, against last night's 0.833** (landscapes of 5, 5 and 6 companies; pairs 1.0, 0.833, 0.833).
  Session 135: 0.429.
- **The one difference is a false match, by the name matching you told me not to touch.** Run 3 first named a
  company called "Geothermal Technologies" (geothermal.tech). The rule tied it through two sentences about geothermal
  technologies in general (ctvc.co, energycapitalhtx.com). Without it: the same five companies in the same order,
  three times (1.0). Written as a test, not changed.
- **0.889 against 0.833 is not a clean win for the pages, and should not be read as one.** Tonight's same paid
  answers read by last night's rule (quotations) give 5, 5, 5 (1.0). Last night's answers read by tonight's rule
  give 3, 5, 5 (0.733). Three runs cannot rank the two. What the pages do change: each run read alone, with no
  store behind it, gives 0.756 by pages against 0.417 by quotations, on the same answers.
- **The figures are the three paid answers read through the final code.** After run 1 the page reader was extended
  once (a page drawn by JavaScript shows only menus to a plain request; its own description and structured data are
  now read). Saved bytes were read again, with no new request. Run 1 as executed printed landscape 4, pipeline 2.

## Verdict: not ready to open. What is left, exactly

1. **Your ruling on the name matching.** A name made of the niche's own words matches running text. Pages multiply
   the sentences (6,477 against 38 quotations), so this gap now decides who is on the map.
2. **Near-duplicate sentences count twice.** Quaise Energy is on the landscape by one remark of its chief executive
   printed on two pages.
3. **The runner has not run the new code.** Nothing is missing there (below); untested until a run after landing.
4. **Stage reserves.** The landscape research cost USD 0.98 against a reserve of 0.85; a full run's stop of 2.00 is
   tighter than report 142 said.
5. **Data vendors' public pages** (cbinsights 3, dealroom 2, sacra 1) hold text and were read: refuse them or not.
6. **A page that fails on a later day holds no sentence that day**, so a company can drop on a bad day. Literal to
   your instruction; yours to rule.
7. Unchanged from report 142: the thresholds; a full run writes its trends anew; facts are the model's reading; the
   PitchBook stage.

## What was built

- **The fetch, in code** (`warehouse/thesis/pages.py`): every address a run's rows cite, one plain request each,
  the page text saved with its hash, day, status and bytes. Ceilings checked before each request.
- **The rule reads the saved sentences** (`tie.py`): the web tier scores the sentences of a saved page that name the
  company. A quotation decides nothing. Every point, threshold, tie, tie-break and the dedupe: unchanged.
- **The store is a bucket object** (`store.py`): private bucket `erw-thesis`, created tonight with one call; one
  object a niche, stage and geography; the previous version copied to a dated name before each replacement (4
  copies tonight). The local file remains the fallback where no key is set. All three runs used the bucket.
- **The runner needs nothing it lacks.** `thesis.yml` already has the two secrets; the bucket exists.
- **Report 142 was wrong on one point:** `energy_companies` and `energy_deals` are in git, so the runner does read
  the warehouse tier. A test now asserts both are tracked.
- `docs/methods/thesis_builder.md` (internal) is brought up to date. No string a user reads changed.

## The three runs side by side

Geothermal mapping and sensing, startups, United States; the five trends held fixed as in session 142; from an
empty store, like for like with 0.833.

| | Run 1 | Run 2 | Run 3 | In all | In any | Overlap | Session 142 | Session 135 |
|---|---|---|---|---|---|---|---|---|
| Found | 28 | 37 | 38 | 28 | 39 | 0.806 | 0.738 | 0.697 |
| Fits stage and geography | 10 | 14 | 15 | | | | | |
| On the landscape | 5 | 5 | 6 | 5 | 6 | **0.889** | 0.833 | 0.429 |
| On the pipeline map | 3 | 4 | 5 | 3 | 5 | 0.717 | 0.667 | 0.402 |

- Landscape, runs 1 and 2: Zanskar Geothermal & Minerals, Thermofilic, Geothermal Radar, Quaise Energy, XGS Energy.
  Run 3: those five and Geothermal Technologies.
- Overlap: the mean of the three pairwise Jaccard overlaps of the landscape sets, session 142's definition.
- Starting instead from the store session 142 kept: the same landscapes, 0.889.
- **Every difference has a recorded cause:** a page that changed, 0; a page refused, 0; the model cited a different
  page, 2 (Thermofilic moved to the pipeline map; one company moved from private to fits); the model named a new
  organisation, 10, of which 1 reached the landscape.
- Both nights end on the same five companies once their pages are held.

## Every pull against its ceiling

| Pull | Ceiling | Read |
|---|---|---|
| The pages the runs cite | 450 addresses in the session; 150 a run; 2 MB a page | **92 addresses** (20 percent); largest run 46; 179 requests, 81 of them robots.txt; 19.6 MB |

- Of the 75 addresses the three runs cite: 55 hold text; 9 answered 403; 3 disallowed by robots.txt; 7 behind a
  robots.txt that could not be read (treated as closed); 1 truncated at 2 MB (holds no sentence).
- **Contact string: exactly "ERW research project, github.com/SamuelEnrique/erw", in every request. No address.**
- **No MISO request** (one such address was offered in a trial and refused before any request). No PJM address
  cited. No PitchBook address cited or requested, no PitchBook call. Run `20261006T193517Z-50a8be`: untouched.
- **To flag: four crunchbase.com addresses were requested once each** (each answered 403, nothing received) before
  the agent added a refusal of licensed databases' sites (pitchbook.com, crunchbase.com, harmonic.ai).
- **robots.txt is honoured: my addition, not your instruction.** It closed 10 of 75 addresses.
- Terms: hundreds of publishers, not read one by one; the method note states what is fetched and how. The saved
  texts are in the private bucket only; the public repository holds 22 short excerpts as a test fixture.

## Model spend: USD 3.2984 of the USD 6.00 cap (stop at 5.50)

| Run | Research | Structure | Total |
|---|---|---|---|
| 1 | 0.9810 | 0.2439 | 1.2249 |
| 2 | 0.8463 | 0.2494 | 1.0957 |
| 3 | 0.7812 | 0.1966 | 0.9778 |
| **All** (6 calls, session 147 in the ledger: 3.298394) | | | **3.2984** |

- Nothing refused; no paid answer discarded; no other model call. Two stops stood before every stage.
- The six rows were written to the main ledger under the lock (`api_cost_ledger` 2,759 rows).

## The landing

- **Not landed when this was written.** `REVIEW_FREEZE` reads frozen through 7 October (UTC); it ends by its own
  dates at 00:00 UTC. The landing follows then, with the snapshot before and after, and a line is added here.
- Nothing a live page shows or reads is touched: no site file, no table but the ledger.

## Checks

- `tests/test_session147.py`: 65 passed (a MISO address and a disallowed address refused before any request; the
  ceiling stops before the request that would pass it; a truncated or refused page yields no sentence; the same
  saved pages give the same landscape under shuffles; the exact User-Agent; the bucket against a fake transport).
- `tests/test_session142.py` and `test_session135.py`: 71 passed; three assertions of 142 changed on purpose (the
  web tier's source of sentences).
- The whole suite in the working copy: 1,672 passed, exit 0. The clean-copy run is made at the landing.

## Decisions made without you

1. robots.txt honoured, and an unreadable robots.txt closes the host.
2. "The addresses a run cites" are those its rows cite, not every search result.
3. A bucket of its own (`erw-thesis`), not a prefix of the archive's.
4. The empty start is the main reading (like for like with session 142).
5. Runs 2 and 3 ran with a run stop of USD 1.80, since run 1's research passed its reserve; the reserves in code are
   unchanged.
6. The sites of three licensed databases are refused before any request.

## The five most interesting numbers

1. **0.889 against 0.833 and 0.429**, and 1.0 but for one false match of a company's name.
2. **0.756 against 0.417**: each run alone, by pages and by quotations, on the same paid answers.
3. **31 of 31**: every quotation whose page could be fetched is on the saved page word for word.
4. **55 of 75**: cited addresses that hold text after one plain request.
5. **6,477 sentences against 38 quotations**: what the rule now reads; 719 of them name a company.
