#!/usr/bin/env python3
"""Session 5202 (chain 235): the evaluation set of the AI chat over the warehouse widened to the whole platform, each
expected answer computed from the live set by this script, never typed.

Energy Research Warehouse (ERW). No model call of any kind. Reads only: the live set's `catalogue`, `series`, `entities`
and `events` views (Supabase REST, the anon key from the repository's .env, or the main checkout's beside a worktree),
1,000 rows a page, through lab_questions.py's reader (session 2224): what a visitor's chat can read, and nothing else.
Writes warehouse/chat/eval/questions_platform.yaml (the set, read by eval_s1113.py, eval_loop.py and eval_site.py with
--set platform) and warehouse/chat/eval/keys_platform.json (the keys with the time they were computed).

    python scripts/ask_eval/platform_questions.py            computes the keys and writes both files
    python scripts/ask_eval/platform_questions.py --check    exit 1 when the YAML on disk differs from a fresh computation

Twelve areas of the platform (the chain's prompt): power, prices, gas, oil, nuclear, renewables, storage, transmission,
projects, deals, policy, datacenters. Every question carries its `sector` and its `kind`:

  figure     the live set holds the answer: the key is the figure (or a word), the table, the tolerance
  hold       a table or a grid held for a license: the hold's words ("license needed") and no figure
  pause      MISO's own rows: the pause's word ("paused") and no figure
  not_live   a table of the ERW's record that is not loaded into the live set the chat reads (catalogue in_live_set
             "no"): a refusal that says where it is (Redivis, or that the live set does not hold it), and no figure
  outside    nothing in the warehouse holds it: "not in the warehouse", the missing thing named, no figure

A refusal names what is missing: each refusal key's text holds a word of the thing asked for beside the refusal's own
words. A text entry with "|" is met by any one of its parts (eval_s1113.py grade_set).

A day or a week is a window of local time, as trader_questions.py's (session 3280): the day is Tuesday 10 November 2026,
the week Monday 19 to Sunday 25 October 2026 (before the clocks went back on 1 November, so a week of 168 hours), each in
the grid's own time zone and said so in the question. Every window is checked whole before a key is written. The live
set holds the hourly tables' last 35 days only, so the week's keys stand until about 22 November 2026 and the day's until
about 14 December; --check says when they no longer do.

Session 5251 (chain 238) ran this script to its end for the first time. The day and the week were session 5202's 5
November and 2 to 8 November: on 13 November 2026 the live set held no row of 5 to 8 November in its EIA-930 tables (and
none of 30 October to 8 November for PJM's and CAISO's demand), none of 6 to 8 November in the real-time hub prices and
48 hours fewer than the week in the day-ahead ones. So the windows moved to days every series holds whole, and the
missing days became questions of their own, two kinds more:

  gap        the table holds the series and not the day asked for (no row of it): "not in the warehouse", the day named,
             no figure. The script stops when a row of the day has arrived (the question is then a figure's)
  partial    the window asked for is held in part (the script counts the steps held and stops when the window is whole):
             the answer says so in its own words (missing, incomplete, not complete, partial, a gap, "only" so many),
             whether it then gives the figure of the steps held or refuses; a figure given as the window's own, with no
             such word, is wrong
"""
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lab_questions as L  # noqa: E402  the reader, the hold and the key shapes of session 2224
import trader_questions as T  # noqa: E402  the local windows of session 3280

ROOT = L.ROOT
EVAL = L.EVAL
OUT = os.path.join(EVAL, "questions_platform.yaml")
KEYS_JSON = os.path.join(EVAL, "keys_platform.json")
TODAY = "2026-11-13"
SECTORS = ("power", "prices", "gas", "oil", "nuclear", "renewables", "storage", "transmission", "projects", "deals", "policy", "datacenters")
KINDS = ("figure", "hold", "pause", "not_live", "outside", "gap", "partial")
DAY = ("2026-11-10", "2026-11-11")
WEEK = ("2026-10-19", "2026-10-26")
DAY_WORDS, WEEK_WORDS = "on 10 November 2026", "in the week of Monday 19 to Sunday 25 October 2026"
# session 5251: the days the live set does not hold (the module's note), asked of in the kinds gap and partial
GAP_DAY = ("2026-11-06", "2026-11-07")
GAP_DAY_WORDS, GAP_DAY_TEXT = "on 6 November 2026", "6 November|November 6|2026-11-06|6 Nov"
GAP_WEEK = ("2026-11-02", "2026-11-09")
GAP_WEEK_WORDS = "in the week of Monday 2 to Sunday 8 November 2026"
PARTIAL = ("missing|incomplete|not complete|partial|gap|not held|no rows|no data|does not hold|do not hold|does not have|not all|not cover|not whole|not available|"
           "of the 168|of 168|only the|only for|only through|only holds|only has|only covers|only includes|only part|"
           "only 1|only 2|only 3|only 4|only 5|only 6|only 7|only 8|only 9|not a full|not the full|not full")
CT, PT, ET, UTC = "America/Chicago", "America/Los_Angeles", "America/New_York", "UTC"
TZ_WORDS = {CT: "Central time", PT: "Pacific time", ET: "Eastern time", UTC: "UTC"}
NIW = "not in the warehouse"
NOT_LIVE = "Redivis|live set|not loaded|not available here|cannot read|can't read"
E_HUB, SP15, NP15, SPPN = "ercot:HB_HUBAVG", "caiso:TH_SP15_GEN-APND", "caiso:TH_NP15_GEN-APND", "spp:SPPNORTH_HUB"


def series(table, entity, variable, lo, hi):
    """The rows of one entity and variable with lo <= ts_utc < hi (ISO dates or stamps), as (ts, value), oldest first."""
    rows = L.get("series", table_name=f"eq.{table}", entity=f"eq.{entity}", variable=f"eq.{variable}", select="ts_utc,value",
                 **{"and": f"(ts_utc.gte.{lo},ts_utc.lt.{hi})"})
    return sorted((r["ts_utc"], float(r["value"])) for r in rows if r["value"] is not None)


def months_of(table, entity, variable, year):
    """The twelve monthly rows of a calendar year, checked whole."""
    rows = series(table, entity, variable, f"{year}-01-01", f"{year + 1}-01-01")
    if len(rows) != 12 or len({t[:7] for t, _ in rows}) != 12:
        raise SystemExit(f"{table} {entity} {variable} {year}: {len(rows)} monthly rows, 12 expected")
    return [v for _, v in rows]


def trading_days(table, entity, variable, lo, hi, least):
    rows = series(table, entity, variable, lo, hi)
    if len(rows) < least or len({t for t, _ in rows}) != len(rows):
        raise SystemExit(f"{table} {entity} {variable} {lo} to {hi}: {len(rows)} rows, at least {least} expected, none twice")
    return rows


def entity_rows(table):
    return L.get("entities", table_name=f"eq.{table}", select="capacity_mw,status,status_date,extra")


def event_rows(table):
    return L.get("events", table_name=f"eq.{table}", select="event_date,event_type,status,mw,extra")


def cap_sum(rows):
    return round(sum(float(r["capacity_mw"]) for r in rows if r.get("capacity_mw") not in (None, "")), 4)


