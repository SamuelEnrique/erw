# Session 1049 report: a node on a map, at the county's resolution, designed

23 October 2026, about 08:00 UTC, on samueloldlaptop, unattended, on `wip/1042-allgrids`. Chain `queue/done/072-day-23-october-code-allgrids-packages-2.md`, session 1049. Model spend USD 0. No request; no site build (a headless browser drew the frame from a local file).

## Read these first

- **A node can be drawn only at the county's resolution, as a count.** `ercot_node_places` gives 569 nodes a county, never a point, and no table holds a settlement point's coordinates or bus (`ercot_settlement_points` and `hifld_substations` have not landed). A dot at a county's centre would be a guess.
- **The design**: `docs/reviews/siting-map-design.md`, with one frame, `docs/brand/review-1049/frame_counties_1280.png` and `frame_counties_390.png` (and the SVG). Texas's counties are shaded by the count of placed nodes (148 counties, every one matched to a us-atlas shape; the most, 25, in Harris); the 304 unplaced nodes are counted and not drawn. Not wired: the map is a ruling of its own.
- At 390 the SVG's own text is too small; a wired map would put its words in the page's HTML.

## What to review

1. `docs/brand/review-1049/frame_counties_1280.png`.
2. `docs/reviews/siting-map-design.md`, "For Samuel's ruling".

## Checks

| Check | Exit | Result |
|---|---|---|
| `docs/brand/review-1049/frame1049.mjs` | 0 | 148 of 148 counties shaded, 0 unmatched |

## The landing

Lands with the next landing of this chain (documents only).

## Decisions made without you

1. **A county shaded by count, never a point**: the chain's rule (nothing placed by a guess).
2. **Counties outside ERCOT are drawn unshaded** in the frame, and the frame says so; greying them needs a ruling (below).

## For Samuel's ruling

- Whether to wire the county map, and where (the design proposes above the node list, folded).
- Whether counties outside ERCOT are greyed from `utility_service_territories`.

## Files

- New: `docs/reviews/siting-map-design.md`, `docs/brand/review-1049/` (two PNGs, the SVG, the script), this report.
