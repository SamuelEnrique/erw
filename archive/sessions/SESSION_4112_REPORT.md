# Session 4112 report: two names that missed their verdicts, and four copyright lines

Energy Research Warehouse (ERW). Chain 229, session 13 of 50, lab-desktop third window, 13 November 2026 11:29 to 11:34 UTC. Opus 5.5. Model spend USD 0. Branch `wip/4110-licenses`.

## Two verdicts the document could not see

- **The registry names differed from the verdict keys:** "Centro Nacional de Control de Energia (CENCE, ICE)" against "(CENCE, ICE, Costa Rica)", and "Viceministerio de Minas y Energia (VMME), Paraguay" against "Viceministerio de Minas y Energia, Paraguay (VMME)". Their verdicts (needs written permission, reads 678 and 1092, sessions 2390 and 2445) were written, but the document listed the publishers as unread.
- **The fix:** two `CANON` rules in `scripts/licenses.py`, and `licenses.py tables` run again over the data machine's headers (read only). Exactly those two rows of `license_tables.csv` changed.
- **GASTAT is not a mismatch:** its verdict excludes "clearly identified third-party material", and these tables name the Ministry of Energy as their source.

## Four verdicts from pages read again (reads 1776 to 1783; robots first)

- **The precedent:** CNDC's (read 1026): a copyright line and no grant means "needs written permission".
- **State Statistical Office of North Macedonia:** "© State Statistical Office" (read 1780, the English home page).
- **Central Statistical Office of Grenada:** "The materials located on this website [...] are protected by copyright [...] All rights, title and interest in the Contents are owned by, licensed to or controlled by the CSO. [...] Access and use of the Data is subject to the requirements set forth under the Open Licence Agreement." (read 1781). The agreement's page has no text (read 845), so no licence can be read.
- **ERU, Czechia:** "2026 © Energetický regulační úřad • Informace jsou poskytovány v souladu se zákonem č. 106/1999 Sb., o svobodném přístupu k informacím." (read 1782). That law governs access, not reuse.
- **HOPS, Croatia:** "© 2026. Hrvatski operator prijenosnog sustava d.d." (read 1783). Its terms page covers personal data only.
- **Their tables are all internal,** so they now agree.

## The tool

- **`license_confirm.py verdict --start PHRASE`:** a footer's notice that ends a run of menu words is cut from that phrase on, still the page's own words. Tested.

## Counts

- **Agreement:** 539 agree, 52 settled by a ruling, **0 disagree**, **31 not settled** (71 at session 4100), 24 waiting for a ruling.
- **Package record and checks:** `build_tables.py` written again; `build_llms.py` and `release_v1.py` agree.

## Tests

- **Tests 205, 4101, 4109 and 378:** 43 passed.

## Decisions made without you

- **A copyright line with no grant reads as "needs written permission",** as earlier sessions read CNDC's and CENCE's.

## For Samuel's ruling

- None new.
