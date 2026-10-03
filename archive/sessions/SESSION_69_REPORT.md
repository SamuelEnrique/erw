# Session 69 report: the storage build-out tracker

Energy Research Warehouse (ERW), session 69, in the worktree `C:\Users\samen\Documents\erw-build` on the branch `wip/069-storage-buildout`, 2026-10-02 about 20:40 to 21:15 UTC. **Model spend: USD 0.00** (the cap was USD 0). No paid service, no pull, no model call, no force push. Nothing pushed to main or to a `task/` branch, no Supabase write, no Redivis upload, the data lock never taken. `/storage` and every shared component are untouched. **The finish step was not run.**

## To finish

**Read this before the commands.** The work is on `origin/wip/069-storage-buildout`. Step 12 pushes it to a `task/` branch, and `.github/workflows/code-branch.yml` merges a `task/` branch into main by itself when the checks pass, which deploys. Run it after sessions 67 and 68 have landed.

The table is valid in a scratch directory (`runs/session69/storage_buildout_monthly/`, not in git). The finish step rebuilds it in `warehouse/output` from the EIA-860M tables there; nothing is pulled.

```bash
# 1. the branch, brought up to date with main (never a rebase, never a force)
git checkout wip/069-storage-buildout
git fetch origin
git merge origin/main            # sessions 67 and 68 will have landed; this branch adds files only, so no conflict is expected

# 2. swap the page's own pieces for the shared ones (by hand; see "The swap" below), then
cd site && npm ci && cd ..

# 3. four small edits to shared files (see "The edits" below): build_coverage.py, live_set.yaml, run_daily.sh, llms.txt

# 4. the data lock, then sync
python warehouse/lock.py acquire --task "session 69 finish" --minutes 120; echo "exit=$?"
python scripts/sync.py; echo "exit=$?"

# 5. the table into warehouse/output (no pull: it reads the three EIA-860M tables there)
python warehouse/derived/storage_buildout.py > runs/session69/finish_build.out 2>&1; echo "exit=$?"

# 6. the validator, then coverage (gates: never piped, read each exit code before the next line)
python warehouse/validate/erw_validate.py --json warehouse/output/*.csv > runs/validate_reports.json; echo "exit=$?"
python warehouse/metadata/build_coverage.py --reports runs/validate_reports.json > runs/session69/finish_coverage.out 2>&1; echo "exit=$?"

# 7. the append-only archive
python warehouse/archive/archive.py write --tables "^storage_buildout_monthly$"; echo "exit=$?"

# 8. the Redivis draft, by table name (a draft only; releasing a version stays a human click)
python warehouse/redivis/upload.py --changed --dry-run; echo "exit=$?"
python warehouse/redivis/upload.py --tables storage_buildout_monthly; echo "exit=$?"
python warehouse/redivis/upload.py --check-license; echo "exit=$?"

# 9. the Supabase live set (after the live_set.yaml edit of step 3)
python warehouse/supabase/load.py > runs/session69/finish_load.out 2>&1; echo "exit=$?"

# 10. the site: the menu entry and the release gate status (review), check-routes and check-values entries
#     (see "The site entries" below), then the site against Supabase
cd site
npm run build > ../runs/session69/finish_site_build.out 2>&1; echo "exit=$?"
npx next start -p 3049 &
node scripts/check-routes.mjs http://localhost:3049 > ../runs/session69/finish_routes.out 2>&1; echo "exit=$?"
node scripts/check-values.mjs http://localhost:3049 > ../runs/session69/finish_values.out 2>&1; echo "exit=$?"
node scripts/test-buildout.mjs; echo "exit=$?"
cd ..

# 11. tests, then commit
python -m unittest discover -s tests > runs/session69/finish_tests.out 2>&1; echo "exit=$?"
git add warehouse/metadata docs/coverage.md warehouse/supabase/live_set.yaml warehouse/run_daily.sh package/llms.txt site
git commit -m "Session 69 finish: storage_buildout_monthly in the warehouse, the Redivis draft and the live set; /storage/buildout in the menu under review"

# 12. THE MERGE: this push runs the checks and, when they pass, merges into main and deploys
git push origin wip/069-storage-buildout:task/069-storage-buildout

# 13. release the lock, and remove the wip branch once main holds the merge
python warehouse/lock.py release
git push origin --delete wip/069-storage-buildout
```

