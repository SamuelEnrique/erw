# Session 297: the battery's finance model, passes 2 to 4

Screenshots in the internal view at 1280 and 390 px, quantized to 32 colors, 19 October 2026, each page in its default
state (the box's two open sections open, the three closed ones closed). "Before" is production serving session 296;
"after" is the local build of branch `wip/297-battery-finance`. Taken with `runs/chain_oct19/capture296.mjs`, which
also kept each page's checked numbers and visible text under `runs/chain_oct19/s297/` (not in git).

| File | Address | What it shows |
|---|---|---|
| `before_battery_*.png`, `after_battery_*.png` | `/cost-of-power/battery` | the default page: the stress test row joins "Is it worth building?", at 0 |
| `before_battery8_*.png`, `after_battery8_*.png` | `/cost-of-power/battery?grid=ercot&dur=8&strat=dayahead` | the 8-hour battery, unchanged |
| `before_caiso_*.png`, `after_caiso_*.png` | `/cost-of-power/battery?grid=caiso&dur=4&strat=dayahead` | CAISO: the stress test names its own largest notice window |
| `after_set_*.png` | `/cost-of-power/battery?ai=30&ao=1&am=5&ax=1` | a 30 percent credit, the fade method with augmentation every 5 years, one repeat of Winter Storm Uri: the headline's coverage holds, NPV and IRR move |

What to look at, after:

1. "Is it worth building?": the row "Stress test: scenario A repeats Winter Storm Uri, February 2021 [0] times over its life", with the event's window revenue per kW under it.
2. Open "Financing" in the box: after the hurdle rate, "Investment tax credit, percent of capital cost" (0); the sub-group "Degradation and augmentation": "Degradation method" (revenue cut), "Capacity fade" (2.6), "Augmentation" (none), "Augmentation cost" (241); then "The contract".
3. `after_set_1280.png`: the box's Financing line reads "..., no contract, 30% tax credit, capacity fade 2.6% a year restored every 5 years"; the results table's NPV and IRR differ from the default; "What matters most" by a percent step would draw the credit's and the fade's rows.

Every checked number at the default is the same before and after (660 of 660 check-values keys, no key gone, no key new, no value changed).
