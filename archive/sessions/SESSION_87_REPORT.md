# Session 87 report: who owns the batteries

**Built.** A table, `storage_owners_monthly`, and a review page, `/storage/owners`, in the battery page's layout: operating and planned battery storage by owner and grid, in MW and MWh, with the average duration and the largest owners, from EIA-860M's inventory of August 2026. One deploy, with snapshots before and after. No number changed; **one number was missing from the home page for about twelve minutes after the deploy**, and came back by itself. Details below.

**Read these three first:**

1. **"Owner" is the company that reports the plant to EIA, and that is often a project company.** EIA-860M names one company per plant and no parent. So the country's largest "owner", Engie North America, is a real operator with 1,989 MW, but New England's largest is "Medway Grid LLC", one plant. Nothing merges names. The shares of the largest are therefore a floor on how concentrated ownership is: **the ten largest reporting companies hold 17.4 percent of the country's 54,489 MW.** The page says this in its panel, under its chart and in a fold.
2. **After the deploy the home page's battery tile read "not held" instead of USD 81.40 per kW, from 05:01 to about 05:13 UTC.** A deploy empties the page cache; the home page's first render asked the database for the tile's rows, that one read timed out, and the page was cached with the tile empty until its 15-minute cache turned. The value never changed: a third snapshot at 05:13 shows 81.40 again and no difference in any number. It is not caused by this session's change (which touches neither the home page nor that table), but it is caused by deploying, and I deployed. It can happen on any deploy. See "For Samuel".
3. **The new table is public and held out of the live catalogue**, like session 85's two, so the home page's count of tables and rows does not move. The page reads the site's own copy of the table.

Energy Research Warehouse (ERW), session 87, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from about 04:20 (the builder and its trial run, written while session 85's download ran) to 05:20 UTC, unattended. **Model spend: USD 0.00.** No pull: the two EIA-860M tables already held. No model call, no force push. No instruction arrived for session 84. The data lock was held from about 04:46 to 04:51 UTC for the table's write, coverage, the archive and the upload, and released.

## To finish

```bash
# Nothing is left half done. What is yours:

# 1. Parents. To say who really owns the batteries, the project companies have to be tied to their parents. EIA's
#    annual EIA-860 (Schedule 4) has ownership shares by plant; it names owners, still not parents. A real answer
#    needs a table of parents kept by a person. Not started: it is a matching problem with judgment in it.

# 2. When the reviewer is done, release the table to the live catalogue: delete its line under catalogue_hold in
#    warehouse/supabase/live_set.yaml, and add it to the live set if the page should read Supabase instead of its copy.

# 3. The table is rebuilt by hand, not by the daily run (EIA-860M changes once a month):
python warehouse/lock.py run --task "storage owners" -- python warehouse/derived/storage_owners.py --snapshot
#    then commit site/data/storage_owners.json. To put it in the daily run, add one run_other line after
#    storage_buildout in warehouse/run_daily.sh.

# 4. The Vercel token (session 77's step, still open): the page cannot be opened on production until it is set.
```

## In plain words

### The table

`storage_owners_monthly`: 9,540 rows, one inventory month (August 2026), public (EIA-860M is in the public domain). It passed the validator, is in coverage, in the archive, and in the public Redivis draft (9,540 rows counted there).

- **What is counted** is what the build-out table counts: generators whose prime mover is EIA's "Batteries", in plants of 1 MW and above; operating is EIA's operating inventory, planned its planned inventory; the grid is the unit's balancing authority where that is one of the seven ISOs.
- **Per company and grid:** operating MW, operating MWh, the average duration (MWh over MW), units, its rank and its share of the grid's operating MW, planned MW and units. A company has a row only where it has a unit: no zero rows.
- **Per grid:** the count of companies, and the share held by the five and the ten largest.
- **No planned MWh:** EIA's planned inventory has no energy column, so no planned duration is written or shown.

**It agrees with the build-out table.** For every grid, operating MW, operating MWh, operating units and planned MW equal the newest month of `storage_buildout_monthly`; each grid's companies sum to the grid; the seven grids and the rest sum to the country. These are tests, and they pass on this machine's tables.

### What it shows

| Grid | Operating MW | Companies | The largest, and its MW | Five largest hold | Ten largest hold | Planned MW |
|---|---|---|---|---|---|---|
| United States | 54,489 | 657 | Engie North America, 1,989 | 11.3 percent | 17.4 percent | 64,458 |
| ERCOT | 18,205 | 160 | Engie North America, 1,954 | 22.0 percent | 31.3 percent | 24,569 |
| CAISO | 17,094 | 177 | AES Clean Energy, 965 | 19.9 percent | 31.9 percent | 10,922 |
| ISO-NE | 1,022 | 99 | Medway Grid LLC, 250 | 65.1 percent | 75.0 percent | 1,048 |

Across the country: 1,137 operating units of 657 companies and 482 planned units of 323 companies; 41 companies have both. Every operating unit reports its energy. The largest planned: Vesper Energy Development LLC, 2,740 MW in 13 units, with nothing operating today.

Two things a reader should take from that table: Texas's largest reporter runs short batteries (Engie's Texas fleet averages 1.4 hours), and the planned megawatts are held by different companies from the operating ones.

