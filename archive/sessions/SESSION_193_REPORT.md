# Session 193 report: the balancing authorities on the Map, third attempt (a derived map from counties, labeled as derived)

11 October 2026, 07:36 to about 08:35 UTC (beside sessions 185, 191 and 192), unattended, on `lab-desktop`. First request 07:37:55, last 07:40:07 UTC. Branch `wip/193-ba-map` in `C:\Users\Shared\Documents\erw-193` (from `wip/180-network-map`, brought up to main), on this machine only. Model spend USD 0, no model call. Outputs: `runs/session193/` of the data checkout.

## Read these first

- **NOT LANDED**: this machine cannot push to GitHub (session 185's report, first bullet). The Map is drawn and checked on a local build; production still has no Map button.
- **No published boundary answered, a third time.** EIA's own site holds none: its list of map layers now redirects to the atlas (searched in session 180), and the Hourly Electric Grid Monitor draws thirteen regions with each balancing authority as a point. NREL's ReEDS publishes 134 model regions with no EIA-930 code: 0 of the page's 70 grids match.
- **So the Map is the third option, a derived map, and says so inside its frame.** Each county is given to one balancing authority from EIA-861's 2025 files (released 7 October 2026). 44 of 70 grids have an area; 3,067 of 3,107 counties of the lower 48 are drawn.
- **Twelve requests of thirty, 9.9 MB of 300 MB.** Terms read first: EIA's robots file and its reuse page ("U.S. government publications are in the public domain ..."). County shapes came from the package the site already ships; nothing was asked of the Census Bureau.
- **One mistake of mine, caught before anything was drawn.** The first build left out EIA-861's file of delivery companies. Texas's wires utilities (Oncor, CenterPoint and five more, 8.5 million customers) report there, so 39 Texas counties had gone to a neighbour or to none; Harris County (Houston) to MISO. I found it by looking up the 8 blank counties. The file is in the rule now and a test holds Harris County to ERCOT.
- **Holes you will see:** 37 counties in Colorado, South Dakota, Wyoming, Nebraska, Utah and New Mexico are blank. EIA-861 gives them to `WACM`, which is not one of the page's grids; the page draws `SWPW`, which EIA-861 does not name. Nothing was moved from one to the other. For your ruling.
- **What it is not:** not a boundary. A county has exactly one balancing authority here, so a small one inside a large one's counties disappears (9 grids are named by utilities and won no county).

## What to review (after the landing; until then `runs/session193/map_1280.png`, `map_1280_uri.png`, `map_390.png`)

- `https://erw-flame.vercel.app/network` (internal view).
  1. Open it. Expect the page as it is, with two buttons above "Watch:", **Map** and **Network**, Network dark.
  2. Click **Map**. Expect the lower 48 states in place of the 3D canvas: 44 regions colored on the page's carbon scale, grey where the intensity is not held, ties as dashed lines with arrowheads. Under the map, inside its frame: "Derived map: each county is given to one balancing authority from the utilities that serve it (EIA-861). It is not a boundary any balancing authority or agency published. Data year: 2025 (EIA's final data, released 7 October 2026)." The address ends `?shape=map`.
  3. Hover Texas: its name. Click it: ERCOT's panel ("Electric Reliability Council of Texas, Inc."), the same as on the network.
  4. Look at Colorado and Wyoming: white patches (the `WACM` counties).
  5. Click **Texas during Uri**, then **Pause**: ERCOT's panel opens beside the map, ERCOT's area is outlined and the Southwest Power Pool's is red.
  6. Click **Network**: the canvas comes back on the same day and grid.
- `https://erw-flame.vercel.app/network/ba_counties.csv`: every county with its code, the winning share and how many codes its utilities named. Harris, Texas: `ERCO`. Cook, Illinois: `PJM`. Los Angeles: `LDWP`.
- `https://erw-flame.vercel.app/data/methods/grid_network` (internal view): "The third pull (session 193 ...)" with the twelve requests, and "The derived map: counties (session 193)" with the rule and what the map is not.
- On a phone (390 px): the whole country, the label under it, nothing wider than the screen.

## The pull against its ceiling

- Ceiling: 30 requests, 300,000,000 bytes. Used: 12 requests, 9,917,072 bytes. Log: `runs/session193/pull/requests.csv`; each answer with its headers beside it. The plan was written before the first request (`pull_plan.txt`).