**The swap (step 2).** The page's own pieces are all in `site/app/storage/buildout/parts.tsx`. I could not see session 67's shared components, so the names on the right are for whoever finishes to fill in:

| This page's piece | Swap for |
|---|---|
| `Panel` (the fog beige left panel, choices as links) | session 67's shared panel of the battery revenue page |
| `V` (a number with its check key, or "not held") | `components/Num.tsx`; keep the "not held" branch |
| `H2`, `Fold` | the shared section heading and folded section, if session 67 made them; else keep |
| `RAMP`, `GREY`, `SURFACE` (five colors not in the tokens) | move into `app/tokens.css` as tokens; the page then holds no color of its own |
| `DurationBars`, `SolarLine` (server-drawn SVG) | keep, unless session 67 made a shared stacked-bar chart |
| the page's own "no data" block | `components/NoData.tsx` |
| the grey source line | `components/Cite.tsx` with `tables={["storage_buildout_monthly"]}` |

`site/scripts/check-buildout.mjs` asserts the page's text and markup; after the swap, rerun it against the stand-in (the commands are at its top) and adjust the few markup assertions (the highlighted row's class, `aria-current`).

**The edits (step 3).** None was made in this session, because they are in shared files:

- `warehouse/metadata/build_coverage.py`: the sector rule `(r"^storage_(daily_cycle|capacity)$", "power")` becomes `(r"^storage_(daily_cycle|capacity|buildout_monthly)$", "power")`; and in `iso_of`, add `if table == "storage_buildout_monthly": return "CAISO;ERCOT;ISO-NE;MISO;NYISO;PJM;SPP"`. Without the first the coverage build fails by design. The tier needs no rule: a table with a `Derived from:` line is `derived`. I did not run `table_row` on the scratch table, so read the coverage output: expect `derived`, `public`, `power`, 21,229 rows.
- `warehouse/supabase/live_set.yaml`: `'^storage_(daily_cycle|capacity)$'` becomes `'^storage_(daily_cycle|capacity|buildout_monthly)$'`. The whole table is 21,229 rows; the page reads about 2,000 of them.
- `warehouse/run_daily.sh`: after the `storage_capacity` line, add `run_other storage_buildout "$PYTHON" warehouse/derived/storage_buildout.py`. The script skips with a warning when the runner has no EIA-860M tables, as `storage_capacity.py` does.
- `package/llms.txt`: under "Battery storage", add the table, its entities (`iso:<grid>`, `us:outside_isos`, `us:total`) and its variables, from `docs/methods/storage_buildout.md`.

**The site entries (step 10).** Not added in this session, so that nothing conflicts with tonight's release gate:

- `site/lib/pages.ts`, in the Grid group after `/storage`: `{ href: "/storage/buildout", label: "Storage build-out", line: "How much battery storage each US grid has built, of what duration, how it compares with solar, and what is planned.", tables: "storage_buildout_monthly", related: ["/storage", "/cost-of-power/seller"] }`. The Grid menu then has eight entries, the limit a test checks.
- The release gate's list (session 67 or 68's file, not on this branch): `/storage/buildout` with status `review`.
- `site/scripts/check-routes.mjs`, `PAGES`: `"/storage/buildout", "/storage/buildout?grid=ercot&measure=mwh", "/data/methods/storage_buildout"`.
- `site/scripts/check-values.mjs`, `PAGES`: `"/storage/buildout", "/storage/buildout?grid=ercot&measure=mwh", "/storage/buildout?grid=caiso"`. No new code is needed there: every number on the page carries the existing key `series|storage_buildout_monthly|<entity>|<variable>|<month>` and is written as that script expects.
- Optional: a link from `/storage` to this page (this page already links to `/storage`).

## In plain words

**The question was whether battery duration is keeping up.** The answer from EIA's August 2026 inventory: the US has 54,488.9 MW of utility-scale batteries holding 150,437.6 MWh, an average of 2.76 hours. A year earlier it had 36,800.2 MW. Power and energy are growing fast, about half again in twelve months. **Average duration is not growing: it has been between 2.66 and 2.77 hours at every year end since 2021.**

**Against solar, storage is gaining.** The US had 0.06 MWh of batteries per MW of solar at the end of 2020, 0.60 at the end of 2024 and 0.89 in August 2026. Solar grew; batteries grew much faster.

