# Session 236: "What a datacenter pays" on the brand

Screenshots of `/cost-of-power` in the internal view, a local build of branch `wip/236-datacenter`, 13 October 2026.
Each is the whole page, quantized to a 48-color palette to keep this folder small (the originals are in
`runs/session236/shots/`, not in git).

| File | What it shows |
|---|---|
| `datacenter_before_1280.png`, `datacenter_before_390.png` | the page as the branch stood at `c78835d4` (sessions 213 and 228, merged with main and the brand's foundation), in the site's own style |
| `datacenter_after_1280.png`, `datacenter_after_390.png` | the default page on the brand: ERCOT, the North load zone, 100 MW, flat, real time |
| `datacenter_two_sites_1280.png`, `datacenter_two_sites_390.png` | scenario B at a site of its own (`?bsite=caiso:TH_SP15_GEN-APND`): the table's heading, B's column, "What differs", "B against A", and B's site in each of the three answers |
| `datacenter_caiso_1280.png` | `?grid=caiso`: CAISO's notices as the second count beside the price level; no Texas delivery table |

After the hand-back (ERCOT's adders, 13 October, 09:25 UTC): `datacenter_adders_1280.png` is the default page with ERCOT's own signal counted from `ercot_rtm_price_adders` in the table "the two counts" (two rows where the line "is coming" stood), and `numbers_adders_before_after.txt` sets the checked numbers and the results cells of that build against the build of the branch as it stood. The earlier screenshots show the line "is coming" and the cached hourly carbon window.

What to look at:

1. The look: the battery page's (white page, Source Serif 4 titles, IBM Plex text and figures, a light rule above each
   title, no header band on a table). No rule was added to `app/tokens.css`.
2. "What will it pay?": under the cost table, "Delivery charges in Texas, USD per MWh": one row a component
   (transmission, distribution, other riders) and "Total delivery", a column a utility. No tariff line is on the page.
3. "Will the power be there?": the table "the two counts" under the three numbers. Its first row states the level
   (USD 1,000 per MWh, every grid); its second is the grid's own signal: for ERCOT the line that its reserve adders are
   coming, for CAISO its notices (two counts), for the other grids "not held".
4. "Which option is better?": the block's title "Scenarios A and B: two sites, or two contracts", the one line of how
   to use it, and the list "Scenario B's site".
5. The numbers: `numbers_before_after.txt` (every checked number and every results cell, before against after).
