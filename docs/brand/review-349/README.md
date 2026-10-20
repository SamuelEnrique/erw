# Session 349: the project map, phase two

Shots of the local production build in the internal view, 20 October 2026, by `site/scripts/shot.mjs`, at 1280 and
390 px. Every checked number on the map's addresses matched Supabase (907 of 907 with `/impact`).

| File | Address | What it shows |
|---|---|---|
| `map-queues-caiso_1280.png`, `_390.png` | `/map?tab=queues` | the Queues tab: entered against operating, the share withdrawn and the median wait by entry year, and every year in a table |
| `map-queues-ercot_1280.png`, `_390.png` | `/map?tab=queues&iso=ercot` | a queue with no withdrawn positions held: the line that says so, no withdrawal chart |
| `map-projects_1280.png`, `_390.png` | `/map` | the Projects tab with the count of unplaced queue positions above the map |

The map itself draws `site/data/map.json` as committed: the positions the place gazetteers place appear once the data
machine's daily run has rebuilt `energy_projects` and the map's copy (its step `dm_project_map`, session 349).
The card's generator link is not shot (it needs a click on a unit). Impeccable was not run: not installed here.
