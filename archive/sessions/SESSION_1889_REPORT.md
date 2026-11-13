# Session 1889: the lab path and the On.Energy walkthrough written down (chain 217, 13 November 2026)

Energy Research Warehouse (ERW). Chain 217, session 1889, samueloldlaptop, unattended, Opus 5.5. About 00:40 to 00:50 UTC, beside session 1888's gate. Chain 214's second unfinished step: session 1885 walked the lab path and the On.Energy walkthrough on a local build (`runs/s1885/`) and wrote neither down. Written by an agent from 1885's own records only.

## What it did, with commits

- **`docs/reviews/lab-path.md`**, "Walked 13 November 2026 (session 1885)", 13 steps (`757193f63`). Session 1885's first walk misclicked steps 11 to 13 (its shots show the All grids tab); the section uses the second walk (`lab2-1280.json`) for them and says so. 1885 did not walk the old steps 2 (bought day-ahead) and 6 (`/ask`); said so.
- **`docs/reviews/onenergy-walkthrough.md`**, the same heading, 7 steps (same commit). The walk script could not type into the contract boxes at step 04, so its shots 04, 04b and 05 show B equal to A; the contract figures come from 1885's probes (`probe-contract2.out`, `probe-contract-caiso.out`): ERCOT B 3.48 times, USD -51.13 million, 0.7 percent, as on 6 November; CAISO B 3.14, -56.1, -0.7, the contract kept across the grid change.

## Faults found

- Lab 1: ERCOT's queue reads 298,606 MW on All grids (`iso_queue_snapshot_summary`, the figure of 6 November) against 1,159 positions and 308,488 MW on the tracker and the grid page. The data machine's.
- Lab 2: "The facilities against each grid" prints "license needed" in every grid's Peak hour MW and Capacity MW and in ERCOT's reserve margin, the grids' own public figures. Site code fix.
- Lab 3: `/grid`, the Lower 48's Net export card reads "by grid MW", words where the figure goes. Site code fix.
- Lab 4: the grid page's "In the news" hides the count ("license needed") then says "No story in the last 14 days matched". Site code fix.
- On.Energy 1: ERCOT's twelve months end September, CAISO's October, the year chart says "10 months": the trader path's fault 2 (session 1892 takes the site part).
- Noted, not called a fault: All grids' "2030 peak forecast +0.4 MW since the 2024 filing" for ERCOT.

## Decisions made without you

- The sections were written from 1885's records rather than walked again: the pages have not changed since its build except by the stack being landed.
- Lab faults 2 to 4 join this chain's fault sessions after the periodicals rows.

## For Samuel's ruling

- None new.
