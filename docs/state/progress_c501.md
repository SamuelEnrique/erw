# Progress of chain 501 (19 November 2026, lab-desktop, data machine, first window)

The chain: `queue/done/501-day-19-november-desktop-whole-country-data.md`. One line a landing, request, file, table or layer, with its state and session. A restarted session continues from the first line not marked done.

## Ground

| Part | Item | What | State | Session |
|---|---|---|---|---|
| ground | chain file | saved as pasted (`79e403523`) | done | 8000 |
| ground | resume file | `queue/next/510-resume-chain-501.md` (`645a3e185`); no other resume file of the data machine was in `queue/next/` | done | 8000 |
| ground | precheck | passed, on duty for "session 8000" | done | 8000 |

## Part A: the desk and the requests

| Part | Item | What | State | Session |
|---|---|---|---|---|
| A | landing requests | `landing_request_desktop_w3`, `_w4`, `_oldlaptop`, `_portable` on origin/main at 10:30 UTC: no row whose state begins "requested" (`runs/c501/desk_scan.py`); no `landing_request_window2.md` yet | nothing requested | 8000 |
| A | data requests | five rows still read "requested", none new: five_tools 2 (ruling on six tests, default off), five_tools 5 (done before chain 401), forecast 5 (comptroller.texas.gov robots refuses), licenses 11 and 12 (api.bls.gov robots disallows every path) | standing, not new | 8000 |

## Part B: the whole country's page data

| Part | Item | What | State | Session |
|---|---|---|---|---|
| B1 | contract | `docs/state/page_files_regions.md` (`733e7d3d5`, 10:30 UTC) | done | 8000 |
| B2 | ba_boundaries | HIFLD Control Areas from PASDA (71 polygons, 67 keyed through EIA-861 BA IDs), table 71 rows validated and archived, web file 979,100 bytes; DataLumos not read (robots name ClaudeBot), NASA mirror unreachable; branch `wip/c501-data` at `23760f290`, gate started 10:50 UTC | gating | 8000 |
