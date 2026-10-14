# The problem sets (`/learn/problems`)

Energy Research Warehouse (ERW). Five sets of five questions for a class, written in session 44 (sets A to C), 46 (D) and 55 (E). The code is `site/lib/problems.ts`; the index is `/learn/problems`, and since session 288 it is the one entry of the Games menu for the sets (Samuel's ruling 14 of 14 October 2026).

## How an answer is made

- Every figure is computed on the server when the page is built, from the live set (Supabase) or a committed file the site reads (`site/data/bill_rules.json`, `site/data/severance_rules.json`, `site/data/merchant_snapshot.json`, the network snapshot). None is typed.
- Each figure carries a check key; `site/scripts/check-values.mjs` recomputes it on its own and compares it with the page. A derived figure is `calc|<op>|<A>|<B>` (ratio, difference, percent) of two keys that are each recomputed.
- The pages are rebuilt at most once an hour, so the numbers move as the tables update.

## Which month, which hubs, which days (session 288, Samuel's rulings of 14 October 2026)

- **The latest complete month (ruling 5a).** A month of `cost_of_power_monthly` is complete for a hub when its `rt_hours` equals its `hours_in_month`: every hour held. Set B question 1, the bill questions B3 and B4, and since session 288 B2, B5 and D3 take the latest such month. B5 and D3 read `cost_of_power_hourly_profile`, which has no hour count of its own: they take the latest profile month that is complete for ERCOT's hub average in `cost_of_power_monthly`. Until session 288 these three took the latest month held, often one that had just begun.
- **All hubs, named and counted (ruling 4).** Set B question 2 names every hub of `cost_of_power_monthly` with its grid (two are CAISO's: NP15 and SP15), says how many there are, and takes the latest month in which every one of them is complete. A hub with gaps (ISO-NE's internal hub misses hours in several recent months) pulls that month back; the question then says which month it is. Until session 288 it read "all six ISO hubs" and listed seven.
- **The storm's days against as many normal days (ruling 6a).** Set E question 5 sets what the solar plant earned over the event window (18 days for Uri) against the mean baseline day of the same event (the same dates of earlier years) times the window's days. The keys are `mrs|<inputs>|<event>|days`, `|base_mean` and `|base_window`, recomputed from `lib/merchant.ts`'s `stress()`. Until session 288 the window was set against one normal week, seven days, which made the ratio about 2.6 times too large.
- **The ratio questions (ruling 7a)** ask in the order a student reads: "ERCOT's peak was how many times CAISO's?" (A1, A3, C1, C5).

## Limits

- The answers move every day; a class that prepares on one day meets other numbers on the next. A dated edition of each set beside the live one is ruling 8a (a later session).
- The battery questions of set D use the game's assumed battery (`site/lib/battery.ts`): 13.5 kWh, 90 percent round trip.