| # | Address | Status | Bytes | What came back |
|---|---|---|---|---|
| 1 | `www.eia.gov/robots.txt` | 200 | 718 | `Allow: /`; a list of folders disallowed, none of them asked; no delay |
| 2 | `www.eia.gov/about/copyrights_reuse.php` | 200 | 52,528 | the public-domain statement; an acknowledgment with the date is asked |
| 3 | `www.eia.gov/maps/layer_info-m.php` | 301 | 0 | `Location: https://atlas.eia.gov/search` (not followed) |
| 4 | `www.eia.gov/electricity/gridmonitor/dashboard/electric_overview/US48/US48` | 200 | 43,735 | the page; it names `main-62AHFAMH.js` |
| 5 | `www.eia.gov/electricity/gridmonitor/main-62AHFAMH.js` | 200 | 4,903,073 | the program: states, 13 regions (`REG-CAL` to `REG-TEN`), balancing authorities as bubbles at a latitude and longitude |
| 6 | `api.github.com/repos/NREL/ReEDS-2.0/license` | 301 | 206 | moved; it names the next address |
| 7 | `api.github.com/repositories/189060033/license` | 200 | 3,120 | BSD 3-Clause (not public domain) |
| 8 | `.../contents/inputs/shapefiles` | 200 | 8,059 | the folder `US_PCA` |
| 9 | `.../contents/inputs/shapefiles/US_PCA` | 200 | 4,638 | `US_PCA.dbf`; the shapes are a pointer to a large-file store |
| 10 | `raw.githubusercontent.com/NatLabRockies/ReEDS-2.0/main/inputs/shapefiles/US_PCA/US_PCA.dbf` | 200 | 67,124 | 134 regions `p1` to `p134`; no EIA-930 code in any field |
| 11 | `www.eia.gov/electricity/data/eia861/` | 200 | 77,055 | "Release date: October 7, 2026 (final data)"; `zip/f8612025.zip` |
| 12 | `www.eia.gov/electricity/data/eia861/zip/f8612025.zip` | 200 | 4,756,816 | EIA-861, 2025; sha256 `f59f6c73...e3a396` |

