# Note: lab-desktop window 4, 13 November 2026, chain 240 (the forecast tool continued, Local impact)

Energy Research Warehouse (ERW). Sessions 4250 to 4263 and 4266 to 4268, about 13:50 to 17:45 UTC; 4264 and 4265 were not needed. Model spend USD 0. Reports: `archive/sessions/SESSION_4250_REPORT.md` to `SESSION_4266_4267_REPORT.md`. Chain 239's note: `docs/state/note_2026-11-13_desktop_window4.md` (kept up to date through this chain as well). Method (internal, never on the page): `docs/methods/forecast.md`. Faults: `docs/reviews/forecast-faults-2026-11-13.md` (21 rows). Review pack: `docs/reviews/packs/impact.md`, rewritten for the forecast.

## What changed since chain 239's note

- **Property tax statutes added**, each read from the state's own page with its robots file first and quoted in `site/data/forecast/property_rules.json`:
  - Wyoming: the wind generation excise, USD 1 per MWh from the fourth operating year, added to the reader's own property tax rate.
  - Florida, Arizona and North Carolina: shares of the value exempt, applied to the reader's own rate. Florida exempts 80 percent through 2037, Arizona values equipment at 20 percent through 2040, North Carolina excludes 80 percent with no end date.
  - Michigan: the solar specific tax, USD 7,000 per MW AC (USD 2,000 on some sites) for 20 years where a township or city establishes a district. Off by default.
  - Vermont: the solar capacity tax, USD 4 per kW, added to the reader's own rate.
  - Wisconsin: the state pays the municipality and county USD 5,000 per MW a year in place of the property tax.
  - Nevada: 55 percent of the property tax abated for 20 years where approved. Off by default, applied to the reader's own rate.
- **Statutes read and not held:**
  - Montana, Colorado and New Mexico: no formula in statute.
  - Nebraska's sales tax exemption for community-based projects: repealed by LB901.
  - North Dakota's exemption reaches power plants but not new wind.
- **Cross-check:** six studies of seven projects, and a tax check. New since chain 239:
  - Indiana's first 1,000 MW of wind: 1.03 of its construction jobs.
  - Rush Creek, Colorado: 0.51 of its construction jobs, because its turbines were made in Colorado.
  - NREL's Wyoming study, gas plant: 0.96 of its construction jobs and 0.90 of its sales tax.
  - The same study, wind plant: 1.03 of its construction jobs, and the generation tax within 1 percent.
- **Faults 19 to 21:**
  - 19, fixed: a sentence under the other states' jobs chart became a tip.
  - 20, fixed: the table now shows Wyoming's MWh column.
  - 21, open: the other states' taxes chart writes neighbouring figures into each other at 1280. It is a ruling with fault 13.
- **Check addresses:** a fifth and a sixth (Oregon with North Dakota; Michigan with Vermont). The last read gave 937 of 937 on the six.
- **Downloads:** the Python file and the do-file carry every new rule kind: a capacity tax that adds to the property tax, an exclusion with no end year, an exclusion behind the switch.

## What waits in which landing row (`docs/state/landing_request_desktop_w4.md`, on main)

- Row 1 landed at `71f8442ed`.
- Row 2 (`wip/4220-forecast`, `52dc1001a`) and row 3 (`wip/4225-forecast`, `925e9e481`) are requested.
- Row 4 (`wip/4250-forecast`, `c84bc11aa`, or a later commit of reports and notes) holds rows 2 and 3, so landing row 4 lands everything. It has been built and read; the 179 related test files gave 2,222 passed, 0 failed.

## Sources missing, refused or paid

- **BLS:** both hosts refuse automated reads.
- **BEA:** its flat files are disallowed and its API needs a key. The deflator comes from EIA's STEO.
- **Illinois's statute site:** answers "Access Denied".
- **Ohio's code site:** disallows every path.
- **Texas's statute site:** builds its pages by script, so they can't be read as text.
- **The Lincoln Institute's study:** its host disallows automated reads.
- **County levies:** none held. Data request row 5 asks window A for Texas's.
- **West Virginia's gas plant study:** its host names Claude's agents in its robots file.
- **Tax Foundation's tables:** CC BY-NC 4.0.
- No paid source was used.

## Rulings waiting (default in brackets)

1. The page's name ["Local impact"].
2. A BEA API key [STEO's copy of the deflator].
3. BLS QCEW [not used].
4. Tax Foundation's CC BY-NC tables [used with attribution while the ERW sells nothing].
5. The Lincoln Institute study [not used].
6. Whether Iowa's solar exemption reaches racking and wiring [it does not].
7. Texas's sales tax exemption share [0, an upper bound].
8. Kansas's exemption [assumed granted].
9. Oregon's fee [USD 7,000 per MW].
10. Virginia's revenue share [left out].
11. Illinois and Ohio [no rule held].
12. The shared chart's spacing, faults 13 and 21 [left as it is].
13. Whether a Vermont plant also pays the education property tax [not held].
14. Whether Wisconsin's payments belong on the property tax line, and whether its per-resident caps should be an input [on the line; caps not modeled].
15. Whether `docs/methods/economic_impact.md` stays as the table's method [it stays].

## Data requests for window A (`docs/state/data_requests_forecast.md`)

- Rows 1 to 5 are still requested: the deflator, JEDI's cost per MW, the property rules as a table, the forecast parameters, and Texas's rates by taxing unit. None is done, so the page still reads `site/data/forecast/`.
