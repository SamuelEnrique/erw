# Session 7405 report: the deal tracker's method note and its decisions block

Energy Research Warehouse (ERW). Chain 303, portable-laptop, 16 November 2026, about 09:56 to 10:05 UTC. Model spend: USD 0.

## What was done

- **Checked first:** `docs/methods/deal_tracker.md` was on no branch of origin. `/deals` carries session 465's list of seventeen choices with their sessions, in another form than the five tools': it is kept.
- **The note** (`docs/methods/deal_tracker.md`): the views; what a deal is and is not; how two stories of one deal become one row (the extraction, the code's rule, the register) and what each view does with a folded pair; how megawatts, US dollars and a price are read and when they are empty; how a deal is tagged AI power, and what the tag does not say; the grid; every figure view by view, with how many deals each median rests on; what "Sure" means; what the tracker cannot see; the replication; what a second reading of the older rows would change; the decisions; what waits for you; the sign-off block. Its figures are held to the day's by a test.
- **Thirteen decisions** (`site/lib/decisions.ts`, `DEAL_TRACKER_DECISIONS`), each with its default and its source on hover, drawn by the shared block above session 465's list, under every tab and under the hold. The note carries the list word for word.
- **Tests.** `tests/test_session7405_trackers.py` (with session 7406's): 12 pass. The decisions tests of sessions 462, 463, 465 and 5001: pass. Type check: 0 diagnostics.

## A finding the note states plainly

- **"A deal is energy's where its asset is energy" is written in no prompt and no rubric.** The chain's prompt and the faults file name it as the rule. The extraction is asked for "energy transactions", and its list of what is not a deal has no line for an asset that is not energy. So the table holds funding rounds and purchases of AI and cloud companies, chip contracts and fund raises, most tagged AI power, and a second reading with the stricter prompt as it stands would not take them out. The note says so (section 2); a test fails the day the rule is written, so the note is changed with it.

## Needs the key

- **The second reading of the 529 rows extracted before 6 November** (the method note, section 10). By this session's reading of their stories' titles (a word search, then every candidate line read by eye; no model):
  - about 22 are a plan, a pledge, a seeking, one-sided talks or a permission, which the stricter prompt's own list would not return;
  - about 51 are not energy's, and would leave only if that rule is written into the prompt first;
  - about 4 would change kind (compute contracts typed as an offtake or as other);
  - about 19 cannot be told from a title; about 433 stand.
  - **Estimated cost:** USD 3.0 to read again the 814 stories behind the 529 rows, or USD 10.6 for `--reextract` of all 2,899 stories the deals extraction has checked, at USD 0.00365 a story (the median of the step's last nine runs in `run_status.csv`). Not run.

## For Samuel's ruling

- **Whether the energy-asset rule is written into the extraction's prompt** before the second reading (faults row 28). Default: not written.
- **Whether a folded pair carries over a figure only the folded row states** (faults row 23: 433 MW of the loan to Vistra is in no sum). Default: the row kept stands as extracted.

## Decisions made without you

- Two blocks stand at the foot of `/deals`: the new one (the choices that move the figures, with default and source) and session 465's (every choice with its session), retitled "Every choice, with the session that made it". Not seen in a browser: no build on this laptop.
- The counts of section 10 are "about": they come from titles, not from a second extraction.

## Commit

- `wip/7400-trackers`: this session's commit, named in the progress file.
