# Session 2304 report: the brand pass on the two pages, from the code; the screenshots wait for a build

23 October 2026, about 20:42 to 20:55 UTC, unattended, on portable-laptop (the code machine). Chain `queue/done/087-day-23-october-portable-map-tracker.md`, session 2304. Model Fable 5.1. Precheck 0. Model spend USD 0. No warehouse data written; no request but GitHub and the ERW's own database (the probe). Code in the worktree `C:\Users\samen\Documents\erw-2304` on `wip/2304-map-tracker`, stacked on `wip/2303-map-tracker`; the branch carries sessions 2300 to 2304.

## Read these first

- **The two pages were read against `docs/brand.md` sections 1 to 7, rule by rule, in their code**, and what departed was changed in the pages' own files; structure, density and every figure are as they were. The changes, each with the brand's line: (1) labels in sentence case without letter-spacing (section 1, "no capitals by style, no letter-spacing"): the map's totals headings, the tile labels, the panel's list summaries and group labels, "Size, MW"; (2) nothing smaller than 12 px (section 1, the scale): two 11 px labels of the map and the source line of its hover card are 12 px; (3) a field's and a control's edge in the captions grey, not the rule color (section 2): the map's size fields and Reset, the tracker's five filters, its MW field and its two buttons; (4) corners square (section 3, "the one radius is the mark's"): the color swatches of the map's key and technology table; (5) one dark rule under a table's header (section 4, rule 1): the facilities table's header, which had the light rule. No color is written as a hex value in either page; no shadow, gradient or legend box; the charts are the shared ones.
- **No screenshot was taken.** A build is needed for them and the chain's rule allows one here only on a probe under 3 s with the build lock free: the probe passed once (2.61 s at 20:42) and the build was started, but chain 088's session 2403 had taken the lock a minute before, so the start was stopped before any build ran (nothing built, nothing served); at the end of the session the lock was still held. The build, the before and after screenshots and the browser checks of 2303 are under "To finish", for session 2305's one build if the lock frees, else for a person. "Before" is production's internal view (`docs/brand/review-2304/before/`), "after" the build.
- **Two things the brand says that the shared components do not do** are not this chain's to change and go to the owner: the shared table's header is a cardinal band with white text (`ToolTable`, `components/tool/ToolPage.tsx`) where section 5 says "no colored header band"; and a section title is cardinal (`ToolSection`) where section 1 says "a section title is ink, not cardinal". Every page of the site draws them so; the two pages here do too.
- **The Resources tab** (`/map?tab=resources`) is the resources explorer's own component (`app/resources/ResourceMap.tsx`), outside this chain's files but for its counts' sources; it was not restyled.

## What to review (on a build of `wip/2304-map-tracker`, in the internal view)

- `/map`: the "Choose" panel's list labels ("Kind: all"), "Size, MW", the totals' headings and tile labels read in sentence case; the size fields and Reset have a grey edge; the key's color marks are square.
- `/datacenters`: the filters' edges are grey; the facilities table's header has an ink rule.

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 2304"` | 0 | on duty |
| the code scan (hex colors, `rounded`, `shadow`, legend, pixel sizes, off-token colors, bare tables) | | 0 hex, 2 round swatches (fixed), 0 shadows, 3 sizes under 12 px (fixed), 0 off-token colors; one bare `<table>` (the facilities table, its header rule fixed) |
| `eslint app/map app/datacenters` | 0 | clean |
| `test-map-sources.mjs`, `test-queue-sites.mjs` | 0, 0 | 43 of 43, 16 of 16 |
| `scripts/db_probe.py` | 0 then 1 | 2.61 s at 20:42 (the build was allowed and started); later probes in the table of the next report |
| `scripts/buildlock.py acquire s2304` | stopped | the lock held by `s2403` since 20:43:23 UTC; the command was stopped before its wait ran out, so no build ran without the lock |
| free memory | | 3,251,648 KB |
| `scripts/db_probe.py`, again at the report | 0 | open 2.58 s 1000 rows of iso_dam_hub_prices (free memory then 3139864 KB; build.lock held by s2403 since 2026-10-23T20:43:23Z (C:SERSSAMENDOCUMENTSERWUNSBUILD.LOCK)) |
| screenshots, `check-390.mjs`, `check-links.mjs`, `check-map.mjs`, `check-datacenters.mjs` | not run | no build |

## The landing

Not run. The branch is pushed and carries the stack. Session 2305 stacks on it and runs the one gate if the probe and the lock allow.

## Files

- `site/app/map/ProjectMap.tsx` (the labels, the fields, the swatches, the hover card's size), `site/app/datacenters/DatacentersTable.tsx` (the filters, the buttons, the header rule).

## Decisions made without you

1. The facilities table's header took the brand's ink rule (rule 1) rather than the shared table's cardinal band, since the brand text and the shared component disagree and the table was already plain; the disagreement itself is yours (below).
2. The label weight is 500 (`font-medium`), the brand's weight for a label, where the capitals were.
3. The background build command was stopped by hand when the lock was found held: its wait of five minutes would have ended with the build running unlocked (the command chained the steps with `;`). The next attempt chains them with `&&`.

## For Samuel's ruling

- The shared table's header band (`ToolTable`: cardinal with white text) against `docs/brand.md` section 5 ("no colored header band; the header is 12 px captions grey sans with rule 1 under it"), and the shared section title in cardinal (`ToolSection`) against section 1 ("a section title is ink, not cardinal"). Both are the site's shared components; a change is one file and moves every page.

## To finish (session 2305, or a person; each its own command, its exit read)

```
cd C:\Users\samen\Documents\erw
.venv\Scripts\python.exe scripts\db_probe.py                       (under 3 s)
.venv\Scripts\python.exe scripts\buildlock.py acquire s2304         (exit 0, else stop)
.venv\Scripts\python.exe scripts\duty.py beat
cd ..\erw-2304\site && npm run build                                (stopped after 30 minutes)
npx next start -p 3304                                              (in the background)
node scripts\screenshots.mjs https://erw-flame.vercel.app --only map,datacenters     (before: production, then copy to docs\brand\review-2304\before\)
node scripts\screenshots.mjs http://localhost:3304 --only map,datacenters            (after: copy to docs\brand\review-2304\after\)
node scripts\check-390.mjs http://localhost:3304 ..\..\erw\runs\s2304\390.json ..\..\erw\runs\s2304\shots --pages /map,/map?tab=queues,/map?tab=resources,/datacenters,/datacenters?view=grids
node scripts\check-links.mjs http://localhost:3304
node scripts\check-map.mjs http://localhost:3304
node scripts\check-datacenters.mjs http://localhost:3304
.venv\Scripts\python.exe scripts\buildlock.py release s2304
```

Then the gate: `land_check.py --ref wip/2304-map-tracker --lock-as s2304 --port 3304` (or `wip/2305-map-tracker` once the method notes are on it), the freeze status, the snapshot before, the push to `task/`, the snapshot after, `compare`.
