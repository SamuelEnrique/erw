# "Your load" and All grids, side by side (22 October 2026)

Energy Research Warehouse (ERW), session 775 of chain 064. Every figure both views of `/cost-of-power` draw for the same place, read from one build (`wip/775-allgrids`, the internal view): "Your load" at its default (ERCOT LZ_NORTH, 100 MW) and the All grids tab's row `ercot:LZ_NORTH`. The keys and raw values are in `runs/chain_062/keys775.json` on this machine (234 keys on "Your load", 519 on the tab).

| Figure | "Your load" | All grids | Equal? |
|---|---|---|---|
| ERCOT's large loads approved to energize, newest report (2026-06-19), MW | `ll:report:2026-06-19:approved` 8,927 | `allgrids|llapproved|ercot:LZ_NORTH` 8,927 | **Yes** |
| Energy, day-ahead, twelve months | not a keyed figure on "Your load" (its price is drawn by its own chart) | `allgrids|energy|ercot:LZ_NORTH|da` 35.33 | **Yes by construction**: one function computes both (`lib/datacenter.ts` through `lib/siting.ts`), held by `tests/test_session701.py` (OK on this branch) |
| Carbon, kg CO2 per MWh | twelve months, consumption-based, EIA-930's hourly intensity: `co2:l12:kg:flat` 303.14 | eGRID's subregion, annual, generation-based: `allgrids|carbon|ercot:LZ_NORTH` 332.87 | **Different measures, by design**, each tip says which. Rulings item 7 asks whether All grids' annual figure should be consumption-based too |
| Transmission | the wires utilities' delivery charges (`dcd|100|oncor:transmission` and the others) | the four-peak charge, `allgrids|tx|...` 7.83 | **Different charges**: "Your load" shows the utility's delivery tariff, All grids the four-peak transmission charge. Neither is drawn by the other view |
| Time to connect, demand growth, capacity above the peak | not drawn as keyed figures on "Your load" | 45.80 months; +5.41 percent; 97 percent | Not comparable here |

**No difference is a fault**, so nothing was fixed. Two of the rows compare measures that differ on purpose and say so in their tips: carbon (rulings item 7) and transmission, where the views draw different charges.
