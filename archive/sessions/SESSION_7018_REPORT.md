# Session 7018 report: the data machine's eight tools at the done line

Energy Research Warehouse (ERW). Chain 301, data machine (lab-desktop), 16 November 2026. Opus 5.5. Model spend USD 0.

## What was built

The done line's form (chain 303's: a complete note, a replication, a cross-check, a decisions block, the faults, a sign-off) for the eight tools `docs/state/done_line_claims.md` gives the data machine. The replications and faults were sessions 7010 to 7014; this session added the rest. Each tool's decisions are one list in `site/lib/decisions.ts`, drawn at the foot of its page by the shared block (each choice's default and source on hover) and written word for word in its note, held by a test `tests/test_session7018_<tool>_done.py`.

| Tool | Decisions | Cross-check |
|---|---|---|
| `/board` | 11 | EIA's closes beside the World Bank's monthly averages: Henry Hub within two cents; WTI and Brent up to 2.91 USD in the widest months |
| `/prices` (first tab) | 8 | no second public publisher held; the replication's 74,258 of 74,258 |
| `/prices/compare` | 9 | no second public publisher held; the replication's 578 of 578 |
| `/supply` | 11 | EIA's weekly crude production against its Petroleum Supply Monthly: within 0.0 to 2.8 percent, February to July 2026 |
| `/storage` | 9 | each grid's nameplate against its highest reported output: 51 to 91 percent |
| `/demand` | 9 | ERCOT's own load (means within 0.5 percent, peaks in the same hour) and CAISO's own load against EIA-930 |
| `/curtailment` | 11 | EIA, Today in Energy, 28 May 2025: 3.4 million MWh in 2024, up 29 percent, solar 93 percent; the file 3,423,377 MWh, 28.7 and 93.3 |
| `/queues` | 9 | Berkeley Lab's own summary of the 2026 edition: solar, gas and wind within 0.4 GW; storage 552.7 GW against approximately 749, not reconciled |

- `docs/reviews/desktop-tools-signature-pack-2026-11-16.md`: per tool what Samuel signs, the five choices that move its figures, its cross-checks, its Stata run and expected values, and the rulings waiting.
- `docs/state/done_line_claims.md`: tools 17 to 24 marked done line on `wip/c301-later`.
- Pages read on the web, each after its robots file in a call of its own: EIA's Today in Energy article 65364; Berkeley Lab's publication page of the 2026 edition (on `eta-publications.lbl.gov`, since `emp.lbl.gov` refuses the ERW reader). EIA's weekly petroleum and gas pages were read and carried another week's text than the tables', so they are not used. `ir.eia.gov` refused its robots file and was not asked.

## Errors

- One decision named a source the session had not read (PJM's Data Miner) and one note line gave a session number not checked (1130 for the ICE table's hold, which is 2014): both corrected before the commit. Three decisions named only the newest session of a rule; corrected to the session that made it, each checked with `git log -S`.
- The page-tables check found one decision's source naming a table the page does not read; reworded.

## Gate

- Gate h on `wip/c301-later` (`44d82be7a`, all the chain's work to this session) started at 15:04 UTC; lands at 16:15 UTC with gate g's content inside it.

## For Samuel's ruling

- Queues: the storage difference against Berkeley Lab's summary (default: the file's parts as filed).
- The rest are in the pack's last section, each with its default.
