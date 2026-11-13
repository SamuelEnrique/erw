# Session 4103 report: the impact tax publishers and the dams

Energy Research Warehouse (ERW). Chain 229, session 4 of 50, lab-desktop third window, 13 November 2026 10:30 to 10:45 UTC. Opus 5.5. Model spend USD 0. Branch `wip/4100-licenses`.

## Read

- **3 robots files** (reads 1693 to 1695): revenue.louisiana.gov and www.legis.la.gov have none (404); www.tax.newmexico.gov allows the page.
- **4 pages** (reads 1696 to 1699):
  - the Louisiana Department of Revenue's terms: read;
  - the Louisiana Legislature's disclaimer: read, no terms of reuse;
  - New Mexico Taxation and Revenue's privacy and security page: read, no terms of reuse (the site has no terms page);
  - data.gov's catalog API for the National Inventory of Dams: 404.

## Verdict (1 new; 264 publishers with a verdict)

- **Louisiana Department of Revenue: needs written permission.** "This website contains material which is owned by or licensed to us. This material includes, but is not limited to, the design, layout, look, appearance and graphics. Reproduction is prohibited other than in accordance with the copyright notice, which forms part of these terms and conditions." (read 1696, https://revenue.louisiana.gov/terms/, 13 November 2026)
- **`impact_tax_rules` is now "license needed"** (the standing ruling of 12 October), and is out of release v1: 135 tables in v1, 49 held. `licenses.py status`: 49 tables.
- **Not settled, as before:**
  - the Louisiana Legislature and New Mexico Taxation and Revenue (pages read, no terms);
  - USACE's National Inventory of Dams (two addresses answered 404). `usace_nid_dams` stays flagged public and unsettled.

## Fixed

- **A bad README:** the chain's helper (`erw-w3-work/sync_held.py`, outside git) wrote files through unflushed handles. One `release_v1.py --calls-only` therefore read a cut file and wrote a README saying 119 tables. Test 275 caught it; the README was written again (135), and the helper now closes its files.

## Tests

- **License, package and release tests:** 972 passed, 30 skipped, 1 failed (275, the README above). Then 275, 207, 215 and 248: 44 passed.

## Decisions made without you

- **A page with no terms gives no verdict.** The Louisiana Legislature's and New Mexico's pages say nothing of reuse, so neither is read as a permission or a refusal. Their table's verdict is decided by the Louisiana Department of Revenue's anyway.

## For Samuel's ruling

- **`impact_tax_rules`:** held because it cites the Louisiana Department of Revenue, whose terms forbid reproduction outside their copyright notice. The table holds state tax rules (law), which courts treat as uncopyrightable (the government edicts doctrine). **Default: held** until you rule that statutes and rule citations are not the department's material.
- **`usace_nid_dams`:** stays flagged public, unsettled (USACE's pages not read). **Default: unchanged**, since the flag is the owner's earlier choice and it is not loosened.
