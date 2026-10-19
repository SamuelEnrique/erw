# Session 298: the generator and datacenter pages, the section 9 rulings

Screenshots in the internal view at 1280 and 390 px, quantized to 32 colors, 19 October 2026, each page in its default
state. "Before" is production serving session 297; "after" is the local build of branch `wip/298-generator-datacenter`.
Taken with `runs/chain_oct19/capture296.mjs`, which also kept each page's checked numbers and visible text under
`runs/chain_oct19/s298/` (not in git).

| File | Address | What it shows |
|---|---|---|
| `before_seller_*.png`, `after_seller_*.png` | `/cost-of-power/seller` | solar in ERCOT: the Financing fold around the assumptions (open), the two chart notes as hover tips, "Degradation 0.7" with the ATB as its source, the decisions line in the source line |
| `before_peaker_*.png`, `after_peaker_*.png` | `/cost-of-power/seller?iso=caiso&asset=peaker` | the CAISO peaker: the margin over fuel falls from USD 43.19 to 19.66 per kW with the allowance in its run rule; the panel's note names the allowance and its source |
| `before_datacenter_*.png`, `after_datacenter_*.png` | `/cost-of-power` | the datacenter page: the Assumptions fold around the panel (open); nothing else moves at the defaults |

What to look at, after:

1. The generator page: "Is it worth building?" opens with "Financing" and a minus marker; close it and the line reads "Scenario A: 60% debt at 8%, 12% hurdle, no contract". The marks beside the two chart titles are hover tips.
2. The CAISO peaker: "Margin over fuel, last twelve months: USD 19.66 per kW" (43.19 before); the hours run 624 (2,294 before); the panel's note ends with California's allowance, USD 32.48 per tCO2 at the latest auction, USD 1.72 per MMBtu.
3. The generator page's source line: "Checked against: 21 published figures (..., Potomac Economics)" and the decisions line on solar's degradation.
4. At 390 px nothing scrolls sideways (page width 390 in a 390 window, every address).

Every checked number on the three default pages is the same before and after (234, 225 and 660 keys; no key gone, none new, no value changed). The CAISO peaker page is not a check-values page; its figures are the ones the methods note states.