**The grids differ a great deal.** CAISO's fleet is long: 3.46 hours on average, three quarters of its MW in the 4 to under 6 hour bucket. ERCOT's is short: 1.65 hours, more than half its MW under 2 hours. ERCOT now has more battery power than CAISO (18,204.5 MW against 17,094.2) and half the energy (30,019.8 MWh against 59,118.3). ERCOT's duration is rising, from 1.29 hours at the end of 2022.

**What was built.** One derived table, `storage_buildout_monthly` (21,229 rows, valid in scratch), and one page, `/storage/buildout`, checked locally against a fixture of the table's real rows. The page does no arithmetic: every number on it is a row of the table.

**What is not held.** Planned energy (MWh). EIA's monthly inventory gives no energy figure for planned units.

## Energy capacity (MWh): held, parsed, or not available

- **Operating and retired units: held.** `energy_capacity_mwh` is already a column of the held `eia860m_operating_generators` and `eia860m_retired_generators` (since session 34). All 1,137 operating battery units and all 8 retired ones carry a value. Nothing was parsed from raw files.
- **Planned units: not available in EIA-860M.** I opened the saved August 2026 workbook in the main folder's `warehouse\raw\eia860\20260926T000340Z\` (read only): the Operating and Retired sheets have "Nameplate Energy Capacity (MWh)", the Planned sheet does not. So the table writes no planned MWh and the page says "not held".
- **What a person would need to approve to get it:** a new source, the annual Form EIA-860 (its energy storage schedule reports energy capacity for proposed units), and a pull of the annual files. It is yearly, so it would lag the monthly planned list.

## The table: `storage_buildout_monthly`

Code: `warehouse/derived/storage_buildout.py`. Method: `docs/methods/storage_buildout.md`. Shape `series`, freq `P1M`, derived, public (EIA). 21,229 rows, 9 entities, 26 variables, 140 months (2015-01 to 2026-08). Validator: PASS, 0 errors, 0 warnings.

- **Inputs.** The three EIA-860M tables, copied once, read only, into `runs/session69/inputs/` at 2026-10-02 20:45 to 20:46 UTC, each after two size reads four seconds apart that agreed: `eia860m_operating_generators` 11,214,722 bytes (modified 2026-09-29 16:58 local), `eia860m_planned_generators` 1,002,507 bytes (2026-09-29 16:58), `eia860m_retired_generators` 101,796 bytes (2026-10-01 23:42). All three are the 2026-08 inventory.
- **Entities.** `iso:caiso`, `iso:ercot`, `iso:isone`, `iso:miso`, `iso:nyiso`, `iso:pjm`, `iso:spp`, `us:outside_isos`, `us:total`.
- **Every month:** battery MW, MWh and unit count; MW in five buckets (under 2 hours, 2 to under 4, 4 to under 6, 6 and more, energy not reported); MWh in the four duration buckets; solar MW; average duration (MWh per MW); battery MWh per solar MW; and, from the thirteenth month, the change in MW and MWh over twelve months.
- **At the inventory month only:** planned battery MW in total, under construction, and by year online; planned unit count.
- **How the months are made.** The ERW holds one inventory, the newest. Each month is rebuilt from it: a unit counts from its first operating month, and a unit of the retired table counts until the month before it retired.

## The United States and each grid, August 2026

| Grid | MW | MWh | Average hours | Net added in 12 months, MW | Net added, MWh | Units | Planned MW | Of it under construction |
|---|---|---|---|---|---|---|---|---|
| United States | 54,488.9 | 150,437.6 | 2.76 | 17,688.7 | 47,375.7 | 1,137 | 64,458.1 | 23,543.8 |
| CAISO | 17,094.2 | 59,118.3 | 3.46 | 2,826.9 | 10,121.3 | 310 | 10,921.6 | 4,707.5 |
| ERCOT | 18,204.5 | 30,019.8 | 1.65 | 7,158.9 | 13,248.6 | 259 | 24,569.1 | 8,236.7 |
| ISO-NE | 1,021.7 | 2,130.8 | 2.09 | 427.2 | 855.4 | 157 | 1,047.7 | 274.7 |
| MISO | 1,175.9 | 3,449.9 | 2.93 | 549.0 | 1,073.0 | 42 | 3,713.2 | 2,165.5 |
| NYISO | 268.7 | 760.6 | 2.83 | 20.6 | 88.0 | 58 | 778.7 | 107.4 |
| PJM | 665.9 | 1,504.0 | 2.26 | 223.0 | 1,038.5 | 43 | 729.1 | 378.1 |
| SPP | 490.5 | 1,609.5 | 3.28 | 291.0 | 1,056.0 | 16 | 1,679.5 | 281.0 |
| Outside the seven ISOs | 15,567.5 | 51,844.7 | 3.33 | 6,192.1 | 19,894.9 | 252 | 21,019.2 | 7,392.9 |