class Set:
    def __init__(self):
        self.qs, self.failed, self.cat = [], [], L.catalogue()

    def live(self, table):
        c = self.cat.get(table)
        return c is not None and c["in_live_set"] in ("yes", "review")

    def add(self, qid, sector, kind, make):
        try:
            q = make()
        except SystemExit as exc:
            self.failed.append(f"{qid}: {exc}")
            return
        q.update({"id": qid, "sector": sector, "kind": kind})
        q.setdefault("count", False)
        self.qs.append(q)

    def figure(self, qid, sector, grid, via, question, table, value, note, text=(), count=False, tolerance=None, tables=()):
        def make():
            v = value() if callable(value) else value
            if not self.live(table):
                raise SystemExit(f"{table} is not in the live set as yes or review: a figure key cannot be written for it")
            q = L.figure(qid, grid, via, question, table, float(v), note() if callable(note) else note, text() if callable(text) else text)
            q["tables"] = [table, *tables]
            q["count"] = count
            if tolerance is not None:
                q["tolerance"] = tolerance
            return q
        self.add(qid, sector, "figure", make)

    def word(self, qid, sector, grid, via, question, table, text, note):
        """A key met by a word of the answer (a rate the table holds as a fraction, written either way)."""
        def make():
            if not self.live(table):
                raise SystemExit(f"{table} is not in the live set as yes or review")
            if L.held(table, grid if grid != "none" else None):
                raise SystemExit(f"{table} is held for a license ({grid})")
            t = text() if callable(text) else text
            return {"grid": grid, "via": via, "question": question, "expected": [], "tolerance": 0.01, "text": list(t), "tables": [table],
                    "refuse": False, "hold": False, "note": note}
        self.add(qid, sector, "figure", make)

    def refusal(self, qid, sector, kind, grid, via, question, text, note, tables=()):
        def make():
            if kind == "hold":
                for t in tables:
                    if not L.held(t, grid if grid != "none" else None):
                        raise SystemExit(f"{t} is not held for a license ({grid}): a hold key cannot be written for it")
            if kind == "not_live":
                for t in tables:
                    c = self.cat.get(t)
                    if c is None or c["in_live_set"] != "no":
                        raise SystemExit(f"{t} is not a table of the catalogue marked in_live_set no ({None if c is None else c['in_live_set']})")
            if kind == "outside":
                for t in tables:
                    if t in self.cat:
                        raise SystemExit(f"{t} is in the catalogue a visitor's chat reads: the question is not outside the warehouse")
            return L.refusal(qid, grid, via, question, text, note, hold=(kind == "hold"), tables=tables if kind in ("hold", "pause") else ())
        self.add(qid, sector, kind, make)

    def gap(self, qid, sector, grid, via, question, table, entity, variable, days, tz, step, text, note):
        """Session 5251: a day (or a daily row) the table's series does not hold. A refusal that names the day."""
        def make():
            if not self.live(table) or L.held(table, grid if grid != "none" else None):
                raise SystemExit(f"{table} is not an open table of the live set ({grid}): a gap key cannot be written for it")
            held, want = steps(table, entity, variable, days, tz, step)
            if held:
                raise SystemExit(f"{table} {entity} {variable} {days} ({tz}): {held} of {want} steps are held now: the gap is filled, the question is a figure's")
            if not series(table, entity, variable, "2026-10-12", "2026-10-19"):
                raise SystemExit(f"{table} {entity} {variable}: no row of 12 to 18 October either: the series itself is missing, not a day of it")
            return L.refusal(qid, grid, via, question, text, f"{note}: 0 of {want} steps held on {TODAY}; not in the warehouse, the day named, no figure")
        self.add(qid, sector, "gap", make)

    def partial(self, qid, sector, grid, via, question, table, entity, variable, days, tz, step, note):
        """Session 5251: a window the table's series holds in part. The answer says so, whatever else it does."""
        def make():
            if not self.live(table) or L.held(table, grid if grid != "none" else None):
                raise SystemExit(f"{table} is not an open table of the live set ({grid}): a partial key cannot be written for it")
            held, want = steps(table, entity, variable, days, tz, step)
            if not 0 < held < want:
                raise SystemExit(f"{table} {entity} {variable} {days} ({tz}): {held} of {want} steps held: the window is not held in part")
            return {"grid": grid, "via": via, "question": question, "expected": [], "tolerance": 0.01, "text": [PARTIAL], "tables": [table], "refuse": False,
                    "hold": False, "note": f"{note}: {held} of {want} steps held on {TODAY}; the answer says the window is not whole (a figure of the steps held, said so, or a refusal that says so)"}
        self.add(qid, sector, "partial", make)

    def partial_row(self, qid, sector, grid, via, question, table, entity, month, held_variable, unit, note):
        """Session 5251: a month's row that the table's own count says covers part of the month (cost_of_power_monthly's
        October 2026 held 48 of 744 hours on 13 November). The answer says so; the row's figure is not keyed."""
        def make():
            if not self.live(table) or L.held(table, grid if grid != "none" else None):
                raise SystemExit(f"{table} is not an open table of the live set ({grid}): a partial key cannot be written for it")
            held, want = L.month_value(table, entity, held_variable, month), month_steps(month, unit)
            if not 0 < held < want:
                raise SystemExit(f"{table} {entity} {held_variable} {month}: {held:g} of {want} {unit}: the month's row is not held in part (the question is a figure's)")
            return {"grid": grid, "via": via, "question": question, "expected": [], "tolerance": 0.01, "text": [PARTIAL], "tables": [table], "refuse": False,
                    "hold": False, "note": f"{note}: {held_variable} says {held:g} of {want} {unit} on {TODAY}; the answer says the month is not whole (the row's figure, said so, or a refusal that says so)"}
        self.add(qid, sector, "partial", make)


def month_steps(month, unit):
    """The hours or the days a calendar month has."""
    a, b = dt.date.fromisoformat(f"{month}-01"), dt.date.fromisoformat(f"{L.next_month(month)}-01")
    return (b - a).days * (24 if unit == "hours" else 1)


