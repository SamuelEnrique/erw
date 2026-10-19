* ERW, the Grid tool (/grid?view=network): the figures of the Network view and of its gravity shape, rebuilt from erw_2026_grid_replication.csv.

* The hour shown is the newest hour every reporting pair holds. Method: docs/methods/grid_network.md; the gravity rule: site/lib/networkGravity.ts.

* This do-file has not been run: Stata is not installed on the machine that wrote it. erw_2026_grid_replication.py follows it step for step and prints the same lines.

* Expected values (session 304, 19 October 2026): what this file displays at the page's defaults, equal to the page value by value;

* the Python mirror beside it printed these lines on 19 October 2026 from the committed erw_2026_grid_replication.csv (its hour, 2026-10-12T03:00Z; a file written today shows today's hour):

*   hour_shown = 2026-10-12T03:00:00Z

*   snapshot_built = 2026-10-14T08:05:18Z

*   lag_hours = 53

*   nodes = 70

*   pairs_reporting = 157

*   generation_US48 = 449872

*   ties_CISO = 11

*   net_import_CISO = 6591

*   generation_CISO = 18499

*   gravity_share_CISO = 0.356290

*   gravity_r_CISO = 16.2

*   gravity_d_CISO = 115.0

*   ties_ERCO = 2

*   net_import_ERCO = 128

*   gravity_r_ERCO = 29.4

*   gravity_d_ERCO = 196.7

* The file has 8 comment lines; the column names are on line 9 and the rows start on line 10. Lines 7 and 8 hold the snapshot's refresh and the hour shown.

clear all

local f "erw_2026_grid_replication.csv"

* The refresh and the hour, from the header

local built ""

local hour ""

file open fh using "`f'", read text

file read fh line

local n = 1

while r(eof) == 0 & `n' <= 8 {
    if substr(`"`line'"', 1, 17) == "# snapshot_built," local built = substr(`"`line'"', 18, .)
    if substr(`"`line'"', 1, 13) == "# hour_shown," local hour = substr(`"`line'"', 14, .)
    file read fh line
    local n = `n' + 1
}

file close fh

display "hour_shown = `hour'"

display "snapshot_built = `built'"

* The two-day lag: hours from the hour's start to the refresh

scalar s_lag = round((clock(subinstr(substr("`built'", 1, 19), "T", " ", 1), "YMDhms") - clock(subinstr(substr("`hour'", 1, 19), "T", " ", 1), "YMDhms")) / 3600000)

display "lag_hours = " s_lag

import delimited using "`f'", delimiter(comma) varnames(9) rowrange(10) stringcols(1 2 3 4 6) clear

destring value, replace

quietly count if kind == "node"

display "nodes = " r(N)

quietly count if kind == "tie"

display "pairs_reporting = " r(N)

* The gravity shape's constants (site/lib/networkGravity.ts GRAVITY)

scalar s_size = 640

scalar s_rc = 80

scalar s_dmid = 205

scalar s_dspan = 90

scalar s_sfull = 0.25

scalar s_rmin = 6

scalar s_gap = 4

* The scale: the Lower 48's net generation in the hour

quietly summarize value if kind == "generation" & id == "US48"

scalar s_g0 = r(mean)

display "generation_US48 = " s_g0

foreach b in CISO ERCO ISNE MISO NYIS PJM SWPP {
    quietly count if kind == "tie" & (id == "`b'" | other == "`b'")
    local nt = r(N)
    display "ties_`b' = " `nt'
    * net imports: a tie the grid reports as "id" is its export, so its sign is flipped; as "other", its import
    quietly gen double imp = cond(id == "`b'", -value, value) if kind == "tie" & (id == "`b'" | other == "`b'")
    quietly summarize imp
    scalar s_net = r(sum)
    drop imp
    if `nt' == 0 display "net_import_`b' = no tie reported"
    if `nt' > 0 display "net_import_`b' = " s_net
    quietly summarize value if kind == "demand" & id == "`b'"
    if `nt' > 0 & r(N) > 0 & r(mean) != 0 display "net_share_of_demand_pct_`b' = " %4.2f round(abs(s_net) / r(mean) * 100, 0.01)
    quietly summarize value if kind == "generation" & id == "`b'"
    scalar s_held = r(N)
    scalar s_g = r(mean)
    scalar s_r = s_rmin
    scalar s_pull = 0
    if s_held > 0 & s_g > 0 scalar s_r = max(s_rmin, s_rc * sqrt(s_g / s_g0))
    if `nt' > 0 & s_held > 0 & s_g > 0 scalar s_pull = min(1, max(-1, (s_net / s_g) / s_sfull))
    if `nt' > 0 & s_held > 0 & s_g <= 0 & s_net != 0 scalar s_pull = sign(s_net)
    scalar s_d = min(s_size / 2 - s_r - s_gap, max(s_rc + s_r + s_gap, s_dmid - s_dspan * s_pull))
    if s_held > 0 display "generation_`b' = " s_g
    if s_held == 0 display "generation_`b' = not held"
    if `nt' > 0 & s_held > 0 & s_g > 0 display "gravity_share_`b' = " %8.6f s_net / s_g
    if !(`nt' > 0 & s_held > 0 & s_g > 0) display "gravity_share_`b' = none"
    display "gravity_r_`b' = " %3.1f round(s_r, 0.1)
    display "gravity_d_`b' = " %3.1f round(s_d, 0.1)
}
