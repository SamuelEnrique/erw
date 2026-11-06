# The company database's cross-checks

Written by `warehouse/derived/check_companies.py --crosscheck` (session 3303, chain 200). Checks, not corrections: nothing here changes a table. Method: `docs/methods/companies.md`, "Cross-checks".

## A. A utility's EIA-861 retail sales (2025) against its EIA-860M operated capacity

295 companies have both: an EIA utility id with retail sales (Parts A and B of `eia861_utility_sales`, 2025) and operating capacity in `eia860m_operating_generators` (`plants_mw`). The implied use is sales / (capacity x 8,760 h). Above 1, a company sells more at retail than its own fleet could make running every hour of the year: it buys power. Near 0, it sells little at retail: its plants sell at wholesale.

- Implied use above 1: 110; from 0.2 to 1: 166; below 0.2: 19.
- Median 0.60.

The thirty with the most capacity:

| Company | EIA id | Kind | Capacity MW | Retail sales MWh | Implied use |
|---|---|---|---|---|---|
| Florida Power & Light Co | 6452 | utility | 40,818 | 129,983,672 | 0.36 |
| Tennessee Valley Authority | 18642 | utility | 36,337 | 22,483,191 | 0.07 |
| Duke Energy Carolinas, LLC | 5416 | utility | 23,868 | 81,397,950 | 0.39 |
| Georgia Power Co | 7140 | utility | 21,592 | 89,298,710 | 0.47 |
| Virginia Electric & Power Co | 19876 | utility | 20,208 | 98,687,113 | 0.56 |
| Alabama Power Co | 195 | utility | 16,163 | 52,177,426 | 0.37 |
| Duke Energy Progress - (NC) | 3046 | utility | 14,279 | 44,407,482 | 0.36 |
| PacifiCorp | 14354 | utility | 13,628 | 59,211,862 | 0.50 |
| Duke Energy Florida, LLC | 6455 | utility | 13,508 | 41,139,849 | 0.35 |
| MidAmerican Energy Co | 12341 | utility | 13,198 | 32,912,845 | 0.28 |
| Entergy Louisiana LLC | 11241 | utility | 12,819 | 62,178,357 | 0.55 |
| DTE Electric Company | 5109 | utility | 12,584 | 40,079,159 | 0.36 |
| Northern States Power Co - Minnesota | 13781 | utility | 10,954 | 32,715,709 | 0.34 |
| Arizona Public Service Co | 803 | utility | 10,906 | 34,197,800 | 0.36 |
| Union Electric Co - (MO) | 19436 | utility | 10,758 | 31,738,926 | 0.34 |
| Entergy Arkansas LLC | 814 | utility | 9,635 | 25,862,910 | 0.31 |
| City of San Antonio - (TX) | 16604 | utility | 9,580 | 25,925,365 | 0.31 |
| Consumers Energy Co - (MI) | 4254 | utility | 8,955 | 33,807,873 | 0.43 |
| Salt River Project | 16572 | utility | 8,869 | 34,397,819 | 0.44 |
| Oklahoma Gas & Electric Co | 14063 | utility | 8,707 | 33,544,594 | 0.44 |
| Public Service Co of Colorado | 15466 | utility | 8,140 | 28,263,197 | 0.40 |
| Pacific Gas & Electric Co. | 14328 | utility | 7,799 | 24,189,223 | 0.35 |
| Tampa Electric Co | 18454 | utility | 7,251 | 20,943,274 | 0.33 |
| Duke Energy Indiana, LLC | 15470 | utility | 7,121 | 27,498,071 | 0.44 |
| Los Angeles Department of Water & Power | 11208 | utility | 7,110 | 20,722,817 | 0.33 |
| Appalachian Power Co | 733 | utility | 7,003 | 25,931,936 | 0.42 |
| Southwestern Electric Power Co | 17698 | utility | 6,640 | 17,159,584 | 0.30 |
| Nevada Power Co | 13407 | utility | 6,478 | 21,291,918 | 0.38 |
| Indiana Michigan Power Co | 9324 | utility | 6,358 | 19,023,160 | 0.34 |
| Basin Electric Power Coop | 1307 | utility | 6,343 | 1,102,362 | 0.02 |

The ten with the highest implied use (at least 50 MW of capacity):

| Company | EIA id | Kind | Capacity MW | Retail sales MWh | Implied use |
|---|---|---|---|---|---|
| Public Service Elec & Gas Co | 15477 | utility | 79 | 24,723,900 | 35.59 |
| New York State Elec & Gas Corp | 13511 | utility | 62 | 8,851,612 | 16.27 |
| Rochester Gas & Electric Corp | 16183 | utility | 55 | 3,362,527 | 6.97 |
| PUD No 1 of Snohomish County - (WA) | 17470 | utility | 133 | 6,859,233 | 5.90 |
| Entergy New Orleans, LLC | 13478 | utility | 156 | 5,575,178 | 4.08 |
| Consolidated Edison Co-NY Inc | 4226 | utility | 785 | 23,457,015 | 3.41 |
| Evergy Kansas South, Inc | 10005 | utility | 378 | 9,592,292 | 2.90 |
| Loup River Public Power Dist | 11251 | utility | 53 | 1,194,376 | 2.55 |
| City of Santa Clara - (CA) | 16655 | utility | 252 | 4,988,099 | 2.26 |
| PUD No 1 of Clark County - (WA) | 3660 | utility | 248 | 4,695,742 | 2.16 |

## B. A developer's queue MW against its deals' MW

0 companies hold both positions in the ERCOT or NYISO queue (not withdrawn, not completed) and deals in `energy_deals`. The two measure different things (a queue position is a request to connect; a deal's MW is what a story states), so neither is expected to equal the other; a company whose deals' MW far exceeds its queue MW in these two grids builds elsewhere or buys.

| Company | Kind | Queue positions | Queue MW | Deals | Deals MW |
|---|---|---|---|---|---|
| (none) | | | | | |