Planned battery MW by the year developers expect it online (planned MWh: not held):

| Grid | 2026 | 2027 | 2028 | 2029 | 2030 | 2031 |
|---|---|---|---|---|---|---|
| United States | 12,093.0 | 25,154.4 | 14,788.7 | 9,020.9 | 2,182.5 | 1,218.6 |
| CAISO | 2,368.6 | 4,016.0 | 3,048.4 | 725.0 | 550.0 | 213.6 |
| ERCOT | 5,581.0 | 9,277.2 | 5,989.9 | 2,651.0 | 660.0 | 410.0 |
| ISO-NE | 49.0 | 785.7 | 168.0 | 0.0 | 0.0 | 45.0 |
| MISO | 400.0 | 1,528.2 | 555.0 | 980.0 | 250.0 | 0.0 |
| NYISO | 26.5 | 101.7 | 471.5 | 0.0 | 129.0 | 50.0 |
| PJM | 177.6 | 501.5 | 50.0 | 0.0 | 0.0 | 0.0 |
| SPP | 250.0 | 380.6 | 382.0 | 466.9 | 200.0 | 0.0 |
| Outside the seven ISOs | 3,240.3 | 8,563.5 | 4,123.9 | 4,198.0 | 393.5 | 500.0 |

## Duration buckets by year (MW at year end; 2026 is to August)

Energy not reported is 0.0 MW in every year and grid, so it is left out of these three tables.

**United States**

| Year | Under 2 h | 2 to under 4 h | 4 to under 6 h | 6 h and more | Total MW | MWh | Average hours |
|---|---|---|---|---|---|---|---|
| 2015 | 231.2 | 18.0 | 0.0 | 1.0 | 250.2 | 153.3 | 0.61 |
| 2016 | 416.6 | 21.8 | 22.0 | 1.0 | 461.4 | 380.0 | 0.82 |
| 2017 | 475.9 | 23.3 | 75.3 | 4.5 | 579.0 | 653.1 | 1.13 |
| 2018 | 600.2 | 54.1 | 124.3 | 20.8 | 799.4 | 1,154.1 | 1.44 |
| 2019 | 676.6 | 120.0 | 166.2 | 41.2 | 1,004.0 | 1,705.5 | 1.70 |
| 2020 | 957.4 | 161.4 | 427.8 | 42.4 | 1,589.0 | 3,147.5 | 1.98 |
| 2021 | 1,635.7 | 1,224.8 | 2,117.9 | 42.4 | 5,020.8 | 13,379.1 | 2.66 |
| 2022 | 3,310.8 | 1,777.7 | 4,197.4 | 43.9 | 9,329.8 | 25,194.8 | 2.70 |
| 2023 | 5,679.6 | 3,170.1 | 7,632.2 | 86.4 | 16,568.3 | 44,946.8 | 2.71 |
| 2024 | 9,731.8 | 4,830.1 | 12,945.6 | 126.8 | 27,634.3 | 75,500.3 | 2.73 |
| 2025 | 13,587.2 | 9,830.1 | 20,114.7 | 128.8 | 43,660.8 | 120,977.5 | 2.77 |
| 2026 to August | 16,289.3 | 13,086.0 | 24,984.8 | 128.8 | 54,488.9 | 150,437.6 | 2.76 |

The share of US battery MW that can run 4 hours or more: 43.0 percent at the end of 2021, 47.3 at the end of 2024, 46.1 in August 2026. Flat.

**ERCOT**

