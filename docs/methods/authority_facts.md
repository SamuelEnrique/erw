# Every balancing authority's own facts (`site/data/regions/authority/`)

Session 8012, chain 505 (part C), 19 November 2026. Builder: `warehouse/derived/authority_facts.py`, a step of the data machine's daily run after the region files. Contract: section 10 of `docs/state/page_files_regions.md`. License: public (every source is a U.S. Energy Information Administration publication, or a public document a row of `large_load_public` names).

## What a file holds

One file for each balancing authority of `index.json` that files Form EIA-930 in the lower 48 (72 on 19 November 2026, retired ones included), and one for each of EIA's thirteen regions (`region-<code>.json`), the region's authorities summed. Each part names its ERW table, its vintage and its source in words. A part a source does not cover is present with null values and `why`, never a zero.

- **What it owns.** Operating generators of EIA-860M (the newest month the warehouse holds, 2026-09 on the first build) whose plant EIA places in the authority (`balancing_authority`): their count, their net summer capacity (`capacity_mw`) by the ERW's technology group, and the ten largest plants by summed capacity, each with its largest generator's group and its operator. EIA-860M, the monthly inventory, is used rather than the annual EIA-860 because it is the newer and carries the same balancing authority code.
- **What is coming and going.** EIA-860M's planned generators by planned operation year and group; operating generators with a planned retirement date, by its year; and the generators EIA-860M lists as retired, by year.
- **What it generates and how clean it is.** Net generation by source over the twelve complete months before the newest month the demand files hold (November 2025 to October 2026 on the first build), from EIA's six-month Form EIA-930 files, read with the region fuel connector's own reader (`eia930_region_fuel_hourly.read_file`: EIA's adjusted value where it prints one; its sources folded into the site's eight, petroleum and geothermal under other). Shares are of the sum of the sources. Carbon: EIA's own hourly CO2 estimates (CO2 Emissions Generated, `eia930_all_emissions`) summed over the hours that also hold net generation, and that sum over the same hours' net generation, kg per MWh. The ERW holds EIA's estimates for the seven ISOs and the Lower 48 only; every other authority has `null` with that reason.
- **Whom it trades with.** The five largest partners by gross exchange in the newest year with at least 8,700 hours of interchange in `ba_trade_partners`, with the net import from each, and the authority's net imports as a share of its demand that year. A region's partners are the neighbouring regions by the mean of each side's report of the year's flow (`trade_matrix.json`), with its direction; a region's share of demand is not given (its net imports by month are in `trade/<region>.json`).
- **Its size.** The highest whole-day peak of the demand file (`demand/ba/<code>.json` or `demand/<region>.json`, which follow their own method: `docs/methods/regions_pages.md`), its hour in UTC and in the authority's time zone, and the newest whole year's average demand against 2019's, from the file's `growth`.
- **What is said of large loads there.** The rows of `large_load_public` placed in the authority, newest first. A row whose grid is one of the seven ISOs is placed in that ISO's authority. A utility group whose rows all lie in one authority is placed by a fixed list in the builder (`GROUP_BA`: Arizona Public Service AZPS, El Paso Electric EPE, Georgia Power SOCO, JEA JEA, Florida Power & Light FPL, PPL's Kentucky rows LGEE, PacifiCorp's Utah rows PACE, Tampa Electric TEC, Tucson Electric Power TEPC, Xcel Energy's Colorado rows PSCO). A group whose rows span several authorities is not placed (`NOT_PLACED`: Duke Energy's South Carolina rows, AEP, FERC, National Grid, Wabash Valley).

## What the files do not say

- Capacity is where EIA places a plant, not who buys its power; an authority's plants can serve load elsewhere.
- Generation is what the authority's plants made, not what its load used; with net imports the two differ.
- A planned date is the owner's own, as EIA-860M reports it; planned generators often slip or are cancelled.
- The large-load rows are the public record the ERW has read (`docs/methods/large_load_public.md`), not every request.

## Build

`python warehouse/derived/authority_facts.py` (about 30 seconds); `--site-dir` writes elsewhere for a trial; `--only CODE` builds named authorities alone. It reads the six-month files EIA's daily step of the data machine's run already saves.

## On the page (session 8013, chain 505)

The Grid tool's panel, which opens on a click of the map or the network, shows these facts under what it showed before, in a block "Its own facts", and the region's sum in a fold below it. The page reads one file at a time from `/grid/authority/<code>` (a static address made for each file when the site is built) when the panel opens. Each heading names its table and vintage on hover. A block the file does not hold says "Not held" with the file's own reason; nothing is drawn as a zero. Planned additions and retirements are summed from the current year on, by source. The block is drawn only where the whole country's index is on the server, so the panel of `/network` is unchanged.
