#!/usr/bin/env python3
"""Session 6191 (chain 283): a held-out set for the AI chat over the warehouse, written after the fixes of chains 280 to
282 and asked once before anything is changed for it.

Energy Research Warehouse (ERW). No model call. Reads only: the live set with a visitor's key, through the readers and
the checks of platform_questions.py (its Set class: a figure key only for a table of the live set, a window checked
whole, a hold only for a held table, a gap only where no step is held, a partial only where some are). Writes
warehouse/chat/eval/questions_heldout.yaml and keys_heldout.json.

    python scripts/ask_eval/heldout_questions.py            computes the keys and writes both files
    python scripts/ask_eval/heldout_questions.py --check    exit 1 when the YAML on disk differs from a fresh computation

Why: every fix of 14 November 2026 was measured on questions the chat had already been asked, or on a slice held out
within the same sets. A fix can fit the questions it was measured on. These questions ask the same kinds of thing of
other hubs, other days, other months and other tables. None was ever asked. A question that cannot be keyed today (its
window is not whole, its table is not live) is left out and named in what the script prints; it is not replaced by an
easier one after the asking.

The day is Wednesday 11 November 2026, the second day Thursday 12 November, the week Monday 12 to Sunday 18 October
2026, each in the grid's own time zone and said so in the question.
"""
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lab_questions as L  # noqa: E402
import platform_questions as P  # noqa: E402

ROOT, EVAL = L.ROOT, L.EVAL
OUT = os.path.join(EVAL, "questions_heldout.yaml")
KEYS_JSON = os.path.join(EVAL, "keys_heldout.json")
TODAY = "2026-11-14"
D1, D2 = ("2026-11-11", "2026-11-12"), ("2026-11-12", "2026-11-13")
D1_WORDS, D2_WORDS = "on 11 November 2026", "on 12 November 2026"
WK = ("2026-10-12", "2026-10-19")
WK_WORDS = "in the week of Monday 12 to Sunday 18 October 2026"
GAP = ("2026-11-06", "2026-11-07")
PART = ("2026-11-02", "2026-11-09")
CT, PT, ET, UTC = P.CT, P.PT, P.ET, P.UTC
NIW, NOT_LIVE = P.NIW, P.NOT_LIVE
DAM, RTM, DEMAND = "iso_dam_hub_prices", "iso_rtm_hub_prices", "eia930_all_demand"


def day_row(table, entity, variable, day):
    """The one row of a daily table on a day (labelled with its date at 00:00Z)."""
    nxt = (dt.date.fromisoformat(day) + dt.timedelta(days=1)).isoformat()
    rows = P.series(table, entity, variable, f"{day}T00:00:00Z", f"{nxt}T00:00:00Z")
    if len(rows) != 1:
        raise SystemExit(f"{table} {entity} {variable} {day}: {len(rows)} rows, one expected")
    return rows[0][1]


def whole(table, entity, variable, days, tz, step=60):
    held, want = P.steps(table, entity, variable, days, tz, step)
    if held != want or not want:
        raise SystemExit(f"{table} {entity} {variable} {days} ({tz}): {held} of {want} steps held: the window is not whole")
    return True


def mean_of(table, entity, variable, days, tz, step=60):
    whole(table, entity, variable, days, tz, step)
    return P.local_mean(table, entity, variable, days, tz, step)


def max_of(table, entity, variable, days, tz, step=60):
    whole(table, entity, variable, days, tz, step)
    return P.local_max(table, entity, variable, days, tz, step)


