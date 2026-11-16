# Session 7006 report: the policy monitor's replication mirror (goal 4) and what it found

Energy Research Warehouse (ERW). Chain 301, data machine (lab-desktop), 16 November 2026. Opus 5.5. Model spend USD 0. No request made.

- **`replication/policy/replicate.py`**, from `docs/methods/policy_monitor.md` section 16 and `policy_actions` alone: the documents regrouped into records by the method's words (the proceeding ids, the same-day RIN split, a repeat of a title within 45 days), then for each of the 1,523 records of `monitor.json`: its documents, count, dates, body, title, instrument, status, significance and its document's sector, every step, the next step, the figure, the sources, the plain read's and the significance's documents.
- **First run: 23,069 of 23,129 equal** (after my labels for the next step were set to the file's words). The 60 differences were all on **27 DOE releases kept from earlier runs that carry no fields in the table**: the monitor's builder derived their instrument, status and figure as it built the file, so the page showed values that are in no table. **Policy faults row 32**, fixed at the cause: `policy_sources.fill_bare` reads a kept row's fields from its own row before the write (test 7006). The table is rewritten by the next pull, after which the replication reads N of N; that pull waits for the data lock (the price days' fill holds it) and is in session 7004's report.
- **`replication/policy/replicate.do`**: five document counts (2,063 documents; 1,401 with a dated step; 959 FERC; 404 of significance 5 or more; 1,064 comment deadlines), expected values at its top.
- **The method note** gains the replication and the monitor as it now stands (`plain_doc`, `significance_doc`, 1,033 records with steps).

## Commits (on `wip/c301-data`)

- The replication, `fill_bare`, test 7006 (3 tests, the grouping's rules among them); row 32 added to `docs/reviews/policy-faults-2026-11-11.md` (first numbered 26 in a commit message; the code and test say 32).

## Decisions made without you

- **The next step's words** are the page's (the file's), since the method names the kinds and not their words.

## For Samuel's ruling

- None new.
