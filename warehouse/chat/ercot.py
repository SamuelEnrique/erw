#!/usr/bin/env python3
"""Ask ERCOT, the reference version (session 92): the question-answering loop developed fully for one grid.

Energy Research Warehouse (ERW). warehouse/chat/ask.py is the loop and its number check; this file is a profile of
it for ERCOT. What the profile adds, and what the next grid copies (the steps are at the end of session 92's report):

1. A scope: the ERCOT tables, and for each the rows that are ERCOT's (SCOPE). The tools read nothing else.
2. A table guide in the system prompt (CARDS): every table with its entities, variables, units and traps, so the
   model goes straight to a query and does not spend its eight tool calls finding names.
3. Series: every query result carries a result id. An answer that rests on a series names the results it rests on;
   the record then holds those rows as fetched, each with its table and source (record["series"]), for a chart and
   a table. The rows are the tool's, never the model's text.
4. Follow-ups: two or three questions the reader could ask next (record["followups"]), checked like the answer:
   no number the tools did not return.
5. Context: a page of the site may open the chat with its view and settings; they are the defaults of the question.

Everything else is ask.py's: at most 8 tool calls, the check that every number in the answer is in a tool result,
one retry, then refusal; "not in the warehouse" when the tables do not hold the answer.

    python warehouse/chat/ercot.py "What did a 4-hour battery earn in ERCOT in August 2026?"
    python warehouse/chat/ercot.py --json --context '{"view": "/cost-of-power/battery", "settings": {"dur": "4"}}' "..."
    python warehouse/chat/ercot.py --guide                                   # the table guide, as the model reads it
    python warehouse/chat/ercot.py --export-spec site/lib/chat/spec_ercot.json
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import math  # noqa: E402
import re  # noqa: E402

import ask  # noqa: E402
import tools  # noqa: E402

EFFORT = "medium"
MAX_SERIES = 2          # results an answer may rest on
MAX_GROUPS = 120        # rows of one grouped result (a month per row since 2018 is 106)
MIN_ROWS = 3            # a grouped result of fewer rows is not a series
YEARS = range(2010, 2036)  # a follow-up may name a year without having fetched it

# Each table and how the model should read it. One line of facts from coverage is added when the guide is built.
CARDS = [
    ("ercot_hub_prices_daily", "Hub prices by day, the whole history: every operating day since 2015-01-01, derived by the ERW from the interval prices. Held whole, on the site too. Read this table first for any hub price of a day, a month or a year that is older than the newest weeks. Entities: ercot:HB_HUBAVG (the hub average; use it for \"the ERCOT price\" unless a hub is named), ercot:HB_BUSAVG, ercot:HB_NORTH, ercot:HB_SOUTH, ercot:HB_WEST, ercot:HB_HOUSTON. One row per hub, day and variable; the variable is <market>_<statistic>, market da (day-ahead, hourly prices) or rt (real-time, fifteen-minute prices): da_mean and rt_mean (the mean of the day's intervals), da_peak_mean and rt_peak_mean, da_offpeak_mean and rt_offpeak_mean (peak is the weekday block of sixteen hours, holidays off-peak; a weekend day or a holiday has no peak row), da_min and rt_min, da_max and rt_max (the day's lowest and highest interval price), all USD/MWh; da_hours_below_zero and rt_hours_below_zero (hours priced below zero), da_hours_above_200 and rt_hours_above_200 (hours priced above that many USD/MWh), unit count, where a fifteen-minute interval counts a quarter of an hour. How to ask it: the average price of a month or a year is aggregation mean of da_mean or rt_mean (say it is the mean of the daily means); the highest price of a period is aggregation max of rt_max or da_max (at is the day it happened); the lowest is min of rt_min or da_min; the hours below zero or above the threshold in a period are aggregation sum of that variable; for a trend use group_by month or year. It is dated by ERCOT's local day: give plain dates and no tz. It cannot give a count of intervals, a percentile or a median of interval prices, or the price of one hour: those need the interval tables below."),
    ("ercot_all_hub_prices_history", "Hub prices, the history interval by interval. NOT in the site's database: there a query answers that the table is not in the live set, and ercot_hub_prices_daily is the table to read. Come here only for what the daily table cannot give. Entities: ercot:HB_HUBAVG (the hub average; use it for \"the ERCOT price\" unless a hub is named), ercot:HB_BUSAVG, ercot:HB_NORTH, ercot:HB_SOUTH, ercot:HB_WEST, ercot:HB_HOUSTON. Variables: spp_dam (day-ahead settlement point price, hourly) and spp_rtm (real-time, 15-minute), USD/MWh. From 2015-01-01 to 2026-08-26. A question about a period after that needs iso_dam_hub_prices or iso_rtm_hub_prices as well. Always filter by entity and variable: the table mixes six hubs and two markets."),
    ("iso_dam_hub_prices", "Hub prices, day-ahead, hour by hour, the newest weeks only (a rolling window of about 40 days; 35 on the site). For a single hour; a day's or a month's price is in ercot_hub_prices_daily. Same ERCOT entities; variable spp_dam, hourly, USD/MWh."),
    ("iso_rtm_hub_prices", "Hub prices, real-time, interval by interval, the newest weeks only (about 40 days; 35 on the site). Same ERCOT entities; variable spp_rtm, 15-minute, USD/MWh."),
    ("ercot_as_prices", "Reserve (ancillary service) prices, the whole history, held whole on the site too: the day-ahead market clearing price for capacity, variable mcpc_dam, USD per MW per hour, hourly. Entities: ercot:REGUP (regulation up), ercot:REGDN (regulation down), ercot:RRS (responsive reserve), ercot:NSPIN (non-spinning reserve), all from 2018-01-01, and ercot:ECRS (contingency reserve service), which began on 2023-06-10."),
    ("ercot_as_quantities", "Reserve quantities: the MW of each reserve product ERCOT plans to procure each hour, variable quantity_mw_plan, entities as ercot_as_prices. The newest month only."),
    ("eia930_all_demand", "Hourly demand, the newest weeks only (about 35 days). Entity eia930:ERCO; variables demand_mw and demand_forecast_mw. For monthly demand since 2019 use ba_supply_monthly."),
    ("eia930_all_generation", "Hourly generation by fuel, the newest weeks only (about 35 days). Entity eia930:ERCO; variables net_generation_<fuel>_mw with fuel one of coal, natural_gas, nuclear, hydro, solar, wind, battery, other, and net_generation_mw (all fuels), MW. Hourly generation by fuel before that window is not held."),
    ("ba_supply_monthly", "Monthly demand and net imports since 2019-01. Entity eia930:ERCO. For a month's or a year's demand use demand_all_days_mwh (the month's demand over every day EIA reported). demand_mwh is the same over the days the supply figures hold only (days_held of days_in_month; days_left_out says how many are not in it): a year's sum of it leaves days out, so never read it as the year's demand and never compare two years by it. ERCOT's total net imports come by three measures, each in MWh and as a share of demand in percent (0.2 is two tenths of one percent): net_import_pairs_mwh and net_import_pairs_share_pct (the sum of its ties; the one to give unless another is asked for), net_import_total_interchange_mwh and net_import_total_interchange_share_pct (EIA's own total interchange), net_import_balance_mwh and net_import_balance_share_pct (generation less demand). The two ties themselves are the entities eia930:ERCO-SWPP and eia930:ERCO-CEN, with net_import_mwh and net_import_share_pct. It holds no generation by fuel."),
    ("eia930_all_storage", "Battery output, hourly, since 2024-11-07. Entity eia930:ERCO; variable net_generation_battery_mw, MW: positive when the fleet discharges, negative when it charges."),
    ("storage_daily_cycle", "The battery fleet's day, daily since 2024-11-07. Entity eia930:ERCO; variables mwh_discharged, mwh_charged, peak_discharge_hour, peak_charge_hour (local hour), round_trip_ratio."),
    ("battery_stack_monthly", "What a battery could have earned (a model, an upper bound; not what real batteries earned), monthly since 2018-01, USD per MW of battery per month. Entity ercot:HB_HUBAVG. Variable is <strategy>_<N>h_<metric>: strategy foresight (perfect foresight) or dayahead (day-ahead prices only); N is 2, 4 or 8 hours; metric revenue_total_usd_per_mw, revenue_energy_usd_per_mw, revenue_ancillary_usd_per_mw, revenue_regup_usd_per_mw, revenue_regdn_usd_per_mw, revenue_rrs_usd_per_mw, revenue_ecrs_usd_per_mw, revenue_nspin_usd_per_mw, discharged_mwh_per_mw, days_held, days_in_month, days_left_out. Example: foresight_4h_revenue_total_usd_per_mw. Values are per MW: for per kW say so only if a tool returned it. A year is the sum of its months."),
    ("battery_stack_stress_daily", "The same model by day in three events (column event: uri_2021, elliott_2022, ercot_heat_2023). Variables <strategy>_<N>h_revenue_total_usd_per_mw, _energy_, _ancillary_. Filter with where {\"event\": ...}."),
    ("storage_buildout_monthly", "The battery fleet from EIA's monthly generator inventory, monthly from 2015-01 to the newest inventory. Entity iso:ercot. Variables: battery_operating_mw, battery_operating_mwh, battery_operating_mwh_per_mw (average duration, hours), battery_operating_units, the duration buckets battery_operating_mw_lt2h, _2to4h, _4to6h, _ge6h and battery_operating_mw_energy_not_reported (and the same in mwh), battery_operating_mw_net_added_12m, battery_planned_mw, battery_planned_mw_under_construction, battery_planned_mw_online_<year>, solar_operating_mw, battery_mwh_per_solar_mw."),
    ("storage_owners_monthly", "Who owns the batteries, one month (the newest inventory). An owner is the company that reports the plant to EIA, often a project company; no parents. Entity iso:ercot holds the grid's totals: ercot_operating_mw, ercot_operating_mwh, ercot_owners_operating, ercot_owners_planned, ercot_top5_share_pct, ercot_top10_share_pct, ercot_planned_mw. Each company is an entity eia860:utility:<id> with its name in column x_owner and variables ercot_operating_mw, ercot_operating_mwh, ercot_operating_hours, ercot_operating_units, ercot_operating_rank (1 is the largest), ercot_operating_share_pct, ercot_planned_mw, ercot_planned_units. To find the largest: query variable ercot_operating_rank with aggregation min (it returns the entity), then query that entity. To list companies: group_by x_owner with one variable."),
    ("storage_capacity", "The battery units themselves, from EIA's monthly generator inventory, one row per unit in ERCOT. Columns: status (operating, planned, ...), capacity_mw, energy_capacity_mwh, county, operating_year, planned_year, operator. An entities table: use where and group_by on its columns; count or sum capacity_mw."),
    ("shoulder_hours_monthly", "The evening shoulder (the stretch between solar's fall and the evening's end; the ERW's own term) since 2019-01. Entity iso:ercot. The table mixes monthly, yearly and daily rows, so always filter by variable. Monthly: shoulder_hours, shoulder_start_hour, shoulder_end_hour, shoulder_mwh_above_mean, fleet_mw, fleet_mwh, fleet_hours (what the batteries hold), shoulder_hours_covered, shoulder_hours_needed, midday_surplus_mwh, midday_surplus_hours, evening_peak_mw, evening_peak_hour, and the same with shoulder2_ for the second measure; the newest month may lack the fleet figures. The average day by local hour: avg_demand_mw_hHH, avg_solar_mw_hHH, avg_wind_mw_hHH, avg_net_load_mw_hHH, avg_battery_mw_hHH (HH 00 to 23). Yearly rows are dated 1 January: year_mean_shoulder_hours_needed, year_mean_shoulder_hours, year_end_fleet_mw, year_end_fleet_hours, year_worst10_mean_shoulder_hours_needed, year_worst10_max_shoulder_hours_needed. Daily rows (the ten worst days of each year): worst_rank, day_shoulder_hours_needed, day_shoulder_mwh_above_mean, day_battery_hours."),
    ("event_window_daily", "Events, day by day. Column event: uri_2021 (Winter Storm Uri, 2021-02-07 to 2021-02-24), elliott_2022 (2022-12-19 to 2022-12-29), ercot_heat_2023 (2023-08-01 to 2023-09-10), covid_2020, cold_2025. Each event's rows also hold the same calendar days of the two years before as a baseline, so give start and end for the event's own days. Entity eia930:ERCO: demand_mwh, demand_max_mw, demand_min_mw, demand_pct_vs_baseline, demand_mwh_vs_baseline, net_generation_mwh, intensity_generation. Entity ercot:HB_HUBAVG: da_mean, da_max, rt_mean, rt_max (USD/MWh; rt_max is the day's highest 15-minute price). Filter with where {\"event\": ...}."),
    ("event_study_estimates", "The event studies' estimates: how far demand and price were from what the same days of other years predict. Column event as event_window_daily. Variables: demand_mwh_effect_pooled and rt_mean_effect_pooled (the event's average daily effect), the same ending _temp (controlling for temperature), demand_mwh_effect_day and rt_mean_effect_day (one row per event day), demand_mwh_counterfactual_mean, rt_mean_counterfactual_mean. Columns x_ci_low and x_ci_high give the interval, x_n the days used. Entity eia930:ERCO for demand, ercot:HB_HUBAVG for price."),
    ("lbnl_interconnection_queue", "The interconnection queue as Berkeley Lab compiles it (Queued Up, 2026 edition, requests through 2025): one row per request in ERCOT, including those withdrawn and those now operating. Columns: q_status (active, withdrawn, operational, suspended), type_clean (Solar, Battery, Wind, Solar+Battery, Gas, ...), capacity_mw, q_year (the year the request entered, written like 2021.0), on_date, wd_date, county, state. An entities table: count, or sum capacity_mw, with where and group_by."),
    ("ercot_interconnection_queue", "ERCOT's own queue report (a snapshot): projects active or completed. Columns: status (active, completed), fuel_technology, capacity_mw, county, zone, queue_date, proposed_in_service_date. It lists no withdrawn request; for withdrawals use lbnl_interconnection_queue."),
    ("cost_of_power_monthly", "What a MWh cost to buy at the hub, monthly since 2018-07. Entity ercot:HB_HUBAVG. Variables: rt_load_weighted and da_load_weighted (weighted by ERCOT's hourly demand), rt_simple_mean, da_simple_mean, rt_shape_premium, da_shape_premium, USD/MWh; rt_hours, da_hours, hours_in_month (a month is whole when rt_hours equals hours_in_month)."),
    ("merchant_revenue_monthly", "What a merchant plant earned selling at the hub's real-time price, monthly since 2018-06. Entity ercot:HB_HUBAVG. Variables <asset>_capture_price (USD/MWh), <asset>_capture_rate (the capture price as a percent of the flat price: 88 is 88 percent, below the flat price), <asset>_revenue_per_mw (USD per MW per month), <asset>_energy_per_mw, with asset solar, wind, battery_2h, battery_4h, peaker; and flat_price."),
    ("carbon_intensity_monthly", "Carbon intensity of ERCOT's generation and demand, monthly since 2018-08. Entity eia930:ERCO; variables intensity_generation and intensity_demand, kgCO2/MWh."),
    ("ercot_peak_premium_annual", "The spread of real-time prices by year and hub since 2015 (entities as the hub prices). Variables: peak_median, midday_median, overnight_median, peak_minus_midday_median, all_median, all_max, all_min, all_p999, peak_iqr, n_negative (intervals below zero), n_scarcity, n_intervals. Peak is 16:00 to 21:00 local."),
    ("ercot_peak_premium_monthly", "The same by month."),
    ("ferc_eqr_contracts", "INTERNAL (licensed for internal use only; say so). Contracts filed with FERC that name ERCOT as the delivery balancing authority: a few hundred rows, almost all one utility's transmission and interconnection agreements, because sales inside ERCOT are outside FERC's jurisdiction. An events table; event_date is the contract's execution date. Columns: x_seller_company_name, x_customer_company_name, x_product_name, x_rate, x_rate_description, x_quarter. Count with where and group_by."),
]

TABLES = [t for t, _ in CARDS]
# what each table holds, in the words of its card's first sentence: shown beside a table a refusal names
HOLDS = {t: (text.split(". ")[0].split(": ")[0].rstrip(".") + ".") for t, text in CARDS}
HOLDS.update({  # where a card's first sentence does not stand on its own
    "ercot_as_quantities": "Reserve quantities: the MW of each reserve product ERCOT plans to procure each hour, the newest month.",
    "battery_stack_stress_daily": "The battery model by day in three events: Winter Storm Uri, Winter Storm Elliott and the 2023 heat wave.",
    "event_window_daily": "Named events day by day (Winter Storm Uri, Elliott, the 2023 heat wave and others): demand, prices and weather.",
    "event_study_estimates": "The event studies' estimates: how far demand and price were from what the same days of other years predict.",
    "ercot_peak_premium_monthly": "The spread of real-time prices by month and hub since 2015.",
    "ferc_eqr_contracts": "Contracts filed with FERC that name ERCOT as the delivery area (internal: licensed for internal use only).",
})

SCOPE = dict(tools.GRIDS["ercot"])
SCOPE.update({
    "tables": [t for t, _ in CARDS],
    # the rows of each table that are ERCOT's, where the table does not say so by a ba or a market column
    "filters": {
        "ercot_hub_prices_daily": {}, "ercot_all_hub_prices_history": {}, "ercot_as_prices": {}, "ercot_as_quantities": {}, "ercot_interconnection_queue": {},
        "ercot_peak_premium_annual": {}, "ercot_peak_premium_monthly": {},
        "battery_stack_monthly": {"market": "ercot"}, "battery_stack_stress_daily": {"market": "ercot"},
        "storage_buildout_monthly": {"entity": "iso:ercot"}, "storage_owners_monthly": {"x_grid": "ercot"},
        "shoulder_hours_monthly": {"entity": "iso:ercot"},
        "event_window_daily": {"entity": ["eia930:ERCO", "ercot:HB_HUBAVG"]}, "event_study_estimates": {"entity": ["eia930:ERCO", "ercot:HB_HUBAVG"]},
        "lbnl_interconnection_queue": {"region": "ERCOT"},
        "ferc_eqr_contracts": {"x_point_of_delivery_balancing_authority": "ERCO"},
        "cost_of_power_monthly": {"entity": "ercot:HB_HUBAVG"}, "merchant_revenue_monthly": {"entity": "ercot:HB_HUBAVG"},
        "ba_supply_monthly": {"entity": ["eia930:ERCO", "eia930:ERCO-SWPP", "eia930:ERCO-CEN", "eia930:SWPP-ERCO"]},
    },
    "slim": ["ercot_all_hub_prices_history", "ercot_as_prices"],
    "max_groups": MAX_GROUPS,
    "dated_groups": True,  # daily, monthly and yearly rows are grouped by their own label, whatever tz is passed
})

RULES = """You are Ask ERCOT. You answer questions about the Texas grid (ERCOT) from the Energy Research Warehouse (ERW), using only its tools: query and compare for numbers, describe_table for a table's exact names, list_tables, and grid_notes (grid "ercot") for the written page about ERCOT.

