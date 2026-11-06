# Session 1491 report: the datacenter's replication, in Python; one figure the page and the file do not share

Energy Research Warehouse (ERW), session 1491, chain 158, samueloldlaptop, 6 November 2026, 08:58 to 09:10 UTC. Model: Claude Opus 5.5 (this window's). Model spend USD 0. No warehouse data written; nothing sent or posted; web requests to the ERW's own database (a local build's reads) only. Branch `wip/1487-replication`.

## What it did, with commits

- `071180721`: `replication/datacenter/`, in the form of the battery's and the generator's. `replicate.py` reads only the page's two public files (`site/public/datacenter/erw_2026_datacenter_hourly.csv` and `erw_2026_datacenter_carbon.csv`, exported 5 November: LZ_NORTH, a flat load in real time, the last twelve months 2025-11 to 2026-10) and `assumptions.json` (size, 1.3 kW a GPU, an overhead ratio of 1.56). It recomputes with the page's published mirror and prints each figure beside the page's.
- **The page's figures were read from a local build of main** (`next start` of the main copy's build of 08:35 UTC on port 3891, the internal view; `runs/s1487/cop.html`). Session 582's reading of 22 October was for the file as it then stood, and the file was exported again on 5 November.
- Tests: `tests/test_session1491.py`. Every figure is inside its tolerance but the one named; the script exits 0. A changed overhead ratio moves the GPU-hour and not the energy price. The assumptions equal the mirror's defaults.

## Found

- **13 of 14**: USD 34.07 per MWh over the last twelve months (29,841,981 for 100 MW), 0.0691 a GPU-hour, 49,310 GPUs, 35.70 bought day-ahead, a bad month of 37.88 (August 2026), 4 hours at or above USD 1,000 (446,175 paid in them), 300.38 kg CO2 per MWh (263,102 tonnes), the years 2016 (21.68) and 2021 (150.61).
- **One difference, open**: a flat load's carbon over the hourly window (10,160 hours, 2025-08-26 16:00 to 2026-10-27 23:00 UTC in both). The mirror on the public file computes 309.84 kg CO2 per MWh; the page prints 311.68, the same figure it prints for the grid's mean beside it (`co2:window:grid`). The twelve-month figure, from the monthly intensities, agrees. Two readings fit: the live hourly intensity was revised after the file's export, or the page's flat-load figure is the grid's mean under another name. Not settled here. `page_figures.json` names it as a known difference, so the run says so and still exits 0, and it is in chain 158's faults (the note) for the next chain.

## Decisions made without you

- The page's figures were read from a local build in the internal view, not production (the snapshots are the chain's only touch of production).

## For Samuel's ruling

- None (the difference is a fault for the next chain to settle, not a ruling).
