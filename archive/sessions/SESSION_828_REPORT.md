# Session 828 report: the method notes

23 October 2026, 09:25 to about 09:35 UTC, unattended, on portable-laptop (the code machine), in the worktree `C:\Users\samen\Documents\erw-828` on `wip/828-deals` (cut from `wip/827-deals`). Chain `queue/done/080-night-23-october-portable-landing-deals-.md`, session 828. Model Fable 5.1. Model spend USD 0. No warehouse data written; no request.

## Read these first

- **`docs/methods/energy_deals.md` and `docs/methods/datacenter_facilities.md` gain "What is shown and what is held (chain 080, 23 October 2026)"**: the three sorts' rules (shown, held, unsettled), what each page draws from the file, where the file comes from and when it goes stale, and a decisions block of the chain's choices with their sessions.
- The `/data/methods/` links hold: both notes keep their slugs; `tests.test_session409` (the method notes against the pages' keys) passes.

## What to review

- `/data/methods/energy_deals`, the last two sections; `/data/methods/datacenter_facilities`, the last section.

## Checks

| Check | Exit | Result |
|---|---|---|
| `tests.test_session409` | 0 | OK |

## The landing

`wip/828-deals` pushed (sessions 822 to 828 over origin/main). The gate on `wip/827-deals` stopped at `task_branches`: the data machine's `task/909-922-data` is in flight and conflicts with main on `docs/reviews/siting-gaps.md` (not a file of this chain); the gate asks to wait for it to merge. The line's gate runs again from `wip/828-deals` once it has (session 829's report).

## Decisions made without you

1. The sections are written as the chain's rules stand tonight; the two ruling items (the every-story rule, the data machine writing the file) are named in them and not decided.

## For Samuel's ruling

- Nothing new.

## Files

- Changed: `docs/methods/energy_deals.md`, `docs/methods/datacenter_facilities.md`. New: this report.