| Year | Under 2 h | 2 to under 4 h | 4 to under 6 h | 6 h and more | Total MW | MWh | Average hours |
|---|---|---|---|---|---|---|---|
| 2015 | 36.0 | 0.0 | 0.0 | 0.0 | 36.0 | 13.6 | 0.38 |
| 2016 | 36.0 | 0.0 | 0.0 | 0.0 | 36.0 | 13.6 | 0.38 |
| 2017 | 66.0 | 0.0 | 0.0 | 0.0 | 66.0 | 26.2 | 0.40 |
| 2018 | 85.8 | 1.5 | 0.0 | 0.0 | 87.3 | 49.0 | 0.56 |
| 2019 | 95.8 | 1.5 | 9.9 | 0.0 | 107.2 | 101.0 | 0.94 |
| 2020 | 207.0 | 1.5 | 9.9 | 0.0 | 218.4 | 231.1 | 1.06 |
| 2021 | 652.2 | 158.8 | 9.9 | 0.0 | 820.9 | 1,060.7 | 1.29 |
| 2022 | 1,961.3 | 158.8 | 9.9 | 0.0 | 2,130.0 | 2,748.0 | 1.29 |
| 2023 | 3,144.9 | 1,018.7 | 9.9 | 0.0 | 4,173.5 | 5,975.8 | 1.43 |
| 2024 | 6,254.8 | 2,029.1 | 9.9 | 0.0 | 8,293.8 | 11,894.6 | 1.43 |
| 2025 | 8,757.7 | 5,091.7 | 59.9 | 0.0 | 13,909.3 | 21,578.8 | 1.55 |
| 2026 to August | 10,138.4 | 7,579.4 | 486.7 | 0.0 | 18,204.5 | 30,019.8 | 1.65 |

**CAISO**

| Year | Under 2 h | 2 to under 4 h | 4 to under 6 h | 6 h and more | Total MW | MWh | Average hours |
|---|---|---|---|---|---|---|---|
| 2015 | 0.0 | 8.0 | 0.0 | 1.0 | 9.0 | 27.3 | 3.03 |
| 2016 | 42.0 | 8.0 | 22.0 | 1.0 | 73.0 | 157.3 | 2.15 |
| 2017 | 42.0 | 8.5 | 61.5 | 4.5 | 116.5 | 337.3 | 2.90 |
| 2018 | 82.8 | 8.5 | 61.5 | 15.8 | 168.6 | 445.0 | 2.64 |
| 2019 | 84.1 | 9.9 | 66.5 | 25.2 | 185.7 | 539.1 | 2.90 |
| 2020 | 191.8 | 12.3 | 317.5 | 25.2 | 546.8 | 1,640.1 | 3.00 |
| 2021 | 329.0 | 294.3 | 1,844.4 | 25.2 | 2,492.9 | 8,856.9 | 3.55 |
| 2022 | 528.8 | 672.3 | 3,759.4 | 25.2 | 4,985.7 | 17,720.2 | 3.55 |
| 2023 | 1,296.6 | 695.4 | 6,050.2 | 65.2 | 8,107.4 | 27,727.0 | 3.42 |
| 2024 | 1,695.8 | 1,054.9 | 8,930.4 | 65.2 | 11,746.3 | 40,849.5 | 3.48 |
| 2025 | 2,508.4 | 1,409.6 | 11,776.6 | 65.2 | 15,759.8 | 54,150.5 | 3.44 |
| 2026 to August | 2,608.3 | 1,512.8 | 12,907.9 | 65.2 | 17,094.2 | 59,118.3 | 3.46 |

## Storage hours per MW of solar, by year (battery MWh over solar MW)

| Year | United States | ERCOT | CAISO | US solar, MW |
|---|---|---|---|---|
| 2015 | 0.0111 | 0.0439 | 0.0038 | 13,867.8 |
| 2016 | 0.0172 | 0.0236 | 0.0157 | 22,046.7 |
| 2017 | 0.0239 | 0.0212 | 0.0314 | 27,299.9 |
| 2018 | 0.0358 | 0.0259 | 0.0384 | 32,252.3 |
| 2019 | 0.0448 | 0.0390 | 0.0427 | 38,107.2 |
| 2020 | 0.0645 | 0.0475 | 0.1136 | 48,767.9 |
| 2021 | 0.2139 | 0.1200 | 0.5618 | 62,545.1 |
| 2022 | 0.3412 | 0.2419 | 0.9914 | 73,846.6 |
| 2023 | 0.4799 | 0.4007 | 1.3572 | 93,668.4 |
| 2024 | 0.6048 | 0.5358 | 1.7670 | 124,833.3 |
| 2025 | 0.7832 | 0.7189 | 2.1707 | 154,462.7 |
| 2026 to August | 0.8894 | 0.9164 | 2.2903 | 169,136.8 |

August 2026, the other grids: ISO-NE 0.5686, MISO 0.1412, NYISO 0.2536, PJM 0.0778, SPP 0.6677, outside the seven 0.8994.

## Generators not assigned to a grid

