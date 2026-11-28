* Energy Research Warehouse (ERW): /impact's datacenter, the tax arithmetic in Stata (chain 740, session 10804).
* docs/methods/forecast.md, section 13. Three announced projects, each at its own document's figures:
*   Louisiana, Meta in Richland Parish (LED, 13 July 2026): 5,000 MW, USD 50 billion, 1,000 operational jobs, 7,500 at peak;
*     built 2026 to 2030, 20 operating years, the reader's property rates 10 percent of assessed value.
*   Virginia, CleanArc in Caroline County (VEDP, November 2025): 1,000 MW, USD 3 billion, 50 jobs; built 2026 to 2027,
*     20 operating years, 5,000,000 MWh a year bought.
*   West Virginia, Penzance in Berkeley County (the governor, 26 February 2026): 600 MW, USD 4 billion, 125 permanent;
*     built 2026 to 2027, 20 operating years.
* Expected (site/scripts/test-datacenter.test.mjs works each by hand from the statutes):
*   LA sales tax before the exemption 13,817,320,000; forgone 10,362,990,000; paid 3,454,330,000; property 12,190,000,000
*   VA before 472,216,800; forgone 236,108,400; paid 236,108,400; electricity tax 4,375,141.30 a year
*   WV before 720,192,000; forgone 0; operating income tax 216,081.825 a year
* Not run on the machine that wrote it: Stata is not installed there. replicate.py recomputes every figure of these
* cases and the others of page_figures.json against the page (39 cases, 8,700 figures on 26 November 2026, session 10815).

clear all
set more off

program define dc_sales
    * args: invest (USD), equipment share, rate, build, life, start, refresh, exempt (1/0), last exempt year (or 9999), term years (or 999)
    args invest eqshare rate build life start refresh exempt lastyear term
    clear
    quietly set obs `= `build' + `life''
    gen i = _n - 1
    gen year = `start' + i
    gen build = i < `build'
    gen op = i - `build'
    gen equipment = cond(build, `invest' * `eqshare' / `build', cond(`refresh' > 0 & op > 0 & mod(op, `refresh') == 0, `invest' * `eqshare', 0))
    gen before = equipment * `rate'
    gen runs = year <= `lastyear' & year < `start' + `term'
    gen forgone = `exempt' * runs * before
    gen paid = before - forgone
    quietly summarize before
    scalar s_before = r(sum)
    quietly summarize forgone
    scalar s_forgone = r(sum)
    quietly summarize paid
    scalar s_paid = r(sum)
end

* ---- Louisiana: R.S. 47:305.73, 20 years from 2026, equipment and construction (no building share given) ----
dc_sales 50000000000 0.682 0.1013 5 20 2026 5 1 9999 20
display "LA before " %18.2f s_before "  forgone " %18.2f s_forgone "  paid " %18.2f s_paid
* Constitution art. VII, s. 18: building at 10 percent, equipment at 15 percent of cost, the reader's 10 percent rate
scalar la_prop = 20 * (50000000000 * 0.196 * 0.10 * 0.10 + 50000000000 * 0.682 * 0.15 * 0.10)
display "LA property over 20 years " %18.2f la_prop

* ---- Virginia: 58.1-609.3(18), purchases through 2034 ----
dc_sales 3000000000 0.682 0.0577 2 20 2026 5 1 2034 999
display "VA before " %18.2f s_before "  forgone " %18.2f s_forgone "  paid " %18.2f s_paid
* 58.1-2900: a twelfth of 5,000,000 MWh each month, by blocks
scalar kwh = 5000000 * 1000 / 12
scalar va_elec = 12 * (2500 * 0.001595 + 47500 * 0.001085 + (kwh - 50000) * 0.000875)
display "VA electricity tax a year " %18.2f va_elec

* ---- West Virginia: no datacenter statute held, before exemptions ----
dc_sales 4000000000 0.682 0.066 2 20 2026 5 0 9999 999
display "WV before " %18.2f s_before "  forgone " %18.2f s_forgone "  paid " %18.2f s_paid
* income tax: CBP 2023 518210 payroll per job 53,902.39 in 2025 dollars, 56,743; exemption 2,000; 2026 brackets
scalar w = 56743 - 2000
scalar t = min(w, 10000) * 0.0211 + max(0, min(w, 25000) - 10000) * 0.0281 + max(0, min(w, 40000) - 25000) * 0.0316 + max(0, min(w, 60000) - 40000) * 0.0422 + max(0, w - 60000) * 0.0458
display "WV operating income tax a year " %18.3f 125 * t

* ---- Georgia: 48-8-3(68.1) as HB 1291 of 2022 amended it, purchases through 2033 as the state auditor writes (session 10813; the ready branch of session 11408) ----
* USD 2 billion and 100 jobs from 2027: expected before 412,473,600, forgone 103,118,400 (the build only), paid 309,355,200
dc_sales 2000000000 0.682 0.0756 2 20 2027 5 1 2033 999
display "GA before " %18.2f s_before "  forgone " %18.2f s_forgone "  paid " %18.2f s_paid

* ---- Arkansas: 26-52-456 as Act 548 of 2025 amended it, the state's 6.5 percent only, no term (session 10813) ----
* USD 2 billion from 2027: the equipment's forgone at the state's rate, expected 354,640,000 (four purchases of 1.364e9);
* with 40 percent of the 392,000,000 building taxable, 10,192,000 more: 364,832,000, as the page and the downloaded Python give.
dc_sales 2000000000 0.682 0.065 2 20 2027 5 1 9999 999
display "AR equipment forgone at the state rate " %18.2f s_forgone
display "AR with the building's taxable 40 percent " %18.2f s_forgone + 392000000 * 0.40 * 0.065
