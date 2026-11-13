# Session 4201 report: the parameters and the method note (chain 239, window 4)

13 November 2026, about 10:30 to 10:45 UTC. Branch `wip/4200-forecast`. Model spend USD 0.

- **EIA's capital cost by state** (`warehouse/forecast/eia_capex.py` to `site/data/forecast/eia_capex.json`): the AEO2025 study's Appendix A, wind, PV and gas for 48 states and DC, geothermal for the 5 states EIA gives (N/A elsewhere, kept as "not given"); each case's construction time, operating life and (gas) heat rate from its own table.
- **Generated parameters** (`warehouse/forecast/params.py`): the GDP deflator (EIA STEO's copy of BEA's series), Tax Foundation's 2026 sales tax and income tax tables, state capacity factors and the PV loading ratio from LBNL's tables joined to EIA-860 plant states.
- **Statute rules read** (`property_rules.json`, each quoted): Minnesota's wind and solar production taxes, South Dakota's capacity and production taxes in lieu of property tax, Nebraska's nameplate capacity tax, Iowa's special valuation of wind property.
- **JEDI's taxable share** of construction spending (`jedi_taxable.json`), with its cells; one arithmetic slip of mine (wind 0.819258) found by recomputing and corrected to 0.819282 before anything read it.
- **The method note** `docs/methods/forecast.md`, internal: added to `INTERNAL_METHODS` in `site/scripts/build-content.mjs`, so the site's method pages never show it.
- **Refused or failed, not bypassed:** codes.ohio.gov (robots: disallow all), www.ilga.gov (certificate verification failed), storage.pardot.com (the Lincoln study; robots: disallow all), BLS (both hosts).

## Decisions made without you

- Default discount rate 7 percent real (OMB A-94's base case), with Appendix C's 2.0 percent named in its tip.
- A state with several EIA cities takes their plain mean; a state EIA does not give takes EIA's base case.
- Construction years are EIA's construction months rounded up to whole years.
- Property tax only from a statute read; elsewhere the reader may type an effective rate (no default).

## For Samuel's ruling

- **Tax Foundation's tables are CC BY-NC 4.0.** Default: used with attribution while the ERW sells nothing; replaced by state statutes before any paid product.
- **The Lincoln Institute study** (effective property tax rates): its host refuses automated reads. Default: not used. One manual download by you would let a session read it.
