# Session 159 report: the resource map finished, and the menu

Run on 8 October 2026 (UTC), unattended, the last session of the chain 155 to 159. An agent finished the map in a
working copy of its own to a written brief (`runs/session159/BRIEF.md`); I prepared the menu and did the landings.
`/resources` stays `review`.

## Five things to know first

- **The frame time is a headless figure, not a real-browser one.** The laptop's screen was locked all session; a
  visible window at 1366 by 768 was tried four times and drew no frame. Headless, on the laptop's own graphics, with
  all 18 on (14 layers, 4 overlays): **median 17.6 to 17.7 ms, 95th percentile 18.2 to 18.3 ms, longest 35.3 to
  52.3 ms, none over 100 ms.** With the screen on:
  `node scripts/frametime-resources.mjs http://localhost:3150 --size 1366x768 --only "nothing;all;nothing"`.
- **With everything on it was not smooth as first built** (95th percentile 52.9 to 70.5 ms, longest up to 125.5
  ms): the cost is the overlays at the widest view (30,921 plant marks), not the resource layers. The page now moves
  a heavy map as a picture of itself and redraws in full at rest. The agent's decision; the Method note says so.
- **Hydropower is on the map, in the form published, and the publisher is Oak Ridge National Laboratory, not
  USGS.** Two layers: non-powered dams as 2,616 points; new stream-reach development as the publisher's own totals
  by watershed. No form was filled and no name or e-mail sent.
- **Neither NYISO's nor MISO's queue rows are drawn, and nothing was loaded.** MISO reads "paused while terms are
  reviewed". NYISO's notice grants no license (session 149's reading), so its line reads "NYISO's terms do not
  allow it". **But both operators' queues already sit in the live set as tables of their own, readable with the
  public key** (`nyiso_interconnection_queue` 1,814 rows, `miso_interconnection_queue` 3,881), and the registry
  still says public for NYISO's. Not changed: yours to rule with the other NYISO tables.
- **The menu: adding `/demand` to Grid needed one entry moved.** Grid already held eight, the limit a test
  enforces. "Consumption" moves from Grid to Data. One line to change if you would rather move another.

## Verdict: the map is finished for what can be had; one thing waits for a person at the screen

1. The frame time in a visible window (the command above).
2. Your ruling on the two queue tables already in the live set.
3. NYISO's queue workbook has answered "202" with no file on all eight scheduled runs since 27 September: its
   rows in the warehouse are of before then.
4. A gross capacity factor layer needs a key tied to a person: not fetched, by your ruling; the greyed toggle's
   hover and the Method note say so.
5. No hub or zone is drawn; the Census ZIP shapes are not used, by your ruling.

## Hydropower

| Layer | Form | Unit | Count | Minimum, mean, maximum | Total |
|---|---|---|---|---|---|
| Non-powered dams | points | MW | 2,616 | 0.001, 1.506, 222.069 | 3,939 MW |
| New stream-reach development | the publisher's watersheds | MW | 2,027 of 15,401 watersheds hold a capacity | 1.000, 25.41, 922.2 | 51,515 MW |

- Nothing re-estimated, nothing spread over an area it was not published for.
- **The pull:** 6 files, 567 MB; the connector's ledger now stands at 1,135 MB of the 4 GB ceiling (26.4 percent).
  HEAD and GET only, the User-Agent "ERW research project, github.com/SamuelEnrique/erw".
- **Terms quoted:** "Data hosted on HydroSource is openly shared, without restriction, in accordance with
  Department of Energy's Public Access Plan."

## The queue overlay

- The live set's queue rows: 3,717 (ERCOT 1,758, SPP 1,023, CAISO 514, ISO-NE 422); 3,446 drawn in counties, 271
  not drawn (no county).
- Why the other two are absent from that table: the scheduled run skips MISO (paused), and NYISO's workbook
  request has answered "202" with no file since 27 September. Not a loader's filter and not a license.

## Every pull against its ceiling

| Pull | Ceiling | Read |
|---|---|---|
| Hydropower's published files | 4 GB for all resource layers | 567 MB (1,135 MB in all) |

- **No MISO request, no PJM request, no model spend, no form, no personal detail sent.**

## Model spend: none

## The landings

- **The map.** **Added after the landing.** Pushed with sessions 156, 157 and 159 as `task/156-157-159` (`bc1fba0`): checks passed (run
  37764344933), merged as `a161ec5`. **Vercel built it:** "Deployment has completed" at 10:43:19 UTC on 8 October.
- **Snapshot before** (`157_before`, 10:34:04 UTC) **and after** (`157_after`, 10:43:32 UTC): **0 differences** on the
  25 live addresses, 3,357 checked number keys. Nothing was reverted.
- **On production, in the internal view:** the policy page's check 45 of 45, the resource map's 97 of 97, the Ask
  panel's 13 of 13 (recorded answers).
- **The menu**, after 18:00 UTC: `wip/held-menu` (the Projects entry for `/resources`, Thesis Builder's move to
  Tools, `/demand` in Grid, Consumption's move to Data), then the removal of `REVIEW_FREEZE`, which you authorized;
  then production read as a visitor. Lines are added here.
- `wip/held-grid-network` is still held: you did not name it, and it lets the next daily run change what
  `/network` shows.

## Checks

- On the merged build: `check-resources` 97 of 97, twice (a first run showed 1 failure: a grid's finer level had
  not yet arrived under the pointer after the mouse wheel; the same check passed on the next two runs);
  `check-routes` 0 failed. `test-resources.mjs` 88; `tests/test_session159.py` 26.
- Two of session 153's test assertions changed, since the Ask panel reads the list of layers and the list grew.

## Decisions made without you

1. A heavy map moves as a picture of itself.
2. Consumption moved to Data.
3. The two queue tables in the live set left as they are.

## The five most interesting numbers

1. **51,515 MW**: the new stream-reach potential the publisher totals over 2,027 watersheds, against 3,939 MW at
   2,616 dams that have no powerhouse.
2. **30,921 plant marks**: what made the map slow with everything on, not the resource layers.
3. **17.7 ms**: the median frame with all 18 on, headless.
4. **3,881 and 1,814**: MISO's and NYISO's queue rows already in the live set as tables of their own.
5. **8 runs**: scheduled pulls of NYISO's queue workbook that have come back "202" with no file since 27 September.
