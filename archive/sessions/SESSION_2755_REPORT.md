# Session 2755 report: the licenses' sixtieth round (WAPA, SWPA and SEPA may be public, under DOE's notice; TVA's terms unreadable)

25 October 2026, about 22:12 to 22:13 UTC, on lab-desktop (the data machine), chain 139, unattended. Precheck passed (`runs/c139/pre2755.out`). Model spend USD 0. Pulls: none of 20.

## Read these first

- **`license_verdicts.csv` was read first.** None of this chain's publishers had a verdict: the Tennessee Valley Authority, the Western Area Power Administration, and the Southwestern and Southeastern Power Administrations.
- **Three verdicts, "may be public"** (`runs/c139/s2755_verdicts.py`), each from DOE's Web Policies (read 54, outcome exactly `read`). The sentence was copied by code from the Bonneville Power Administration's verdict, which rests on the same read (session 2047's form): "Government information at DOE websites is in the public domain. [...] it is requested that in any subsequent use the Department of Energy be given appropriate acknowledgement."
  - **WAPA:** one of DOE's power marketing administrations. Its own Web Policies (read 1490) state no copyright or reuse term. **This settles `wapa_energy_sales_annual`:** its flag (public) and the verdict now agree.
  - **SWPA and SEPA:** their pages and reports are on www.energy.gov itself (reads 1494 and 1497). The ERW holds no table of either; the verdicts serve a later chain.
- **TVA not given a verdict:** its terms are on www.tva.com, behind a Cloudflare challenge (session 2750). TVA is a federal corporation, not a DOE agency, so DOE's notice does not cover it.
- **The record:** 600 tables, 250 publishers with a verdict, 0 problems; the verdict: 438 public, 112 internal, 50 unsettled. Tests 378, 205 and 152 pass (36 tests).
- Sessions 2756 and 2757 come after this one, so their publishers fall to a later chain's round, as chain 138's did.

## Decisions made without you

- **DOE's notice taken for the three administrations,** as for the BPA. No request was spent re-reading it (read 54, six days old).

## For Samuel's ruling

- None new.

## Files

- New: this report. Changed: `warehouse/metadata/license_verdicts.csv` (three rows), `docs/licenses.md`.
- On the data machine only: `runs/c139/s2755_verdicts.py`.
