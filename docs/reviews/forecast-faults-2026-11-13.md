# The forecast tool's faults (Local impact, /impact): 13 November 2026

Energy Research Warehouse (ERW), chain 239 (lab-desktop window 4), sessions 4211 on. The page read: `/impact` (the left box and its five groups, each field's default and tip, scenarios A and B, the A and B table, the two charts by year with their hover, the table by year, the other states' chart, the CSV, Python and Stata files), its model `site/lib/forecast.ts`, its fields `site/lib/forecastui.ts`, its files `site/lib/forecastfiles.ts`. Method: `docs/methods/forecast.md` (internal).

States: `fixed` (with the test that holds it), `open` (a fix this chain can make), `ruling` (Samuel's, with a default), `data machine` (a table window A would make; `docs/state/data_requests_forecast.md`), `not a fault` (checked, with what was checked).

## The faults

| # | Where | Fault | State | Fix and test |
|---:|---|---|---|---|
| 1 | `app/impact/Forecast.tsx`, `Years` | The table-by-year's open state was a hook called after an early return (a scenario with no figure), so React's hook order would change between draws | fixed (session 4213, before the first commit) | the hook moved above the return; the build's lint (react-hooks) and the page read hold it |
| 2 | `lib/forecastfiles.ts`, the Python script | A geothermal scenario carries no capacity factor (null in the file), and the script multiplied it: the script stopped with a TypeError | fixed (session 4214) | the script takes 0 where none is held (no production tax applies to geothermal); `test-forecast.test.mjs`, "the run's Python script recomputes every total of the tool" (three pairs, 14 totals each, geothermal among them) |
| 3 | the model, PV operations | JEDI's 2010 utility PV operating costs give 3.5 times the operating jobs of Ohio University's 2018 study (section 9 of the note) | fixed (session 4210) | the "Operating spending, % of JEDI's" input (default 100, JEDI's own); `test-forecast.test.mjs`, "operations: JEDI per MW times MW (DC for PV) ...", the 45 percent case |
| 4 | the left box | No county field and no way to pick a planned project from EIA-860M (the prompt's "a project the user picks or types") | fixed (session 4216) | the "Planned project" list: EIA-860M's planned generators of the technology in the state (`energy_projects` in the live set), a plant's generators added; picking one sets the size and the first construction year and names the county in the left box and the A and B heading; the address carries its id (`proj`, `bproj`). `test-forecast.test.mjs`, "planned projects: ..." |
| 5 | property tax | 45 states and DC have no property tax rule held (Minnesota, South Dakota, North Dakota, Nebraska and Iowa are); the figure says "no rule held" unless the reader types an effective rate | ruling | default: states are added one statute at a time as each is read; Illinois (its server failed certificate verification) and Ohio (its code site disallows automated reads) wait on Samuel |
