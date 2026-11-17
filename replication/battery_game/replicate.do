* ERW, the home battery game (/play/battery): the five headline figures, rebuilt from the game's stated rules.

* Method: docs/methods/battery_game.md ("The battery's settings", "Difficulties", "Version 3", "The fleet call",
* "The California days"). Session 7535, chain 304, 16 November 2026.

* Input: stata_input.csv beside this file: one row an interval of two frozen days (site/data/battery_levels.json),
* the heat day (2023-08-10, ERCOT HB_HUBAVG) and the CAISO duck day (2026-07-24, SP15), with the local clock, the real
* price and two plays on Normal: the perfect plan (the page's own optimum, cases.json) and the plain rule (charge in the
* day's 8 cheapest intervals, sell in its 8 dearest). Written by "python replication/battery_game/replicate.py --write".
* Run this file from its own folder.

* This do-file has not been run: Stata is not installed on the machine that wrote it. "python replicate.py" prints the
* same five figures under "the five headline figures".

* Expected values (the levels as frozen on 26 September and 1 October 2026; they do not change unless the builder is
* rerun with --rebuild-ercot):
*   1. The heat day at a glance: lowest 24.90, average 511.93 (511.9258), highest 3,842.89 USD/MWh
*   2. The heat day, Normal, the default battery: the perfect battery's score USD 60.97 (60.9710)
*   3. The same day and rules: the plain rule's score USD 43.89 (43.8903)
*   4. The perfect battery's fleet of 10,000 homes: USD 609,710.12
*   5. The duck day: the rise from the 12:00 to 15:00 Pacific mean to the 18:00 to 21:00 mean, 408.90 USD/MWh

clear all

import delimited using "stata_input.csv", delimiter(comma) varnames(1) stringcols(1 3) clear

* 1. The day at a glance: the lowest, the mean and the highest real price of the day's 96 intervals.

preserve
keep if slug == "heat"
summarize price
display "1. heat: lowest " %9.2f r(min) ", average " %9.4f r(mean) ", highest " %9.2f r(max)
restore

* 2 to 4. A play on Normal (the note's rules): the battery holds 13.5 kWh, starts half full, moves 5 kW x 0.25 h =
* 1.25 kWh at the meter each interval; the efficiency is split evenly, sqrt(0.9) in and again out; a charge stops at
* full, a sale at empty; no reserve, no wear, no emergency on Normal. The fleet call is the day's dearest clock hour
* (four intervals from the day's start, the earliest on a tie): each kWh delivered in it earns the hour's mean price
* again, never below zero. Money is USD 5 plus the score; the play ends in the first interval it falls below zero.

preserve
keep if slug == "heat"
sort i
gen hour = floor(i / 4)
bysort hour: egen hmean = mean(price)
sort i
quietly summarize hmean
scalar callmean = r(max)
quietly summarize i if hmean == callmean
scalar callfirst = 4 * floor(r(min) / 4)
scalar bonusp = max(0, callmean)
scalar eta = sqrt(0.9)
scalar cap = 13.5
scalar grid = 5 * 15 / 60

foreach play in act_perfect act_rule8 {
    scalar soc = cap * 0.5
    scalar score = 0
    scalar over = 0
    forvalues k = 1/`=_N' {
        if over == 0 {
            scalar a = `play'[`k']
            scalar p = price[`k']
            scalar ii = i[`k']
            scalar cash = 0
            scalar out = 0
            if a == 1 {
                scalar stored = min(grid * eta, cap - soc)
                if stored > 0 {
                    scalar cash = -(stored / eta) * p / 1000
                    scalar soc = soc + stored
                }
            }
            if a == -1 {
                scalar taken = min(grid / eta, soc)
                if taken > 0 {
                    scalar out = taken * eta
                    scalar cash = out * p / 1000
                    scalar soc = soc - taken
                }
            }
            scalar bonus = cond(ii >= callfirst & ii <= callfirst + 3, out * bonusp / 1000, 0)
            scalar score = score + cash + bonus
            if 5 + score < 0 scalar over = 1
        }
    }
    display "`play': score " %12.4f score ", fleet of 10,000 homes " %14.2f score * 10000
}
restore

* 5. The duck day: the mean price of the intervals starting 12:00 to 14:45 Pacific, of those starting 18:00 to 20:45,
* and the rise between them.

preserve
keep if slug == "caiso-duck"
quietly summarize price if clock >= "12:00" & clock <= "14:45"
scalar mid = r(mean)
quietly summarize price if clock >= "18:00" & clock <= "20:45"
scalar eve = r(mean)
display "5. duck: " %9.2f mid " to " %9.2f eve ", a rise of " %9.2f eve - mid
restore
