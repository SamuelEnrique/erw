# Session 8601 report (portable-laptop, 19 November 2026)

Energy Research Warehouse (ERW). Chain 504, part B: the Grid tool's map of the balancing authorities, with the trading on it. About 10:50 to 11:40 UTC. Branch `wip/8601-grid-map` at `a25a0504c`, landing request row 41. Model spend USD 0; no model was called.

## What a reader of `/grid` can now do on the map

The map has been a shape of the Network view since session 180. It was not built again. Added tonight:

- **Hover a region:** its name and, for the hour or day shown, its carbon intensity (as the panel writes it), demand, net imports over the ties that reported, its batteries when the switch is on, the hour, and the tables. Until tonight a hover gave the name alone.
- **Hover a tie:** both names in the direction of flow, the megawatts, the hour, and who reported it. Until tonight a tie did not answer to the mouse. The hover takes the nearest line, so a short tie is not hidden under a long one.
- **Read a line's size:** a key under the map draws three widths with their megawatts (the largest flow of the period, a quarter, a sixteenth).
- **Batteries on the map:** the switch draws the network's ring (fuller as they discharge) on each region whose batteries are reported.
- **Move and zoom:** the wheel, two fingers, a drag once zoomed, and three buttons (one to twelve times).
- **See every authority:** the 26 with no boundary in the file are listed by name under the map, each with the region's hover and click. None is dropped.
- **On a phone (390 px):** nothing scrolls sideways; a tap on a tie shows its figures whole under the map.
- **The whole country's boundary file:** the map reads `site/data/regions/ba_boundaries.json` (the data machine's, in the contract's form) the day the server holds it, with no change of code. Until then it draws the county file of session 193, with its label.

## What was measured and checked

- **Speed:** the map is drawn and answers 376 to 456 ms after "Map" is chosen (six runs; the limit is 3,000). No boundary file and no code of the map is fetched before it is chosen.
- **The same megawatts:** the 93 ties on the map carry the megawatts and the direction of the network's own 3D scene for the same pair and hour (148 ties in the scene; 55 end at an authority with no boundary).
- **One carbon scale:** each of the 44 regions has exactly its sphere's color.
- **A story switched in its middle** (Texas during Uri, to the map and back) keeps its hour.
- **Nothing the network shows moved:** the default Network view of the branch against a build of main made the same hour: the same scene, the same 70 spheres' colors, the same page but for 25 characters of the snapshot's refresh time.
- `site/scripts/check-grid-map.mjs` 44 of 44 and `site/scripts/check-network-map.mjs` 31 of 31 on the build; `tests/test_session8601.py` 23 passed; the 57 test files that name a changed module: 739 passed, 15 skipped, 1 failed (below).
- Ten pictures at 1280 and 390 px: `docs/reviews/grid-map-2026-11-19/` on the branch (`map_1280.png`, `map_1280_hover_region.png`, `map_1280_hover_flow.png`, `map_1280_batteries.png`, `map_1280_story_uri.png`, `map_1280_zoomed.png`, `map_390.png`, `map_390_tie.png`, `map_390_zoomed.png`, `network_1280.png`).

## Faults found

- **"Batteries: on" and "Prices: on" could not be read** (ink letters on the switch's own ink ground), on the Network view too and on production: the brand's rule for a button that is not pressed did not know a switch. Fixed in `site/app/tokens.css`, checked in the browser, held by a test.
- **37 of the 44 regions are grey, "not held".** The warehouse computes a carbon intensity for the seven ISO balancing authorities only, so a map "colored by carbon intensity" is mostly grey, and so are 63 of the 70 spheres. Data request 540.
- **The files do not record which side reported an hour's flow.** The tie's hover says the pair rule and "The file does not mark which". Data request 541; the hover names the side the day a file carries the mark.
- **Not this branch's:** `tests/test_session7203_allgrids_read.py` (the All grids tab, its check of row 10) fails on origin/main at `b24de36b8` as on the branch, with the env loaded. Said in landing row 41 so the desk does not read it as this branch's.

## What to review (after row 41 lands; the page is in review, so in the internal view)

1. `https://erw-flame.vercel.app/grid?view=network`: the 3D network opens, as before. Press "Batteries: off": the button turns dark and reads "Batteries: on" in white.
2. Press "Map": the country in regions, the ties as lines with a running dash. Move the mouse over Texas: a card with ERCOT's name, its carbon intensity, demand, net imports and the hour. Click it: the same panel as in the network, with the same figures.
3. Move the mouse along a line between two regions: a card with both names, the megawatts, the hour and who reported it.
4. Press "+" twice, drag the map, press "Reset".
5. Under the map: "Not on the map: no boundary in the file (26)". Click "Alberta Electric System Operator": its panel opens.
6. Press "Texas during Uri", then "Network", then "Map": the hour on the slider does not change.
7. On a phone, `https://erw-flame.vercel.app/grid?view=network&shape=map`: spread two fingers on the map, then move it with one; tap a line.

## Not as the chain expected

- The map existed (session 8600's report). The boundary file is not on main yet; the code does not wait for it.
- The first full run of the new check found three ties that could not be reached by the mouse (two lines running almost on top of each other); the hover was changed to take the nearest line. The session 180 check then found the opposite fault (a tie taking the hover at a region's own point); a tie no longer answers at its two ends.

## Decisions made without you

- The names of the authorities with no boundary stand under the map, in its frame, not in a column beside it: the column took a quarter of the map's width at 1280 px.
- A tie's width, the dash and the ring are sizes in screen pixels at every zoom; on a frame narrower than 748 px they shrink with it, to six tenths at most (at full size the arrowheads of the West ran into each other on a phone).
- On a short frame (a phone, or the map beside an open panel) the hover stands across the frame right under the map: beside the pointer its top was cut off.
- The boundary file is read through `/grid/boundaries`, an address under `/grid`, so the release gate covers it as it covers the page. `site/lib/release.ts` is not touched.
- The two data requests took numbers 540 and 541 (chain 504's own block), clear of the other chains' rows.
- A double click does not zoom: a double click on a region would open its panel and zoom at once.

## Needs the key

- Nothing.

## For Samuel's ruling

- **The color at the hour shown.** The chain asks for a region "colored by its carbon intensity at the hour shown, on the same scale as the spheres". In the live week a sphere's color is the latest hour of intensity held, not the hour on the slider (the page's key says so: "The color updates daily"). Coloring the map by the hour shown would either make a region and its sphere disagree, or change the Network view. **Default taken:** a region has its sphere's color, as since session 180, and the Network view is not touched. To have both views follow the hour: the week's hourly intensity read from the live set for both, which changes the spheres' colors as the slider moves.
- **Data request 540 colors grey spheres too.** A carbon intensity for the other balancing authorities would color 63 spheres of the Network view that are grey today. **Default taken:** the request stands as written to the data machine; nothing was coded around it.
