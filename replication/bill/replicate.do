* ERW, What is on an electricity bill (/learn/bill): the five headline figures, the five default bills, rebuilt from the
* tariffs' rates. Method: docs/methods/bill.md, "The arithmetic, line by line" (session 7533, chain 304).
*
* The bills read no table: each rate below is typed as site/data/bill_rules.json holds it, with the tariff passage there.
* Every default bill: 600 kWh, 30 days, winter in California, 20 percent of use from 4 to 9 p.m.
*
* Not run: Stata is not on the machine that wrote this file. Its Python mirror printed these lines on 16 November 2026
* (python replication/bill/replicate.py --headline):
*
*   California: a PG&E home on time-of-use rate E-TOU-C: the default bill (USD): 229.63
*   California: an SCE home (Southern California Edison, TOU-D-4-9PM): the default bill (USD): 224.76
*   California: an SDG&E home (San Diego Gas & Electric, TOU-DR1): the default bill (USD): 332.91
*   Texas: a home in Oncor's area of ERCOT: the default bill (USD): 95.27
*   Texas: a home in CenterPoint's area (Houston): the default bill (USD): 95.28
*
* The page shows each to the cent, on its five cards: 229.63, 224.76, 332.91, 95.27 and 95.28 USD.

clear all
scalar kwh = 600
scalar days = 30
scalar pk = 0.2

* 1: PG&E E-TOU-C, by Sheet 2's total rates (the unbundled lines add up to them): winter peak 0.39757, off-peak 0.36757;
* the baseline credit 0.0814 on territory T's winter 7.5 kWh a day; Income Tier 3's Base Services Charge 0.79343 a day
scalar base = min(kwh, 7.5 * days)
scalar pge = kwh * (pk * 0.39757 + (1 - pk) * 0.36757) - base * 0.0814 + days * 0.79343
display "PG&E E-TOU-C, the default bill (USD): " %9.2f pge

* 2: SCE TOU-D-4-9PM, winter: 4 to 9 p.m. mid-peak, a third super off-peak, the rest off-peak; delivery plus generation
* per period (mid 0.33156 + 0.17956, super 0.25153 + 0.08452, off 0.27270 + 0.10245), the Fixed Recovery Charge 0.00619;
* the baseline credit 0.10099 on Region 9's winter 12.0 kWh a day; the Base Services Charge 0.794 a day
scalar sup = 0.3333
scalar sce = kwh * (pk * (0.33156 + 0.17956) + sup * (0.25153 + 0.08452) + (1 - pk - sup) * (0.27270 + 0.10245)) + kwh * 0.00619 ///
    - min(kwh, 12.0 * days) * 0.10099 + days * 0.794
display "SCE TOU-D-4-9PM, the default bill (USD): " %9.2f sce

* 3: SDG&E TOU-DR1, winter total rates (on-peak 0.61471, super off-peak 0.43719, off-peak 0.53060), 34.52 percent super
* off-peak; no baseline credit (the allowance is 0 until the reader types it); the Base Services Charge 0.79343 a day
scalar sups = 0.3452
scalar sdge = kwh * (pk * 0.61471 + sups * 0.43719 + (1 - pk - sups) * 0.53060) + days * 0.79343
display "SDG&E TOU-DR1, the default bill (USD): " %9.2f sdge

* 4: Oncor: the retailer's default energy charge 0.0907; Oncor's fixed 1.48 + 2.58 a month; its per-kWh charges and
* riders 0.036043 + 0.019046 + 0.001487 + 0 + 0 + 0.000086 + 0.001027 + 0.003633 = 0.061322
scalar oncor = kwh * 0.0907 + 1.48 + 2.58 + kwh * (0.036043 + 0.019046 + 0.001487 + 0.000086 + 0.001027 + 0.003633)
display "Oncor, the default bill (USD): " %9.2f oncor

* 5: CenterPoint: the default energy charge 0.0853; fixed 2.11 + 2.79; per kWh 0.023240 + 0.030812 + 0.006137 + 0.001576
* + 0.000013 + 0.000742 + 0.000048 + 0 + 0.000636 - 0.000023 + 0.002848 - 0.000418 - 0.000278 = 0.065333
scalar cnp = kwh * 0.0853 + 2.11 + 2.79 + kwh * (0.023240 + 0.030812 + 0.006137 + 0.001576 + 0.000013 + 0.000742 + 0.000048 ///
    + 0.000636 - 0.000023 + 0.002848 - 0.000418 - 0.000278)
display "CenterPoint, the default bill (USD): " %9.2f cnp

* The wholesale share of each (the page's cards): kWh x the price of September 2026 in cost_of_power_monthly (NP15 44.8469,
* SP15 38.5194, ERCOT's hub average 39.5037 USD/MWh) / 1000, over the bill. Expected: 11.72, 10.28, 6.94, 24.88, 24.88.
display "shares (percent): " %6.2f (kwh * 44.8469 / 1000 / pge * 100) " " %6.2f (kwh * 38.5194 / 1000 / sce * 100) " " ///
    %6.2f (kwh * 38.5194 / 1000 / sdge * 100) " " %6.2f (kwh * 39.5037 / 1000 / oncor * 100) " " %6.2f (kwh * 39.5037 / 1000 / cnp * 100)
