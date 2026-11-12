# The deals and datacenter backfill: claimed

Energy Research Warehouse (ERW). **Claimed by lab-desktop, session 3756** (chain 211, `queue/done/211-day-11-november-data-main-unblocked-catchup.md`), 12 November 2026 at about 10:30 UTC.

- The window: 27 October to 5 November 2026, one run: `scripts/deals_backfill.py --from 2026-10-27 --to 2026-11-05 --run`, under the data lock, with the extractor on main (row 8, `886afe777`).
- The cap: USD 15, approved by the owner on 5 November; the estimate is USD 2.93 (`docs/state/backfill_estimate_2026-11-06.md`). The steps' own call caps bound the run below USD 5.
- No other machine runs this backfill while this file says claimed. The result is written in session 3756's report and in chain 211's note.
