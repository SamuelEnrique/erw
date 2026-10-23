# Session 2300 report: the project map's figures keyed, with their source tips

23 October 2026, about 20:05 to 20:25 UTC, unattended, on portable-laptop (the code machine). Chain `queue/done/087-day-23-october-portable-map-tracker.md`, session 2300 (the chain file was written first by this session, committed alone, pushed to main at 20:12 UTC and taken by name). Model Fable 5.1. Precheck 0 (the machine was on duty for session 2200 already; it is on duty for this chain now). Model spend USD 0. No warehouse data written; no request but GitHub and the ERW's own database (the probe). Code in the worktree `C:\Users\samen\Documents\erw-2300` on `wip/2300-map-tracker`, cut from `origin/main` at `e1eaadf5`.

## Read these first

- **Every figure the project map computes now says where it comes from.** A figure summed in the browser from the page's own copy of the tables (`data/map.json`) cannot carry a check key the value checker reads back from the live set, so it carries `data-source="<tables>|<vintage>|<rule>"` (`site/lib/projectmap.ts`, `sourceOf`) and stands beside a hover tip (`Tip`, `components/tool/ToolPage.tsx`) with the same words: the tables, EIA's month or the queue's and the tracker's day, the copy's build day, and the rule (summed over the rows chosen; counted over the whole file; the row's own fields). The sentence's six figures, every total by status, every count and MW of "By technology", the rows not drawn, the unit count in the lead and the unit card's fields carry it. The one figure read from the live set, the unplaced queue positions, keeps its check key.
- **The Queues tab:** each of the three charts stands in a frame with `data-source` naming `iso_queue_statistics`, the ISO's own queue table and the variables drawn, and each chart's note now says so in words; the table "Every entry year" has a tip saying every figure is a row of the live set with its check key (the keys were there since session 349).
- **The Resources tab's seven counts** (operating units, planned units, queue rows drawn, counties, queue rows not drawn, facilities drawn, facilities not drawn) carry `data-source` with the layer's own vintage and a `title`; three of them had a hover note before, four had none.
- **Not built, not landed.** The database probe took 8.38 s (the gate needs under 3 s), so the chain's rule forbids a build this session; free memory was 0.8 GB at the start and 2.7 GB at the end. The gate's commands are under "To finish". Nothing of this session is on production.
- **The other session on this machine** is chain 086 (`wip/2200-explorers`, worktree `erw-2200`), on the three explorers; nothing of it was touched. The data machine has `task/2014-2027-data` in flight (and the leftover `task/198-battery-data`).

## What to review (on a build of `wip/2300-map-tracker`, in the internal view)

- `/map`: hover the small "i" after the summary sentence, after each totals heading ("Generating units, by EIA's status", "Queue positions...", "Datacenters..."), in the note under "The map", in the note of "By technology", and after the unit count in the lead: each names the tables, the vintage and the rule. In the page's HTML every figure of the sentence, every tile and every cell of the technology table carries `data-source`.
- `/map?tab=queues&iso=ercot`: under each chart, the note names `iso_queue_statistics` and `ercot_interconnection_queue`; the "i" after "Every entry year".
- `/map?tab=resources`: turn the plants, queue and datacenters layers on; hover each count under "What is built or planned".

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 2300"` | 0 | on duty |
| `node --import ./scripts/alias-register.mjs scripts/test-map-sources.mjs` (new, no browser) | 0 | 37 of 37: the tables and vintage of each kind on the file and on a fixture, the words, the components' attributes and tips, no em dash |
| `eslint app/map app/resources/ResourceMap.tsx lib/projectmap.ts` | 0 | clean |
| `tsc --noEmit` | 2 | 15 errors, every one pre-existing and outside this session's files (Next's generated `PageProps` and `LayoutProps`, and `content/*.json` that `prebuild` writes); none in the changed files |
| `scripts/db_probe.py` | 1 | 8.38 s for 1,000 rows: no build this session |
| `scripts/db_probe.py`, again at the end | 0 | open 2.60 s 1000 rows of iso_dam_hub_prices (free memory then 2454000 KB) |
| free memory | | 787,892 KB at the start; 2,698,748 KB after the tests |
| `scripts/check-map.mjs` (browser) | not run | extended with three checks (every figure carries `data-source` or a key; each `data-source` names a table of the file, a vintage and a rule; the five tips stand); runs under the gate |

## The landing

Not run: the probe said no build. The branch is pushed. Session 2301 stacks on `wip/2300-map-tracker` unless this branch has landed by then.

## Files

- `site/lib/projectmap.ts`: `SourceKind`, `SOURCE_RULE`, `sourceTables`, `sourceVintage`, `sourceOf`, `sourceWords`.
- `site/app/map/ProjectMap.tsx`, `page.tsx`, `QueueCharts.tsx` (an `iso` prop), `QueuesView.tsx`; `site/app/resources/ResourceMap.tsx` (seven attributes and four titles, nothing else).
- `site/scripts/test-map-sources.mjs` (new); `site/scripts/check-map.mjs` (three checks added to "opens").

## Decisions made without you

1. The browser-computed figures carry `data-source` and a tip rather than a check key: a key would be compared with the live set, which the page's copy lags by design (the copy is built from the tables; the live set can move after). The chain file says so; the choice is recorded here too.
2. The Resources tab's counts live in `site/app/resources/ResourceMap.tsx`, outside the chain's owned files; the chain says a figure there with no key and no tip gets one, so seven attributes and four `title` words were added and nothing else in that file changed.
3. The tip's words say "Nothing is read from the live set for this figure", so a reader does not take the copy for the live table.
4. The worktree has no `node_modules`; a directory junction to the main checkout's was made for the tests and the lint (not in git).
5. No build on a probe over 3 s, as the chain's rule says, although free memory had reached 2.7 GB by the end.

## For Samuel's ruling

- None from this session.

## To finish (the gate, on a machine with memory and a probe under 3 s)

From the main checkout, each its own command, its exit read: `.venv\Scripts\python.exe scripts\db_probe.py`; `.venv\Scripts\python.exe scripts\land_check.py --ref wip/2300-map-tracker --lock-as s2300 --port 3300`; then the commands it prints (freeze status, the snapshot before, the push to `task/2300-map-tracker`, the snapshot after, `compare`). If 2301 to 2304 stack on this branch, the last branch's gate carries this work and this one is not run on its own.