def build():
    S = P.Set()
    f, r = S.figure, S.refusal

    # ------------------------------------------------------------------ power
    f("h01", "power", "SPP", "general", f"What was SPP's average hourly demand {D1_WORDS} (Central time), in MW?", DEMAND,
      lambda: mean_of(DEMAND, "eia930:SWPP", "demand_mw", D1, CT), "eia930_all_demand, eia930:SWPP, demand_mw: the mean of the 24 hourly rows of the local day (America/Chicago); checked whole")
    f("h02", "power", "CAISO", "general", f"What was the highest hourly demand in CAISO {D2_WORDS} (Pacific time), in MW?", DEMAND,
      lambda: max_of(DEMAND, "eia930:CISO", "demand_mw", D2, PT), "eia930_all_demand, eia930:CISO, demand_mw: the maximum of the 24 hourly rows of the local day (America/Los_Angeles); checked whole")
    f("h03", "power", "ERCOT", "general", f"What was ERCOT's highest hourly demand {WK_WORDS} (Central time), in MW?", DEMAND,
      lambda: max_of(DEMAND, "eia930:ERCO", "demand_mw", WK, CT), "eia930_all_demand, eia930:ERCO, demand_mw: the maximum of the 168 hourly rows of the local week (America/Chicago); checked whole")
    f("h04", "power", "none", "general", "How much electricity was sold to commercial customers in Florida in May 2026, in MWh?", "eia_retail_sales_monthly",
      lambda: L.month_value("eia_retail_sales_monthly", "eia:retail_sales:FL:COM", "retail_sales", "2026-05"), "eia_retail_sales_monthly, eia:retail_sales:FL:COM, retail_sales: the 2026-05 row")
    f("h05", "power", "PJM", "general", "By how much had PJM's average demand in 2025 grown since 2019, in percent?", "eia930_demand_growth",
      lambda: L.year_value("eia930_demand_growth", "eia930:PJM", "avg_demand_growth_since_2019_pct", 2025), "eia930_demand_growth, eia930:PJM, avg_demand_growth_since_2019_pct: the 2025 row")
    f("h06", "power", "ERCOT", "general", "What was the carbon intensity of ERCOT's generation in August 2026, in kg of CO2 per MWh?", "carbon_intensity_monthly",
      lambda: L.month_value("carbon_intensity_monthly", "eia930:ERCO", "intensity_generation", "2026-08"), "carbon_intensity_monthly, eia930:ERCO, intensity_generation: the 2026-08 row")
    f("h07", "power", "PJM", "general", "What was PJM's peak demand in 2025, in MW?", "grid_peak_vs_capacity",
      lambda: L.year_value("grid_peak_vs_capacity", "grid_peak_vs_capacity:pjm", "peak_demand_mw", 2025), "grid_peak_vs_capacity, grid_peak_vs_capacity:pjm, peak_demand_mw: the 2025 row",
      tables=("grid_stress_yearly", "ai_power_regions"))

    # ------------------------------------------------------------------ prices
    f("h08", "prices", "ERCOT", "general", f"What was the average hourly day-ahead price at ERCOT's South hub (HB_SOUTH) {D1_WORDS} (Central time), in USD per MWh?", DAM,
      lambda: mean_of(DAM, "ercot:HB_SOUTH", "spp_dam", D1, CT), "iso_dam_hub_prices, ercot:HB_SOUTH, spp_dam: the mean of the 24 hourly rows of the local day; checked whole", tables=("iso_trader_daily", "price_board_latest"))
    f("h09", "prices", "CAISO", "general", f"What was the highest hourly day-ahead price at CAISO's NP15 hub {D2_WORDS} (Pacific time), in USD per MWh?", DAM,
      lambda: max_of(DAM, "caiso:TH_NP15_GEN-APND", "lmp_dam", D2, PT), "iso_dam_hub_prices, caiso:TH_NP15_GEN-APND, lmp_dam: the maximum of the 24 hourly rows of the local day; checked whole", tables=("iso_trader_daily",))
    f("h10", "prices", "SPP", "general", f"What was the average hourly day-ahead price at SPP's South hub {WK_WORDS} (Central time), in USD per MWh?", DAM,
      lambda: mean_of(DAM, "spp:SPPSOUTH_HUB", "lmp_dam", WK, CT), "iso_dam_hub_prices, spp:SPPSOUTH_HUB, lmp_dam: the mean of the 168 hourly rows of the local week; checked whole", tables=("iso_trader_daily",))
    f("h11", "prices", "ERCOT", "general", f"What was the average real-time price at ERCOT's Houston hub (HB_HOUSTON) {D1_WORDS} (Central time), over its 15-minute intervals, in USD per MWh?", RTM,
      lambda: mean_of(RTM, "ercot:HB_HOUSTON", "spp_rtm", D1, CT, 15), "iso_rtm_hub_prices, ercot:HB_HOUSTON, spp_rtm: the mean of the 96 fifteen-minute rows of the local day; checked whole", tables=("iso_trader_daily", "price_board_latest"))
    f("h12", "prices", "CAISO", "general", f"What was the highest 15-minute real-time price at CAISO's ZP26 hub {D2_WORDS} (Pacific time), in USD per MWh?", RTM,
      lambda: max_of(RTM, "caiso:TH_ZP26_GEN-APND", "lmp_rtm_15m_mean", D2, PT, 15), "iso_rtm_hub_prices, caiso:TH_ZP26_GEN-APND, lmp_rtm_15m_mean: the maximum of the 96 fifteen-minute rows of the local day; checked whole")
    f("h13", "prices", "SPP", "general", "What was the simple average day-ahead price at SPP's North hub in August 2026, in USD per MWh?", "cost_of_power_monthly",
      lambda: L.month_value("cost_of_power_monthly", "spp:SPPNORTH_HUB", "da_simple_mean", "2026-08"), "cost_of_power_monthly, spp:SPPNORTH_HUB, da_simple_mean: the 2026-08 row")
    f("h14", "prices", "CAISO", "general", "What was the load-weighted real-time price at CAISO's SP15 hub in July 2026, in USD per MWh?", "cost_of_power_monthly",
      lambda: L.month_value("cost_of_power_monthly", "caiso:TH_SP15_GEN-APND", "rt_load_weighted", "2026-07"), "cost_of_power_monthly, caiso:TH_SP15_GEN-APND, rt_load_weighted: the 2026-07 row")

    # ------------------------------------------------------------------ gas
    f("h15", "gas", "none", "general", "What was the Henry Hub natural gas spot price on 4 November 2026, in USD per MMBtu?", "eia_fuel_spot_prices",
      lambda: day_row("eia_fuel_spot_prices", "eia:henry_hub", "spot_price", "2026-11-04"), "eia_fuel_spot_prices, eia:henry_hub, spot_price: the row of 2026-11-04")

    # ------------------------------------------------------------------ storage
    f("h16", "storage", "none", "general", "How many MW of battery storage were planned in the United States as of August 2026?", "storage_buildout_monthly",
      lambda: L.month_value("storage_buildout_monthly", "us:total", "battery_planned_mw", "2026-08"), "storage_buildout_monthly, us:total, battery_planned_mw: the 2026-08 row")
    f("h17", "storage", "none", "general", "How many MW of battery storage were operating in the United States in June 2026?", "storage_buildout_monthly",
      lambda: L.month_value("storage_buildout_monthly", "us:total", "battery_operating_mw", "2026-06"), "storage_buildout_monthly, us:total, battery_operating_mw: the 2026-06 row")

    # ------------------------------------------------------------------ projects, transmission
    f("h18", "projects", "ERCOT", "general", "How many MW are withdrawn in ERCOT's interconnection queue, summed over its withdrawn requests?", "ercot_interconnection_queue",
      lambda: L.queue_mw("ercot_interconnection_queue", "withdrawn")[0], "ercot_interconnection_queue: the sum of capacity_mw over the rows whose status is withdrawn")
    f("h19", "projects", "SPP", "general", "How many MW are withdrawn in SPP's interconnection queue, summed over its withdrawn requests?", "spp_interconnection_queue",
      lambda: L.queue_mw("spp_interconnection_queue", "withdrawn")[0], "spp_interconnection_queue: the sum of capacity_mw over the rows whose status is withdrawn")
    f("h20", "transmission", "ERCOT", "general", "What was the median time from interconnection request to commercial operation for ERCOT projects that reached operation in 2023, in months?", "interconnection_durations_summary",
      lambda: L.year_value("interconnection_durations_summary", "lbnl_durations:ercot", "median_months", 2023), "interconnection_durations_summary, lbnl_durations:ercot, median_months: the 2023 row")
    f("h21", "transmission", "SPP", "general", "How many projects in SPP reached commercial operation in 2024, according to Berkeley Lab's interconnection durations?", "interconnection_durations_summary",
      lambda: L.year_value("interconnection_durations_summary", "lbnl_durations:spp", "projects", 2024), "interconnection_durations_summary, lbnl_durations:spp, projects: the 2024 row", count=True)

    # ------------------------------------------------------------------ datacenters
    f("h22", "datacenters", "none", "general", "How many public large-load statements does the warehouse hold in all?", "large_load_public",
      lambda: len(P.event_rows("large_load_public")), "large_load_public: the count of its rows", count=True)

    # ------------------------------------------------------------------ what must not be answered with a figure of its own
    r("h23", "prices", "hold", "ISO-NE", "general", f"What was the average day-ahead price at ISO New England's Internal Hub {D1_WORDS}, in USD per MWh?", ["license needed"],
      "ISO-NE's rows are held for a license: the hold's words, and no ISO-NE figure (the public grids' figures of the same day may follow)")
    r("h24", "prices", "hold", "NYISO", "general", f"What was the average day-ahead price in NYISO's Zone A (West) {D2_WORDS}, in USD per MWh?", ["license needed"],
      "NYISO's rows are held for a license: the hold's words, and no NYISO figure")
    r("h25", "deals", "hold", "none", "general", "How many energy deals were announced in September 2026?", ["license needed"],
      "energy_deals is held whole for a license: the hold's words and no figure", tables=("energy_deals",))
    r("h26", "policy", "hold", "none", "general", "How many policy actions does the warehouse's policy table record for September 2026?", ["license needed"],
      "policy_actions is held whole for a license: the hold's words and no figure", tables=("policy_actions",))
    r("h27", "prices", "pause", "MISO", "general", f"What was the average day-ahead price at MISO's Minnesota hub {D1_WORDS}, in USD per MWh?", ["paused"],
      "MISO is paused since 4 October 2026: the pause's words and no MISO figure")
    r("h28", "gas", "not_live", "none", "general", "How much LNG did the United States export to South Korea in 2025?", [NOT_LIVE, "LNG"],
      "eia_lng_exports_monthly is a table of the record, not loaded into the live set: the answer says so and states no figure", tables=("eia_lng_exports_monthly",))
    r("h29", "datacenters", "not_live", "none", "general", "How many sites does Equinix operate, according to the warehouse's datacenter operator sites table?", [NOT_LIVE, "operator|site"],
      "datacenter_operator_sites is a table of the record, not loaded into the live set: the answer says so and states no figure", tables=("datacenter_operator_sites",))
    r("h30", "power", "not_live", "none", "general", "What planning reserve margin did CAISO's 2026 summer assessment say was achieved, according to the warehouse's reserve margin reports?", [NOT_LIVE, "reserve"],
      "iso_reserve_margin_reports is a table of the record, not loaded into the live set: the answer says so and states no figure", tables=("iso_reserve_margin_reports",))
    r("h31", "prices", "outside", "ERCOT", "general", "What is the forward price of power at ERCOT's North hub for calendar year 2028, in USD per MWh?", [NIW, "forward|2028|futures"],
      "the warehouse holds what settled, and no forward or futures price of power: not in the warehouse, no figure")
    r("h32", "oil", "outside", "none", "general", "What was the price of lithium carbonate in October 2026, in USD per tonne?", [NIW, "lithium"],
      "no table of the live set holds a metals price: not in the warehouse, the thing named, no figure")
    r("h33", "power", "outside", "ERCOT", "general", "How many people does ERCOT employ?", [NIW],
      "nothing in the warehouse holds a grid operator's headcount: not in the warehouse, no figure")
    r("h34", "storage", "outside", "none", "general", "What did a 4-hour battery earn in ISO New England in August 2026, in USD per kW?", [NIW + "|license needed"],
      "the battery model covers ERCOT and CAISO; ISO-NE is held for a license besides: a refusal, no figure")
    S.gap("h35", "prices", "ERCOT", "general", "What was the average real-time price at ERCOT's North hub (HB_NORTH) on 6 November 2026 (Central time), in USD per MWh?", RTM,
          "ercot:HB_NORTH", "spp_rtm", GAP, CT, 15, [NIW, "6 November|November 6|2026-11-06|6 Nov"], "iso_rtm_hub_prices, ercot:HB_NORTH, spp_rtm, the local day 6 November 2026")
    S.partial("h36", "power", "none", "general", "What was the average hourly electricity demand of the Lower 48 states in the week of Monday 2 to Sunday 8 November 2026 (UTC), in MW?", DEMAND,
              "eia930:US48", "demand_mw", PART, UTC, 60, "eia930_all_demand, eia930:US48, demand_mw, the UTC week of 2 to 8 November 2026")
    S.partial("h37", "prices", "CAISO", "general", "What was the average hourly day-ahead price at CAISO's NP15 hub in the week of Monday 2 to Sunday 8 November 2026 (Pacific time), in USD per MWh?", DAM,
              "caiso:TH_NP15_GEN-APND", "lmp_dam", PART, PT, 60, "iso_dam_hub_prices, caiso:TH_NP15_GEN-APND, lmp_dam, the local week of 2 to 8 November 2026")
    # Three of the figure questions above could not be keyed on 14 November 2026 because their window is held in part (h01,
    # h02, h10: 6 of 24 hours, 16 of 24, 144 of 168). Decided before any asking: each is asked as what it is, a window
    # held in part, under an id of its own; the figure question stays written above and is keyed the day its window is whole
    S.partial("h38", "power", "SPP", "general", f"What was SPP's average hourly demand {D1_WORDS} (Central time), in MW?", DEMAND,
              "eia930:SWPP", "demand_mw", D1, CT, 60, "eia930_all_demand, eia930:SWPP, demand_mw, the local day 11 November 2026")
    S.partial("h39", "power", "CAISO", "general", f"What was the highest hourly demand in CAISO {D2_WORDS} (Pacific time), in MW?", DEMAND,
              "eia930:CISO", "demand_mw", D2, PT, 60, "eia930_all_demand, eia930:CISO, demand_mw, the local day 12 November 2026")
    S.partial("h40", "prices", "SPP", "general", f"What was the average hourly day-ahead price at SPP's South hub {WK_WORDS} (Central time), in USD per MWh?", DAM,
              "spp:SPPSOUTH_HUB", "lmp_dam", WK, CT, 60, "iso_dam_hub_prices, spp:SPPSOUTH_HUB, lmp_dam, the local week of 12 to 18 October 2026")
    return S


