# Session 2125 report: the licenses' eighteenth round

23 October 2026, from 23:05 UTC, on lab-desktop (the data machine), the sixth session of `queue/done/079-day-28-october-data-quakes-credits-rates-world-renewables.md`, unattended. Model spend USD 0. Pulls: 9 requests of 20 (below). (Session 2124's six method notes were drafted by a helper beside this session and are checked in session 2124's report.)

## Read these first

- **This chain's publishers first:** the USGS (read 87), EPA (read 55) and Berkeley Lab already have verdicts; Eurostat's was added in session 2123 (read 280). FEMA's verdict stands (read 217), its National Risk Index host refusing the reader (read 274).
- **Our World in Data, for session 2126** (a new verdict, may be public in both columns, read 284): its energy dataset's README says everything Our World in Data produces is under CC BY 4.0, and "The data produced by third parties and made available by Our World in Data is subject to the license terms from the original third-party authors"; its FAQs (read 282) say the same. Its energy dataset compiles the Energy Institute's Statistical Review, Ember's yearly electricity data, EIA's international data and a few historical sources; the new dataset's sources file (read 286) names each source and states no license, and its codebook names the sources of each of its 130 columns.
  - So session 2126 takes only the columns whose every source has a verdict that allows them: EIA (record 1), Ember (record 133, CC BY 4.0) and Our World in Data's own processing. The Energy Institute's columns wait on the Energy Institute's terms (www.energyinst.org refuses the ERW's reader, chain 067).
  - **Ember's data through Our World in Data:** Ember's own file host disallows readers (session 924), which is why no ERW table holds Ember's data; Our World in Data's catalog host allows every path (read 285), and Ember's license allows the redistribution. Taking Ember's columns there is a decision written below.
- **IRENA's terms from another address** (chain 068 could not read www.irena.org): IRENASTAT's landing page on pxweb.irena.org lists the tables and states no terms (read 288), and chain 068's saved table metadata holds none. `irena_capacity_annual` stays "not settled".
- **The other publishers without a verdict** were not asked again: FERC, the Public Utility Commission of Texas, the Corps of Engineers and the Transportation Energy Data Book wait on standing rulings; the state commissions, revenue departments and Grant PUD were each read in rounds of sessions 902 to 914 and 928 without a page that grants or refuses reuse (reads 47 to 129, 185 to 187); the news outlets' tables are internal.
- **The record:** 416 tables, 93 publishers with a verdict, 250 requests; the license check finds no problem.

## The pulls

1. `ourworldindata.org/robots.txt` (read 281): a sitemap, no rule.
2. Our World in Data's FAQs (read 282).
3. `raw.githubusercontent.com/robots.txt` (read 283): HTTP 404, no robots file.
4. The energy dataset's README on GitHub (read 284): its License section.
5. `catalog.ourworldindata.org/robots.txt` (read 285): allows every path.
6. The new energy dataset's sources file (read 286).
7. Its codebook (data for session 2126, not a license read).
8. `ember-energy.org/robots.txt` again (read 287), before deciding on Ember's columns (read 132 had found the same).
9. IRENASTAT's landing page (read 288).

## Errors

- **Request 8 repeated read 132** (Ember's robots file, read this morning); the record already held it.
- **Decision 65 renumbered to 66** during this session: chain 068 landed Decision 62 (`degC`), and chain 069's three units take 63 to 65, as the agents of chains 069 and 090 agreed. The data standard, the validator's comment, the TRI connector, its test and sessions 2120 and 2121's reports were corrected; `epa_tri_energy_releases_annual`'s header, written with 65, is written again in session 2129.

## Decisions made without you

- **No repeat reads** of publishers earlier rounds found without terms.
- **Ember's columns taken through Our World in Data's catalog** in session 2126: Ember's CC BY 4.0 allows them and the catalog host allows the reader; Ember's own file host is not asked.
- **Our World in Data's verdict as "may be public"** for its own work, with each column following its sources' verdicts.

## For Samuel's ruling

- **Ember's data through Our World in Data:** taken in session 2126 on the reading above; if you would rather Ember's own host decide, say so and the columns are dropped.
- **The Energy Institute's terms** decide the rest of Our World in Data's energy columns, as they decide the Statistical Review (chain 067's note).

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv` (281 to 288), `warehouse/metadata/license_verdicts.csv` (Our World in Data), `docs/licenses.md`; the Decision 66 corrections above.
- On the data machine only: `runs/c079/s2125/`, `runs/license_reads/s2125/`.
