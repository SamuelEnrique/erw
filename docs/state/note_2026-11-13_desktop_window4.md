# Note: lab-desktop window 4, 13 November 2026 (chain 239, the forecast tool, Local impact)

Energy Research Warehouse (ERW). Sessions 4200 to 4227 so far, from about 10:00 UTC. Model spend USD 0. Reports: `archive/sessions/SESSION_4200_REPORT.md` to `SESSION_4225_4226_REPORT.md`. Faults: `docs/reviews/forecast-faults-2026-11-13.md`. Method (internal, never on the page): `docs/methods/forecast.md`.

## What the tool does

- **`/impact` is now "Local impact"** (in review, under Economics, where "Economic impact" stood; the name is a ruling with that default). Master plan tool 17.
- For a wind, utility solar, gas or geothermal plant, typed or picked from EIA-860M's planned projects in the state (the pick names its county): each year from the first construction year to the last operating year, jobs (on site, supply chain, induced), earnings and output from NLR's JEDI models read for every state; property tax by the state's statute where one is read; sales and use tax on construction spending; state income tax on the earnings; severance on a gas plant's in-state fuel; present values at a real discount rate (default 7 percent, OMB A-94's base case).
- Inputs in a left box in five folding groups, every default in grey with its source in a hover tip, editable, with a Reset; scenarios A and B side by side; taxes and jobs by year (hover gives each year); the table by year (with MWh and taxable value where they apply); the scenario in other states (construction jobs, and the taxes' present value with whether each state's property tax is counted); downloads of the run: CSV, a Python script and a Stata do-file that recompute both scenarios and check the tool's totals.
- Every dollar is a 2025 dollar (BEA's GDP deflator, as EIA's STEO carries it). Defaults: EIA's capital cost by state (AEO2025 study, its location tables), EIA's construction time and life, LBNL's capacity factors by state, Tax Foundation's 2026 sales and income tax tables, JEDI's taxable share and default cost per state (read with JEDI's own formulas).
- Property tax statutes held: Minnesota (wind and solar production taxes), South Dakota (capacity and production taxes in lieu), North Dakota (generation taxes in lieu), Nebraska (nameplate tax), Iowa (special valuation by ordinance, needs the levy), Kansas (ten-year exemption), Oregon (solar fee in lieu by county agreement). Sales tax exemptions held: Minnesota wind, Iowa wind and solar equipment.

## The cross-check (method note, section 9)

- **Jayhawk Wind, Kansas** (2019 study): the model gives 0.82 of its construction jobs (supply chain 0.96, induced 1.07, onsite 0.40: the developer's own in-state spending) and 0.79 of its operating jobs.
- **Ohio utility solar** (Ohio University, 2020): 1.10 of its construction jobs, 1.16 of its direct jobs, but 3.5 times its operating jobs: JEDI's 2010 PV operating costs. The page's "operating spending" input lets a reader correct it.
- **Glendive Wind, Montana** (NextEra's summary of a 2024 study): its "approx. 400" construction jobs sit nearer the model's onsite figure (272) than its total (1,730); the summary does not say which it counts.
- check-values: every figure on the four `/impact` addresses matches its recomputation (78 of 78 at the last read).

## What waits in which landing row (`docs/state/landing_request_desktop_w4.md`, on main)

- **Row 1** `wip/4200-forecast` at `1a1008073`: the tool, its model, parameters, tests, check-values and menu.
- **Row 2** `wip/4220-forecast` at `52dc1001a`: the three readers' additions, Kansas, faults 14 and 15. Holds row 1.
- **Row 3** `wip/4225-forecast` at `b485a6eee` (fault 17's fix after it, to be read on a build): Oregon, fault 16. Holds rows 1 and 2. Landing row 3 lands all three.

## Sources missing, refused or paid

- **BLS** (QCEW, CPI): www.bls.gov and api.bls.gov refuse automated reads. **BEA's own tables**: its flat files are disallowed by robots and its API needs a key (the GDP deflator is read through EIA's STEO instead).
- **Statutes not readable**: Illinois (www.ilga.gov failed certificate verification; not bypassed), Ohio (codes.ohio.gov disallows all paths), Texas (statutes.capitol.texas.gov builds its pages by script), Wyoming (only third-party copies found).
- **The Lincoln Institute's 50-state property tax study** (effective rates on industrial property): its host disallows automated reads.
- **County levies**: none held in any state (data request row 5 asks window A for Texas's rates by taxing unit).
- **Tax Foundation's tables** are CC BY-NC 4.0: may be public as the ERW is today, need permission if the ERW sells anything.
- No paid source was used.

## Rulings waiting (default in brackets)

1. The page's name ["Local impact"].
2. A BEA API key, for BEA's own deflator [the STEO copy stands].
3. BLS QCEW [not used; JEDI's earnings stand].
4. Tax Foundation's CC BY-NC tables [used with attribution while the ERW sells nothing; replaced by statutes before any paid product].
5. The Lincoln Institute study, one manual download [not used].
6. Iowa's solar sales tax exemption reaching racking and wiring [it does not: 67.2 percent of the tax exempt].
7. Texas's sales tax exemption share for generation equipment [0: the figure is an upper bound and its field says so].
8. Kansas's exemption assumed granted by the Board of Tax Appeals [assumed].
9. Oregon's fee rate [USD 7,000 per MW, the statute's maximum].
10. Virginia's revenue share with a price forecast [left out].
11. Illinois and Ohio statutes, which this machine cannot read [no rule held].
12. The shared chart's label and figure spacing for long lives (fault 13) [left as it is; it would move every page].

## Data requests for window A (`docs/state/data_requests_forecast.md`)

- Rows 1 to 5: the GDP deflator into `eia_steo_forecasts`; JEDI's default cost per MW into `nlr_jedi_multipliers`; the property rules into `impact_tax_rules`; a forecast parameters table; Texas's property tax rates by taxing unit.