### The page: `/storage/owners`, in review

"Who owns the batteries", laid out as the battery page is: a panel on the left (the grid), then one sentence, three headline numbers, a chart (the fifteen largest by operating MW), a table of the 25 largest operating owners, a table of the 25 largest planned, two folds (what an owner is here; what is counted) and the source line. Every number on it is a row of the table and carries the row's key as its hover title. The page does no arithmetic. It is in the Projects menu, because the Grid menu already holds eight pages and a test caps a menu at eight.

Read on this machine's build in the internal view: "The United States has 54,489 MW of operating batteries, reported by 657 companies. The largest, Engie North America, has 1,989 MW; the ten largest hold 17.4 percent."

### The deploy, and every difference

One push, `task/087-storage-owners`; the checks passed (run 37178417280) and the workflow merged it into `main` as `9da1643`. Snapshots of the 20 live pages before (04:55 UTC), after (05:01 UTC) and after again (05:13 UTC).

**First after-snapshot, 05:01 UTC: 29 differences.**

| Where | Differences | What |
|---|---|---|
| All 20 pages | 20 | The menu gains one greyed item: "Who owns the batteries in review" |
| `/` | 9 more | **One checked number gone: the battery tile's `bs|grid=ercot&dur=4&strat=foresight&mw=100&fom=22&ds=6783357|l12_kw:total`, 81.40 before, "not held" after**, with its two lines of text ("USD 81.40 per kW" became "not held per kW", and the tile's sentence lost its dates); and two lines of text that age by themselves ("6.0 days in the ERW table" became "5.9", "5.0 days" became "4.9"). Each changed line counts twice, once as it was and once as it is |

**Second after-snapshot, 05:13 UTC: 60 differences, and the battery tile is not among them.** It reads 81.40 again; the count of checked numbers is 4,098, as before the deploy.

| Where | Differences | What |
|---|---|---|
| All 20 pages | 20 | The same greyed menu item |
| `/` | 34 | The six latest real-time prices and their lines of text: the site's own 15-minute refresh (12 number keys, 22 lines of text) |
| `/network` | 6 | Its hourly refresh: "refreshed 04:05 UTC" became "05:05", and the newest hour of demand moved on by one |

So: no number changed. One number was absent from the home page from the deploy until the cache turned, about twelve minutes.

## Tests and checks

| Check | Result |
|---|---|
| `tests/test_session87.py` | 13 tests pass: the builder on made-up units (sums by company and grid, ranks with ties broken by name, shares, a duration omitted where no unit reports energy, a company with planned units only, an Entity ID with two names stops the build); the table against the build-out table, grid by grid; the companies of a grid sum to the grid; the page's copy is the table, row for row and nothing else; the page's model; the hold |
| The suite on the runner | passed (run 37178417280) |
| Validator, coverage, archive, upload by name, license check | exit 0 each |
| Site: types, build, route check on this machine | exit 0 each; `/storage/owners` answers 200 in the internal view and the in-review page to a visitor |

## Errors and decisions

- **The validator blocked my first table name and two units.** `storage_owners` has two parts and the standard asks three; "percent" and "rank" are not in the unit vocabulary. The table is `storage_owners_monthly`, a share is `pct`, a rank is a `count` (a position, 1 the largest, stated in the header).
- **The menu test failed**: a ninth page in the Grid menu. The page went to Projects.
- **My first count of battery units was one short** (1,136, not 1,137): I had read the generator table telling pandas that "#" starts a comment, and one plant's name holds a "#". The builder reads the table as the build-out builder does, by skipping the header lines, and its totals equal that table's.
- **Decision: the page reads a committed copy of the table**, because the table is held out of Supabase. The copy is written by the builder and tested equal to the table.

## For Samuel

1. **A deploy can blank a home page tile for up to fifteen minutes.** The home page caches whatever its first render after a deploy got, and one slow read gives "not held". Two cheap fixes, neither made tonight because both change how a live page behaves: have the home page refuse to cache a render in which a read failed, or warm the page from the deploy workflow before it goes live. Until then every deploy carries this risk. Tonight's other deploys did not hit it.
2. **Parents** (To finish, 1).
