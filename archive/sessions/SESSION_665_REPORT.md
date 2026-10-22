# Session 665 report: the erw package against the Stanford draft

22 October 2026, from about 09:58 UTC, on lab-desktop (the data machine), a session of `queue/done/043-night-23-october-data-redivis-gaps.md`. Model spend USD 0.

## Read these first

- **The package's Redivis backend now opens the Stanford dataset**: `erw.RedivisBackend(owner="datapages", dataset="erw:b9wm", owner_kind="organization")`, or `ERW_REDIVIS_DATASET=datapages.erw:b9wm`. It listed the draft's 187 tables (the 186 public tables and the starter; the metadata tables are left out of the list) and read its version (`datapages.erw:b9wm:next`, unreleased, "not citable").
- **No row could be read.** Every read of rows (`fetch`, `coverage`, `cite`, which reads `erw_headers`) was refused by Redivis: "Cannot stream more than 100GB to external environments within a 30 day period. Please use the export API instead." The cap is the token's user's, reached on 15 October (session 305), so it frees on a rolling 30 days. `fetch`, `filter`, `cite` and `coverage` on the five tables are not proven against the draft.
- **The exact test for the day the cap frees** (or with another member's token): `package/tests/test_backends_stanford.py`, five public tables (one derived, one entities, one events, two series) against the local files: `ERW_REMOTE_TESTS=1 python -m pytest package/tests/test_backends_stanford.py -v -m remote`. Today all 11 skip with the cap's message as the reason.
- **`llms.txt`** names the Stanford dataset as a backend and gives its citation line with its DOI, `10.57761/4f55-6d55`.
- The chain asked for the package against a released version where only that is possible: the backend reads the draft (`version="next"`) as well as a released tag, so nothing waits on the click except the citation itself.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| Redivis API | 15 of 100 | the trial (9: the dataset, the table list, one refused read) and the remote tests' fixture (about 6: the same, refused) |

## Decisions made without you

- The Stanford test is a module of its own rather than a third parameter of `test_backends.py`: that file's events table, `news_index`, is unsettled by its ERW verdict and not in the Stanford dataset; `ercot_grid_notices` stands in.
- The package's default backend is unchanged (the owner's account), as the uploader's is.

## For Samuel's ruling

- Redivis's 30-day streaming cap on the token's user blocks every read of the Stanford draft from code. Ask Redivis or Datapages whether an organization's dataset can be read under the organization's allowance, or wait for the cap to roll off.

## Files

- Changed: `package/src/erw/remote.py`, `package/llms.txt`. New: `package/tests/test_backends_stanford.py`, this report. On the data machine only: `runs/s665/`.