A generator's grid is its balancing authority code in EIA-860M: CISO, ERCO, ISNE, MISO, NYIS, PJM and SWPP map to the seven ISOs. Every other code, and no code, is `us:outside_isos`. The US total is every unit, Puerto Rico included (9 operating battery units), so it equals the seven grids plus that entity.

| | Not assigned | MW | Other codes | With no code at all |
|---|---|---|---|---|
| Operating batteries (of 1,137) | 252 units | 15,567.5 | 29 codes | 21 units, 238.9 MW |
| Operating solar (of 8,313) | 2,324 units | 57,643.5 | 44 codes | 77 units, 325.3 MW |
| Planned batteries (of 482) | 124 units | 21,019.2 | 34 codes | 5 units, 86.7 MW |

No unit was dropped. The largest codes outside the seven, by operating battery units: CPLE 29, AZPS 28, PNM 16, FPL 13, NEVP 13, SRP 12, SOCO 12, IPCO 12.

## Tests

| What | Result |
|---|---|
| `python -m unittest tests.test_session69` | 16 tests, OK. On a made-up inventory: bucket edges (exactly 2, 4 and 6 hours start a bucket); MW by bucket sums to the total, every grid and month; a unit with no energy lands in "energy not reported" and nowhere else, and its MWh is not estimated; the US total equals the regions plus unassigned; retirement months; ratios omitted at a zero denominator; planned by year; five loud failures; a scratch run that validates and reruns unchanged. On real values: the same three sums on the scratch table and on the fixture, and the fixture's rows equal the scratch table's |
| `python -m unittest discover -s tests` (as CI runs it) | 313 tests, OK, 34 skipped |
| Validator on the scratch table | exit 0, PASS, 0 errors, 0 warnings |
| `node scripts/test-buildout.mjs` | 915 checks pass: the page model on the fixture, all eight grids and both measures; and the production code path (page, reader, pieces, model) reads no file and no fixture |
| `node scripts/check-buildout.mjs` | 7,313 checks pass: the built site rendered against the fixture through a local stand-in for Supabase; 16 pages; 3,530 rendered numbers equal the fixture's rows, read from the file independently |
| `npm run build`, `npx eslint` on the new files | exit 0 both |

Not run, because they need the table in Supabase: `check-routes.mjs` and `check-values.mjs` on this page. They are in the finish step.

## The page as built

`/storage/buildout`, "How much storage has been built". Files: `site/app/storage/buildout/page.tsx`, `parts.tsx` (its own pieces), `read.ts` (its Supabase read), `site/lib/buildout.ts` (the model).

