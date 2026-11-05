# The datacenter tracker's rows, sorted by who stands behind them: 23 October 2026

Energy Research Warehouse (ERW), session 827 (chain `queue/done/080-night-23-october-portable-landing-deals-.md`, portable-laptop). The same sort as the deals' (`docs/reviews/deals-public-rows-2026-10-23.md`, `warehouse/deals/public_rows.py`), run on `datacenter_projects` (150 rows, extracted 2026-10-22T15:02:50Z) and `datacenter_projects_evidence` (168 rows, the same run), with `datacenter_queue_positions` (3 rows) and `datacenter_facilities` (426 rows) read for the power side. Every figure is `public_rows.py --datacenters` and a count over the files as `scripts/sync.py --check` found them current. No row changed; no request.

## Read these first

- **No row of `datacenter_projects` can be shown: 0 shown, 150 held, 0 unsettled.** Every one of its 168 evidence rows comes from a publisher whose terms ask for permission; no row rests on an operator's own announcement, a utility's or an ISO's filing, or an outlet whose terms read as public, because the tracker's feeds are news feeds and none of them is public (World Nuclear News, the one public outlet of the deals' feeds, reports no datacenter).
- **The power side already draws what is public.** Session 467's section on `/datacenters` reads the interconnection-queue positions that name a datacenter or a large load from each ISO's own queue table (`datacenter_queue_positions`: 2 of 3 from ERCOT, whose terms read as public; 1 from NYISO, whose terms ask), never from the held table. Those are the rows a public source stands behind, and they are drawn with their power-side fields only (the grid, the county, the queue's MW, the point of interconnection, the queue's status and dates). Nothing of this session changes them.
- **`datacenter_facilities` (426 rows) is held whole and stays so**: 275 rows are the nine operators' own site lists, which `docs/licenses.md` gives the verdict "needs written permission" (session 441's variant B would show them if the owner rules a company's own list public); 148 are news rows, every one on a publisher who asks; 3 are the queue rows above.
- **What this session adds on the page**: the line that counts the three sorts for the projects table, each count a check key (`dcpub|counts|shown`, `|held`, `|unsettled`; `check-values` reads the live set's row count of `datacenter_projects` against the file), in place of the whole-table words, and the method note's section (session 828). No figure is drawn from a held row.

## The counts

| Table | Rows | Shown | Held | Unsettled | Why |
|---|---|---|---|---|---|
| `datacenter_projects` | 150 | 0 | 150 | 0 | 168 evidence rows, every publisher asks for permission |
| `datacenter_queue_positions` | 3 | 2 | 1 | 0 | ERCOT's queue (public) and NYISO's (asks); drawn by the power side since session 467 |
| `datacenter_facilities` | 426 | 2 | 424 | 0 | the two ERCOT queue rows; 275 operator-site rows and 148 news rows ask (session 441's count, unchanged in kind) |

## The publishers behind the held projects

| Publisher | Verdict | Evidence rows |
|---|---|---|
| Data Center Dynamics | needs written permission | 81 |
| Reuters | needs written permission | 41 |
| Bloomberg | needs written permission | 17 |
| WSJ | needs written permission | 10 |
| Hart Energy | needs written permission | 4 |
| Heatmap News | needs written permission | 3 |
| Financial Times | needs written permission | 3 |
| Data Center Knowledge | needs written permission | 2 |
| Data Center Frontier | needs written permission | 2 |
| Latitude Media | needs written permission | 2 |
| OilPrice.com, POWER Magazine, Natural Gas Intelligence | needs written permission | 1 each |

## The shown rows and their power-side fields

None of `datacenter_projects`. The two public queue positions, as the power side draws them from the queue tables (not from this sort): `ercot_queue:25INR0688` (Giga Texas Data Center, Texas, 133 MW of generation or storage asked to connect, not the load) and `ercot_queue:28INR0499` (Alpha Digital Campus Combined-cycle and Co-located Load, Texas, 58.26 MW). The NYISO position (`nyiso_queue:1630`, Suffern Quarry Data Center) is held with its grid's queue.

## What would change the count

- **A ruling that an operator's own site list is public** (session 441's variant B): 275 operator-site rows of `datacenter_facilities` (15 with MW, 4,799 MW) become shown; nothing of `datacenter_projects` moves.
- **A filing source for the projects**: the utilities' large-load filings and the ISOs' queues already name sites (`large_load_statements`, the queue tables); joining a project to its queue position by operator and county would give it a public evidence row. That is the desktop's data chain (`deals-gaps-2026-10-23.md`, source 3).

## Decisions made without you (session 827)

- The sort is the deals' reader with the table's id columns (`entity_id`, `facility_id`), so the two trackers share one rule and one test.
- With no shown row, the page's change is the counting line and its keys; the power side's public rows are session 467's and were not redrawn.
- `datacenter_facilities` is not re-sorted row by row here: its members' publishers are session 441's method, and its count above is that review's, restated by kind.

## For Samuel's ruling

- Whether an operator's own site list is a public source (the nine operators' pages, each "needs written permission" by its sentence in `docs/licenses.md`).
