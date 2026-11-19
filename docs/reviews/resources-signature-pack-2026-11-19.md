# The natural resource map: a signature pack for Samuel (19 November 2026)

Energy Research Warehouse (ERW). Written by session 8609 of chain 504 (`queue/done/504-night-19-november-portable-grid-map-whole-country.md`), the portable laptop, for one sitting. It is in the form of the trackers' pack (`docs/reviews/trackers-signature-pack-2026-11-16.md`), and stands beside the pack of the Grid tool's map and regions (`docs/reviews/grid-map-regions-signature-pack-2026-11-19.md`, on `wip/8602-grid-regions`).

- **What a signature is.** You fill the three lines of the block "Sign-off" in `docs/methods/resources.md` and commit it, or say it in a prompt and a session writes your words there. A session never signs.
- **What you sign accepts** the rules the block lists, at the defaults of the rulings below. It does not freeze the layers: the data side adds them.
- **Nothing here is published.** The map is a tab of `/map`, in review, as every page is. Signing does not open it. The datacenter overlay stays held for its license.
- **Where it is.** Branch `wip/8603-resources` (landing request row 43). The coal fields, the data machine's layer, are on main and on production since 18:10 UTC on 19 November, with the page as it stood after session 8613; what sessions 8614 to 8616 added waits at the landing desk.
- **About fifteen minutes.** The replication is Python and runs in seconds; its Stata do-file has not been run.

---

## 1. What you sign

`docs/methods/resources.md`, section "Sign-off".

**The choices that matter most** (on the page: "Decisions on this page (10)" under the map, each with its default and its source on hover):

| Choice | Default | Source |
|---|---|---|
| What a switch is | One publisher's file, drawn as published; layers are never added or blended | the list of layers, one section a layer in the method note |
| What the map shows | The resource itself; plants, the queue and datacenters are separate switches, off until switched on | session 146 |
| A kind with no layer | Its switch is greyed and says why; nothing is drawn in its place | the owner's list of 7 October 2026: uranium and critical minerals today |
| An outline's area | The area of the shape drawn, not the formation's extent and not a measure of oil, gas or coal | the publisher's own figure, or the data side's from the outline |
| Two lists of layers | Read as one; the first list wins a name | the data machine's second list (data request 542) |

## 2. Replication (`python replication/resources/replicate.py`; exit 0)

- The layer of tight oil and shale gas plays against the publisher's own file (EIA, 323,424 bytes, the same sha256 as on 7 October): **556 of 556 figures are the publisher's** (50 plays; each one's name, area and nine fields; the smallest, mean and largest area).
- Written from the method note and the publisher's file with Python's standard library alone.
- A second layer since (session 8619, `python replication/resources/replicate_basins.py`): the sedimentary basins against EIA's own file (440,871 bytes, the same sha256 as on 7 October): **199 of 199 figures are the publisher's** (32 basins); every basin's published area is within 0.2 percent of the area of its own outline.
- `replication/resources/replicate.do` prints the five headline figures in Stata. It has not been run.

## 3. Cross-checks (no figure adjusted)

| Our figure | Published figure | Source | Gap | Why |
|---|---|---|---|---|
| The 50 plays' areas, summed: 514,017 square miles | 514,014 square miles, the area of the publisher's own outlines on the WGS 84 ellipsoid | computed from the same file | 0.001 percent | the hover's figure is the area of the shape the map draws |
| Woodford-Caney (Arkoma): 2,892.5 square miles | 2,900 | EIA, "Review of Emerging Resources", July 2011 | -7.5 | the two agree |
| Marcellus: 58,326.4 | 95,000 | the same | -36,673.6 | the review: the whole formation; the file: the play's general area |
| Barnett: 26,311.4 | 6,458 | the same | +19,853.4 | the review: two sections as the USGS estimated them |
| Bakken: 25,929.2 | 6,522 | the same | +19,407.2 | the review: the acreage leased in 2011 |

Nine plays are set beside the 2011 review in `replication/resources/crosscheck_published.csv`. The two documents answer different questions under the same names, which is why the page says an area is the outline's.

## 4. What to look at (five minutes, in the internal view, after the landings)

1. `/resources`: rest the mouse on the map: the first line ends with the state.
2. Switch "Coal fields" on, rest the mouse on West Virginia: the field, its area, its age and rank.
3. Rest the mouse on "not held" beside "Uranium deposits": the reason.
4. "Decisions on this page" under the map: ten lines.
5. The reader's read: `docs/reviews/resources-read-2026-11-19.md` (two reads of five cases, the phone with a finger, the keyboard: seventeen rows).
6. On a phone: tap the map. A card with the value stays (it showed nothing until session 8614).
7. With the keyboard: Tab to the map, then the arrow keys. The card reads the place under the small ring at the centre.

## 5. For your ruling (each has its default taken; nothing waits on you)

| # | The question | Default taken |
|---:|---|---|
| 1 | Uranium and critical mineral deposits: the two USGS hosts that serve them refuse automated reading (ScienceBase names Claude). A person could download the two files by hand and give them to the data machine | Not fetched; the two switches greyed with that reason |
| 2 | A wind or sun layer's hover repeats its vintage sentence with every value. It could stand once, in the legend | Left as it is |
| 3 | The coal fields' area was in square kilometres where the basins' and plays' are in square miles (data request 552) | Settled by the data machine the same day: square miles, with the square kilometres beside it. Nothing for you to rule |
| 4 | Two layers are replicated (the plays, and since session 8619 the basins). The geothermal layers are on a host that refuses Claude's agents; the coal fields' source is a 230 MB archive the data machine fetched | Two layers; chain 504 asked for one |
| 5 | With a sun layer on, Alaska is blank north of 60 degrees north (the source's file ends there). Should the hover say so where the reader points? | Left; the layer's entry under the map says it |
| 6 | A card that stays after a tap on a phone: a close mark? | None; the next tap, a drag or a map button takes it off |
| 7 | **Site-wide:** a reason given on hover ("not held" beside a greyed layer) is the browser's own tooltip, which a finger never opens (about 1,100 on the site, 12 on this map) | Left as the site has it |
| 8 | With the method note under the map open, the page has two headings of level 1 (the page's and the note's own title). The level can only be set inside the site's one renderer, which every page shares | Left as it is; a fix from the page went round the renderer and was taken out |

## 5a. Since this pack was first written (sessions 8611 to 8616, the same day)

- **On a phone a tap now shows the value** (session 8614). It had shown nothing since the page was built: a finger's lift counted as leaving the map. On a narrow map the card takes the map's width.
- **The keyboard reads the map** (8615): the place at the map's centre, under a small ring, after each key; announced to a screen reader.
- **The map's controls are 44 px on a phone**, and its card is the brand's (8611).
- **The check** switches the coal fields on, taps with a finger, uses the Tab key, and holds frames back to try the map's own record: 102 of 105, the three that fail the datacenter overlay's license hold.
- **Data request 553**: plain words and units for the hover of the wind sites and the hot-water systems, which read as raw column names. Done by the data machine on its next stack.

## 6. What is not done

- No layer of uranium or of critical mineral deposits.
- The datacenter overlay is held for its license and draws nothing.
- The accessibility read (axe-core on a build, 1280 and 390 px) found no rule broken on the tab. A keyboard's path over the map has been tried since (session 8615); a person with a screen reader has not tried it.
- A table of a layer's values under the map, which the brand asks of a chart, is not given: a layer is up to 150,000 cells.
