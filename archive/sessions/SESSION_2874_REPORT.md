# Session 2874 report: the registry, the last named utilities, and the table written

5 November 2026, about 22:04 to 22:25 UTC, on lab-desktop (the data machine), chain 147, unattended. Model spend USD 0. Pulls: 4 of 25 (efis.psc.mo.gov 2, lpsc.louisiana.gov 1, puc.colorado.gov 1).

## Read these first

- **`utility_large_load_tariffs` is written:**
  - 10 rows, 4 schedules, 3 utilities: Georgia Power; Indiana Michigan Power (Tariff I.P., two schedules); Portland General Electric (Schedule 96). The rows are session 2872's.
  - The write ran under the data lock with `runs/c147/write_table.sh` and passed every step: the validator (PASS, its new `filing_cited` check with the branch's copy), coverage (public, sector power, tier source), the archive (run `20261105T220705Z-local`), `licenses.py tables/write/check` (0 problems) and the release package's rows.
  - It is not in the live set and not wired (session 2880).
- **No schedule was added in this session:**
  - **Ameren Missouri and Evergy:** EFIS (no robots file) runs its case search in the page's script; the search address answers the form, not a result.
  - **Entergy Louisiana and Xcel Colorado:** robots read (none at the LPSC; the Colorado PUC disallows only its CMS paths). Their large-load filings sit in separate e-filing hosts whose proceeding numbers I could not name with confidence, and no search was run to guess them.
- **The chain's fifteen utilities, where they stand:**
  - In the registry: Georgia Power, I&M, and PGE (in AEP Ohio's place).
  - Commission closed to this reader: NV Energy (robots disallows all), Duke Energy Carolinas (robots names ClaudeBot), Dominion (the SCC is paused).
  - Terms bar the utility's site: AEP Ohio.
  - No filed large-load schedule: PacifiCorp Utah (contracts one by one).
  - The commission posts no tariff: Alabama Power.
  - Not reached (to chain 148): Ameren Missouri, Evergy, Entergy Louisiana and Texas, Xcel Colorado, APS, SRP, Oncor and CenterPoint (`texas_delivery_charges`, internal: the utilities' sites restrict reuse, so its rows could not go into a public table).
- **Cross-check (this session's utility, Georgia Power):** no demand charge was recorded, because the 100 MW rules print none. So there is no EIA-861 check for it. Session 2872's I&M check stands.

## Decisions made without you

- **Oncor's and CenterPoint's four rows were not reused.** `texas_delivery_charges` is internal, and this table is public.
- **The search for the remaining utilities stopped** short of the ceiling: each needs a proceeding number or a page's script, and a guess costs requests on a commission's host.

## Files

- On `wip/c147-data`: this report; the table's metadata (coverage, sources, archive manifest, licenses, release rows), committed with session 2877's.
- On the data machine only: `warehouse/output/utility_large_load_tariffs.csv`, `runs/s2874/`, `runs/license_reads/s2874/`.
