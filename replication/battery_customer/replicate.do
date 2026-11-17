* ERW, What a battery saves a customer (/battery/customer): the five headline figures, rebuilt from the nine numbers a
* reader types. Method: docs/methods/battery_customer.md, section 3 (session 7504, chain 304).
*
* The page reads no table, so this file reads none: each case's nine numbers are typed below, as cases.json holds them
* (the rates are the publisher's, as its document prints them; the customer's peak and the battery are the case).
*
* Not run: Stata is not on the machine that wrote this file. Its Python mirror printed these lines on 16 November 2026
* (python replication/battery_customer/replicate.py --headline):
*
*   Seattle City Light, medium, City of Seattle, time of use: saved a year (USD): 11830.26
*   Seattle City Light, medium, Downtown Network, time of use: saved a year (USD): 19538.69
*   Salt River Project E-32, summer peak: saved a month (USD): 1033.70
*   Austin Energy, secondary voltage 10 to under 300 kW: saved a year (USD): 7549.66
*   Southern California Edison TOU-GS-2 B, summer 2013, as NREL prints it: saved a month (USD): 3224.87
*
* The page shows each to the whole dollar: $12,795, $21,733, $1,115, $8,931 and $3,677.

clear all

* saving: peak kW, demand charge, peak rate, off-peak rate, battery kW, battery kWh, peak hours, days, round trip (percent)
* leaves the month in r(month) and the year in r(year)
capture program drop saving
program define saving, rclass
    args peak dcharge prate orate bkw bkwh hours days rt
    * what comes off the peak: the smallest of the battery's power, its energy over the peak's hours, and the peak
    scalar shaved = min(`bkw', `bkwh' / `hours', `peak')
    scalar demand = shaved * 0.85 * `dcharge'   // ruling alternative 3 (wip/alt-battery-customer-3): NREL's 85 percent; main: all of it
    * one full cycle a day: the battery out at the peak rate, that over the round trip in at the off-peak rate
    scalar eta = `rt' / 100
    scalar perday = `bkwh' * `prate' - (`bkwh' / eta) * `orate'
    * when moving energy does not pay, the battery cycles for the peak alone and the loss is a cost
    scalar forpeak = shaved * `hours'
    scalar energy = cond(perday > 0, perday, forpeak * `prate' - (forpeak / eta) * `orate') * `days'
    return scalar month = demand + energy
    return scalar year = 12 * (demand + energy)
end

* 1: Seattle City Light, Medium General Service, City of Seattle, Time of Use (Business Rates, read 16 November 2026)
saving 400 5.36 0.1218 0.0609 100 400 4 26 86
display "Seattle City Light, medium, City of Seattle, time of use: saved a year (USD): " %12.2f r(year)

* 2: the same, Downtown Network
saving 400 12.19 0.1360 0.0680 100 400 4 26 86
display "Seattle City Light, medium, Downtown Network, time of use: saved a year (USD): " %12.2f r(year)

* 3: Salt River Project, E-32, summer peak (effective the November 2025 billing cycle): the battery's energy sets 80 kW
saving 400 6.75 0.1924 0.1093 100 400 5 22 86
display "Salt River Project E-32, summer peak: saved a month (USD): " %12.2f r(month)

* 4: Austin Energy, Secondary Voltage 10 kW to under 300 kW (tariff of October 1, 2026): one price for every hour,
*    so moving energy does not pay and the energy lost is a cost
saving 200 15.35 0.06797 0.06797 50 100 2 21 86
display "Austin Energy, secondary voltage 10 to under 300 kW: saved a year (USD): " %12.2f r(year)

* 5: Southern California Edison, TOU-GS-2 Option B, summer, about April 2013, as NREL/TP-5400-63162 prints it
saving 400 30.14 0.1466 0.0582 100 400 4 21 86
display "Southern California Edison TOU-GS-2 B, summer 2013, as NREL prints it: saved a month (USD): " %12.2f r(month)
