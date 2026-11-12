# Session 3786 report, with 3787: the findings (parked 197): the landing service, the drafts checked

Energy Research Warehouse (ERW). Chain 212, data machine (lab-desktop), 12 November 2026 13:38 to 13:48 UTC (taken early while the daily run holds the data lock). Opus 5.5. Model spend USD 0. Requests: none to any publisher; Supabase reads only (`check_cards.py`).

## Read these first

- **The landing service has nothing to land.** Every row of both requests on origin's main is an ancestor of main and is marked landed:
  - `docs/state/landing_request_portable.md`: rows 1 to 16;
  - `docs/state/landing_request_oldlaptop.md`: rows 1 to 8.
- **Every draft holds** (3787), on `wip/c212-data` with main at `53d8a2f69` merged:
  - `check.py --tables <main checkout>/warehouse/output`: **185 of 185 drafts reproduce** from their own `reproduce.py`, each copied alone into an empty folder.
  - `check_cards.py` (Supabase, read only): **185 of 185 cards hold**, every one still a draft.
  - `check_do.py`: **185 of 185 do-files hold**.
- **The count by family, before and after (unchanged, 185):**
  - generation_pipeline 35, prices 33, queues_deals_datacenters 27, oil_products_world 18;
  - tariffs_policy 12, demand 12, gas 11;
  - cross_family 8, coal_uranium_metals 8;
  - other_us 7, markets_operations 7, emissions_climate 7.
- **The hunt again where data moved: not run.** The tables the drafts read have not moved since the drafts were made, because the catch-up run (43212054910) has not committed. Every draft's last full year still reproduces on this machine's tables (above), so no draft has a newer full year to recompute. The next data chain repeats this after the catch-up and the data machine's own run.
- **Nothing approved, nothing published.**

## Outputs

`runs/c212/s3787_check.out`, `s3787_check_cards.out`, `s3787_check_do.out` (not in git).

## Decisions made without you

- **The hunt's recompute waits for the tables to move.** Re-running `--replace` on unchanged tables would rewrite 185 drafts to the same figures.
- **The records and the clean-up of chain 164's session 3022** have nothing new to record: no draft was added, removed or corrected.

## For Samuel's ruling

- None.
