# Session 5301 report: the list's second round, the re-reads and the license audit

13 November 2026, unattended, `portable-laptop` window P4 (Opus 5.5, xhigh). Branch `wip/5300-large-load`, worktree `erw-p4`. Nothing built, nothing landed, no warehouse data written.

## Read these first

- **The dataset now holds 106 rows from 15 utility groups.** All 1,504 cites match exactly on their cited pages, checked again together at the end. Read it in `docs/research/large_load/utilities_2026-11-13.csv`.
- **Statuses:** 58 in effect, 18 approved, 29 proposed, 1 denied (Duke Energy Florida, 3 November 2026).
- **Licenses:** 87 rows public, 19 internal. Two public rows name fields that rest only on restricted hosts (`internal_fields`).
- **Requests on main (`0d7adb94d`):** data request rows 9 to 14 are new, row 8 is widened, and landing row 26 now points at `dab4c005d`.
- **Still reading:** the remainder group and the second co-ops group (the list); the 90-day pass in five groups (operators and FERC, South, East, Midwest, West); the first legislation group.

## What was done

- **Groups merged:** Ameren, Evergy and SPP (11 rows); Xcel and the Plains (9); TVA and the Southeast (6); co-ops and public power (4); the Northeast (10); the Great Lakes (7); the Northwest and Mountain (10).
- **Each group:** the form check, then every quote on its cited page, then one row in five read in place, then its notes and its commit.
- **Re-reads of documents that had failed only on this machine's certificate check:**
  - Texas: the adopted 16 TAC 25.194 now from the PUCT's own order; a statewide row; Oncor's facility extension terms.
  - Duke: the Florida PSC's vote sheet.
  - AEP: SWEPCO Texas from the PUCT's proposed order; the PUCO's DCT order found as a public copy in a Florida PSC filing.
  - Southwest: PG&E Rule 30 re-cited on the CPUC's own decision; NV Energy's Nevada docket, 26-05007.
- **The license audit,** applied in `merge_group.py` and run over the merged rows by `license_audit.py`:
  - each host's terms read and quoted (README, "The hosts' terms");
  - a row is internal when its main document, or every value, rests only on a restricted host;
  - a public row names its restricted-only fields in `internal_fields`;
  - the reader now refuses the hosts whose terms bar robots.
- **The reader's .docx and .xlsx reading.** It found the Georgia PSC's orders.
- **The forms and checks of the second pass** (`changes/`, `changes_<date>.csv`) **and the third** (`legislation/`, `legislation_<date>.csv`): `build_passes.py`, the checker, two tests.
- **Reads:** 831 documents cached in all.
- **The hand check:** 17 more rows in place, all pass (`docs/research/large_load/spotcheck_2026-11-13.md`).

## What was found

- **Rules adopted in 2026, for example:**
  - Pacific Power's Oregon Schedule 401, Order 26-443, entered today: 20 MW, 10 to 30 years.
  - Texas's 16 TAC 25.194: 75 MW and 50,000 USD per MW, effective 8 October.
  - Santee Cooper's L-27-HIL: 20 MW, 15 years, 180 months of collateral.
  - Wisconsin Electric's VLC.
  - LG&E and KU's EHLF.
  - IID's Schedule LL.
  - Minnesota's very large customer tariff.
  - New Jersey's Data Center Fair Share Act: at most 50 MW, 85 percent for 10 years.
  - Idaho Code 61-335.
- **Duke Energy Florida's large-load tariff was denied** on 3 November 2026, with an order to refile.
- **More queue sizes,** from the utilities' and commissions' own documents:
  - National Grid New York: about 7,792 MW requested.
  - LG&E and KU: over 6,000 MW.
  - Tri-State: about 5 GW.
  - We Energies: 4.9 GW expected.
  - Ameren Missouri: 2.8 GW signed.
  - DTE: 2.4 GW signed, plus a pipeline of 5 to 6 GW.
  - Grant PUD: about 800 MW.

## Decisions made without you

1. **Two more statuses, `denied` and `withdrawn`.** The prompt names three, but Duke Energy Florida's tariff was denied on 3 November, and writing "proposed" would mislead.
2. **A "see row" pointer may name any row of its group.** A holding company states one queue for several utilities: Evergy for Kansas and Missouri.
3. **Licenses by field.** A public row whose one figure rests on a restricted host stays public and names the field (`internal_fields`). Example: PGE's 1.7 GW pipeline, from its investor site.
4. **Words after a status date move to notes.** The merge keeps the date, YYYY-MM or YYYY-MM-DD, and records the words as the group wrote them.
5. **Unsearched utilities are not "none found".** The first co-ops group ran out of searches. Its unsearched list went to a second group rather than into `none_found`.
6. **The 90-day pass and the first legislation group started while the list's last two groups were still reading.** Slots were free, and neither depends on those two groups.

## For Samuel's ruling

1. **The license list is now twelve of window A's registry files** (data request row 8). Default: hold each internal until it is re-read from a commission's copy.
   - Public copies are named where found: Rule 30 at the CPUC, Oncor's tariff at the PUCT, AEP Ohio's DCT order in a Florida PSC filing.
2. **Lincoln Electric System's rate book says "may not store".** The reader keeps a copy, so the Xcel group did not read it. Default: leave it unread.
3. **The Massachusetts DPU directive was read only on mass.gov,** and the group marked it internal. Default: internal until the DPU's file room serves a copy.
