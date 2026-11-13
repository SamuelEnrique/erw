# Sessions 4217 and 4218 report: requests, exemptions, waiting for the build lock (chain 239, window 4)

13 November 2026, about 11:13 to 11:36 UTC. Branch `wip/4200-forecast`. Model spend USD 0.

- **4217**: data requests 3 to 5 for window A (`docs/state/data_requests_forecast.md`: the property rules into `impact_tax_rules`, the forecast parameters as a table, Texas's rates by taxing unit); the landing request file `docs/state/landing_request_desktop_w4.md` (no row yet); fault 5's count corrected.
- **4218**: sales tax exemptions read from statutes become the default exemption (`site/data/forecast/sales_exemptions.json`, quoted): Minnesota wind (297A.68, subd. 12: 100 percent), Iowa wind (423.3(54): 100 percent) and Iowa solar (423.3(90), "solar energy equipment": the modules and inverters, 67.2 percent of the tax on JEDI's materials and equipment). Tests 20 of 20.
- **Wyoming** (the wind generation tax, USD 1 per MWh): only third-party copies of the statute were found, so it waits; the state's own compilation is the source this tool cites.
- **The build lock**: held by window B's gates (`c226-gate` from 10:53, `w2-s4003` from 11:17). Two waits of 9 minutes each (11:18 to 11:36) did not get it. The page is type-checked and its tests pass; it has not been built or read in a browser yet.

## For Samuel's ruling

- **Iowa's solar exemption** (423.3(90)): whether "solar energy equipment" reaches racking and wiring. Default: it does not (67.2 percent of the tax exempt).
