# Session 3782 report: ERCOT's four coincident peaks of summer 2026 (taken early, while the daily run holds the lock)

Energy Research Warehouse (ERW). Chain 212, data machine (lab-desktop), 12 November 2026 13:25 to 13:28 UTC. Opus 5.5. Model spend USD 0. Requests: 3 to www.ercot.com (cap 10), robots first in a call of its own; none to `/misapp` or `/misdownload` (ruling 2).

## Read these first

- **Not posted on an allowed page.** ERCOT's 2026 workbook (NP9-83-M, due by 1 December 2026) is not linked from any page ERCOT's robots file allows. The table `ercot_4cp_intervals` is unchanged, and the row waits.
- **The four peak intervals' node prices** stay "source needed" (ruling 2). Not a session.

## What it did

- `https://www.ercot.com/robots.txt` (200), read with comments stripped: `/misapp` and `/misdownload` are disallowed. `/mktinfo/` and `/mp/data-products/` are allowed. No crawl delay. Kept as `runs/c212/s3782/robots.txt`.
- `https://www.ercot.com/mktinfo/data_agg/4cp` (200, 53 KB). Its only file link is the 1996 to 2020 zip under `/files/docs/2022/01/13/`, already held. No 2026 file.
- `https://www.ercot.com/mp/data-products/data-product-details?id=NP9-83-M` (200, 64 KB). The page draws its file list in script from `IceDocListJsonWS` under `/misapp`, which is disallowed. No file link is in the page.
- `ercot_4cp.py --pull` was not run: its list is the `/misapp` servlet.

## Decisions made without you

- **No request to the list servlet,** although it is the only place the workbook is listed. Ruling 2 and the robots file both bar it.
- **Taken early:** this session needs no data lock, and the daily catch-up run held the lock. The chain's order is otherwise kept.

## For Samuel's ruling

- None new. The standing ones still apply: ruling 2's API key (api.ercot.com) would open NP9-83-M and the node prices. Recommendation: register for the free key. Default: the row waits for an allowed page, re-checked by the next data chain after 1 December.
