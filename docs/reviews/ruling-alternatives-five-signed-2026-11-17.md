# Ruling alternatives: across the five signed tools (17 November 2026)

Session 7623 (portable-laptop, code role). The one line of `docs/reviews/ruling-impact-five-signed-2026-11-17.md`. **No branch: the line is under the chain's threshold, and its other choice is a change to the data machine's daily run, not to the site.** No default on main changed. Model spend USD 0.

| # | Line | Change in the impact file | Why no branch |
|---|---|---|---|
| 1 | Rebuild the "Price years" table (`price_years_by_window`) in the data machine's daily run, so each page's "Price years" default keeps up with its headline | Before the hand rebuild of 14 November the default lagged its headline by 0.6 to 1.0 percent: CAISO's battery 79.31 against 79.80 (-0.49, -0.61 percent), the datacenter page 33.73 against 34.07 (-0.34, -0.998 percent) | **Under 1 percent** on both figures the impact file measured, and it adds or removes no figure. And the other choice is a step of `warehouse/run_daily.sh` on the data machine (running `site/scripts/price-years.mjs` over the live set and loading the table), which this code machine does not run and which writes a warehouse table (the owner's rules of 16 November 2026, rule 6). A branch could add the step to the run's script, but no page on it would show a different figure until the data machine ran it, so there is no figure to pin or picture |

## For Samuel's ruling

- If the daily rebuild is chosen, it is one step for the data machine's chain (after `battery_stack` and the datacenter monthly table, before `supabase_load`); the lag it closes is under 1 percent on the figures measured, and one month at most between hand rebuilds.
