# ERCOT evaluation: before and after

44 questions (questions_ercot.yaml, today = 2026-10-04), backend local. Before: the grid page's chat as it was (ask.py --grid ercot), 28 questions asked. After: Ask ERCOT, the reference version (ercot.py), run 20261004T073235Z, all 44.

| Measure | Before | After |
|---|---|---|
| Correct, on the questions the arm was asked | 17 of 28 (61%) | 44 of 44 (100%) |
| Correct, on the 28 questions both were asked | 17 of 28 | 28 of 28 |
| Correct, lookup | 9 of 11 | 22 of 22 |
| Correct, series | 2 of 4 | 6 of 6 |
| Correct, join | 1 of 5 | 8 of 8 |
| Correct, refuse | 5 of 5 | 5 of 5 |
| Correct, context | 0 of 3 | 3 of 3 |
| followups | not offered | 44 of 44 |
| series | not offered | 6 of 6 |
| full | not offered | 44 of 44 |
| Retried after the check | 6 of 28 | 3 of 44 |
| Mean tool calls | 6.68 | 3.30 |
| Cost of the records counted | USD 2.3284 | USD 1.2219 |
| Mean cost per question | USD 0.0832 | USD 0.0278 |

The reference version's first whole run (20261004T072151Z), before the three fixes it led to: 41 of 44 correct, 21 sent back once by the check, USD 1.0653.

Not asked of the chat as it was (16; the spend cap): e05, e06, e09, e10, e11, e12, e15, e16, e17, e18, e22, e26, e27, e30, e35, e36. Each needs a table outside its scope; they are not counted.

| Id | Kind | Before | After | Question |
|---|---|---|---|---|
| e01 | lookup | correct | correct | What was the average real-time price at ERCOT's hub average in 2023 (ERCOT's local year)? |
| e02 | lookup | wrong (not_in_warehouse) | correct | What was the average day-ahead price at HB_NORTH in July 2022? |
| e03 | lookup | correct | correct | What was the highest real-time price at the ERCOT hub average in 2021, and in which month did it happen? |
| e04 | lookup | correct | correct | How many fifteen-minute real-time intervals were priced below zero at HB_WEST in 2024? |
| e05 | lookup | not asked | correct | What was the average day-ahead price of regulation up (REGUP) in ERCOT in 2022? |
| e06 | lookup | not asked | correct | What did ECRS clear at on average in August 2023? |
| e07 | lookup | correct | correct | How many MW of batteries are operating in ERCOT in the newest inventory held? |
| e08 | lookup | correct | correct | What is the average duration, in hours, of ERCOT's operating batteries? |
| e09 | lookup | not asked | correct | Which company reports the most operating battery capacity in ERCOT, and how many MW? |
| e10 | lookup | not asked | correct | What share of ERCOT's operating battery capacity do the ten largest reporting companies hold? |
| e11 | lookup | not asked | correct | In August 2026, how many hours would ERCOT's batteries have needed to cover the evening shoulder on the average day? |
| e12 | lookup | not asked | correct | On the ten worst evenings of 2026, how many hours of storage did ERCOT's shoulder ask for on average? |
| e13 | lookup | wrong (not_in_warehouse) | correct | With perfect foresight, what could a four-hour battery have earned per MW in ERCOT in February 2021? |
| e14 | lookup | correct | correct | During Winter Storm Uri, what was the highest real-time price at the ERCOT hub average? |
| e15 | lookup | not asked | correct | On which day of Winter Storm Uri was ERCOT's demand lowest, and how many MWh was it? |
| e16 | lookup | not asked | correct | How many interconnection requests in ERCOT has Berkeley Lab recorded as withdrawn? |
| e17 | lookup | not asked | correct | How many MW of stand-alone battery requests are active in ERCOT's queue, by Berkeley Lab's count? |
| e18 | lookup | not asked | correct | What did ERCOT's load pay on average at the hub in real time in August 2026, weighted by demand? |
| e19 | lookup | correct | correct | What was the carbon intensity of ERCOT's generation in November 2025? |
| e20 | lookup | correct | correct | What was ERCOT's highest hourly demand in September 2026? |
| e21 | lookup | correct | correct | What is the highest hourly discharge of ERCOT's battery fleet on record in the warehouse? |
| e22 | lookup | not asked | correct | How many contract rows filed with FERC name ERCOT as the delivery balancing authority? |
| e23 | series | wrong (not_in_warehouse) | correct | How did the monthly average real-time price at the ERCOT hub average move through 2022, and which month was highest? |
| e24 | series | correct | correct | How has ERCOT's operating battery fleet grown year by year since 2020? Give the MW at the end of 2020 and of 2025. |
| e25 | series | wrong (not_in_warehouse) | correct | Year by year since 2018, what could a four-hour battery have earned per MW in ERCOT with perfect foresight? Which year was highest? |
| e26 | series | not asked | correct | How has the average price of regulation up changed by year since 2018? Give 2021 and 2024. |
| e27 | series | not asked | correct | Month by month in 2025, how many hours would ERCOT's batteries have needed to cover the evening shoulder? Which month asked the most? |
| e28 | series | correct | correct | How has the carbon intensity of ERCOT's generation changed by year? Give the average of the months held of 2019 and of 2025. |
| e29 | join | wrong (not_in_warehouse) | correct | In the month of 2023 when ERCOT's load paid the most at the hub in real time (load-weighted), what could a four-hour battery have earned per MW with perfect foresight? |
| e30 | join | not asked | correct | In August 2026, how did the hours of storage the evening shoulder asked for compare with the average duration of ERCOT's batteries in the inventory? |
| e31 | join | wrong (not_in_warehouse) | correct | In February 2021, what was the average real-time hub price, and what was the average price of regulation up? |
| e32 | join | correct | correct | How does ERCOT's operating battery capacity compare with its highest hourly demand in September 2026? |
| e33 | join | wrong (answered) | correct | How many MW of batteries operate in ERCOT today, and how many MW of stand-alone battery requests are active in Berkeley Lab's queue data? |
| e34 | join | wrong (not_in_warehouse) | correct | Since January 2022, in which month did ERCOT's load pay the most at the hub in real time (load-weighted), and what was the carbon intensity of generation that month? |
| e35 | join | not asked | correct | In July 2025, what price did solar capture at the hub, and what did load pay on average in real time, weighted by demand? |
| e36 | join | not asked | correct | For Winter Storm Uri's month, February 2021: what was the highest real-time hub price, and what could a four-hour battery have earned per MW on day-ahead prices alone? |
| e37 | refuse | correct | correct | What was the average day-ahead price at PJM's Western Hub last week? |
| e38 | refuse | correct | correct | How many MWh did ERCOT generate from natural gas in each hour of 14 July 2022? |
| e39 | refuse | correct | correct | What was the average real-time price in the Houston load zone, LZ_HOUSTON, in 2023? |
| e40 | refuse | correct | correct | How much revenue did the Gambit battery near Angleton actually earn in 2023? |
| e41 | refuse | correct | correct | What will the average real-time hub price be in 2027? |
| e42 | context | wrong (not_in_warehouse) | correct | What could this battery have earned per MW in July 2025? |
| e43 | context | wrong (not_in_warehouse) | correct | How many hours of storage did the shoulder ask for in this month, and how many did the batteries hold? |
| e44 | context | wrong (answered) | correct | How much was added over the last twelve months? |
