# Session 1498 report: the On.Energy walkthrough, written and walked

Energy Research Warehouse (ERW), session 1498, chain 158, samueloldlaptop, 6 November 2026, 10:00 to 10:03 UTC. Model: Claude Opus 5.5 (this window's). Model spend USD 0. No warehouse data written; nothing sent or posted; web requests to the ERW's own database (the local build's reads) only. Branch `wip/1497-paths`.

## What it did, with commits

- `d09317471`: `docs/reviews/onenergy-walkthrough.md`, click by click, in the trader path's form, on the scope the owner's file of 5 November gives:
  - an ERCOT merchant battery, with foresight and on the day-ahead schedule (81.40 and 73.00 USD per kW);
  - a CAISO merchant battery (65.22);
  - scenario B with half its power contracted at USD 10 per kW-month, beside A, read from the page's own cells: ERCOT coverage 2.63 to 3.48 times, NPV -69.78 to -51.13 million, IRR -8.8 to 0.7 percent; CAISO coverage 1.91 to 3.12, NPV -80.19 to -56.34, IRR none to -0.8;
  - the saved comparison (the address holds both scenarios, and opened again it draws the same);
  - the two downloads (the months CSV: 5 lines of provenance and 107 more; the dispatch CSV: 4,266,963 bytes), with the replication of session 1487.
  - A screenshot a step (`docs/brand/review-1497/onenergy-*.png`); a feedback table for On.Energy.

## Found

- Every step loaded with no error; every scenario figure is the page's keyed cell; both downloads answer `text/csv`.

## Decisions made without you

- The scope is the owner's file's. The questions `trader-path.md` listed as needed before the walk are named at its head as still his: who at On.Energy walks it, how they see a page in review, and what may be shown under the hold.

## For Samuel's ruling

- Who at On.Energy walks it, and how they see the page: the internal view given to a person outside the project, or the battery page set live (rule 8's snapshot).
