# Session 5302 report: the second pass, what changed from 15 August to 13 November 2026

13 and 14 November 2026, unattended, `portable-laptop` window P4 (Opus 5.5, xhigh). Branch `wip/5300-large-load`. Nothing built, nothing landed, no warehouse data written.

## Read these first

- **`docs/research/large_load/changes_2026-11-13.csv`: 98 changes.** One row a filing, order, effective date, amendment, denial, suspension or hearing, each printed in the document its cite names.
- **The quote check:** all 364 cites match their cached pages.
- **By group:** South 29, East 21, West 19, operators and FERC 15, Midwest 14.

## What was done

- **Five reading groups**, one per region plus one for the operators' and FERC's documents. The forms are in the README, "The second pass". Merged by `merge_pass.py`, which checks form and dashes and that an "affects" pointer names a row of the same utility.
- **Stable row ids.** Each row stores its id; a re-merge keeps it (by utility and rule name), and a new row takes the next number.
  - Why: the AEP re-read had inserted a row, and three groups' pointers named the old numbers.
  - Those six pointers are remapped, and the test now checks every pointer.
- **`apply_change.py`** writes a change that alters a row's status into the row, cites included:
  - Alabama's Docket 33709 procedures: approved 6 October 2026.
  - Maryland's COMAR 20.96.01: in effect 28 September 2026.
- **Duplicates across groups dropped:** 25.194 twice, ERCOT's order of 20 August, Michigan Tariff LP, CAISO's Board approval, Tri-State's review cycle. Each file keeps a `dropped_duplicates` list.
- **The TVA Board resolution is written as "other", not "approved".** Its text layer is headed "PROPOSED BOARD RESOLUTION" and prints no approval.

## What was found

- **Florida:** on 3 November the PSC suspended the large-load tariffs of Tampa Electric, Florida Public Utilities and FPL, with hearings in 2027, and denied Duke Energy Florida's tariff.
- **Texas:** the PUCT proposed a standard large-load interconnection agreement (5 November). SWEPCO's settlement went to a proposed order (28 October).
- **Pennsylvania:** the PUC's tentative order on data center curtailment (1 October), clarified 5 November (now 50 MW). A consumer advocate's complaint against PPL's LP-6.
- **Operators:**
  - CAISO's Board approved its large-load proposal (28 October).
  - FERC accepted PJM's 50 MW large-load definition but rejected IRAS (9 October), and dismissed rehearing of its show-cause order (21 September).
  - FERC accepted SPP's CHILLS compliance filing (26 October).
- **Oregon:** PGE's Order 26-309 (31 August) adjusted the exit fee; compliance effective 1 October; appealed by AWEC. PacifiCorp's Schedule 401 was adopted 13 November.
- **New proposals:** Washington UTC's draft large-load policy (6 November: 50 MW, or over 20 MW at over 75 percent load factor).

## Decisions made without you

1. **Changes are their own file, linked to rows.** A change that alters a row's status is also written into the row, with its cite.
2. **Duplicates keep one entry:** the group that owns the document (the operators for CAISO and ERCOT; the East for Michigan).
3. **A document that prints its resolution as proposed is "other",** whatever its posting folder suggests.