- **Layout.** A fog beige panel on the left, the answer on a white ground on the right. Below 768 px the panel stacks on top, with Grid and Measure side by side. Looked at in headless Chrome at 1280 px and 500 px (screenshots in `runs/session69/shots/`, not in git): no horizontal page scroll; the grid table scrolls inside itself on a narrow screen.
- **Left panel.** Grid (United States, then CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP) and Measure (Power, MW; Energy, MWh). Each choice is a link (`?grid=ercot&measure=mwh`), so the page works with no script.
- **Summary sentence,** from the table: "ERCOT has 18,204.50 MW of batteries holding 30,019.80 MWh, an average of 1.65 hours, up from 11,045.60 MW a year ago." 21 to 23 words for every grid.
- **Three headline numbers:** operating power with the unit count; operating energy with the average duration; added over the last twelve months, net of retirements, in MW and MWh.
- **Chart 1:** one bar per year end, 2015 to the year so far, stacked by duration bucket in one cardinal hue from light (under 2 hours) to dark (6 hours and more), in the chosen measure. Server-drawn SVG; each segment has its value as a hover title.
- **Chart 2:** one line, battery MWh per MW of solar by year, with one sentence under it on what the ratio means.
- **A folded table** with every number behind both charts.
- **The table by grid:** the seven ISOs, "Outside the ISOs", and the United States in bold; MW, MWh, average hours, added in 12 months, planned in total and by year online. Cardinal header row; the chosen grid's row in fog beige. PJM is included.
- **Folded sections:** how generators are assigned and how many were not (from the table's values); what EIA-860M covers and misses; the newest month held.
- **A grey source line** naming the table and EIA-860M, with the method link.
- **Production data path:** `read.ts` makes two reads through `lib/supabase.ts`: the newest month, then the rows of the 13 months the page shows (about 2,000 of 21,229). No fixture is in that path; a test checks it.
- **Local verification:** `site/scripts/buildout-stub.mjs` serves the fixture as Supabase's REST API would, and the site was built and started with `SUPABASE_URL` pointing at it.
- Until the finish step, the deployed page would show "no data" with the reason, because the table is not in Supabase. It is in no menu.

## Errors and decisions

Errors:

1. **A shell line of mine hung and its edit did not apply.** A command meant to fall back between two Python interpreters ran the system one with an empty script and waited. I stopped it, confirmed no file had changed, and reran the edit with the main folder's interpreter. No data effect.
2. **My first full-suite test command used the wrong form** (`discover -s tests -t .`) and failed to import. Rerun as CI runs it: 313 tests OK.
3. **One assertion in my own page check was wrong** (it counted table rows by splitting markup badly). Fixed; the page was right.

Decisions where the prompt was silent:

1. **History is rebuilt from the one inventory held.** The ERW keeps only the newest EIA-860M inventory, so "by month" is each unit's first operating month, less the retirements the retired table holds (2025 and 2026). Units retired before 2025 are in no month. Stated in the table header, the method and the page.
2. **Months start at 2015-01.** Earlier units are in every total. 21,229 rows.
3. **Twelve-month additions and the two ratios are variables of the table,** so the page computes nothing and `check-values.mjs` needs no new code.
4. **Average duration is MWh over the MW of units that report energy.** Today that is every unit.
5. **Solar is photovoltaic plus solar thermal** (12 thermal units), nameplate MW.
6. **Puerto Rico is in the US total** and in "outside the ISOs", as `storage_capacity` already counts it.
7. **Entities** `iso:<grid>` follow `ai_power_regions`; `us:total` and `us:outside_isos` are new.
8. **`npm ci` was run in this worktree's `site/`** (it had no `node_modules`). It downloads packages from the lockfile; it is not a data pull and changes no tracked file.
9. **Numbers are written as the site's check script expects:** whole, or two decimals ("54,488.90 MW"). Whole MW would read better but needs an entry in the shared `check-values.mjs`.
10. **The answer's side is white** (`#FFFFFF`), because the site's page ground is already fog beige and the panel would not show against it. This and the duration ramp are five colors outside `tokens.css`; the finish step moves them there.
11. **No shared file was edited:** not `pages.ts`, `tokens.css`, `check-routes.mjs`, `check-values.mjs`, `build_coverage.py`, `live_set.yaml`, `run_daily.sh` or `llms.txt`. Each needed edit is listed under "To finish".
12. **The prompt was copied** to `archive/sessions/SESSION_69_PROMPT.md`; the copy at the root is left where it was, untracked.
13. **In the main folder** I ran its Python by path, copied the three tables once, and opened one saved raw workbook read only to check its column headers. Nothing was written there and no git command was run there.

Flagged, not smoothed:

- **Planned for 2026 looks high.** Developers report 12,093.0 MW of batteries coming online in the last four months of 2026; 10,828.1 MW was added in the first eight. Planned dates slip.
- **"Energy not reported" is zero everywhere.** Every battery unit in this inventory has an energy value, so the bucket is tested only on made-up units.
- **The newest months understate.** Units that started in mid 2026 and reported late will appear in later inventories.
- **Early ERCOT durations are very short** (0.38 hours in 2015 and 2016): 36 MW holding 13.6 MWh, as EIA reports those units.
- **CAISO here is the CISO balancing authority only.** California batteries in other balancing authorities (LADWP, IID, BANC) are in "outside the ISOs".
- **The chart labels are small on a phone;** the folded table carries the numbers.

## For Samuel

1. **Run the finish step** after sessions 67 and 68 land. The swap of the page's own pieces for the shared ones is by hand; I could not see session 67's components.
2. **For tomorrow's demo, before the finish step:** the page can be shown locally against the fixture with the three commands at the top of `site/scripts/check-buildout.mjs`. The deployed site does not have it.
3. **Planned MWh needs your approval of a new source,** the annual Form EIA-860, if you want it.
4. **Decide whether MW should be written whole** ("54,489 MW") on this page; it is one line in `check-values.mjs` plus one in the page.
5. **The headline for the credit investor, to check against your own reading:** deployment is keeping up with solar and gaining; duration is not lengthening nationally (2.7 to 2.8 hours since 2021), and ERCOT, the fastest-growing fleet, is the shortest.