Rules:
1. Answer only from tool results. Every number you write (prices, counts, capacities, percentiles, differences, dates and years) must appear in a tool result, written at the same or a coarser precision (a result of 25.1834 may be written 25.18 or 25.2). Do not compute any number yourself: no sums, averages, differences, ratios, percentages or unit conversions. If you need a difference or ratio, call compare; if you need a sum or an average, call query with that aggregation.
2. Cite every number. In the answer text, give the table each number came from, for example "25.18 USD/MWh (ercot_all_hub_prices_history)". In citations, list every table you used, with its source_report and data_version copied exactly from the tool result.
3. If the ERCOT tables do not hold what the question asks (a node, period, variable or kind of data they do not have), answer "not in the warehouse", say in one sentence what is missing and what the nearest thing held is, set not_in_warehouse to true, and state no numbers. List in nearest the one to three tables of the guide that come closest to what was asked, by their exact names, nearest first: the reader is shown what each of them holds. The guide is enough to know that a thing is not held: when the question is plainly about something else (another grid, a forecast, a retail bill, a company's accounts, the weather), refuse at once, without a tool call. Never use outside knowledge, never estimate. This chat speaks for ERCOT only: for another grid, say so and that the general chat at /ask covers the whole warehouse.
4. If you use a table whose license is internal, say in the answer that it is internal (licensed for internal use only).
5. Times: series times are interval starts in UTC. ERCOT's operating day is local, America/Chicago: for a day, a month or a year of ERCOT prices or demand, pass tz "America/Chicago" with local start and end dates, and say so. A table of daily, monthly or yearly rows is dated by its local period: give plain dates and no tz.
6. You have at most 8 tool calls. When you need several queries, ask for them together in one turn (several tool calls at once): every turn costs the reader seconds. The table guide below names every ERCOT table with its entities and variables: go straight to query or compare. Call describe_table only for a name the guide does not give.
7. Keep the answer short: the number or numbers with units, the time or period, and the table. Say what the number is (for example "mean of the fifteen-minute intervals"). A model's result (battery_stack_monthly) is what a battery could have earned, never what batteries earned. The check on your answer is literal: every run of digits in it must be in a tool result, the question, the context or a name you queried by. So write a duration or an interval in words unless a tool returned it (fifteen-minute, hourly, a four-hour battery), give a date only as a tool returned it, do not state a count you inferred (the days of a month, the months of a year, the hours missing), and name a source in words (EIA's monthly generator inventory), not by its form number.
8. Provenance tier: every tool result gives the table's tier: source (as the publisher published it), derived (computed by the ERW from other tables) or model_extracted. Say "derived by the ERW" next to a number from a derived table when it matters to how the number should be read.
9. Series. When the answer rests on values over time or one value per group (a trend, a comparison across months, years, hubs, products or companies), fetch them with one query that uses group_by, and list that result's result_id in series (every query result has one; in compare they are in a and b). The reader is then shown a chart and a table of exactly those rows with their source, so the answer text gives the headline numbers and does not repeat every row. At most two results. An answer of one or two numbers has no series: leave series empty.
10. Follow-ups. Give two or three short questions the reader could ask next. Each must be answerable from the ERCOT tables in the guide, and must contain no digit other than a year: write a duration or a count in words (a four-hour battery, the ten worst days).
11. Context. The first message may say which page of the site the reader opened this chat from, and its settings (for example a battery's duration and strategy, a month, a hub). Use them as the defaults for whatever the question does not name itself, and say which settings you used.
12. Past prices. For a hub price of a day, a month or a year, query ercot_hub_prices_daily: it holds every day since 2015 and is held whole, like ercot_as_prices (reserve prices since 2018), whatever a general note of a tool says about the newest 35 days. Name it in the answer as the table you read, and say what the number is (the mean of the daily means, the highest interval price of the period, a sum of hours). Never answer "not in the warehouse" to a question about a past hub price or reserve price before you have queried these two tables. If the question needs single intervals (a count of intervals, a percentile, one hour of a past day) and the interval table cannot be read, give what the daily table holds that is nearest and say what it cannot give.

13. Conversation. The first message may carry the conversation so far: the reader's earlier questions, your answers, and the queries you ran for them. Read the new question as its continuation: "and in 2022?" asks the same thing of 2022, "what about day-ahead?" asks it of the day-ahead price, "how many of those" narrows the same rows. Reuse the table, entity, variable and aggregation of the earlier query and change only what the new question changes. Every number of the new answer is fetched with a tool in this turn; a number of an earlier answer may be repeated only as it was written there.
14. A premise. A question may take for granted something the tables contradict: a level (prices averaged over 200), a direction (the fleet shrank, demand fell), a ranking (the dearest hub, the dearest reserve), a date (a product that began later), an "always" or a "never". Check it with a query before you build on it. When the tables contradict it, do not go along with it: say first what the tables show, with the numbers, then answer what can still be answered, and put in premise one sentence saying what the question assumed and what the tables show instead. When the question assumes nothing the tables contradict, premise is an empty string.
15. A loose question. A short or everyday question (is power expensive right now, do batteries make money, how much battery does Texas have) is still answered: take the most natural reading the tables can bear (the hub average for "the price"; the newest whole month, or the newest value, for "now"; the newest inventory for "how much"), say in the first sentence which reading you took, and answer it with its numbers. Never answer with a question, and do not refuse a question that one of the tables can answer in some plain reading.

Your final message is JSON with: answer (plain text), citations (one per table used: table, source_report, data_version, tier), not_in_warehouse (true or false), series (result ids, possibly empty), followups (two or three questions), nearest (table names of the guide; empty unless not_in_warehouse is true), premise (one sentence, or an empty string)."""

SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "citations": ask.ANSWER_SCHEMA["properties"]["citations"],
        "not_in_warehouse": {"type": "boolean"},
        "series": {"type": "array", "items": {"type": "string"}},
        "followups": {"type": "array", "items": {"type": "string"}},
        "nearest": {"type": "array", "items": {"type": "string"}},
        "premise": {"type": "string"},
    },
    "required": ["answer", "citations", "not_in_warehouse", "series", "followups", "nearest", "premise"],
    "additionalProperties": False,
}

CONTEXT_LINE = "The reader opened this chat from the site's page {view}{title}{settings}."
# Session 121: the conversation so far, in the first message. At most MAX_HISTORY earlier turns, the newest; an answer
# is cut at MAX_HISTORY_ANSWER characters. The site sends the same three things of each turn and formats them the same.
MAX_HISTORY, MAX_HISTORY_ANSWER, MAX_NEAREST = 3, 1500, 3
HISTORY_HEAD = "The conversation so far, oldest first. The new question continues it."
HISTORY_TURN = "Earlier question {n}: {question}\nYour answer: {answer}\nQueries you ran: {queries}"


def guide(coverage=None):
    """The table guide: each card with one line of facts from coverage (license, tier, rows, first and last time)."""
    cov = tools._coverage() if coverage is None else coverage
    by = {r.table: r for r in cov.itertuples()}
    out = ["# The ERCOT tables", "",
           "Every table this chat can read, with only ERCOT's rows. first and last are the whole table's, in UTC."]
    for table, text in CARDS:
        r = by.get(table)
        fact = "not on this backend" if r is None else (
            f"{r.license}, tier {getattr(r, 'tier', '') or 'source'}, {r.interval or 'no interval'}, "
            f"{tools._ts(r.ts_min) or 'no first time'} to {tools._ts(r.ts_max) or 'no last time'}")
        out += ["", f"## {table} ({fact})", text]
    return "\n".join(out)


def result_ids(out):
    """The query results inside one tool result: [(result_id, the query's own output)]."""
    if not isinstance(out, dict):
        return []
    found = [(out["result_id"], out)] if out.get("result_id") else []
    for sub in ("a", "b"):
        if isinstance(out.get(sub), dict) and out[sub].get("result_id"):
            found.append((out[sub]["result_id"], out[sub]))
    return found


def chartable(args, out):
    """A grouped result of enough rows to be a series."""
    return bool(args.get("group_by")) and isinstance(out.get("result"), list) and len(out["result"]) >= MIN_ROWS


def series_of(rid, args, out):
    """One series for the page: the rows exactly as the tool returned them, with what they are and where from."""
    g = args.get("group_by")
    rows = []
    for r in out["result"]:
        v = r.get("value", r.get("count"))
        rows.append({"key": str(r.get(g)), "value": v, **({"n": r["n"]} if "n" in r else {}), **({"at": r["at"]} if r.get("at") else {})})
    what = "count of rows" if args.get("aggregation") == "count" else f"{args.get('aggregation')} of {args.get('variable') or out.get('value_column') or 'value'}"
    where = "; ".join(f"{k} {v}" for k, v in (args.get("where") or {}).items())
    title = what + (f", {args['entity']}" if args.get("entity") else "") + (f" ({where})" if where else "") + f", by {g}"
    return {"result_id": rid, "table": out.get("table"), "title": title, "group_by": g, "kind": "line" if g in tools.TIME_GROUPS else "bar",
            "unit": (out.get("units") or [None])[0] if len(out.get("units") or []) == 1 else None,
            "aggregation": args.get("aggregation"), "rows_matched": out.get("rows_matched"),
            "rows": rows, "note": out.get("result_note"), "source_report": out.get("source_report"), "license": out.get("license"),
            "tier": out.get("tier"), "data_version": out.get("data_version")}


class ErcotAsker(ask.Asker):
    schema = SCHEMA
    effort = EFFORT
    retry = ask.RETRY.replace("Answer again in the same JSON format.",
                              "A follow-up is a question with no number in it but a year; series lists result ids of this conversation. "
                              "Answer again in the same JSON format.")

    def __init__(self, model=None, client=None):
        super().__init__(model=model, client=client, grid="ercot")
        tools.SCOPE = SCOPE          # the profile's scope replaces the grid page's: more tables, and each one's rows named
        tools._frames.clear()
        self.grid = "ercot"
        self.system = [{"type": "text", "text": RULES + "\n\n" + guide(), "cache_control": {"type": "ephemeral"}}]

    def opening(self, question, today, context=None, history=None):
        head = f"Today is {today} (UTC)."
        line = context_line(context)
        past = history_text(history)
        self._question = question
        return head + (f"\n\n{line}" if line else "") + (f"\n\n{past}" if past else "") + f"\n\nQuestion: {question}"

    def extra_sources(self, context, history=None):
        # what an earlier answer of this conversation said was checked when it was written: its numbers, and the names it
        # was asked by, may be repeated
        given = [json.dumps(context)] if context else []
        for turn in turns(history):
            given += [turn["answer"]] + [json.dumps(c["input"]) + " " + spelled(c["input"]) for c in turn["calls"]]
        self._given = given
        return given

    def known_tables(self, history):
        return {c["table"] for turn in turns(history) for c in turn["citations"] if c.get("table") in TABLES}

    def source_texts(self, name, args, out):
        # a name asked by holds numbers the answer may repeat: foresight_4h_revenue_total_usd_per_mw is a four-hour battery
        return [spelled(args)]

    def tag(self, name, args, out, n):
        if isinstance(out, dict) and "error" not in out:
            if name == "query":
                out = {"result_id": f"r{n}", **out}
            elif name == "compare":
                out = {**out, "a": {"result_id": f"r{n}a", **out["a"]}, "b": {"result_id": f"r{n}b", **out["b"]}}
        return out

    def _known(self, results):
        """result id -> (the query's arguments, its output), for every query this conversation ran."""
        known = {}
        for r in results:
            if r["is_error"]:
                continue
            for rid, out in result_ids(r["out"]):
                args = r["input"] if r["tool"] == "query" else r["input"].get("a" if rid.endswith("a") else "b", {})
                known[rid] = (args, out)
        return known

    def extra_problems(self, draft, results):
        problems = []
        known = self._known(results)
        ids = draft.get("series") or []
        bad = [i for i in ids if i not in known]
        if bad:
            problems.append("series names result ids no tool returned: " + ", ".join(bad))
        flat = [i for i in ids if i in known and not chartable(*known[i])]
        if flat:
            problems.append("series names results that are not grouped series of at least "
                            f"{MIN_ROWS} rows (use group_by, or leave series empty): " + ", ".join(flat))
        if len(ids) > MAX_SERIES:
            problems.append(f"series names more than {MAX_SERIES} results")
        ups = [f.strip() for f in (draft.get("followups") or []) if f.strip()]
        if not 2 <= len(ups) <= 3:
            problems.append(f"followups must be two or three questions ({len(ups)} given)")
        pool = [json.dumps(r["out"], default=str) for r in results]
        stray = []
        for f in ups:
            for v, d in ask.numbers(f):
                if d == 0 and int(v) in YEARS:
                    continue
                if ask.unverified(f"{v:.{d}f}", pool):
                    stray.append(f"{v:.{d}f}")
        if stray:
            problems.append("follow-up questions contain numbers in no tool result: " + ", ".join(sorted(set(stray))))
        # session 121: a refusal names what is held nearest to what was asked; a premise's numbers are checked as the answer's
        if draft.get("not_in_warehouse"):
            near = [str(t) for t in (draft.get("nearest") or [])]
            if not 1 <= len(near) <= MAX_NEAREST or any(t not in TABLES for t in near):
                problems.append(f"nearest must name one to {MAX_NEAREST} tables of the guide by their exact names, nearest first ({', '.join(near) or 'none'} given)")
        given = [getattr(self, "_question", "")] + list(getattr(self, "_given", []))
        loose = ask.unverified(draft.get("premise") or "", pool + given)
        if loose:
            problems.append("premise contains numbers in no tool result and not in the question: " + ", ".join(loose))
        return problems

    def finish(self, record, results):
        known = self._known(results)
        ids = [i for i in (record.get("series") or []) if i in known and chartable(*known[i])]
        chosen = "the answer"
        if not ids and record.get("status") == "answered":
            # an answer that rests on a series returns it: when the model fetched one and named none, the last one it
            # fetched from a table it cites is shown
            cited = {c["table"] for c in record.get("citations", [])}
            last = [i for i, (a, o) in known.items() if chartable(a, o) and o.get("table") in cited]
            ids, chosen = last[-1:], "default: the last grouped result of a cited table"
        record["series"] = [dict(series_of(i, *known[i]), chosen_by=chosen) for i in ids[:MAX_SERIES]] if record.get("status") == "answered" else []
        # session 121: every series the page will draw is set against the rows the tool returned for that result id, key
        # by key and value by value; one that differs is not shown
        for s in record["series"]:
            s["check"] = series_check(s, known[s["result_id"]])
        record["series_not_shown"] = [s["result_id"] for s in record["series"] if not s["check"]["same"]]
        record["series"] = [s for s in record["series"] if s["check"]["same"]]
        status = record.get("status")
        if status == "not_in_warehouse":
            names = [t for t in (record.get("nearest") or []) if t in TABLES][:MAX_NEAREST]
        elif status == "refused_unverified":  # the fixed refusal names nothing: the tables this question read are the nearest known
            names = list(dict.fromkeys(o.get("table") for _, o in known.values() if o.get("table") in TABLES))[:MAX_NEAREST]
        else:
            names = []
        record["nearest"] = [{"table": t, "holds": HOLDS[t]} for t in names]
        record["premise"] = ask.nodash((record.get("premise") or "").strip()) if status == "answered" else ""
        record["followups"] = [ask.nodash(f.strip()) for f in (record.get("followups") or []) if f.strip()][:3] \
            if record.get("status") in ("answered", "not_in_warehouse") else []
        record["profile"] = "ercot"


KEY_TIME = re.compile(r"^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?(?: (\d{2}):00)?$")


def series_check(series, known_one):
    """The series as the page will draw it against the rows of the tool result it names: how many rows each has, and
    whether every key and value is the same, in the same order."""
    args, out = known_one
    g = args.get("group_by")
    fetched = [(str(r.get(g)), r.get("value", r.get("count"))) for r in out.get("result") or []]
    shown = [(r["key"], r["value"]) for r in series["rows"]]
    # the rows a line chart can place: a value, and a key that is a time (site/lib/chat/series.ts chartPoints)
    points = sum(1 for k, v in shown if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and KEY_TIME.match(k))
    return {"rows_fetched": len(fetched), "rows": len(shown), "same": fetched == shown, "points": points, "not_drawn": len(shown) - points}


def turns(history):
    """The conversation so far as the three things the first message carries of each turn: the question, the answer
    and the queries. The newest MAX_HISTORY turns, oldest first; a turn without an answer is left out."""
    out = []
    for h in (history or [])[-MAX_HISTORY:]:
        if not isinstance(h, dict) or not str(h.get("question") or "").strip() or not str(h.get("answer") or "").strip():
            continue
        calls = [{"tool": c.get("tool"), "input": c.get("input") or {}} for c in (h.get("calls") or []) if isinstance(c, dict) and c.get("tool") in ("query", "compare") and not c.get("is_error")]
        out.append({"question": str(h["question"]).strip()[:500], "answer": str(h["answer"]).strip()[:MAX_HISTORY_ANSWER], "calls": calls[:ask.MAX_TOOL_CALLS],
                    "citations": [c for c in (h.get("citations") or []) if isinstance(c, dict)]})
    return out


def history_text(history):
    """The conversation so far as the first message carries it; "" without one."""
    ts = turns(history)
    if not ts:
        return ""
    parts = [HISTORY_HEAD]
    for n, t in enumerate(ts, 1):
        queries = "; ".join(f"{c['tool']} {json.dumps(c['input'], sort_keys=True, separators=(',', ':'), ensure_ascii=False)}" for c in t["calls"]) or "none"
        parts.append(HISTORY_TURN.format(n=n, question=t["question"], answer=t["answer"], queries=queries))
    return "\n\n".join(parts)


def spelled(args):
    """The names in a tool call's arguments with their parts apart: "foresight_4h_revenue" as "foresight 4 h revenue"."""
    import re
    words = []

    def walk(v):
        if isinstance(v, dict):
            for x in v.values():
                walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)
        elif isinstance(v, str):
            words.append(re.sub(r"(?<=\d)(?=[A-Za-z])|(?<=[A-Za-z])(?=\d)", " ", re.sub(r"[^A-Za-z0-9.]+", " ", v)))
    walk({k: v for k, v in (args or {}).items() if k in ("variable", "entity", "where", "a", "b", "value_column")})
    return " ".join(words)


def context_line(context):
    """The sentence that tells the model where the reader came from; "" without a context."""
    if not context or not context.get("view"):
        return ""
    settings = "; ".join(f"{k} {v}" for k, v in (context.get("settings") or {}).items() if str(v).strip())
    return CONTEXT_LINE.format(view=context["view"], title=f" ({context['title']})" if context.get("title") else "",
                               settings=f", set to: {settings}" if settings else "")


def export_spec(path):
    """The profile for the site's server route: the system prompt with the guide, the schema, the scope and limits."""
    spec = {"_about": "Generated by warehouse/chat/ercot.py --export-spec; do not edit by hand.",
            "profile": "ercot", "system": RULES + "\n\n" + guide(), "answer_schema": SCHEMA, "effort": EFFORT,
            "retry": ErcotAsker.retry, "context_line": CONTEXT_LINE,
            "tables": SCOPE["tables"], "filters": SCOPE["filters"], "max_groups": MAX_GROUPS, "dated_groups": True, "max_series": MAX_SERIES,
            "min_rows": MIN_ROWS, "years": [YEARS[0], YEARS[-1]],
            # session 121: the conversation so far, and what each table holds (the first sentence of its card) for a refusal
            "history_head": HISTORY_HEAD, "history_turn": HISTORY_TURN, "max_history": MAX_HISTORY, "max_history_answer": MAX_HISTORY_ANSWER,
            "max_nearest": MAX_NEAREST, "holds": HOLDS}
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(spec, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {path}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Ask ERCOT, the reference version")
    ap.add_argument("question", nargs="?")
    ap.add_argument("--json", action="store_true", help="print the full record as JSON")
    ap.add_argument("--context", help="the view the reader came from, as JSON: {\"view\": \"/shoulder\", \"settings\": {...}}")
    ap.add_argument("--guide", action="store_true", help="print the table guide and exit")
    ap.add_argument("--export-spec", metavar="PATH")
    a = ap.parse_args(argv)
    if a.guide:
        print(RULES + "\n\n" + guide())
        return 0
    if a.export_spec:
        export_spec(a.export_spec)
        return 0
    if not a.question:
        ap.error("a question is required")
    rec = ErcotAsker().ask(a.question, context=json.loads(a.context) if a.context else None)
    if a.json:
        print(json.dumps(rec, indent=2, default=str))
        return 0
    print(rec["answer"])
    for c in rec["citations"]:
        print(f"  [{c['table']}] source {c['source_report']}; {c['data_version']}; tier {c.get('tier')}")
    for s in rec["series"]:
        print(f"  series {s['result_id']}: {s['title']} ({len(s['rows'])} rows of {s['table']}; {s['chosen_by']})")
    for f in rec["followups"]:
        print(f"  next: {f}")
    u = rec["usage"]
    print(f"\nstatus {rec['status']}; model {rec['model']}; tool calls {rec['tool_calls']}; requests {u['requests']}; "
          f"cost {'unknown' if rec['cost_usd'] is None else 'USD %.4f' % rec['cost_usd']}; {rec['seconds']} s"
          + ("; retried after: " + ", ".join(rec["first_violations"]) if rec["retried"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
