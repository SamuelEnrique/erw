* ERW, the Grid tool (/grid): the Ask panel's stored answers, the plain queries, rebuilt in Stata from the warehouse's tables.

* Written by figures_of_the_page.py from page_figures.json: do not edit by hand; write it again. Run from this folder, by replicate.do or alone, with the global tables set to the folder of the tables as CSV.

* Each block keeps the rows the query's filter keeps (and, for a grid's own chat, the rows of that grid, as warehouse/chat/tools.py scope_rows), computes the aggregation, and displays each figure the answer states beside it. A figure is met when it equals the value or the count of rows to its shown decimals. A figure whose table was held for its grid on the day prints "license needed" and is not computed.

* This do-file has not been run: Stata is not installed on the machine that wrote it.

capture program drop erw_read

program define erw_read
    args file
    import delimited using "`file'", varnames(nonames) stringcols(_all) clear
    drop if substr(v1, 1, 1) == "#"
    foreach v of varlist _all {
        local nm = strtoname(`v'[1])
        rename `v' `nm'
    }
    drop in 1
end

* ask|s302:q01|0: ercot_hub_prices_daily, aggregation=mean, entity=ercot:HB_HUBAVG, variable=rt_peak_mean, start=2024-01-01, end=2025-01-01

erw_read "$tables/ercot_hub_prices_daily.csv"

keep if entity == "ercot:HB_HUBAVG"

keep if variable == "rt_peak_mean"

keep if ts_utc >= "2024-01-01"

keep if ts_utc < "2025-01-01"

destring value, replace force

summarize value

scalar v_value = r(mean)

scalar v_n = _N

display "ask|s302:q01|0|0: the answer states 31.57; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 31.57), abs(v_n - 31.57)) <= 0.005000001, "yes", "no")

* ask|s302:q02|0: cost_of_power_monthly, aggregation=mean, entity=ercot:HB_HUBAVG, variable=rt_load_weighted, start=2025-07-01, end=2025-08-01

erw_read "$tables/cost_of_power_monthly.csv"

keep if substr(entity, 1, 6) == "ercot:"

keep if entity == "ercot:HB_HUBAVG"

keep if variable == "rt_load_weighted"

keep if ts_utc >= "2025-07-01"

keep if ts_utc < "2025-08-01"

destring value, replace force

summarize value

scalar v_value = r(mean)

scalar v_n = _N

display "ask|s302:q02|0|0: the answer states 34.18; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 34.18), abs(v_n - 34.18)) <= 0.005000001, "yes", "no")

* ask|s302:q03|0: merchant_revenue_monthly, aggregation=mean, entity=ercot:HB_HUBAVG, variable=wind_capture_rate, start=2024-03-01, end=2024-04-01

erw_read "$tables/merchant_revenue_monthly.csv"

keep if substr(entity, 1, 6) == "ercot:"

keep if entity == "ercot:HB_HUBAVG"

keep if variable == "wind_capture_rate"

keep if ts_utc >= "2024-03-01"

keep if ts_utc < "2024-04-01"

destring value, replace force

summarize value

scalar v_value = r(mean)

scalar v_n = _N

display "ask|s302:q03|0|0: the answer states 72.5; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 72.5), abs(v_n - 72.5)) <= 0.050000001, "yes", "no")

* ask|s302:q04|0: ercot_peak_premium_annual, aggregation=latest, entity=ercot:HB_SOUTH, variable=n_scarcity, start=2023-01-01, end=2024-01-01

erw_read "$tables/ercot_peak_premium_annual.csv"

keep if entity == "ercot:HB_SOUTH"

keep if variable == "n_scarcity"

keep if ts_utc >= "2023-01-01"

keep if ts_utc < "2024-01-01"

destring value, replace force

gsort -ts_utc

scalar v_value = value[1]

scalar v_n = _N

display "ask|s302:q04|0|0: the answer states 213; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 213.0), abs(v_n - 213.0)) <= 0.500000001, "yes", "no")

* ask|s302:q05|0: carbon_intensity_monthly, aggregation=mean, entity=eia930:ERCO, variable=intensity_demand, start=2025-01-01, end=2025-02-01

erw_read "$tables/carbon_intensity_monthly.csv"

keep if ba == "erco"

keep if entity == "eia930:ERCO"

keep if variable == "intensity_demand"

keep if ts_utc >= "2025-01-01"

keep if ts_utc < "2025-02-01"

destring value, replace force

summarize value

scalar v_value = r(mean)

scalar v_n = _N

display "ask|s302:q05|0|0: the answer states 356.7; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 356.7), abs(v_n - 356.7)) <= 0.050000001, "yes", "no")

* ask|s302:q11|0: iso_curtailment_monthly, aggregation=sum, variable=curtailed_wind_mwh, start=2024-01-01, end=2025-01-01

erw_read "$tables/iso_curtailment_monthly.csv"

keep if substr(entity, 1, 6) == "caiso:"

keep if variable == "curtailed_wind_mwh"

keep if ts_utc >= "2024-01-01"

keep if ts_utc < "2025-01-01"

destring value, replace force

summarize value

scalar v_value = r(sum)

scalar v_n = _N

display "ask|s302:q11|0|0: the answer states 230,777; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 230777.0), abs(v_n - 230777.0)) <= 0.500000001, "yes", "no")

display "ask|s302:q11|0|1: the answer states 230776.644; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 230776.644), abs(v_n - 230776.644)) <= 0.000500001, "yes", "no")

display "ask|s302:q11|0|2: the answer states 12; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 12.0), abs(v_n - 12.0)) <= 0.500000001, "yes", "no")

* ask|s302:q12|0: carbon_intensity_monthly, aggregation=min, variable=intensity_generation, entity=eia930:CISO

erw_read "$tables/carbon_intensity_monthly.csv"

keep if ba == "ciso"

keep if entity == "eia930:CISO"

keep if variable == "intensity_generation"

destring value, replace force

summarize value

scalar v_value = r(min)

scalar v_n = _N

display "ask|s302:q12|0|0: the answer states 44.2145; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 44.2145), abs(v_n - 44.2145)) <= 5.0001e-05, "yes", "no")

display "ask|s302:q12|0|1: the answer states 69; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 69.0), abs(v_n - 69.0)) <= 0.500000001, "yes", "no")

* ask|s302:q12|1: query with group_by month; replicate.py only

* ask|s302:q12|2: query with group_by year; replicate.py only

* ask|s302:q13|0: cost_of_power_monthly, aggregation=latest, entity=caiso:TH_SP15_GEN-APND, variable=rt_load_weighted, start=2024-09-01, end=2024-10-01

erw_read "$tables/cost_of_power_monthly.csv"

keep if substr(entity, 1, 6) == "caiso:"

keep if entity == "caiso:TH_SP15_GEN-APND"

keep if variable == "rt_load_weighted"

keep if ts_utc >= "2024-09-01"

keep if ts_utc < "2024-10-01"

destring value, replace force

gsort -ts_utc

scalar v_value = value[1]

scalar v_n = _N

display "ask|s302:q13|0|0: the answer states 33.07; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 33.07), abs(v_n - 33.07)) <= 0.005000001, "yes", "no")

* ask|s302:q13|1: compare with its own rules; replicate.py only

* ask|s302:q13|2: cost_of_power_monthly, aggregation=latest, entity=caiso:TH_SP15_GEN-APND, variable=rt_simple_mean, start=2024-09-01, end=2024-10-01

erw_read "$tables/cost_of_power_monthly.csv"

keep if substr(entity, 1, 6) == "caiso:"

keep if entity == "caiso:TH_SP15_GEN-APND"

keep if variable == "rt_simple_mean"

keep if ts_utc >= "2024-09-01"

keep if ts_utc < "2024-10-01"

destring value, replace force

gsort -ts_utc

scalar v_value = value[1]

scalar v_n = _N

display "ask|s302:q13|2|0: the answer states 31.38; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 31.38), abs(v_n - 31.38)) <= 0.005000001, "yes", "no")

* ask|s302:q13|3: cost_of_power_monthly, aggregation=latest, entity=caiso:TH_SP15_GEN-APND, variable=rt_shape_premium, start=2024-09-01, end=2024-10-01

erw_read "$tables/cost_of_power_monthly.csv"

keep if substr(entity, 1, 6) == "caiso:"

keep if entity == "caiso:TH_SP15_GEN-APND"

keep if variable == "rt_shape_premium"

keep if ts_utc >= "2024-09-01"

keep if ts_utc < "2024-10-01"

destring value, replace force

gsort -ts_utc

scalar v_value = value[1]

scalar v_n = _N

display "ask|s302:q13|3|0: the answer states 1.68; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 1.68), abs(v_n - 1.68)) <= 0.005000001, "yes", "no")

* ask|s302:q14|0: merchant_revenue_monthly, aggregation=latest, entity=caiso:TH_SP15_GEN-APND, variable=battery_4h_capture_rate, start=2025-03-01, end=2025-04-01

erw_read "$tables/merchant_revenue_monthly.csv"

keep if substr(entity, 1, 6) == "caiso:"

keep if entity == "caiso:TH_SP15_GEN-APND"

keep if variable == "battery_4h_capture_rate"

keep if ts_utc >= "2025-03-01"

keep if ts_utc < "2025-04-01"

destring value, replace force

gsort -ts_utc

scalar v_value = value[1]

scalar v_n = _N

display "ask|s302:q14|0|0: the answer states 216.5; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 216.5), abs(v_n - 216.5)) <= 0.050000001, "yes", "no")

* ask|s302:q14|1: merchant_revenue_monthly, aggregation=latest, entity=caiso:TH_SP15_GEN-APND, variable=battery_4h_capture_price, start=2025-03-01, end=2025-04-01

erw_read "$tables/merchant_revenue_monthly.csv"

keep if substr(entity, 1, 6) == "caiso:"

keep if entity == "caiso:TH_SP15_GEN-APND"

keep if variable == "battery_4h_capture_price"

keep if ts_utc >= "2025-03-01"

keep if ts_utc < "2025-04-01"

destring value, replace force

gsort -ts_utc

scalar v_value = value[1]

scalar v_n = _N

display "ask|s302:q14|1|0: the answer states 53.71; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 53.71), abs(v_n - 53.71)) <= 0.005000001, "yes", "no")

* ask|s302:q14|2: merchant_revenue_monthly, aggregation=latest, entity=caiso:TH_SP15_GEN-APND, variable=battery_4h_flat_price, start=2025-03-01, end=2025-04-01

erw_read "$tables/merchant_revenue_monthly.csv"

keep if substr(entity, 1, 6) == "caiso:"

keep if entity == "caiso:TH_SP15_GEN-APND"

keep if variable == "battery_4h_flat_price"

keep if ts_utc >= "2025-03-01"

keep if ts_utc < "2025-04-01"

destring value, replace force

gsort -ts_utc

scalar v_value = value[1]

scalar v_n = _N

display "ask|s302:q14|2|0: the answer states 24.81; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 24.81), abs(v_n - 24.81)) <= 0.005000001, "yes", "no")

* ask|s302:q15|0: cost_of_power_monthly, aggregation=latest, entity=caiso:TH_SP15_GEN-APND, variable=da_shape_premium, start=2025-03-01, end=2025-04-01

erw_read "$tables/cost_of_power_monthly.csv"

keep if substr(entity, 1, 6) == "caiso:"

keep if entity == "caiso:TH_SP15_GEN-APND"

keep if variable == "da_shape_premium"

keep if ts_utc >= "2025-03-01"

keep if ts_utc < "2025-04-01"

destring value, replace force

gsort -ts_utc

scalar v_value = value[1]

scalar v_n = _N

display "ask|s302:q15|0|0: the answer states 1.1363; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 1.1363), abs(v_n - 1.1363)) <= 5.0001e-05, "yes", "no")

* ask|s302:q15|1: cost_of_power_monthly, aggregation=latest, entity=caiso:TH_SP15_GEN-APND, variable=da_load_weighted, start=2025-03-01, end=2025-04-01

erw_read "$tables/cost_of_power_monthly.csv"

keep if substr(entity, 1, 6) == "caiso:"

keep if entity == "caiso:TH_SP15_GEN-APND"

keep if variable == "da_load_weighted"

keep if ts_utc >= "2025-03-01"

keep if ts_utc < "2025-04-01"

destring value, replace force

gsort -ts_utc

scalar v_value = value[1]

scalar v_n = _N

display "ask|s302:q15|1|0: the answer states 25.4274; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 25.4274), abs(v_n - 25.4274)) <= 5.0001e-05, "yes", "no")

* ask|s302:q15|2: cost_of_power_monthly, aggregation=latest, entity=caiso:TH_SP15_GEN-APND, variable=da_simple_mean, start=2025-03-01, end=2025-04-01

erw_read "$tables/cost_of_power_monthly.csv"

keep if substr(entity, 1, 6) == "caiso:"

keep if entity == "caiso:TH_SP15_GEN-APND"

keep if variable == "da_simple_mean"

keep if ts_utc >= "2025-03-01"

keep if ts_utc < "2025-04-01"

destring value, replace force

gsort -ts_utc

scalar v_value = value[1]

scalar v_n = _N

display "ask|s302:q15|2|0: the answer states 24.2911; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 24.2911), abs(v_n - 24.2911)) <= 5.0001e-05, "yes", "no")

* ask|s302:q15|3: cost_of_power_monthly, aggregation=latest, entity=caiso:TH_SP15_GEN-APND, variable=da_hours, start=2025-03-01, end=2025-04-01

erw_read "$tables/cost_of_power_monthly.csv"

keep if substr(entity, 1, 6) == "caiso:"

keep if entity == "caiso:TH_SP15_GEN-APND"

keep if variable == "da_hours"

keep if ts_utc >= "2025-03-01"

keep if ts_utc < "2025-04-01"

destring value, replace force

gsort -ts_utc

scalar v_value = value[1]

scalar v_n = _N

display "ask|s302:q15|3|0: the answer states 719; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 719.0), abs(v_n - 719.0)) <= 0.500000001, "yes", "no")

* ask|s302:q15|4: cost_of_power_monthly, aggregation=latest, entity=caiso:TH_SP15_GEN-APND, variable=hours_in_month, start=2025-03-01, end=2025-04-01

erw_read "$tables/cost_of_power_monthly.csv"

keep if substr(entity, 1, 6) == "caiso:"

keep if entity == "caiso:TH_SP15_GEN-APND"

keep if variable == "hours_in_month"

keep if ts_utc >= "2025-03-01"

keep if ts_utc < "2025-04-01"

destring value, replace force

gsort -ts_utc

scalar v_value = value[1]

scalar v_n = _N

display "ask|s302:q15|4|0: the answer states 743; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 743.0), abs(v_n - 743.0)) <= 0.500000001, "yes", "no")

* ask|s267:q29|0: carbon_intensity_monthly, aggregation=latest, entity=eia930:PJM, variable=intensity_demand, start=2025-01-01, end=2025-02-01

erw_read "$tables/carbon_intensity_monthly.csv"

keep if entity == "eia930:PJM"

keep if variable == "intensity_demand"

keep if ts_utc >= "2025-01-01"

keep if ts_utc < "2025-02-01"

destring value, replace force

gsort -ts_utc

scalar v_value = value[1]

scalar v_n = _N

display "ask|s267:q29|0|0: the answer states 375.95; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 375.95), abs(v_n - 375.95)) <= 0.005000001, "yes", "no")

* ask|s267:q29|1: compare with its own rules; replicate.py only

* ask|s302:q16|0: license needed (the table cost_of_power_monthly is held for this grid on the day); not computed

* ask|s302:q16|1: license needed (the table cost_of_power_monthly is held for this grid on the day); not computed

* ask|s302:q16|2: license needed (the table cost_of_power_monthly is held for this grid on the day); not computed

* ask|s267:q18|0: license needed (the table cost_of_power_monthly is held for this grid on the day); not computed

* ask|s267:q18|1: license needed (the table cost_of_power_monthly is held for this grid on the day); not computed

* ask|s267:q18|2: license needed (the table cost_of_power_monthly is held for this grid on the day); not computed

* ask|s267:q18|3: license needed (the table cost_of_power_monthly is held for this grid on the day); not computed

* ask|s267:q18|4: license needed (the table cost_of_power_monthly is held for this grid on the day); not computed

* ask|s267:q18|5: license needed (the table cost_of_power_monthly is held for this grid on the day); not computed

* ask|s267:q18|6: license needed (the table cost_of_power_monthly is held for this grid on the day); not computed

* ask|s267:q19|0: license needed (the table merchant_revenue_monthly is held for this grid on the day); not computed

* ask|s267:q19|1: license needed (the table merchant_revenue_monthly is held for this grid on the day); not computed

* ask|s267:q20|0: license needed (the table nyiso_interconnection_queue is held for this grid on the day); not computed

* ask|s267:q20|1: license needed (the table nyiso_interconnection_queue is held for this grid on the day); not computed

* ask|s302:q18|0: query with its own rules; replicate.py only

* ask|s302:q20|0: license needed (the table merchant_revenue_monthly is held for this grid on the day); not computed

* ask|s302:q20|1: license needed (the table merchant_revenue_monthly is held for this grid on the day); not computed

* ask|s302:q20|2: license needed (the table merchant_revenue_monthly is held for this grid on the day); not computed

* ask|s267:q25|0: license needed (the table cost_of_power_monthly is held for this grid on the day); not computed

* ask|s267:q25|1: license needed (the table cost_of_power_monthly is held for this grid on the day); not computed

* ask|s267:q26|0: carbon_intensity_monthly, aggregation=latest, entity=eia930:ISNE, variable=intensity_demand, start=2025-01-01, end=2025-02-01

erw_read "$tables/carbon_intensity_monthly.csv"

keep if entity == "eia930:ISNE"

keep if variable == "intensity_demand"

keep if ts_utc >= "2025-01-01"

keep if ts_utc < "2025-02-01"

destring value, replace force

gsort -ts_utc

scalar v_value = value[1]

scalar v_n = _N

display "ask|s267:q26|0|0: the answer states 267.44; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 267.44), abs(v_n - 267.44)) <= 0.005000001, "yes", "no")

* ask|s302:q17|0: query with group_by month; replicate.py only

* ask|s302:q17|1: query with group_by month; replicate.py only

* ask|s302:q17|2: query with group_by month; replicate.py only

* ask|s267:q21|0: query with group_by entity; replicate.py only

* ask|s267:q21|1: query with group_by month; replicate.py only

* ask|s267:q22|0: query with group_by variable; replicate.py only

* ask|s267:q23|0: carbon_intensity_monthly, aggregation=min, entity=eia930:SWPP, variable=intensity_generation

erw_read "$tables/carbon_intensity_monthly.csv"

keep if entity == "eia930:SWPP"

keep if variable == "intensity_generation"

destring value, replace force

summarize value

scalar v_value = r(min)

scalar v_n = _N

display "ask|s267:q23|0|0: the answer states 274.64; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 274.64), abs(v_n - 274.64)) <= 0.005000001, "yes", "no")

display "ask|s267:q23|0|1: the answer states 46; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 46.0), abs(v_n - 46.0)) <= 0.500000001, "yes", "no")

* ask|s267:q24|0: spp_interconnection_queue, aggregation=count, where={"status":"active","fuel_technology":["WIND","Wind","Wind - Wind","wind - wind"]}

erw_read "$tables/spp_interconnection_queue.csv"

keep if status == "active"

keep if fuel_technology == "WIND" | fuel_technology == "Wind" | fuel_technology == "Wind - Wind" | fuel_technology == "wind - wind"

destring capacity_mw, replace force

scalar v_value = _N

scalar v_n = _N

display "ask|s267:q24|0|0: the answer states 111; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 111.0), abs(v_n - 111.0)) <= 0.500000001, "yes", "no")

* ask|s267:q24|1: spp_interconnection_queue, aggregation=sum, where={"status":"active","fuel_technology":["WIND","Wind","Wind - Wind","wind - wind"]}

erw_read "$tables/spp_interconnection_queue.csv"

keep if status == "active"

keep if fuel_technology == "WIND" | fuel_technology == "Wind" | fuel_technology == "Wind - Wind" | fuel_technology == "wind - wind"

destring capacity_mw, replace force

summarize capacity_mw

scalar v_value = r(sum)

scalar v_n = _N

display "ask|s267:q24|1|0: the answer states 23208.66; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 23208.66), abs(v_n - 23208.66)) <= 0.005000001, "yes", "no")

* ask|s302:q19|0: carbon_intensity_monthly, aggregation=mean, entity=eia930:US48, variable=intensity_generation, start=2024-01-01, end=2025-01-01

erw_read "$tables/carbon_intensity_monthly.csv"

keep if entity == "eia930:US48"

keep if variable == "intensity_generation"

keep if ts_utc >= "2024-01-01"

keep if ts_utc < "2025-01-01"

destring value, replace force

summarize value

scalar v_value = r(mean)

scalar v_n = _N

display "ask|s302:q19|0|0: the answer states 12; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 12.0), abs(v_n - 12.0)) <= 0.500000001, "yes", "no")

display "ask|s302:q19|0|1: the answer states 337.48; the query gives " v_value " over " v_n " rows; met: " cond(min(abs(abs(v_value) - 337.48), abs(v_n - 337.48)) <= 0.005000001, "yes", "no")

* ask|s302:q19|1: query with group_by month; replicate.py only

* ask|s267:q27|0: query with group_by month; replicate.py only

* 24 plain queries above; the others are replicate.py's.