FIELDS =("expected", "tolerance", "text", "tables", "refuse", "hold", "count", "sector", "kind", "note")


def yaml_text(qs, at):
    n = {k: sum(1 for q in qs if q["kind"] == k) for k in P.KINDS}
    lines = [
        f"# Energy Research Warehouse (ERW): {len(qs)} held-out questions for the AI chat over the warehouse, session 6191 (chain 283, 14 November 2026):",
        "# written after the fixes of chains 280 to 282, never asked before, asked once before anything is changed for them.",
        "# By kind: " + ", ".join(f"{n[k]} {k}" for k in P.KINDS if n[k]) + ". The kinds and the grading are questions_platform.yaml's.",
        f"# Every expected number was computed before any model call from the live set (Supabase, the anon key, reads only) on {at[:10]} by",
        "# scripts/ask_eval/heldout_questions.py, which writes this file; each note names the table, the entity or filter, the variable and the aggregation.",
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
    S = build()
    qs = S.qs
    for line in S.failed:
        print("not keyed, left out: " + line)
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
        json.dump({"_about": "Session 6191: the keys of questions_heldout.yaml as computed from the live set by scripts/ask_eval/heldout_questions.py, not a run.",
                   "computed_at_utc": at, "not_keyed": S.failed, "keys": {q["id"]: {k: q[k] for k in FIELDS} for q in qs}}, fh, indent=1)
        fh.write("\n")
    print(f"wrote {os.path.relpath(OUT, ROOT)}: {len(qs)} questions keyed, {len(S.failed)} left out")
    print("by kind:", {k: sum(1 for q in qs if q["kind"] == k) for k in P.KINDS})
    for q in qs:
        print(f"  {q['id']} {q['kind']:8} {q['expected'] or q['text']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
