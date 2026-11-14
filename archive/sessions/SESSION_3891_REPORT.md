# Session 3891 report: check-values on the Digests of 13 and 14 November

Energy Research Warehouse (ERW). Chain 227, data machine (lab-desktop), 13 November 2026 18:20 to 18:50 UTC. Opus 5.5. Model spend USD 0.

## The Digest of 13 November: written, emailed, not on main

- The daily run wrote `docs/digest/2026-11-13.md` at 16:09 UTC (172 stories, 166 clusters; its model calls cost USD 0.0296, within the day's USD 1.50: USD 0.71 spent by then in 26 calls). The run's `news_email` step ran.
- **The daily commit that carried it was refused** by the push guard (test 3703, fixed by session 3888 and landed at `64bdab7c7`), so the issue is not in `docs/digest/` on main and `/digest` cannot show it. The run's artifact holds only `daily.log` and `runs/`, so the file cannot be recovered from it.
- `docs/digest/` on main holds the issues of 6 and 12 November only. The issues of Monday 9, Tuesday 10 and Wednesday 11 November are missing the same way: those days' daily commits were refused (the merge tests' failures that chains 212 to 221 fixed).
- **Not re-run.** A second daily run would spend the model budget again and email the Digest a second time. The run of 14 November writes its own issue onto main, now that the guard's three faults are fixed.

## The Digest of 12 November: EIA's restated demand hour

- Every gate since the run of 13 November failed check-values on `/digest/2026-11-12`: the issue printed US48 demand at 11 November 23:00 UTC as 488,034 MW, and the live set holds EIA's restated 488,341 (loaded at 16:01). The gate of `wip/w2-land-e` at 16:43 met the same line.
- **The owner's ruling of 23 October (session 2207):** a stored issue keeps the figure it printed, and the page says the warehouse's newer value in one line under the numbers. The page did so only for EIA's fuel closes, and check-values read such a note as a pass only for the day-ahead, real-time and fuel keys.
- **The fix, made twice:** this session made it (the page's revisions read the demand line's hour, the note words it as EIA's demand in whole MW, check-values reads a `digest_demand` note as a pass; a test on the real issue of 12 November), and so did the desktop's second window in its session 4009, which landed first (`1773e7c7d`). This chain's third gate found the conflict at its merge and stopped; this session's commit was reverted (`771ca82eb`) and main's version kept. Nothing of it remains on this chain's branch.

## The Digest of 14 November

- Not yet written (the run of 14 November is at 14:00 UTC tomorrow). Carried to the next file.

## Decisions made without you

- **The daily run was not re-run** for the lost issue of 13 November.
- **The second window's fix kept, this session's reverted:** the two did the same thing; one copy is enough.

## For Samuel's ruling

- **The Digests the refused commits lost** (9, 10, 11 and 13 November). Default: left lost (the run's email step ran on 13 November; the other days' were not read). A run that writes an issue could commit it alone before the guard's suite, if the owner wants issues kept when the rest of a day's commit is refused.
