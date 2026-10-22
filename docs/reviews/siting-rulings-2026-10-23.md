# The All grids tab: the rulings it waits for, in plain words (22 October 2026)

Energy Research Warehouse (ERW), session 741 of chain 062, 22 October 2026. One section per item still waiting for the owner: chain 050's "For Samuel's ruling" lists (`archive/sessions/SESSION_700_REPORT.md` to `SESSION_721_REPORT.md`) and chain 062's (722 to 740). Each section says what the item is, what each answer would change on the page, the work it needs, and a recommendation with its reason. **Nothing here is decided**; a ruling is the owner's.

The page is `/cost-of-power?view=allgrids` (in review, the internal view). Its method note is `docs/methods/siting.md`.

## 1. Retire "Grid by grid"? (700)

- **What**: `/cost-of-power` has three views, "Your load", "All grids" and "Grid by grid" (session 37's). All grids answers what Grid by grid did, for more rows.
- **Yes**: the view and its address go; a link from its old address opens All grids. Its checked addresses leave check-values.
- **No**: nothing changes.
- **Work**: one session (the view, its tests, check-values, a redirect).
- **Recommendation: keep it for now.** Grid by grid shows a year-by-year history that All grids does not; retiring it loses that, and nothing is wrong with it.

## 2. The profiles' open defaults (700)

- **What**: flexible compute's strike (USD 1,000 per MWh) and the electrolyzer's load factor (0.55) and strike (the row's k-th cheapest hour) were set by session 700, as the chain prompt left them open.
- **Another value**: every figure under those profiles moves (energy, hours given up, all-in, the year), and so does the second card (734).
- **Work**: a line in `lib/siting.ts` and the pinned tests.
- **Recommendation: keep them.** At USD 1,000 the strike costs a load only 5 to 15 hours a year at ERCOT's rows (734's card), so the four peaks do most of the work, which is the profile's point; 0.55 is the middle of the 0.40 to 0.70 the prompt gave.

## 3. NYISO's and ISO-NE's prices on the tab (701)

- **What**: ISO-NE, MISO and NYISO prices are "license needed" since 20 October 2026. "Your load" still draws NYISO's and ISO-NE's from its own files, and the tab follows it so the two views agree.
- **Hold them**: both views draw "license needed" for those grids' energy and all-in; their rows keep connect, headroom, carbon and utility.
- **Keep**: nothing changes.
- **Work**: one session, both views together (the files, the keys, the floors).
- **Recommendation: hold them in both views**, to match the license record. It is the only place the site shows a figure its own record calls license needed.

## 4. Grid emergencies as heavy industry's interruptions (702)

- **What**: "interruptible" moves only the capacity column today; no table holds the hours a grid interrupts a load. CAISO's emergency notices are held (`caiso_grid_emergencies`).
- **Yes**: heavy industry in CAISO loses those hours; elsewhere it stays as is, said so.
- **Work**: one session.
- **Recommendation: no.** A grid's emergency notice is not a utility's interruption order, and one grid of seven would make the profile mean different things by grid.

## 5. The Commission's transmission rate (703)

- **What**: `texas_transmission_matrix` is internal in coverage, yet "Your load" and the tab show its rate (the four-peak charge), and the two research cards use it.
- **Hold it**: the four-peak charge and ERCOT's all-in become "license needed" in both views; the cards lose their all-in figures.
- **Work**: one session, both views and both cards.
- **Recommendation: review the table's license first.** The PUCT's approved rates are public orders, so the "internal" mark may be the table's caution, not a term.

## 6. Capacity prices (704, 713)

- **What**: PJM's, ISO-NE's, MISO's and NYISO's capacity prices are computed where held and drawn "license needed" (session 408's rule). NYISO's spot rows are marked public row by row.
- **Show them**: four grids gain a capacity figure and an all-in figure; a permission from each ISO, or MISO's terms reviewed, comes first.
- **A private place**: the figures are written where a reviewer with the internal cookie can read them (the internal view of Supabase), not in the public repository.
- **Recommendation: the private place first.** It lets you see the figures without publishing them; the permissions are a longer road.

## 7. Annual carbon on the same basis as hourly (707)

- **What**: the annual figure is generation-based (eGRID's plants), the hourly one consumption-based (EIA-930). Each tip says which.
- **Yes**: the annual figure becomes EIA-930's yearly intensity, and the two agree in kind.
- **Recommendation: yes.** A load consumes from the grid; the consumption basis is the one a buyer means.

## 8. What "load band" means (710)

- **What**: the screen's "band" was read as an energy band (USD per MWh).
- **A size band**: no row has a size, so a size band would filter nothing.
- **Recommendation: keep the energy band**, and rename it "Energy band" (it is already labelled so).

## 9. The tab's files kept fresh by the data machine (712)

- **What**: the tab's files (`site/data/siting/`) are built from tables a code session rebuilds from the archive. The tab can lag the live set by days.
- **Yes**: the data machine's daily run calls `warehouse/derived/siting_page.py` after its tables, and commits the files.
- **Work**: one data-machine session.
- **Recommendation: yes.** The files are small and the builder keeps a file whose content did not change.

## 10. The page's weight (714, 716, 737)

- **What**: the hub table's page was 1.86 MB of HTML. Session 737 took off what could go without a word changed: the tip's box styled once in `tokens.css`, 1.58 MB now (15 percent less).
- **Shorter tips**: the method stays once in each column's tip; each cell's tip keeps only its own figures. 193 KB of the page's tip text repeats a text drawn elsewhere on it, and the server's payload carries about as much again: about 0.4 MB, a quarter of the page.
- **Work**: one session, choosing the words column by column. 737 built no variant, since the words are this ruling's.
- **Recommendation: yes.** The sources stay one hover away in the column's tip, and a phone loads a quarter less.

## 11. The brand shots of the restyle (715)

- **What**: `docs/brand/review-715/`, the tab's words in sans and its figures mono.
- **Recommendation: look at them**; nothing waits on them but your eye.

## 12. Texas's wires utilities priced (718)

- **What**: ERCOT's rows name a retail seller (TXU) or a coop; Texas's wires utilities (CenterPoint, Oncor, AEP Texas, TNMP) file no sales row, and `texas_delivery_charges` holds four of their tariffs.
- **Yes**: ERCOT's Utility column shows the wires utility's delivery charge, "delivery only" (726's word).
- **Recommendation: yes**, with item 13: a planner asks for the wires.

## 13. A retailer named as the utility (725)

- **What**: for ISO-NE's Massachusetts zones and MISO's Illinois hub, the state's largest seller to industry is Direct Energy Business, an energy-only retailer.
- **Name the wires utility**: those rows show the wires utility's delivery revenue, "delivery only".
- **Recommendation: yes**, with item 12, so every row names the utility a planner means and the kind is always said.

## 14. Naming a tracked facility on the tab (719)

- **What**: the tracker links a facility to its row with its MW, but the tab names no facility: the table is held whole, and the tab reads no database.
- **Once public**: the tab names the facility from the public rows, by one read or by a site file.
- **Recommendation: a site file built from the public rows**, so the tab still reads no database.

## 15. Real time in the sort (723)

- **What**: the hub table sorts by day-ahead energy; real time is shown beside it where held, but no sort uses it.
- **Yes**: a sort by real time, or by day-ahead less real time, with the rows that hold no real time last.
- **Recommendation: day-ahead less real time**, the spread a trader reads; the plain real-time sort adds little to the day-ahead one.

## 16. A 2026 sub-region table (728)

- **What**: the zone growth is 2025 over 2024, since no sub-region table holds 2026 before late July.
- **Yes**: the data machine keeps `eia930_subba_demand_hourly_2026`, and the zone growth takes the grid's twelve months.
- **Recommendation: yes**; one connector run.

## 17. The tracker's operating utility (729)

- **What**: 3 of 422 tracked facilities name a utility, each a holding company.
- **Yes**: the tracker's extraction records EIA-861's operating utility, so the tab can place a facility by it.
- **Recommendation: not now.** Most unplaced facilities are abroad or in split states; a utility would place few.

## 18. The OpenEI key (730)

- **What**: the large-load tariff table waits on an `OPENEI_API_KEY` in the data machine's `.env` (the NREL developer network). Session 730 wrote the tab's side, not wired.
- **Recommendation: yes**, the one step it needs. Where the table holds a utility's large-load rate, CAISO's and SPP's rows could gain an all-in figure.

## 19. Migration 036 (716, 721)

- **What**: session 580's two partial indexes, written and not applied. The tab reads no database, so it needs none.
- **Recommendation: leave it unapplied** until a page's read is slow.
