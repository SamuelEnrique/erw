# Tax rules of the economic impact tool, one row per rule with its citation

Energy Research Warehouse (ERW), method note written in session 2074 (chain 067) for a table first written on 20 October 2026 (session 346).

Tables: `impact_tax_rules`

## Publisher and address

No publisher is asked. `warehouse/derived/impact_tax_rules.py` (session 346) reads `site/data/severance_rules.json`, the record of the severance rules the `/severance` page holds (sessions 40 and 41, every rate read as text on 30 September 2026 from the page that states it), and adds one row for each property-tax treatment the ERW does not hold. The run makes no request. The citations the rows carry:

| Source id | Publisher | Rows |
|---|---|---|
| `la_legislature:la_rs_47_633` | Louisiana State Legislature, La. R.S. 47:633 (`https://legis.la.gov/Legis/Law.aspx?d=102399`) | 14 |
| `tx_cpa:tx_cpa_gas` | Texas Comptroller of Public Accounts, Natural Gas Production Tax (`https://comptroller.texas.gov/taxes/natural-gas/`) | 8 |
| `nm_trd:nm_trd_rates_2026` | New Mexico Taxation and Revenue Department, rate spreadsheet for 04/01/2026 to 08/31/2026 | 6 |
| `tx_cpa:tx_cpa_oil` | Texas Comptroller, Crude Oil Production Tax (`https://comptroller.texas.gov/taxes/crude-oil/`) | 5 |
| `la_ldr:la_rib_26_013`, `la_ldr:la_rib_26_014` | Louisiana Department of Revenue, Revenue Information Bulletins 26-013 and 26-014 | 3, 2 |
| `nm_trd:nm_trd_taxes` | New Mexico TRD, Oil and Gas Production Taxes | 2 |
| `tx_cpa:tx_cpa_lp_gas`, `tx_cpa:tx_cpa_lp_oil` | Texas Comptroller, the low-producing well and lease credits | 1, 1 |
| `erw:impact_tax_rules` | the ERW's own record that it holds no rule (`https://erw-flame.vercel.app/data/methods/economic_impact`) | 7 |

The full addresses are in `sources.csv` and in the table's header.

## Vintage and revision

One run, `20261020T083345Z` (20 October 2026), from `severance_rules.json` version 2026-09-30.2. The file on the data machine was rebuilt from the ERW archive by `warehouse/restore_tables.py`, as of run `20261020T083547Z-local`. Header: "File holds 49 rows, one snapshot; the previous file held 49 rows."

Each run replaces the table (`write_snapshot`). A rate changes only when `severance_rules.json` changes; the script itself reads no page again.

## Shape and variables

Events, 49 rows, one per rule; `event_id` `erw_tax:<state>:<rule>`, none given twice. Texas 18, Louisiana 21, New Mexico 10.

| `event_type` | Rows | `status` |
|---|---|---|
| severance_tax | 16 (14 base rates and Louisiana's two oil rates by completion date) | held |
| severance_fee | 2 (Texas oil 0.00625 a bbl, gas 0.000667 a Mcf, in `x_per_unit`) | held |
| severance_option | 24 (reduced rates, exemptions, credits) | held |
| property_tax_rule | 7 | no_rule_held |

`event_date` is the effective date where the citation gives one as a single date (Texas oil 1951-09-01, condensate 1953-08-27, gas 1969-10-01); else the day the rule was read, 2026-09-30 (39 rows, the citation's own words in `x_effective_text`, such as "2026-07-01 to 2027-06-30"); the seven property rows carry 2026-10-20, the day the repository was searched. `x_date_kind` says which. `parties` is the citation's publisher (empty on the property rows); `mw`, `price`, `currency` and `entity_ids` are empty.

The rule itself is in the `x_` columns: `x_state`, `x_tax` (severance or property), `x_product` (oil 20, gas 19, condensate 3, generating_project 7), `x_rule`, `x_rule_name`, `x_kind`, `x_basis` (pct_value 15, per_unit 1), `x_rate` (a fraction of value, such as 0.046 for Texas oil, or with `x_basis` per_unit an amount a unit, Louisiana gas 0.1514 a Mcf; "variant" or "district" where the rate is given elsewhere), `x_per_unit` and `x_unit`, `x_who`, `x_what`, `x_how_long`, the page's words in `x_quote` (42 rows) and `x_quote2`, the statute in `x_code_section`, `x_code_quote` and `x_code_url` (13 rows), other fields of the record as JSON in `x_detail`, and `x_applies_to`. Every severance row says it applies to oil and gas production, which none of the tool's technologies produces.

The property rows name Texas's general ad valorem tax and Tax Code chapters 312 and 313, Louisiana's general tax and ITEP, and New Mexico's general tax and Industrial Revenue Bonds; each states that no statute is held and no figure is given.

## Reading the source

- Each base rate, fee and option of each product in the JSON is one row; each of a product's variants is one row that takes the base rate's citation.
- A citation's publisher must be one of five in the script's map, or the run stops; an `event_id` given twice stops it.
- A failed run writes nothing and logs the error.

## License

`license_tables.csv` lists the table under the Louisiana Department of Revenue, the Louisiana State Legislature, the New Mexico Taxation and Revenue Department and the Texas Comptroller of Public Accounts. `license_verdicts.csv` records the Texas Comptroller, read 148 (session 942): "may be public", "Information on CPA's sites is public domain and may be copied and used as permitted by law, with the exception of pictures, official symbols, and registered service marked names and logos." It holds no row for the other three publishers. `docs/licenses.md` lists the table as "not settled (needs written permission by default)", not read: Louisiana Department of Revenue, Louisiana State Legislature, New Mexico Taxation and Revenue Department; flag public, ERW verdict unsettled.

## Cross-checks (session 2074)

- The counts above were computed from the rows, read past the header lines.
- The 42 severance `event_id` values equal the 42 rules of `site/data/severance_rules.json` version 2026-09-30.2 in the worktree, and the 40 base, fee and option rows carry the JSON's rate exactly in 40 of 40.

## What it does not hold

- Any property-tax rate, abatement or exemption: seven rows state that none is held.
- Severance rules of any state but Texas, Louisiana and New Mexico, and any rule read after 30 September 2026.
- A row for each New Mexico ad valorem district: the districts' rates are a JSON list in `x_detail` of the two ad valorem rows (`x_rate` "district").