- Two of the twelve were redirects that cost a request each (3 and 6). No redirect was followed without being asked for as its own request.
- Not asked: the atlas again, any ArcGIS Online services host (session 180b's reading stands), HIFLD, the Census Bureau, MISO, PJM, the Virginia SCC.

## The rule, in five lines (whole in the Method note)

1. A utility's customers in a state, under each of its balancing authority codes: Parts A, C and D of `Sales_Ult_Cust`, the delivery companies' file and the short form. Part B (a marketer's energy) is left out.
2. Split evenly over the counties `Service_Territory` lists for that utility in that state. This is the one assumption: EIA-861 has no customers by county.
3. A county goes to the code with the most customers so allotted (no customer reported: the code most of its utilities name; a tie: none, and there was none).
4. County names are matched exactly after a stated cleaning; "<name> City" is the independent city.
5. An area is its counties joined and simplified (0.02 degrees). A code is drawn only when it is exactly one of the page's grids.

## What came out

- 44 of 70 grids with an area; 3,067 of 3,107 lower-48 counties drawn; the file is 145,860 bytes.
- 2,008 counties are served by utilities of one code only; 1,126 by several, given to the largest. The smallest winning share is 33 percent (a county in TVA's area).
- 40 counties blank: 37 `WACM`; Galax, Lynchburg and the city of Roanoke in Virginia, which no utility names. Falls Church has a code and no shape.
- 26 grids with no area: 17 that no utility names (7 operators of Canada and Mexico, and `AVRN`, `BHBA`, `CPLW`, `DEAA`, `GRID`, `GWA`, `SIKE`, `SWPW`, `WWA`, `YAD`), and 9 that are named and won no county (`GCPD`, `GVL`, `HST`, `IID`, `JEA`, `NBSO`, `SEPA`, `SPA`, `TIDC`).
- 25 utility-states have a territory and no code in the files (Wolverine Power Supply Coop's 33 Michigan counties are the largest).

## What was built

- `warehouse/connectors/eia_ba_boundaries.py`: the command `counties` (no request): the workbooks read from the zip, the rule, a decoder for the county file's TopoJSON, the site file with `provenance.derived`, `label`, `rule`, `counts`, and the county list. It refuses a zip whose sha256 is not in the request log.
- `site/public/network/ba_boundaries.json` (the Map's file) and `site/public/network/ba_counties.csv` (3,134 counties, with a header that names source, hash and rule).
- `site/app/network/NetworkMap.tsx`, `site/lib/networkMap.ts`: a derived file is never drawn without its label; the label stands under the map inside the frame. `Network.tsx`: the legend no longer says "published boundary".
- `site/scripts/check-network-map.mjs`: two checks more (a derived file carries its label inside the frame; a file that is not carries none). `site/scripts/shot-network-map.mjs`: the three pictures.
- `docs/methods/grid_network.md`: the third pull, the rule, what the map is not. `warehouse/metadata/sources.csv`: one row, `erw:balancing_authority_counties`, public, no table.
- `tests/test_session193.py`: 24 tests (the rule on made-up workbooks and shapes; the shipped file, its counts, eight counties anyone can check, the registry row, the label, the note).

## Checks run

| Check | Exit | Result |
|---|---|---|
| `counties`, first build | 0 | 44 grids, 3,062 counties: wrong for Texas (above) |
| `counties`, with the delivery companies | 0 | 44 grids, 3,067 counties, 145,860 bytes |
| `tests.test_session193` | 1, then 0 | first run 2 failed: a made-up case's arithmetic was mine to fix, and one real fault (a county with no shape was marked "drawn" in the list); then 24 pass |
| `tests.test_session180`, `test_session180b` | 0 | 28 tests, 1 skipped |
| `tsc --noEmit` | 0 | |
| Site build (three times: the label was moved, then the frame kept from stretching) | 0, 0, 0 | `build.out`, `build2.out`, `build3.out` |
| `check-network-map`, local build | 1, then 0 | first run stopped: the internal token was not in my shell; then 31 of 31 |
| The default Network view, production against the local build | 0 | the same (address, html, scene, spheres), the toggle left out |
| `check-network-v3`, `check-network-v3-hard` | 0, 0 | 33 and 24 |
| `check-routes`, `check-csp`, `check-security`, local | 0, 0, 0 | 319 checks; 85 pages with 0 violations; 48 of 48 |
| Whole suite (`unittest discover -s tests`) on the branch | 0 | 3,137 tests, 231 skipped |

- Two faults of the drawing were found by looking at the pictures and fixed: on a phone the label covered the southern states (it now stands under the map), and beside a tall panel the frame stretched and left an empty band (it no longer does).
- **Not run:** the check against production (not landed); `check-values`.
- **Not verified:**
  - The even split. It is an assumption, not a measurement; the county list shows where it decided (1,126 counties).
  - Whether `WACM`'s counties belong to `SWPW` today. EIA-861's year is 2025.
  - Only headless Chrome.

## Pulls and spend

- Outside hosts: 12 requests (table). Production: read only (the default view's capture).
- Model spend: USD 0. No table written, nothing under the data lock, nothing loaded.

## Decisions made without you

- **The third option, by the prompt's order**: the first two were asked and did not answer with a file that can be matched to the page's grids.
- **Customers, not sales, as the weight.** Customers follow where people are served; one large industrial customer would move a county by sales.
- **Delivery and bundled service count; a marketer's energy does not.** The wires say where a county is.
- **`WACM` stays blank.** Giving its counties to `SWPW` would be a guess.
- **The county list is shipped** beside the file (104 kB), so anyone can check a county.
- **The registry row is the ERW's own source** (`erw:balancing_authority_counties`), as the other derived things are.
- **The ReEDS shapes were not fetched.** Their attribute table was enough to see they cannot be matched, and the licence is not public domain.

## Found, not changed

- `CLAUDE.md` says three pages are live. `site/lib/release.ts` says none is since session 166 ("no page is live"), `/network` included. I worked by the file.

## To finish

After the sign-in (session 185's report), and after `wip/192-roundup-repeat`:

```bash
cd /c/Users/Shared/Documents/erw && git fetch origin
.venv/Scripts/python.exe scripts/freeze.py status; echo "exit=$?"
git -C ../erw-193 merge origin/main
node site/scripts/snapshot-live.mjs take before193
git -C ../erw-193 push origin wip/193-ba-map
git -C ../erw-193 push origin wip/193-ba-map:task/193-ba-map
node site/scripts/snapshot-live.mjs take after193        # after the workflow's merge and the deploy
node site/scripts/snapshot-live.mjs compare before193 after193
cd site && node scripts/check-network-map.mjs https://erw-flame.vercel.app
```

- `/network` is in review, so a visitor sees the in-review page before and after: the comparison should list 0 differences.
- The local server this session started on port 3193 was stopped.
- For your ruling: `WACM` and `SWPW`; whether a derived map is what you want on this page at all (reversible: delete `site/public/network/ba_boundaries.json` and the frame says the file is not held).

## The prompt

"Session 193 (long end 2:00): the balancing-authority boundaries, third attempt, pull approved at most 30 requests and 300 MB, terms read first: look for a public file at EIA (its Energy Atlas or the Hourly Electric Grid Monitor's map data), NREL (the ReEDS or other published region shapes), or the Census-county approach (each county assigned to a balancing authority from EIA-861's utility-to-county and EIA-930's membership, an honest derived map labeled as such). Use the first that is public and reachable; draw the Map view; land. If none works, report what answered." Unattended; the rules of CHAIN_OCT8_PROMPT.md; model spend USD 0, no model call; deploys allowed; this is the data machine.
