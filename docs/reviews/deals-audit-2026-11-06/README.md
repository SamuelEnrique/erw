# The audit's sample (session 2231)

Energy Research Warehouse (ERW), chain 156. The rows of `docs/reviews/deals-audit-2026-11-06.md`, "The audit of the stored records", one line a sampled row.

- `draw_sample.py`: draws the sample from `warehouse/output/energy_deals.csv` and `datacenter_projects.csv` of main at `c750ce225` (the tables of the daily run `20261105T234321Z`), with each row's stories' title and summary from `news_stories.csv`; run from the repository root with the output path as its one argument.
- `sample_deals.csv` (106 rows, D001 to D106) and `sample_facilities.csv` (60 rows, F001 to F060): each row's grade and a note quoting the story's words.
- `duplicates_check.py`: the duplicate tests over the whole tables.
- `tally.py`: the counts and examples of the fault classes, from the two CSVs.

The rubric, as the three readers had it (the stories' title and summary only, no outside knowledge):

- Deals: `not_a_deal` (no specific transaction between named parties); `party` ok, wrong, incomplete, unnamed (a description such as "investors"), na; `kind` and `kind_ok` (the stored type right, or "vocabulary gap" when the store has no word for it); `mw`, `mwh`, `usd`, `price`, `term` each ok, missed, wrong or invented; `status` ok, wrong, missed, unsupported; `ai_power` ok or wrong (true only where a named AI lab, hyperscaler, datacenter operator or AI-load buyer is a party, or the load is a datacenter); `place` ok, missed, wrong; `confidence_fit` ok, too_high (0.7 or more on a non-deal or a badly wrong row), too_low (under 0.6 on a clean row).
- Facilities: `not_a_facility`; `operator`, `site`, `state`, `status`, `power_source`, `utility`, `timeline` each ok, missed or wrong; `mw` with `mw_basis` (it, total, unstated, na); `confidence_fit` as above.