def steps(table, entity, variable, days, tz, step):
    """(the steps of a local window that hold a value, the steps the window has), with step in minutes; a daily series
    (step 1440) is labelled with its local day at 00:00Z, so its window is the dates themselves."""
    if step == 1440:
        rows = series(table, entity, variable, f"{days[0]}T00:00:00Z", f"{days[1]}T00:00:00Z")
        return len({t for t, _ in rows}), (dt.date.fromisoformat(days[1]) - dt.date.fromisoformat(days[0])).days
    a, b = T.window(days, tz)
    rows = series(table, entity, variable, T.z(a), T.z(b))
    return len({t for t, _ in rows}), int((b - a).total_seconds() // (step * 60))


def local_mean(table, entity, variable, days, tz, step=60):
    return T.mean([v for _, v in T.rows_in(table, entity, variable, days, tz, step)])


def local_max(table, entity, variable, days, tz, step=60):
    return max(v for _, v in T.rows_in(table, entity, variable, days, tz, step))


def build():
    S = Set()
    f, w, r = S.figure, S.word, S.refusal
    D, W = DAY, WEEK

    # ------------------------------------------------------------------ power
    f("pw01", "power", "ERCOT", "general", f"What was ERCOT's average hourly demand {DAY_WORDS} (Central time), in MW?", "eia930_all_demand",
      lambda: local_mean("eia930_all_demand", "eia930:ERCO", "demand_mw", D, CT), "eia930_all_demand, eia930:ERCO, demand_mw: the mean of the 24 hourly rows of the local day (America/Chicago); checked whole")
    f("pw02", "power", "PJM", "general", f"What was the highest hourly demand in PJM {WEEK_WORDS} (Eastern time), in MW?", "eia930_all_demand",
      lambda: local_max("eia930_all_demand", "eia930:PJM", "demand_mw", W, ET), "eia930_all_demand, eia930:PJM, demand_mw: the maximum of the 168 hourly rows of the local week (America/New_York); checked whole")
    f("pw03", "power", "none", "general", f"What was the average hourly electricity demand of the Lower 48 states {DAY_WORDS} (the UTC day), in MW?", "eia930_all_demand",
      lambda: local_mean("eia930_all_demand", "eia930:US48", "demand_mw", D, UTC), "eia930_all_demand, eia930:US48, demand_mw: the mean of the 24 hourly rows of the UTC day; checked whole")
    f("pw04", "power", "none", "general", "How much electricity was sold to residential customers in Texas in July 2026, in MWh?", "eia_retail_sales_monthly",
      lambda: L.month_value("eia_retail_sales_monthly", "eia:retail_sales:TX:RES", "retail_sales", "2026-07"), "eia_retail_sales_monthly, eia:retail_sales:TX:RES, retail_sales: the 2026-07 row")
    f("pw05", "power", "none", "general", "What were total retail electricity sales in California, all sectors, in June 2026, in MWh?", "eia_retail_sales_monthly",
      lambda: L.month_value("eia_retail_sales_monthly", "eia:retail_sales:CA:ALL", "retail_sales", "2026-06"), "eia_retail_sales_monthly, eia:retail_sales:CA:ALL, retail_sales: the 2026-06 row")
    f("pw06", "power", "ERCOT", "general", "By how much had ERCOT's average demand in 2025 grown since 2019, in percent?", "eia930_demand_growth",
      lambda: L.year_value("eia930_demand_growth", "eia930:ERCO", "avg_demand_growth_since_2019_pct", 2025), "eia930_demand_growth, eia930:ERCO, avg_demand_growth_since_2019_pct: the 2025 row")
    f("pw07", "power", "ERCOT", "general", "What was ERCOT's peak demand in 2025, in MW?", "grid_peak_vs_capacity",
      lambda: L.year_value("grid_peak_vs_capacity", "grid_peak_vs_capacity:ercot", "peak_demand_mw", 2025), "grid_peak_vs_capacity, grid_peak_vs_capacity:ercot, peak_demand_mw: the 2025 row (in_live_set review)",
      tables=("grid_stress_yearly", "ai_power_regions"))
    f("pw08", "power", "PJM", "general", "What was the carbon intensity of PJM's generation in September 2026, in kg of CO2 per MWh?", "carbon_intensity_monthly",
      lambda: L.month_value("carbon_intensity_monthly", "eia930:PJM", "intensity_generation", "2026-09"), "carbon_intensity_monthly, eia930:PJM, intensity_generation: the 2026-09 row")
    f("pw09", "power", "none", "general", "How many Flex Alerts did the California ISO call in 2022?", "caiso_grid_emergencies",
      lambda: sum(1 for e in event_rows("caiso_grid_emergencies") if e["event_type"] == "flex_alert" and e["event_date"][:4] == "2022"),
      "caiso_grid_emergencies (events): the count of rows with event_type flex_alert and event_date in 2022", count=True)
    f("pw10", "power", "PJM", "general", f"What was PJM's average hourly generation from coal {DAY_WORDS} (Eastern time), in MW?", "eia930_all_generation",
      lambda: local_mean("eia930_all_generation", "eia930:PJM", "net_generation_coal_mw", D, ET), "eia930_all_generation, eia930:PJM, net_generation_coal_mw: the mean of the 24 hourly rows of the local day (America/New_York); checked whole")
    r("pw11", "power", "outside", "ERCOT", "general", "What was ERCOT's peak demand in August 2010, in MW?", [NIW, "2010|August"],
      "no table of the live set reaches 2010 for ERCOT's demand (eia930's history begins in 2018): not in the warehouse, the period named, no figure")
    r("pw12", "power", "not_live", "none", "general", "What was the average residential retail electricity price in California in August 2026, in cents per kWh?", [NOT_LIVE, "retail"],
      "eia_retail_electricity_prices is a table of the record, not loaded into the live set (in_live_set no): the answer says so and states no figure", tables=["eia_retail_electricity_prices"])
    r("pw13", "power", "outside", "ERCOT", "general", "What will ERCOT's peak demand be in the summer of 2028, in MW?", [NIW, "2028|forecast|projection"],
      "the warehouse holds what happened, and day-ahead demand forecasts of the hours ahead, never a forecast of 2028: not in the warehouse, no figure")

    # ------------------------------------------------------------------ prices
    f("pr01", "prices", "ERCOT", "general", f"What was the average hourly day-ahead price at ERCOT's hub average (HB_HUBAVG) {DAY_WORDS} (Central time), in USD per MWh?", "iso_dam_hub_prices",
      lambda: local_mean("iso_dam_hub_prices", E_HUB, "spp_dam", D, CT), "iso_dam_hub_prices, ercot:HB_HUBAVG, spp_dam: the mean of the 24 hourly rows of the local day (America/Chicago); checked whole",
      tables=("iso_trader_daily", "price_board_latest", "price_board_spreads", "ercot_hub_prices_daily"))
    f("pr02", "prices", "CAISO", "grid", f"What was the average real-time price at CAISO's SP15 hub {DAY_WORDS} (Pacific time), over its 15-minute intervals, in USD per MWh?", "iso_rtm_hub_prices",
      lambda: local_mean("iso_rtm_hub_prices", SP15, "lmp_rtm_15m_mean", D, PT, 15), "iso_rtm_hub_prices, caiso:TH_SP15_GEN-APND, lmp_rtm_15m_mean: the mean of the 96 15-minute rows of the local day (America/Los_Angeles); checked whole",
      tables=("iso_trader_daily", "price_board_latest"))
    f("pr03", "prices", "SPP", "grid", f"What was the highest hourly day-ahead price at SPP's North hub {WEEK_WORDS} (Central time), in USD per MWh?", "iso_dam_hub_prices",
      lambda: local_max("iso_dam_hub_prices", SPPN, "lmp_dam", W, CT), "iso_dam_hub_prices, spp:SPPNORTH_HUB, lmp_dam: the maximum of the 168 hourly rows of the local week (America/Chicago); checked whole")
    f("pr04", "prices", "ERCOT", "general", "What was the load-weighted real-time price at ERCOT's hub average in September 2026, in USD per MWh?", "cost_of_power_monthly",
      lambda: L.month_value("cost_of_power_monthly", E_HUB, "rt_load_weighted", "2026-09"), "cost_of_power_monthly, ercot:HB_HUBAVG, rt_load_weighted: the 2026-09 row", tables=("cost_of_power_carbon",))
    S.partial_row("pr05", "prices", "CAISO", "general", "What was the simple average day-ahead price at CAISO's SP15 hub in October 2026, in USD per MWh?", "cost_of_power_monthly",
                  SP15, "2026-10", "da_hours", "hours", "cost_of_power_monthly, caiso:TH_SP15_GEN-APND, the 2026-10 row (da_simple_mean; session 5202 keyed its figure, and the chat's first answer said the row was not October's)")
    f("pr06", "prices", "ERCOT", "general", "What was the average on-peak day-ahead price at ERCOT's hub average over calendar year 2025, in USD per MWh?", "price_board_peak_offpeak",
      lambda: L.year_value("price_board_peak_offpeak", E_HUB, "da_year_peak_mean", 2025), "price_board_peak_offpeak, ercot:HB_HUBAVG, da_year_peak_mean: the 2025 row")
    f("pr07", "prices", "ERCOT", "grid", "What was the mean day-ahead clearing price of ERCOT's Responsive Reserve Service (RRS) in August 2026, in USD per MW per hour?", "ercot_as_prices_monthly",
      lambda: L.month_value("ercot_as_prices_monthly", "ercot:RRS", "mcpc_dam_mean", "2026-08"), "ercot_as_prices_monthly, ercot:RRS, mcpc_dam_mean: the 2026-08 row (in_live_set review)", tables=("ercot_as_prices",))
    f("pr08", "prices", "ERCOT", "general", f"What was the implied heat rate at ERCOT's hub average {DAY_WORDS}, in MMBtu per MWh?", "price_board_spreads",
      lambda: T.one_row("price_board_spreads", E_HUB, "implied_heat_rate", D[0]), "price_board_spreads, ercot:HB_HUBAVG, implied_heat_rate: the 2026-11-10 row (the day-ahead daily mean over Henry Hub, the board's own)",
      tables=("iso_trader_daily",))
    f("pr09", "prices", "ERCOT", "grid", "How many real-time settlement intervals at ERCOT's West hub (HB_WEST) had a negative price in 2025?", "ercot_peak_premium_annual",
      lambda: L.year_value("ercot_peak_premium_annual", "ercot:HB_WEST", "n_negative", 2025), "ercot_peak_premium_annual, ercot:HB_WEST, n_negative: the 2025 row", count=True)
    f("pr10", "prices", "CAISO", "general", f"How much higher or lower was the average hourly day-ahead price at CAISO's SP15 hub than at its NP15 hub {DAY_WORDS} (Pacific time), in USD per MWh?", "iso_dam_hub_prices",
      lambda: local_mean("iso_dam_hub_prices", SP15, "lmp_dam", D, PT) - local_mean("iso_dam_hub_prices", NP15, "lmp_dam", D, PT),
      "iso_dam_hub_prices, lmp_dam: the mean of the 24 hourly rows of the local day (America/Los_Angeles) at caiso:TH_SP15_GEN-APND less the same at caiso:TH_NP15_GEN-APND; a negative key is SP15 lower (the grader's rule sign_in_words)",
      tables=("iso_trader_daily", "price_board_latest"))
    r("pr11", "prices", "hold", "NYISO", "grid", f"What was the average day-ahead price in NYISO's Zone J (New York City) {DAY_WORDS}, in USD per MWh?", ["NYISO", L.LICENSE],
      "nyiso_dam_zone_prices is NYISO's own and held for a license: NYISO named, the hold's words, no figure", tables=["nyiso_dam_zone_prices"])
    r("pr12", "prices", "pause", "MISO", "grid", f"What was the average day-ahead price at MISO's Indiana hub {DAY_WORDS}, in USD per MWh?", ["paused"],
      "MISO's own rows: MISO is paused while its terms are reviewed (since 4 October 2026): the pause's word and no figure", tables=["iso_dam_hub_prices"])
    r("pr13", "prices", "outside", "PJM", "general", "What was the average day-ahead price at PJM's Western Hub in October 2026, in USD per MWh?", [NIW, "PJM"],
      "the live set holds no PJM energy price: not in the warehouse, PJM named, no figure")
    r("pr14", "prices", "hold", "ISO-NE", "general", f"What was the average real-time price at ISO New England's Internal Hub {DAY_WORDS}, in USD per MWh?", [L.LICENSE],
      "ISO-NE's prices are held for a license (by grid): the hold's words and no figure", tables=["isone_rtm_zone_prices"])

    # ------------------------------------------------------------------ gas
    HH = ("eia_fuel_spot_prices", "eia:henry_hub", "spot_price")
    f("ga01", "gas", "none", "general", "What was the Henry Hub natural gas spot price on 10 November 2026, in USD per MMBtu?", HH[0],
      lambda: T.one_row(*HH, "2026-11-10"), "eia_fuel_spot_prices, eia:henry_hub, spot_price: the 2026-11-10 row", tables=("price_board_spreads",))
    f("ga02", "gas", "none", "general", "What was the average Henry Hub spot price over the trading days of October 2026, in USD per MMBtu?", HH[0],
      lambda: T.mean([v for _, v in trading_days(*HH, "2026-10-01", "2026-11-01", 20)]), "eia_fuel_spot_prices, eia:henry_hub, spot_price: the mean of the trading days' rows of 2026-10 (at least 20)")
    f("ga03", "gas", "none", "general", "What was the highest daily Henry Hub spot price in 2025, in USD per MMBtu?", HH[0],
      lambda: max(v for _, v in trading_days(*HH, "2025-01-01", "2026-01-01", 240)), "eia_fuel_spot_prices, eia:henry_hub, spot_price: the maximum of the trading days' rows of 2025 (at least 240)")
    f("ga04", "gas", "none", "general", "How much natural gas did the US industrial sector consume in June 2026, in trillion Btu?", "eia_sector_energy_consumption_monthly",
      lambda: L.month_value("eia_sector_energy_consumption_monthly", "eia:NNICBUS", "energy_consumption", "2026-06"), "eia_sector_energy_consumption_monthly, eia:NNICBUS (natural gas consumed by the industrial sector), energy_consumption: the 2026-06 row")
    f("ga05", "gas", "CAISO", "general", f"What was the spark spread at CAISO's SP15 hub {DAY_WORDS}, at a heat rate of 7.0 MMBtu per MWh against Henry Hub gas, in USD per MWh?", "price_board_spreads",
      lambda: T.one_row("price_board_spreads", SP15, "spark_spread_7", D[0]), "price_board_spreads, caiso:TH_SP15_GEN-APND, spark_spread_7: the 2026-11-10 row (the board's own)")
    f("ga06", "gas", "none", "general", "How much electricity did Texas generate from natural gas in July 2026, in MWh?", "state_generation_mix_monthly",
      lambda: L.month_value("state_generation_mix_monthly", "eia:TX", "net_generation_natural_gas_mwh", "2026-07"), "state_generation_mix_monthly, eia:TX, net_generation_natural_gas_mwh: the 2026-07 row")
    f("ga07", "gas", "ERCOT", "general", f"What was ERCOT's average hourly generation from natural gas {DAY_WORDS} (Central time), in MW?", "eia930_all_generation",
      lambda: local_mean("eia930_all_generation", "eia930:ERCO", "net_generation_natural_gas_mw", D, CT), "eia930_all_generation, eia930:ERCO, net_generation_natural_gas_mw: the mean of the 24 hourly rows of the local day (America/Chicago); checked whole")
    f("ga08", "gas", "ERCOT", "general", "On the generator page's rule, how much margin over fuel did a gas peaker at ERCOT's hub average earn in August 2026, in USD per MW?", "merchant_revenue_monthly",
      lambda: L.month_value("merchant_revenue_monthly", E_HUB, "peaker_revenue_per_mw", "2026-08"), "merchant_revenue_monthly, ercot:HB_HUBAVG, peaker_revenue_per_mw: the 2026-08 row")
    r("ga09", "gas", "not_live", "none", "general", "How much LNG did the United States export to Japan in 2025?", [NOT_LIVE, "LNG"],
      "eia_lng_exports_monthly is a table of the record, not loaded into the live set: the answer says so and states no figure", tables=["eia_lng_exports_monthly"])
    r("ga10", "gas", "not_live", "none", "general", "How much natural gas did Texas leases produce in May 2026, per the Railroad Commission's lease data?", [NOT_LIVE, "Railroad Commission|RRC|lease"],
      "rrc_lease_production_monthly is a table of the record, not loaded into the live set: the answer says so and states no figure", tables=["rrc_lease_production_monthly"])
    r("ga11", "gas", "outside", "none", "general", "What was the Dutch TTF natural gas price on 10 November 2026?", [NIW, "TTF"],
      "the warehouse holds one gas price, Henry Hub: not in the warehouse, TTF named, no figure")
    r("ga12", "gas", "outside", "none", "general", "How much working gas was in US underground storage in the week ending 31 October 2026, in Bcf?", [NIW, "storage"],
      "no table holds natural gas storage inventories: not in the warehouse, the thing named, no figure")

    # ------------------------------------------------------------------ oil
    WTI = ("eia_fuel_spot_prices", "eia:wti_cushing", "spot_price")
    BRENT = ("eia_fuel_spot_prices", "eia:brent", "spot_price")
    f("oi01", "oil", "none", "general", "What was the WTI crude oil spot price at Cushing on 10 November 2026, in USD per barrel?", WTI[0],
      lambda: T.one_row(*WTI, "2026-11-10"), "eia_fuel_spot_prices, eia:wti_cushing, spot_price: the 2026-11-10 row")
    f("oi02", "oil", "none", "general", "What was the average Brent crude spot price over the trading days of October 2026, in USD per barrel?", BRENT[0],
      lambda: T.mean([v for _, v in trading_days(*BRENT, "2026-10-01", "2026-11-01", 20)]), "eia_fuel_spot_prices, eia:brent, spot_price: the mean of the trading days' rows of 2026-10 (at least 20)")
    f("oi03", "oil", "none", "general", "What was the spread of Brent over WTI on 10 November 2026, in USD per barrel?", "price_board_spreads",
      lambda: T.one_row("price_board_spreads", "erw:brent_minus_wti", "brent_minus_wti", "2026-11-10"), "price_board_spreads, erw:brent_minus_wti, brent_minus_wti: the 2026-11-10 row (the board's own difference)",
      tables=("eia_fuel_spot_prices",))
    f("oi04", "oil", "none", "general", "What was the lowest daily WTI spot price in 2020, in USD per barrel?", WTI[0],
      lambda: min(v for _, v in trading_days(*WTI, "2020-01-01", "2021-01-01", 240)), "eia_fuel_spot_prices, eia:wti_cushing, spot_price: the minimum of the trading days' rows of 2020 (a negative price, 20 April 2020: the table's values are real)")
    f("oi05", "oil", "none", "general", "How much petroleum did the US industrial sector consume in May 2026, in trillion Btu?", "eia_sector_energy_consumption_monthly",
      lambda: L.month_value("eia_sector_energy_consumption_monthly", "eia:PAICBUS", "energy_consumption", "2026-05"), "eia_sector_energy_consumption_monthly, eia:PAICBUS (petroleum consumed by the industrial sector), energy_consumption: the 2026-05 row")
    r("oi06", "oil", "hold", "none", "general", "What is the rate of Texas's oil production tax, as the warehouse records it?", [L.LICENSE],
      "impact_tax_rules is held whole for a license (session 5251 found it so; session 5202 had keyed the rate): the hold's words and no rate", tables=["impact_tax_rules"])
    r("oi07", "oil", "not_live", "none", "general", "How much crude oil did the United States import from Canada in 2025?", [NOT_LIVE, "import"],
      "eia_crude_imports_by_country is a table of the record, not loaded into the live set: the answer says so and states no figure", tables=["eia_crude_imports_by_country"])
    r("oi08", "oil", "not_live", "none", "general", "What were US commercial crude oil stocks in the week ending 6 November 2026?", [NOT_LIVE, "stock"],
      "eia_petroleum_stocks_weekly is a table of the record, not loaded into the live set: the answer says so and states no figure", tables=["eia_petroleum_stocks_weekly"])
    r("oi09", "oil", "not_live", "none", "general", "What was the US average retail price of regular gasoline in the week of 9 November 2026?", [NOT_LIVE, "gasoline|retail"],
      "eia_retail_fuel_prices is a table of the record, not loaded into the live set: the answer says so and states no figure", tables=["eia_retail_fuel_prices"])
    r("oi10", "oil", "not_live", "none", "general", "What was the New York Harbor ultra-low sulfur diesel spot price on 10 November 2026?", [NOT_LIVE, "diesel|product"],
      "eia_product_spot_prices is a table of the record, not loaded into the live set: the answer says so and states no figure", tables=["eia_product_spot_prices"])
    r("oi11", "oil", "outside", "none", "general", "How many barrels a day did OPEC produce in October 2026?", [NIW, "OPEC"],
      "no table holds OPEC's production: not in the warehouse, OPEC named, no figure")

    # ------------------------------------------------------------------ nuclear
    f("nu01", "nuclear", "PJM", "general", f"What was PJM's average hourly nuclear generation {DAY_WORDS} (Eastern time), in MW?", "eia930_all_generation",
      lambda: local_mean("eia930_all_generation", "eia930:PJM", "net_generation_nuclear_mw", D, ET), "eia930_all_generation, eia930:PJM, net_generation_nuclear_mw: the mean of the 24 hourly rows of the local day (America/New_York); checked whole")
    f("nu02", "nuclear", "none", "general", f"What was the highest hourly nuclear generation in the Lower 48 states {WEEK_WORDS} (UTC), in MW?", "eia930_all_generation",
      lambda: local_max("eia930_all_generation", "eia930:US48", "net_generation_nuclear_mw", W, UTC), "eia930_all_generation, eia930:US48, net_generation_nuclear_mw: the maximum of the 168 hourly rows of the UTC week; checked whole")
    f("nu03", "nuclear", "none", "general", "How much electricity did Illinois generate from nuclear power in July 2026, in MWh?", "state_generation_mix_monthly",
      lambda: L.month_value("state_generation_mix_monthly", "eia:IL", "net_generation_nuclear_mwh", "2026-07"), "state_generation_mix_monthly, eia:IL, net_generation_nuclear_mwh: the 2026-07 row")
    f("nu04", "nuclear", "none", "general", "How much electricity did Illinois generate from nuclear power over calendar year 2025, the twelve months summed, in MWh?", "state_generation_mix_monthly",
      lambda: sum(months_of("state_generation_mix_monthly", "eia:IL", "net_generation_nuclear_mwh", 2025)), "state_generation_mix_monthly, eia:IL, net_generation_nuclear_mwh: the sum of the 12 monthly rows of 2025")
    f("nu05", "nuclear", "PJM", "general", "How much nuclear capacity did PJM have in 2025, in MW, in the warehouse's yearly grid stress table?", "grid_stress_yearly",
      lambda: L.year_value("grid_stress_yearly", "iso:pjm", "capacity_nuclear_mw", 2025), "grid_stress_yearly, iso:pjm, capacity_nuclear_mw: the 2025 row (in_live_set review)")
    r("nu06", "nuclear", "outside", "none", "general", "What was the spot price of uranium (U3O8) in October 2026, in USD per pound?", [NIW, "uranium|U3O8"],
      "no table holds a uranium price: not in the warehouse, uranium named, no figure")
    r("nu07", "nuclear", "outside", "none", "general", "Which US nuclear reactors were in a refueling outage on 10 November 2026?", [NIW, "outage|reactor"],
      "no table holds reactor status or outages: not in the warehouse, the thing named, no figure")
    r("nu08", "nuclear", "not_live", "none", "general", "What is the nameplate capacity of Vogtle Unit 4 in EIA's generator inventory, in MW?", [NOT_LIVE, "generator|860M"],
      "eia860m_operating_generators is a table of the record, not loaded into the live set: the answer says so and states no figure", tables=["eia860m_operating_generators"])

    # ------------------------------------------------------------------ renewables
    f("re01", "renewables", "CAISO", "general", "How much solar generation did the California ISO curtail in September 2026, in MWh?", "iso_curtailment_monthly",
      lambda: L.month_value("iso_curtailment_monthly", "caiso:ISO", "curtailed_solar_mwh", "2026-09"), "iso_curtailment_monthly, caiso:ISO, curtailed_solar_mwh: the 2026-09 row", tables=("caiso_curtailment_daily",))
    f("re02", "renewables", "SPP", "general", "How much wind generation did SPP curtail in October 2026, in MWh?", "iso_curtailment_monthly",
      lambda: L.month_value("iso_curtailment_monthly", "spp:SPP", "curtailed_wind_mwh", "2026-10"), "iso_curtailment_monthly, spp:SPP, curtailed_wind_mwh: the 2026-10 row", tables=("spp_curtailment_daily",))
    f("re03", "renewables", "ERCOT", "grid", "How much electricity did wind generate in ERCOT on 10 November 2026, in MWh?", "ercot_wind_solar_hsl_daily",
      lambda: T.one_row("ercot_wind_solar_hsl_daily", "ercot:system", "wind_generation_mwh", "2026-11-10"), "ercot_wind_solar_hsl_daily, ercot:system, wind_generation_mwh: the 2026-11-10 row")
    f("re04", "renewables", "CAISO", "general", "What was the solar capture price at CAISO's SP15 hub in August 2026, in USD per MWh?", "merchant_revenue_monthly",
      lambda: L.month_value("merchant_revenue_monthly", SP15, "solar_capture_price", "2026-08"), "merchant_revenue_monthly, caiso:TH_SP15_GEN-APND, solar_capture_price: the 2026-08 row")
    f("re05", "renewables", "SPP", "grid", "Over calendar year 2025, how much revenue did wind earn per MW at SPP's North hub, the twelve monthly revenues summed, in USD per MW?", "merchant_revenue_monthly",
      lambda: sum(months_of("merchant_revenue_monthly", SPPN, "wind_revenue_per_mw", 2025)), "merchant_revenue_monthly, spp:SPPNORTH_HUB, wind_revenue_per_mw: the sum of the 12 monthly rows of 2025")
    f("re06", "renewables", "ERCOT", "general", "What is the highest share of ERCOT's generation that wind has reached in any hour on record, in percent, and in which year?", "generation_mix_records",
      lambda: record("iso:ercot", "wind_share_max_pct")[1], "generation_mix_records, iso:ercot, wind_share_max_pct: the one row (in_live_set review); the year of its stamp in the text",
      text=lambda: [record("iso:ercot", "wind_share_max_pct")[0][:4]])
    f("re07", "renewables", "none", "general", "How much electricity did California generate from solar in June 2026, in MWh?", "state_generation_mix_monthly",
      lambda: L.month_value("state_generation_mix_monthly", "eia:CA", "net_generation_solar_mwh", "2026-06"), "state_generation_mix_monthly, eia:CA, net_generation_solar_mwh: the 2026-06 row")
    f("re08", "renewables", "none", "general", "How much electricity did Texas generate from wind over calendar year 2025, the twelve months summed, in MWh?", "state_generation_mix_monthly",
      lambda: sum(months_of("state_generation_mix_monthly", "eia:TX", "net_generation_wind_mwh", 2025)), "state_generation_mix_monthly, eia:TX, net_generation_wind_mwh: the sum of the 12 monthly rows of 2025")
    f("re09", "renewables", "ERCOT", "general", "What share of ERCOT's generation was carbon-free in September 2026, in percent?", "clean_energy_summary",
      lambda: L.month_value("clean_energy_summary", "iso:ercot", "carbon_free_share_pct", "2026-09"), "clean_energy_summary, iso:ercot, carbon_free_share_pct: the 2026-09 row (in_live_set review)")
    r("re10", "renewables", "outside", "none", "general", "How much rooftop solar capacity was installed in Arizona in 2025, in MW?", [NIW, "rooftop|distributed"],
      "no table holds rooftop or distributed solar installations: not in the warehouse, the thing named, no figure")
    r("re11", "renewables", "outside", "none", "general", "What did a Texas renewable energy certificate (REC) trade for in October 2026?", [NIW, "REC|certificate"],
      "no table holds renewable energy certificate prices: not in the warehouse, the thing named, no figure")

    # ------------------------------------------------------------------ storage
    SB = "storage_buildout_monthly"
    f("st01", "storage", "ERCOT", "general", "How many MW of batteries were operating in ERCOT in September 2026?", SB,
      lambda: L.month_value(SB, "iso:ercot", "battery_operating_mw", "2026-09"), "storage_buildout_monthly, iso:ercot, battery_operating_mw: the 2026-09 row")
    f("st02", "storage", "CAISO", "general", "How many MWh of battery energy capacity were operating in CAISO in September 2026?", SB,
      lambda: L.month_value(SB, "iso:caiso", "battery_operating_mwh", "2026-09"), "storage_buildout_monthly, iso:caiso, battery_operating_mwh: the 2026-09 row")
    f("st03", "storage", "none", "general", "How many MW of batteries were operating in the United States in total in September 2026?", SB,
      lambda: L.month_value(SB, "us:total", "battery_operating_mw", "2026-09"), "storage_buildout_monthly, us:total, battery_operating_mw: the 2026-09 row")
    f("st04", "storage", "ERCOT", "general", "On the battery page, how much did a 4-hour battery with perfect foresight earn in total at ERCOT's hub average in September 2026, in USD per kW?", "battery_stack_monthly",
      lambda: L.month_value("battery_stack_monthly", E_HUB, "foresight_4h_revenue_total_usd_per_mw", "2026-09") / 1000.0,
      "battery_stack_monthly, ercot:HB_HUBAVG, foresight_4h_revenue_total_usd_per_mw: the 2026-09 row over 1,000 (the tool's value_usd_per_kw)", tolerance=0.01)
    f("st05", "storage", "CAISO", "general", "How much energy did CAISO's batteries discharge on 10 November 2026, in MWh?", "storage_daily_cycle",
      lambda: T.one_row("storage_daily_cycle", "caiso:ISO", "mwh_discharged", "2026-11-10"), "storage_daily_cycle, caiso:ISO, mwh_discharged: the 2026-11-10 row")
    f("st06", "storage", "CAISO", "grid", f"What was the highest 5-minute battery discharge on CAISO's grid {DAY_WORDS} (Pacific time), in MW?", "caiso_battery_storage",
      lambda: local_max("caiso_battery_storage", "caiso:ISO", "batteries_mw", D, PT, 5), "caiso_battery_storage, caiso:ISO, batteries_mw: the maximum of the 288 5-minute rows of the local day (America/Los_Angeles); checked whole")
    f("st07", "storage", "none", "general", "How many operating battery storage units does the warehouse's storage capacity table list in Texas?", "storage_capacity",
      lambda: sum(1 for e in entity_rows("storage_capacity") if e["status"] == "operating" and (e.get("extra") or {}).get("state") == "TX"),
      "storage_capacity (entities): the count of rows with status operating and state TX", count=True)
    f("st08", "storage", "none", "general", "How many MW of battery storage are under construction in the United States, in the warehouse's storage capacity table?", "storage_capacity",
      lambda: cap_sum([e for e in entity_rows("storage_capacity") if e["status"] == "under_construction"]), "storage_capacity (entities): the sum of capacity_mw over the rows with status under_construction")
    f("st09", "storage", "CAISO", "general", "Over calendar year 2025, how much did a 4-hour battery at CAISO's SP15 hub earn per MW on the generator page's rule, the twelve monthly revenues summed, in USD per MW?", "merchant_revenue_monthly",
      lambda: sum(months_of("merchant_revenue_monthly", SP15, "battery_4h_revenue_per_mw", 2025)), "merchant_revenue_monthly, caiso:TH_SP15_GEN-APND, battery_4h_revenue_per_mw: the sum of the 12 monthly rows of 2025")
    r("st10", "storage", "outside", "none", "general", "What was the price of lithium carbonate in October 2026, in USD per tonne?", [NIW, "lithium"],
      "no table holds a lithium price: not in the warehouse, lithium named, no figure")
    r("st11", "storage", "outside", "PJM", "general", "How much revenue did a 4-hour battery earn in PJM in August 2026, in USD per kW?", [NIW, "PJM"],
      "the battery tables hold ERCOT's hub average and CAISO's SP15 only, and the live set holds no PJM price: not in the warehouse, PJM named, no figure")

    # ------------------------------------------------------------------ transmission
    BA = "ba_supply_monthly"
    f("tx01", "transmission", "CAISO", "general", "Measured as its demand less its own generation (the balance), how much electricity did the California ISO import on net in August 2026, in MWh?", BA,
      lambda: whole_month(BA, "eia930:CISO", "2026-08", "days_held") and L.month_value(BA, "eia930:CISO", "net_import_balance_mwh", "2026-08"),
      "ba_supply_monthly, eia930:CISO, net_import_balance_mwh: the 2026-08 row, its 31 days held (a balancing authority's rows hold up to three measures of net imports: the question names the one; ERCOT's August holds 27 of its 31 days and is not asked)")
    f("tx02", "transmission", "CAISO", "general", "By the California ISO's own reported total interchange, what share of its demand was met by net imports in August 2026, in percent?", BA,
      lambda: L.month_value(BA, "eia930:CISO", "net_import_total_interchange_share_pct", "2026-08"),
      "ba_supply_monthly, eia930:CISO, net_import_total_interchange_share_pct: the 2026-08 row (the measure named in the question)")
    f("tx03", "transmission", "CAISO", "general", "How much electricity did the California ISO import on net from the Bonneville Power Administration in August 2026, in MWh?", BA,
      lambda: L.month_value(BA, "eia930:CISO-BPAT", "net_import_mwh", "2026-08"), "ba_supply_monthly, eia930:CISO-BPAT (the pair), net_import_mwh: the 2026-08 row")
    S.partial_row("tx04", "transmission", "ERCOT", "grid", "What was the median day-ahead basis of all of ERCOT's settlement points to the hub average in October 2026, in USD per MWh?", "node_basis_summary",
                  E_HUB, "2026-10", "dam_all_days", "days", "node_basis_summary, ercot:HB_HUBAVG, the 2026-10 row (dam_all_basis_p50, in_live_set review)")
    f("tx05", "transmission", "ERCOT", "grid", f"How much higher or lower was the average hourly day-ahead price at ERCOT's West hub than at its North hub {WEEK_WORDS} (Central time), in USD per MWh?", "iso_dam_hub_prices",
      lambda: local_mean("iso_dam_hub_prices", "ercot:HB_WEST", "spp_dam", W, CT) - local_mean("iso_dam_hub_prices", "ercot:HB_NORTH", "spp_dam", W, CT),
      "iso_dam_hub_prices, spp_dam: the mean of the 168 hourly rows of the local week (America/Chicago) at ercot:HB_WEST less the same at ercot:HB_NORTH; a negative key is West lower",
      tables=("iso_trader_daily",))
    f("tx06", "transmission", "ERCOT", "general", "For ERCOT projects that reached operation in 2024, what was the median time from interconnection request to operation, in months?", "interconnection_durations_summary",
      lambda: L.year_value("interconnection_durations_summary", "lbnl_durations:ercot", "median_months", 2024), "interconnection_durations_summary, lbnl_durations:ercot, median_months: the 2024 row (in_live_set review)")
    f("tx07", "transmission", "ERCOT", "general", "In Berkeley Lab's queue data, of the capacity that entered ERCOT's interconnection queue in 2019, how many MW are now operating?",
      "lbnl_interconnection_queue", lambda: lbnl_operating("ERCOT", 2019),
      "lbnl_interconnection_queue (entities): the sum of capacity_mw over the rows with region ERCOT, q_year 2019 and q_status operational. Session 5251 keyed the question, "
      "with no source named, on iso_queue_statistics (5,593.64 MW of 8,443.64 entered, from ERCOT's own file, which lists no withdrawn project); the chat answered from Berkeley "
      "Lab's table (session 5254). The two tables differ, so the question names its source")
    r("tx08", "transmission", "not_live", "CAISO", "general", "How many MW flowed from the Bonneville Power Administration into the California ISO in the hour beginning 18:00 UTC on 10 November 2026?", [NOT_LIVE, "interchange"],
      "eia930_all_interchange (hourly interchange by pair) is a table of the record, not loaded into the live set: the answer says so and states no figure", tables=["eia930_all_interchange"])
    r("tx09", "transmission", "not_live", "none", "general", "In the warehouse's grid network table, what was the latest flow on the link between ERCOT and SPP, in MW?", [NOT_LIVE, "network|link"],
      "grid_network_links is a table of the record, not loaded into the live set: the answer says so and states no figure", tables=["grid_network_links"])
    r("tx10", "transmission", "outside", "none", "general", "How much revenue did ERCOT's congestion revenue right (CRR) auctions raise in 2025?", [NIW, "CRR|congestion revenue"],
      "no table holds congestion revenue right auctions: not in the warehouse, the thing named, no figure")

    # ------------------------------------------------------------------ projects
    f("pj01", "projects", "ERCOT", "general", "How many MW of projects are active in ERCOT's interconnection queue?", "ercot_interconnection_queue",
      lambda: L.queue_mw("ercot_interconnection_queue", "active")[0], "ercot_interconnection_queue (entities): the sum of capacity_mw over the rows with status active")
    f("pj02", "projects", "CAISO", "grid", "How many MW of projects are active in CAISO's interconnection queue?", "caiso_interconnection_queue",
      lambda: L.queue_mw("caiso_interconnection_queue", "active")[0], "caiso_interconnection_queue (entities): the sum of capacity_mw over the rows with status active")
    f("pj03", "projects", "SPP", "general", "How many projects are active in SPP's interconnection queue?", "spp_interconnection_queue",
      lambda: L.queue_mw("spp_interconnection_queue", "active")[1], "spp_interconnection_queue (entities): the count of the rows with status active", count=True)
    f("pj04", "projects", "ERCOT", "general", "How many MW of battery energy storage projects are active in ERCOT's interconnection queue?", "ercot_interconnection_queue",
      lambda: cap_sum([e for e in entity_rows("ercot_interconnection_queue") if e["status"] == "active" and (e.get("extra") or {}).get("fuel_technology") == "Other - Battery Energy Storage"]),
      "ercot_interconnection_queue (entities): the sum of capacity_mw over the rows with status active and fuel_technology 'Other - Battery Energy Storage'")
    f("pj05", "projects", "CAISO", "general", "How many projects in CAISO's interconnection queue have been withdrawn?", "caiso_interconnection_queue",
      lambda: L.queue_mw("caiso_interconnection_queue", "withdrawn")[1], "caiso_interconnection_queue (entities): the count of the rows with status withdrawn", count=True)
    f("pj06", "projects", "none", "general", "Across the United States, what was the median time from interconnection request to operation for projects that reached operation in 2024, in months?", "interconnection_durations_summary",
      lambda: L.year_value("interconnection_durations_summary", "lbnl_durations:us", "median_months", 2024), "interconnection_durations_summary, lbnl_durations:us, median_months: the 2024 row (in_live_set review)")
    f("pj07", "projects", "none", "general", "How many MW of conventional steam coal generators retired in 2025, in the warehouse's table of retired generators?", "eia860m_retired_generators",
      lambda: cap_sum([e for e in entity_rows("eia860m_retired_generators") if (e.get("extra") or {}).get("technology") == "Conventional Steam Coal" and str(e.get("status_date"))[:4] == "2025"]),
      "eia860m_retired_generators (entities): the sum of capacity_mw over the rows with technology 'Conventional Steam Coal' and status_date in 2025")
    r("pj08", "projects", "hold", "ISO-NE", "general", "How many MW of projects are active in ISO New England's interconnection queue?", [L.LICENSE],
      "isone_interconnection_queue is ISO-NE's own and held for a license: the hold's words and no figure", tables=["isone_interconnection_queue"])
    r("pj09", "projects", "pause", "MISO", "general", "How many MW of projects are active in MISO's interconnection queue?", ["paused"],
      "miso_interconnection_queue is MISO's own: MISO is paused while its terms are reviewed: the pause's word and no figure", tables=["miso_interconnection_queue"])
    r("pj10", "projects", "outside", "none", "general", "What does it cost to build a new combined-cycle gas plant, in USD per kW?", [NIW, "cost"],
      "no table holds construction costs of generators: not in the warehouse, the thing named, no figure")

    # ------------------------------------------------------------------ deals
    r("de01", "deals", "hold", "none", "general", "What was the average disclosed price of the solar power purchase agreements signed in 2026, in USD per MWh?", [L.LICENSE],
      "energy_deals is held whole for a license: the hold's words and no figure", tables=["energy_deals"])
    r("de02", "deals", "hold", "none", "general", "Which energy deal announced in October 2026 was the largest by MW, and how many MW was it?", [L.LICENSE],
      "energy_deals is held whole for a license: the hold's words and no figure", tables=["energy_deals"])
    r("de03", "deals", "hold", "none", "general", "How many energy deals were announced in October 2026?", [L.LICENSE],
      "energy_deals is held whole for a license: the hold's words and no figure", tables=["energy_deals"])
    r("de04", "deals", "hold", "none", "general", "What was the total disclosed value of the energy acquisitions announced in 2026, in USD?", [L.LICENSE],
      "energy_deals is held whole for a license: the hold's words and no figure", tables=["energy_deals"])
    r("de05", "deals", "hold", "none", "general", "Who are the buyer and the seller of the largest nuclear power purchase agreement in the deal tracker?", [L.LICENSE],
      "energy_deals is held whole for a license: the hold's words and no figure", tables=["energy_deals"])
    f("de06", "deals", "none", "general", "How many companies does the warehouse's energy companies table list?", "energy_companies",
      lambda: len(entity_rows("energy_companies")), "energy_companies (entities, model-extracted): the count of its rows", count=True)
    r("de07", "deals", "outside", "none", "general", "What was NextEra Energy's share price at the close on 10 November 2026?", [NIW, "share price|share-price|stock|equit|closing price"],
      "no table holds share prices: not in the warehouse, the thing named, no figure")
    r("de08", "deals", "outside", "none", "general", "At what price per MWh did Constellation sell power under its long-term contracts in the second quarter of 2026, per its FERC Electric Quarterly Report?", [NIW, "EQR|Electric Quarterly|contract"],
      "the FERC EQR tables are internal and not in the catalogue a visitor's chat reads: not in the warehouse, the thing named, no figure", tables=["ferc_eqr_contracts"])

    # ------------------------------------------------------------------ policy
    r("po01", "policy", "hold", "none", "general", "How many policy actions does the warehouse's policy table record for October 2026?", [L.LICENSE],
      "policy_actions is held whole for a license (session 5251 found it so; session 5202 had keyed the count): the hold's words and no count", tables=["policy_actions"])
    r("po02", "policy", "hold", "none", "general", "How many FERC actions does the warehouse's policy table record for October 2026?", [L.LICENSE],
      "policy_actions is held whole for a license: the hold's words and no count", tables=["policy_actions"])
    r("po03", "policy", "hold", "none", "general", "What is the rate of Texas's natural gas production tax, as the warehouse records it?", [L.LICENSE],
      "impact_tax_rules is held whole for a license: the hold's words and no rate", tables=["impact_tax_rules"])
    f("po04", "policy", "CAISO", "general", "In the warehouse's Flex Alert model, how many hours of 2022 were under a California Flex Alert?", "flex_alert_effects",
      lambda: L.year_value("flex_alert_effects", "eia930:CISO", "year_hours", 2022), "flex_alert_effects, eia930:CISO, year_hours: the 2022 row (the yearly summary's count of alert hours; the reduction itself is held as a negative figure and is not keyed)",
      count=True, tables=("flex_alert_model",))
    f("po05", "policy", "ERCOT", "general", "How many conservation appeals did ERCOT issue in 2023, in the warehouse's table of ERCOT's grid notices?", "ercot_grid_notices",
      lambda: sum(1 for e in event_rows("ercot_grid_notices") if e["event_type"] == "conservation_appeal" and e["event_date"][:4] == "2023"),
      "ercot_grid_notices (events, in_live_set review): the count of rows with event_type conservation_appeal and event_date in 2023", count=True)
    f("po06", "policy", "none", "general", "How many Stage 3 emergency notices has the California ISO issued since 1998, in the warehouse's table of its grid emergencies?", "caiso_grid_emergencies",
      lambda: sum(1 for e in event_rows("caiso_grid_emergencies") if e["event_type"] == "stage3"),
      "caiso_grid_emergencies (events): the count of rows with event_type stage3 (the table begins in 1998)", count=True, tables=("caiso_reliability_daily",))
    r("po07", "policy", "not_live", "none", "general", "What did a California carbon allowance clear at in the August 2026 auction, in USD per allowance?", [NOT_LIVE, "allowance|auction|carbon"],
      "carb_auction_allowance_prices is a table of the record, not loaded into the live set: the answer says so and states no figure", tables=["carb_auction_allowance_prices"])
    r("po08", "policy", "outside", "none", "general", "What was the clearing price of the RGGI allowance auction in September 2026?", [NIW, "RGGI"],
      "the RGGI table is internal and not in the catalogue a visitor's chat reads: not in the warehouse, RGGI named, no figure", tables=["rggi_auction_allowance_prices"])
    r("po09", "policy", "outside", "none", "general", "What is the value of the federal clean electricity production tax credit (45Y) in 2026, in cents per kWh?", [NIW, "credit|45Y"],
      "no table holds federal tax credit values (the impact tax table holds state severance and property rules): not in the warehouse, the thing named, no figure")
    r("po10", "policy", "outside", "none", "general", "What share of electricity must come from renewables in New York by 2030 under its renewable portfolio standard?", [NIW, "portfolio standard|RPS|standard"],
      "no table holds state renewable portfolio standards: not in the warehouse, the thing named, no figure")

    # ------------------------------------------------------------------ datacenters
    r("dc01", "datacenters", "hold", "none", "general", "How many MW of datacenter capacity does the datacenter tracker list in Virginia?", [L.LICENSE],
      "datacenter_facilities is held whole for a license: the hold's words and no figure", tables=["datacenter_facilities"])
    r("dc02", "datacenters", "hold", "none", "general", "How many datacenter projects has Microsoft announced, in the datacenter tracker?", [L.LICENSE],
      "datacenter_projects is held whole for a license: the hold's words and no figure", tables=["datacenter_projects"])
    f("dc03", "datacenters", "ERCOT", "general", "As of ERCOT's large load report of 19 June 2026, how many MW of large loads were approved to energize?", "ercot_large_load_status",
      lambda: T.one_row("ercot_large_load_status", "ercot:large_load", "approved_to_energize_mw", "2026-06-19"), "ercot_large_load_status, ercot:large_load, approved_to_energize_mw: the 2026-06-19 row (in_live_set review)")
    f("dc04", "datacenters", "ERCOT", "grid", "As of ERCOT's large load report of 19 June 2026, what was the observed simultaneous peak of its large loads, in MW?", "ercot_large_load_status",
      lambda: T.one_row("ercot_large_load_status", "ercot:large_load", "observed_simultaneous_peak_mw", "2026-06-19"), "ercot_large_load_status, ercot:large_load, observed_simultaneous_peak_mw: the 2026-06-19 row")
    f("dc05", "datacenters", "none", "general", "How many of the public large-load statements the warehouse records are at the stage of a signed service agreement?", "large_load_public",
      lambda: sum(1 for e in event_rows("large_load_public") if e["status"] == "4 signed service agreement"), "large_load_public (events, model-extracted): the count of rows with status '4 signed service agreement'", count=True)
    f("dc06", "datacenters", "ERCOT", "general", "In the warehouse's comparison of regions for AI power, what would a flat 1 GW load have paid for a year of power in ERCOT, in USD?", "ai_power_regions",
      lambda: one_value("ai_power_regions", "iso:ercot", "flat_1gw_cost_usd"), "ai_power_regions, iso:ercot, flat_1gw_cost_usd: the one row")
    f("dc07", "datacenters", "none", "general", "What was the datacenter attention index for the United States in the week of 2 November 2026, in percent?", "attention_index_weekly",
      lambda: T.one_row("attention_index_weekly", "attention:datacenters:US", "attention_index", "2026-11-02"), "attention_index_weekly (model-extracted), attention:datacenters:US, attention_index: the row of the week of 2026-11-02")
    f("dc08", "datacenters", "none", "general", "How many stories of opposition to datacenters did the warehouse count for the United States in the week of 2 November 2026?", "friction_index_weekly",
      lambda: T.one_row("friction_index_weekly", "attention:datacenters:US", "opposition_stories", "2026-11-02"), "friction_index_weekly (model-extracted), attention:datacenters:US, opposition_stories: the row of the week of 2026-11-02", count=True)
    f("dc09", "datacenters", "CAISO", "general", "On the datacenter page's measure, what was the load-weighted real-time price at CAISO's SP15 hub in August 2026, in USD per MWh?", "cost_of_power_monthly",
      lambda: L.month_value("cost_of_power_monthly", SP15, "rt_load_weighted", "2026-08"), "cost_of_power_monthly, caiso:TH_SP15_GEN-APND, rt_load_weighted: the 2026-08 row", tables=("cost_of_power_carbon",))
    r("dc10", "datacenters", "outside", "none", "general", "How many AI accelerator chips (GPUs) were shipped to US datacenters in 2025?", [NIW, "GPU|chip|accelerator"],
      "no table holds chip shipments: not in the warehouse, the thing named, no figure")

    # ------------------------------------------------------------------ the days the live set does not hold (session 5251)
    G, GW = GAP_DAY, GAP_WEEK
    S.gap("gp01", "power", "ERCOT", "general", f"What was ERCOT's average hourly demand {GAP_DAY_WORDS} (Central time), in MW?", "eia930_all_demand", "eia930:ERCO", "demand_mw", G, CT, 60,
          [NIW, GAP_DAY_TEXT], "eia930_all_demand, eia930:ERCO, demand_mw: the local day (America/Chicago)")
    S.gap("gp02", "prices", "CAISO", "grid", "What was the average real-time price at CAISO's SP15 hub on 7 November 2026 (Pacific time), over its 15-minute intervals, in USD per MWh?",
          "iso_rtm_hub_prices", SP15, "lmp_rtm_15m_mean", ("2026-11-07", "2026-11-08"), PT, 15, [NIW, "7 November|November 7|2026-11-07|7 Nov"],
          "iso_rtm_hub_prices, caiso:TH_SP15_GEN-APND, lmp_rtm_15m_mean: the local day (America/Los_Angeles)")
    S.gap("gp03", "renewables", "ERCOT", "general", f"How much electricity did wind generate in ERCOT {GAP_DAY_WORDS}, in MWh?", "ercot_wind_solar_hsl_daily", "ercot:system", "wind_generation_mwh",
          G, UTC, 1440, [NIW, GAP_DAY_TEXT], "ercot_wind_solar_hsl_daily, ercot:system, wind_generation_mwh: the daily row")
    S.partial("pt01", "power", "ERCOT", "general", f"What was the highest hourly demand in ERCOT {GAP_WEEK_WORDS} (Central time), in MW?", "eia930_all_demand", "eia930:ERCO", "demand_mw", GW, CT, 60,
              "eia930_all_demand, eia930:ERCO, demand_mw: the local week (America/Chicago)")
    S.partial("pt02", "prices", "ERCOT", "general", f"What was the average hourly day-ahead price at ERCOT's hub average (HB_HUBAVG) {GAP_WEEK_WORDS} (Central time), in USD per MWh?", "iso_dam_hub_prices",
              E_HUB, "spp_dam", GW, CT, 60, "iso_dam_hub_prices, ercot:HB_HUBAVG, spp_dam: the local week (America/Chicago)")
    S.partial("pt03", "nuclear", "none", "general", f"What was the average hourly nuclear generation in the Lower 48 states {GAP_WEEK_WORDS} (UTC), in MW?", "eia930_all_generation", "eia930:US48",
              "net_generation_nuclear_mw", GW, UTC, 60, "eia930_all_generation, eia930:US48, net_generation_nuclear_mw: the UTC week")

    if S.failed:
        raise SystemExit("keys that could not be computed:\n  " + "\n  ".join(S.failed))
    ids = [q["id"] for q in S.qs]
    if len(ids) != len(set(ids)):
        raise SystemExit("an id is used twice")
    return S.qs


_cache = {}


def record(entity, variable):
    """(stamp, value) of the one row of generation_mix_records for a record that is held once."""
    key = ("record", entity, variable)
    if key not in _cache:
        rows = series("generation_mix_records", entity, variable, "2000-01-01", "2100-01-01")
        if len(rows) != 1:
            raise SystemExit(f"generation_mix_records {entity} {variable}: {len(rows)} rows, one expected")
        _cache[key] = rows[0]
    return _cache[key]


def whole_month(table, entity, month, days_variable):
    """True when the table's own count of days says the month's row is whole; the run stops when it is not."""
    held, want = L.month_value(table, entity, days_variable, month), month_steps(month, "days")
    if held != want:
        raise SystemExit(f"{table} {entity} {month}: {days_variable} says {held:g} of {want} days: not a whole month's row")
    return True


def lbnl_operating(region, year):
    """The MW of Berkeley Lab's queue rows of one region and entry year that are operational, checked not empty."""
    rows = [e for e in L.get("entities", table_name="eq.lbnl_interconnection_queue", select="capacity_mw,extra",
                             **{"extra->>region": f"eq.{region}", "extra->>q_status": "eq.operational"})
            if str((e.get("extra") or {}).get("q_year")) in (str(year), f"{year}.0")]
    if not rows:
        raise SystemExit(f"lbnl_interconnection_queue {region} {year} operational: no rows")
    return cap_sum(rows)


def one_value(table, entity, variable):
    rows = series(table, entity, variable, "2000-01-01", "2100-01-01")
    if len(rows) != 1:
        raise SystemExit(f"{table} {entity} {variable}: {len(rows)} rows, one expected")
    return rows[0][1]


def tax_rate(state, product, name):
    """The ways an answer may write a severance tax's rate: the fraction the table holds, or the percent it is."""
    rows = [e for e in L.get("events", table_name="eq.impact_tax_rules", select="event_type,extra")
            if e["event_type"] == "severance_tax" and (e.get("extra") or {}).get("x_state") == state and (e["extra"].get("x_product") == product)
            and (e["extra"].get("x_rule_name") == name)]
    if len(rows) != 1:
        raise SystemExit(f"impact_tax_rules {state} {product} {name!r}: {len(rows)} rows, one expected")
    rate = float(rows[0]["extra"]["x_rate"])
    pct = rate * 100
    return [f"{rate:g}|{pct:g} percent|{pct:g}%|{pct:g} per cent"]


FIELDS = ("expected", "tolerance", "text", "tables", "refuse", "hold", "count", "sector", "kind", "note")


def yaml_text(qs, at):
    n = {k: sum(1 for q in qs if q["kind"] == k) for k in KINDS}
    lines = [
        f"# Energy Research Warehouse (ERW): {len(qs)} questions for the AI chat over the warehouse across the whole platform, sessions 5202 and 5251",
        "# (chains 235 and 238, 13 November 2026): power, prices, gas, oil, nuclear, renewables, storage, transmission, projects, deals, policy and datacenters.",
        f"# {n['figure']} have an answer in the live set (kind figure); {n['hold']} ask of a table or a grid held for a license (hold: the hold's words, no",
        f"# figure); {n['pause']} of MISO's own rows (pause); {n['not_live']} of a table of the record that is not loaded into the live set the chat reads",
        f"# (not_live: the answer says so); {n['outside']} of something no table holds (outside: \"not in the warehouse\", the missing thing named);",
        f"# {n['gap']} of a day a held series lacks (gap: \"not in the warehouse\", the day named); {n['partial']} of a window held in part (partial: the answer",
        "# says the window is not whole, in any of the text entry's words).",
        f"# Every expected number was computed before any model call from the live set (Supabase, the anon key, reads only) on {at[:10]} by",
        "# scripts/ask_eval/platform_questions.py, which writes this file; each note names the table, the entity or filter, the variable and",
        "# the aggregation. tolerance: 0.01 under 1,000, 0.5 from 1,000. A text entry with \"|\" is met by any one of its parts; count: true asks",
        "# the figure apart from a clock time. A refusal key has no figure; hold: true marks a held table, whose answer carries the hold's words.",
        f"today: '{TODAY}'",
        "questions:",
    ]
    for q in qs:
        lines += [f"- id: {q['id']}", f"  sector: {q['sector']}", f"  kind: {q['kind']}", f"  grid: {q['grid']}", f"  via: {q['via']}",
                  f"  question: {json.dumps(q['question'])}", f"  expected: {json.dumps(q['expected'])}", f"  tolerance: {q['tolerance']}",
                  f"  text: {json.dumps(q['text'])}", f"  tables: {json.dumps(q['tables'])}", f"  refuse: {'true' if q['refuse'] else 'false'}",
                  f"  hold: {'true' if q['hold'] else 'false'}", f"  count: {'true' if q['count'] else 'false'}", f"  note: {json.dumps(q['note'])}"]
    text = "\n".join(lines) + "\n"
    if chr(0x2014) in text or chr(0x2013) in text:
        raise SystemExit("a dash in the output")
    return text


def main(argv):
    at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    qs = build()
    if "--check" in argv:
        import yaml
        with open(OUT, encoding="utf-8") as fh:
            stored = {q["id"]: q for q in yaml.safe_load(fh)["questions"]}
        off = [q["id"] for q in qs if q["id"] not in stored or stored[q["id"]]["expected"] != q["expected"] or stored[q["id"]]["question"] != q["question"]
               or stored[q["id"]]["text"] != q["text"]]
        off += [i for i in stored if i not in {q["id"] for q in qs}]
        print("keys on disk differ from today's live set: " + ", ".join(off) if off else "keys on disk are today's live set's")
        return 1 if off else 0
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(yaml_text(qs, at))
    with open(KEYS_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"_about": "Session 5202: the keys of questions_platform.yaml as computed from the live set by scripts/ask_eval/platform_questions.py, not a run.",
                   "computed_at_utc": at, "source": f"{L.base_url().split('//')[1].split('.')[0]} catalogue, series, entities and events views, anon key",
                   "keys": {q["id"]: {k: q[k] for k in FIELDS} for q in qs}}, fh, indent=1)
        fh.write("\n")
    by = {s: sum(1 for q in qs if q["sector"] == s) for s in SECTORS}
    kinds = {k: sum(1 for q in qs if q["kind"] == k) for k in KINDS}
    print(f"wrote {os.path.relpath(OUT, ROOT)} and {os.path.relpath(KEYS_JSON, ROOT)}: {len(qs)} questions, keys computed at {at}")
    print("by sector:", by)
    print("by kind:", kinds)
    for q in qs:
        print(f"  {q['id']} {q['kind']:8} {q['expected'] or q['text']}  {q['note'][:90]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
