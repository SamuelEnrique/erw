# A node on a map: the design, not wired

Session 1049 (chain 072, `queue/done/072-day-23-october-code-allgrids-packages-2.md`), 23 October 2026. Open items line 21 of `docs/reviews/siting-open-2026-10-23.md`: whether an ERCOT node of the All grids tab can be drawn on a map, now that session 1048 gives 569 of the 873 nodes a county and a load zone (`ercot_node_places`, public). The map is a ruling of its own: nothing here is on the site.

## What can be drawn without a guess

- **A county, shaded by the count of nodes placed in it.** `ercot_node_places` gives a node's county, never a point. A county's shade is a count of nodes, a fact of the table, and says nothing about where in the county a node is. 148 counties hold a placed node; every one matched a county shape of us-atlas (`counties-10m.json`, the site's own dependency, the Census Bureau's cartographic boundaries) by its name. The most in one county: 25 (Harris).
- **A load zone, by its counties.** Each placed node has one of ERCOT's six load zones; a county's nodes all have the same zone where the table places them. A zone outline could be drawn as the union of its placed counties' shapes, labelled "the counties of the zone's placed nodes", never as ERCOT's zone boundary, which no table of the warehouse holds.

## What cannot be drawn

- **A node as a point.** No table holds a settlement point's latitude and longitude, or its electrical bus. A dot at the county's centre would say the node is there, which is a guess. What would place one: `ercot_settlement_points` with its bus, and `hifld_substations` (neither landed, session 1046) to put the bus at its substation's coordinates.
- **The 304 nodes the table does not place** (295 with no CDR unit at their station, 9 whose units disagree): not drawn, and counted on the map's own line.
- **Lines and substations near a node**: `hifld_transmission_lines` and `hifld_substations` have not landed.
- **ERCOT's transmission projects by place**: `ercot_transmission_projects` gives counties, not coordinates; a county's count of project phases could be a second shade or a figure in the county's tip, not a line on the map.

## The design (one frame)

`docs/brand/review-1049/frame_counties_1280.png` and `frame_counties_390.png` (with `frame_counties.svg`), drawn by `docs/brand/review-1049/frame1049.mjs` (`node frame1049.mjs <site-dir> <out-dir>`) (d3-geo's Albers projection on us-atlas, the counties of Texas; the node file `site/data/siting/nodes.json` as session 1048 wrote it):

- Texas's counties, white for none placed and six steps of the brand's blue for 1 to 2, 3 to 5, 6 to 10, 11 to 20 and 21 or more nodes. Counties outside ERCOT (the Panhandle's north, El Paso, the northeast) are drawn unshaded, as "none placed"; a wired map would grey them as "not ERCOT" from a table that says which counties ERCOT serves (none held: `utility_service_territories` gives a county's utilities by balancing authority, which session 719 already reads, and could).
- The title, the count line ("569 of 873 resource nodes ... 304 are not placed and not drawn") and a line saying a shade is a count, not a location.
- Each county's tip: its name and its count. A wired map would add its zone, its nodes' names (each a link to the node's panel) and its transmission project phases by status (1048's figures).

At 390 the SVG's own text is too small (the frame shows it): a wired map would put the title, the legend and the notes in the page's HTML text above and below the drawing, and keep only the shapes in the SVG.

## Where it would go

On the node list (`rows=nodes`), above the list, folded by default ("Show the counties on a map"), so that the list's first rows stay on the first screen. A click on a county sets the list's county filter (`ncounty`, session 1048). The drawing is built from the node file at build time; the tab still reads no database (test 716).

## For Samuel's ruling

- Whether to wire the county map as drawn (a shade by count; no node as a point), and where.
- Whether counties outside ERCOT are greyed from `utility_service_territories`, or left unshaded.
