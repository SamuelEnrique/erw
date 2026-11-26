# Session 10213 report: the interconnection queue audited as a hostile expert would

Chain 710, part D, the old laptop, 26 November 2026. Worktree `erw-c710-c`, branch `wip/audit-queues-doc`. Model spend USD 0; no request to any service; no table written; no lock taken.

## What was done

- `docs/reviews/queues-model-audit-2026-11-26.md` and its evidence folder: the ground, the arithmetic re-done, one rule at a time, each claim against the code, an expert's own number, six findings.
- The arithmetic is right: an independent restatement (standard library, from the method note) equals all 17,246 values of the page's 76 views and 312 of the 315 keyed default-view numbers; the other three are one MW high from rounding twice (finding 6).
- Findings: 1 Medium (a hybrid's "both parts" holds only in CAISO and part of the West: CAISO's active MW 32.1 percent above a like count), 4 Low (the US solar-with-storage share unmarked; "recent years mostly open"; "the most entered in"; each grid's dates), 1 Very low (two small figures).
- Seven branches: five words (`wip/audit-queues-1`, `-3`, `-4`, `-5`, `-6`), each drawn with the site's own code and read (pass), tests passing on the five merged; two figure tests not for landing (`-2`, `-7`).

## Decisions made without you

- Berkeley Lab's rows were read from the main copy's `warehouse/output/` (read only); the tests that need them read `ERW_LBNL_CSV` or the warehouse's path and skip where neither exists.
- The operators' own MISO and NYISO queue tables are held ("license needed"), so they were not read; their check is a data request.
- Finding 2's hover reuses the builder's own sentence with " (above)" removed, so the words stay the file's.
- The "as at 31 December 2025" figure of finding 5 was measured (+0.7 percent) and given no branch, as the tracker audit did for its finding 5.

## For Samuel's ruling (default "left as it is" for each)

- Hybrids at their largest part everywhere (`wip/audit-queues-2`): CAISO's active MW 190,717 to 129,435 (-32.1 percent); the US 1,864,963 to 1,749,315 (-6.2).
- MW rounded once, and the places page counting a negative capacity as zero (`wip/audit-queues-7`): three default-view cells one MW lower; TVA's withdrawn MW +75.
- Statuses as at 31 December 2025 (no branch): up to 8,566 active requests, 1,878,238 MW (+0.7 percent).

## Needs the key

- Nothing.
