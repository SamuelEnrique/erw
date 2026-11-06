#!/usr/bin/env python3
"""Session 3280 (the Ask evaluation chain of 6 November 2026, queue/done/199): twenty questions a power trader asks of Ask
the warehouse, each expected answer computed from the live set by this script, never typed.

Energy Research Warehouse (ERW). No model call of any kind. Reads only: the live set's `catalogue` and `series` views
(Supabase REST, the anon key from the repository's .env, or the main checkout's beside a worktree), 1,000 rows a page,
through lab_questions.py's reader (session 2224). Writes warehouse/chat/eval/questions_trader.yaml (the set, read by
eval_s1113.py and eval_loop.py with --set trader) and warehouse/chat/eval/keys_trader.json (the keys with the time they
were computed).

    python scripts/ask_eval/trader_questions.py            computes the keys and writes both files
    python scripts/ask_eval/trader_questions.py --check    exit 1 when the YAML on disk differs from a fresh computation

The twenty, by what a trader asks (the chain's prompt): the hubs' day-ahead and real-time averages and maxima with their
hour, for a named operating day (3 November 2026) and a named week (Monday 26 October to Sunday 1 November 2026, the week
the clocks went back), each in the grid's own time zone and said so in the question; the spread between two hubs; the
spark spread at a stated heat rate against the nearest gas hub (Henry Hub, the only gas hub the live set holds, through
the price board's spark_spread_7 at 7.0 MMBtu/MWh); the count of real-time intervals above a threshold, and the trader
view's count of hours real time cleared 50 USD/MWh over day-ahead; the node basis where public (ERCOT's, node_basis_summary);
the on-peak day-ahead average; and two grids whose prices the site does not show: NYISO's (held for a license: refused by
name, the hold's words, no figure) and MISO's (paused: the pause's words).

A day or a week is a window of local time: [local midnight of the first day, local midnight after the last) converted to
UTC, as the chat's query reads a bound without an offset in its tz (warehouse/chat/tools.py _select). Each window is
checked whole (one row per hour, four per 15 minutes, no time twice) before a key is written; the run stops otherwise.
An hour key's text is a list of the ways the answer may write the hour, joined by "|" (eval_s1113.py grade_set accepts
any one): the hour beginning in UTC and in local time, 24-hour and 12-hour, and the hour ending.
"""
import datetime as dt
import json
import os
import sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lab_questions as L  # noqa: E402  the reader, the hold and the key shapes of session 2224

ROOT = L.ROOT
EVAL = L.EVAL
OUT = os.path.join(EVAL, "questions_trader.yaml")
KEYS_JSON = os.path.join(EVAL, "keys_trader.json")
TODAY = "2026-11-06"
DA, RT, TD, PS, NB = "iso_dam_hub_prices", "iso_rtm_hub_prices", "iso_trader_daily", "price_board_spreads", "node_basis_summary"
TZ = {"ERCOT": "America/Chicago", "SPP": "America/Chicago", "CAISO": "America/Los_Angeles"}
TZ_WORDS = {"America/Chicago": "Central time", "America/Los_Angeles": "Pacific time"}
DAY = ("2026-11-03", "2026-11-04")          # the operating day 3 November 2026
WEEK = ("2026-10-26", "2026-11-02")         # Monday 26 October to Sunday 1 November 2026
DAY_WORDS, WEEK_WORDS = "on 3 November 2026", "in the week of Monday 26 October to Sunday 1 November 2026"
# the variable of a hub's price, by grid (the ISOs' own names, as the table holds them)
VAR = {("ERCOT", "da"): "spp_dam", ("ERCOT", "rt"): "spp_rtm", ("CAISO", "da"): "lmp_dam", ("CAISO", "rt"): "lmp_rtm_15m_mean",
       ("SPP", "da"): "lmp_dam"}
HUB = {"ERCOT North": "ercot:HB_NORTH", "ERCOT Houston": "ercot:HB_HOUSTON", "ERCOT West": "ercot:HB_WEST", "ERCOT hub average": "ercot:HB_HUBAVG",
       "CAISO SP15": "caiso:TH_SP15_GEN-APND", "CAISO NP15": "caiso:TH_NP15_GEN-APND", "CAISO ZP26": "caiso:TH_ZP26_GEN-APND",
       "SPP North": "spp:SPPNORTH_HUB"}
WORDS = {"ERCOT North": "ERCOT's North hub (HB_NORTH)", "ERCOT Houston": "ERCOT's Houston hub (HB_HOUSTON)", "ERCOT West": "ERCOT's West hub (HB_WEST)",
         "ERCOT hub average": "ERCOT's hub average (HB_HUBAVG)", "CAISO SP15": "CAISO's SP15 hub", "CAISO NP15": "CAISO's NP15 hub",
         "CAISO ZP26": "CAISO's ZP26 hub", "SPP North": "SPP's North hub"}


def window(days, tz):
    """[local midnight of days[0], local midnight of days[1]) in UTC, as two datetimes."""
    z = ZoneInfo(tz)
    a = dt.datetime.fromisoformat(days[0]).replace(tzinfo=z).astimezone(dt.timezone.utc)
    b = dt.datetime.fromisoformat(days[1]).replace(tzinfo=z).astimezone(dt.timezone.utc)
    return a, b


def z(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def rows_in(table, entity, variable, days, tz, step_minutes):
    """The rows of one hub and variable in a local window, checked whole: one row each step, no time twice."""
    a, b = window(days, tz)
    rows = L.get("series", table_name=f"eq.{table}", entity=f"eq.{entity}", variable=f"eq.{variable}", select="ts_utc,value",
                 **{"and": f"(ts_utc.gte.{z(a)},ts_utc.lt.{z(b)})"})
    rows = [(dt.datetime.fromisoformat(r["ts_utc"]), float(r["value"])) for r in rows if r["value"] is not None]
    want = int((b - a).total_seconds() // (step_minutes * 60))
    times = [t for t, _ in rows]
    if len(rows) != want or len(set(times)) != want:
        raise SystemExit(f"{table} {entity} {variable} {days} ({tz}): {len(rows)} rows, {len(set(times))} distinct times, {want} expected")
    return sorted(rows)


def one_row(table, entity, variable, day):
    """The one daily row of a table labelled with its local day at 00:00Z (Decision 11)."""
    rows = L.get("series", table_name=f"eq.{table}", entity=f"eq.{entity}", variable=f"eq.{variable}", select="ts_utc,value",
                 **{"and": f"(ts_utc.gte.{day}T00:00:00Z,ts_utc.lt.{day}T00:00:01Z)"})
    rows = [r for r in rows if r["value"] is not None]
    if len(rows) != 1:
        raise SystemExit(f"{table} {entity} {variable} {day}: {len(rows)} rows, one expected")
    return float(rows[0]["value"])


def days_rows(table, entity, variable, days):
    """The daily rows of [days[0], days[1]), one a day, checked whole."""
    rows = L.get("series", table_name=f"eq.{table}", entity=f"eq.{entity}", variable=f"eq.{variable}", select="ts_utc,value",
                 **{"and": f"(ts_utc.gte.{days[0]}T00:00:00Z,ts_utc.lt.{days[1]}T00:00:00Z)"})
    rows = [r for r in rows if r["value"] is not None]
    want = (dt.date.fromisoformat(days[1]) - dt.date.fromisoformat(days[0])).days
    if len(rows) != want or len({r["ts_utc"] for r in rows}) != want:
        raise SystemExit(f"{table} {entity} {variable} {days}: {len(rows)} daily rows, {want} expected")
    return [float(r["value"]) for r in rows]


def mean(vals):
    return sum(vals) / len(vals)


def hour_texts(t, tz, step_minutes):
    """The ways an answer may write the hour (or the interval) a maximum fell in, joined by "|": its beginning in UTC
    (as the tool returns it) and in local time, 24-hour and 12-hour, and for an hour its hour ending."""
    loc = t.astimezone(ZoneInfo(tz))
    alts = [f"{t:%H:%M} UTC", f"{t:%H:%M}Z", f"T{t:%H:%M}", f"{loc:%H:%M}"]
    h12 = loc.hour % 12 or 12
    for ap in ("a.m.", "am") if loc.hour < 12 else ("p.m.", "pm"):
        alts += [f"{h12}:{loc:%M} {ap}", f"{h12}:{loc:%M}{ap}"]
        if loc.minute == 0:
            alts += [f"{h12} {ap}", f"{h12}{ap}"]
    if step_minutes == 60:
        he = loc.hour + 1
        alts += [f"hour ending {he}", f"HE{he}", f"HE {he}", f"HE{he:02d}", f"hour ending {he:02d}"]
    out = []
    for a in alts:
        if a.lower() not in [x.lower() for x in out]:
            out.append(a)
    return "|".join(out)


def build():
    cat = L.catalogue()
    for t in (DA, RT, TD, PS, NB, "nyiso_dam_zone_prices"):
        if t not in cat or cat[t]["in_live_set"] not in ("yes", "review"):
            raise SystemExit(f"{t} is not in the live set's catalogue as yes or review")
    qs = []

    def grid_of(hub):
        return hub.split()[0]

    def da_mean(qid, hub, days, words):
        g = grid_of(hub)
        tz = TZ[g]
        rows = rows_in(DA, HUB[hub], VAR[(g, "da")], days, tz, 60)
        v = mean([x for _, x in rows])
        a, b = window(days, tz)
        qs.append(L.figure(qid, g, "grid", f"What was the average hourly day-ahead price at {WORDS[hub]} {words} ({TZ_WORDS[tz]}), in USD per MWh?", DA, v,
                           f"{DA}, {HUB[hub]}, {VAR[(g, 'da')]}: the mean of the {len(rows)} hourly rows from {z(a)} to {z(b)} (the local days, {tz}); checked whole"))

    def da_max(qid, hub, days, words):
        g = grid_of(hub)
        tz = TZ[g]
        rows = rows_in(DA, HUB[hub], VAR[(g, "da")], days, tz, 60)
        t, v = max(rows, key=lambda r: (r[1], -r[0].timestamp()))
        a, b = window(days, tz)
        qs.append(L.figure(qid, g, "grid", f"What was the highest hourly day-ahead price at {WORDS[hub]} {words} ({TZ_WORDS[tz]}), in USD per MWh, and in which hour?", DA, v,
                           f"{DA}, {HUB[hub]}, {VAR[(g, 'da')]}: the maximum of the {len(rows)} hourly rows from {z(a)} to {z(b)} ({tz}), the hour beginning {z(t)}",
                           text=[hour_texts(t, tz, 60)]))

    def rt_mean(qid, hub, days, words):
        g = grid_of(hub)
        tz = TZ[g]
        rows = rows_in(RT, HUB[hub], VAR[(g, "rt")], days, tz, 15)
        v = mean([x for _, x in rows])
        a, b = window(days, tz)
        qs.append(L.figure(qid, g, "grid", f"What was the average real-time price at {WORDS[hub]} {words} ({TZ_WORDS[tz]}), over its 15-minute intervals, in USD per MWh?", RT, v,
                           f"{RT}, {HUB[hub]}, {VAR[(g, 'rt')]}: the mean of the {len(rows)} 15-minute rows from {z(a)} to {z(b)} ({tz}); checked whole"))

    def rt_max(qid, hub, days, words):
        g = grid_of(hub)
        tz = TZ[g]
        rows = rows_in(RT, HUB[hub], VAR[(g, "rt")], days, tz, 15)
        t, v = max(rows, key=lambda r: (r[1], -r[0].timestamp()))
        a, b = window(days, tz)
        qs.append(L.figure(qid, g, "grid", f"What was the highest 15-minute real-time price at {WORDS[hub]} {words} ({TZ_WORDS[tz]}), in USD per MWh, and in which interval?", RT, v,
                           f"{RT}, {HUB[hub]}, {VAR[(g, 'rt')]}: the maximum of the {len(rows)} 15-minute rows from {z(a)} to {z(b)} ({tz}), the interval beginning {z(t)}",
                           text=[hour_texts(t, tz, 15)]))

    def da_spread(qid, hub_a, hub_b, days, words):
        g = grid_of(hub_a)
        tz = TZ[g]
        ra = rows_in(DA, HUB[hub_a], VAR[(g, "da")], days, tz, 60)
        rb = rows_in(DA, HUB[hub_b], VAR[(g, "da")], days, tz, 60)
        v = mean([x for _, x in ra]) - mean([x for _, x in rb])
        qs.append(L.figure(qid, g, "grid", f"What was the spread between the average hourly day-ahead prices at {WORDS[hub_a]} and {WORDS[hub_b]} {words} ({TZ_WORDS[tz]}), "
                           f"{hub_a.split(maxsplit=1)[1]} minus {hub_b.split(maxsplit=1)[1]}, in USD per MWh?", DA, v,
                           f"{DA}, {VAR[(g, 'da')]}: the mean of {HUB[hub_a]}'s {len(ra)} hourly rows minus the mean of {HUB[hub_b]}'s {len(rb)}, the local days {days[0]} to {days[1]} ({tz}), end not included"))

    # the operating day and the week: averages and maxima with their hour
    da_mean("tr01", "ERCOT North", DAY, DAY_WORDS)
    da_max("tr02", "ERCOT North", DAY, DAY_WORDS)
    rt_mean("tr03", "ERCOT Houston", DAY, DAY_WORDS)
    rt_max("tr04", "ERCOT West", DAY, DAY_WORDS)
    da_mean("tr05", "CAISO SP15", DAY, DAY_WORDS)
    da_max("tr06", "CAISO SP15", DAY, DAY_WORDS)
    da_mean("tr07", "SPP North", WEEK, WEEK_WORDS)
    rt_mean("tr08", "CAISO ZP26", WEEK, WEEK_WORDS)
    da_max("tr09", "ERCOT hub average", WEEK, WEEK_WORDS)
    rt_max("tr10", "CAISO NP15", WEEK, WEEK_WORDS)
    # a spread between two hubs
    da_spread("tr11", "ERCOT West", "ERCOT North", WEEK, WEEK_WORDS)
    da_spread("tr12", "CAISO SP15", "CAISO NP15", DAY, DAY_WORDS)
    # the spark spread at a stated heat rate against the nearest gas hub: the board's own, 7.0 MMBtu/MWh times Henry Hub
    # (docs/methods/price_board.md); the board's daily rows are labelled with the operating day
    for qid, hub, g, via, day, words in (("tr13", "ERCOT hub average", "ERCOT", "grid", "2026-11-03", "3 November 2026"),
                                         ("tr14", "SPP North", "SPP", "grid", "2026-11-02", "2 November 2026")):
        v = one_row(PS, HUB[hub], "spark_spread_7", day)
        qs.append(L.figure(qid, g, via, f"What was the spark spread at {WORDS[hub]} on {words}, at a heat rate of 7.0 MMBtu per MWh against Henry Hub gas, in USD per MWh?", PS, v,
                           f"{PS}, {HUB[hub]}, spark_spread_7: the {day} row (the day-ahead daily mean minus 7.0 times Henry Hub, the board's own)"))
    # the count of intervals above a threshold: ERCOT West's real-time 15-minute rows over 100 USD/MWh in the week
    tz = TZ["ERCOT"]
    rows = rows_in(RT, HUB["ERCOT West"], VAR[("ERCOT", "rt")], WEEK, tz, 15)
    n = sum(1 for _, x in rows if x > 100)
    a, b = window(WEEK, tz)
    qs.append(L.figure("tr15", "ERCOT", "grid", f"How many 15-minute real-time intervals at {WORDS['ERCOT West']} settled above 100 USD per MWh {WEEK_WORDS} (Central time)?", RT, float(n),
                       f"{RT}, ercot:HB_WEST, spp_rtm: the count of the {len(rows)} 15-minute rows from {z(a)} to {z(b)} whose value is above 100 (strictly)"))
    # the trader view's own count: hours real time cleared day-ahead by more than 50 USD/MWh, summed over the week's days
    vals = days_rows(TD, HUB["ERCOT West"], "hours_rt_over_da_50", WEEK)
    qs.append(L.figure("tr16", "ERCOT", "grid", f"In how many hours did the real-time price at {WORDS['ERCOT West']} exceed the day-ahead price by more than 50 USD per MWh {WEEK_WORDS}?", TD, float(sum(vals)),
                       f"{TD}, ercot:HB_WEST, hours_rt_over_da_50: the sum of the {len(vals)} daily rows labelled {WEEK[0]} to 2026-11-01 (each the operating day's count)"))
    # the node basis where public: ERCOT's settlement points against the hub average (node_basis_summary, in review)
    v = L.month_value(NB, HUB["ERCOT hub average"], "dam_solar_basis_p50", "2026-10")
    qs.append(L.figure("tr17", "ERCOT", "grid", "What was the median day-ahead basis of ERCOT's solar nodes to the hub average in October 2026, in USD per MWh?", NB, v,
                       f"{NB}, ercot:HB_HUBAVG, dam_solar_basis_p50: the 2026-10 row (in_live_set review)"))
    # the on-peak block: the trader view's 5x16 day-ahead mean of the operating day
    v = one_row(TD, HUB["ERCOT North"], "da_onpeak_mean_usd", DAY[0])
    qs.append(L.figure("tr18", "ERCOT", "grid", f"What was the on-peak (5x16) day-ahead average at {WORDS['ERCOT North']} {DAY_WORDS}, in USD per MWh?", TD, v,
                       f"{TD}, ercot:HB_NORTH, da_onpeak_mean_usd: the {DAY[0]} row (hours beginning 06:00 to 21:00 local on a weekday, docs/methods/trader_view.md)"))
    # a held grid: NYISO's prices are held for a license (by grid); asked in NYISO's own chat, the answer names NYISO, carries
    # the hold's words and states no figure
    if not L.held("nyiso_dam_zone_prices", "NYISO"):
        raise SystemExit("nyiso_dam_zone_prices is no longer held for NYISO: tr19 wants a figure key")
    qs.append(L.refusal("tr19", "NYISO", "grid", f"What was the average day-ahead price in NYISO's Zone J (New York City) {DAY_WORDS}, in USD per MWh?", ["NYISO", L.LICENSE],
                        "nyiso_dam_zone_prices is NYISO's own and held for a license (site/data/license_status.json): NYISO named, the hold's words, no figure", hold=True,
                        tables=["nyiso_dam_zone_prices"]))
    qs.append(L.refusal("tr20", "MISO", "grid", f"What was the average day-ahead price at MISO's Indiana hub {DAY_WORDS}, in USD per MWh?", ["paused"],
                        "MISO's own rows: MISO is paused while its terms are reviewed (since 4 October 2026), so the answer is the pause's words and no figure", tables=[DA]))
    # a count key: its figure is not met by a clock time's hour (eval_s1113.py grade_set, session 3282)
    for q in qs:
        q["count"] = q["id"] in ("tr15", "tr16")
    if [q["id"] for q in qs] != [f"tr{i:02d}" for i in range(1, 21)]:
        raise SystemExit("the twenty ids are not tr01 to tr20 in order")
    return qs


def yaml_text(qs, at):
    lines = [
        "# Energy Research Warehouse (ERW): 20 questions for Ask a power trader asks, session 3280 (the Ask evaluation chain of 6 November 2026).",
        "# The hubs' day-ahead and real-time averages and maxima with their hour for the operating day 3 November 2026 and the week of 26 October",
        "# to 1 November 2026 (local time, said in each question), a spread between two hubs, the spark spread at 7.0 MMBtu/MWh against Henry Hub,",
        "# a count of real-time intervals above a threshold, the trader view's hours of real time over day-ahead, ERCOT's node basis, the on-peak",
        "# average, and two grids the site shows no price of (NYISO held for a license, MISO paused). Every expected number was computed before any",
        f"# model call from the live set (Supabase, the catalogue and series views, the anon key, reads only) on {at[:10]} by",
        "# scripts/ask_eval/trader_questions.py, which writes this file; each note names the table, the entity, the variable, the window and the",
        "# aggregation. `via` as in questions_s302.yaml. tolerance: 0.01 under 1,000, 0.5 from 1,000. A text entry with \"|\" is met by any one of",
        "# its parts (the ways an hour may be written); count: true asks the figure apart from a clock time. A refusal key has no figure; hold: true marks a held table, whose answer carries the hold's",
        "# words and no figure.",
        f"today: '{TODAY}'",
        "questions:",
    ]
    for q in qs:
        lines += [f"- id: {q['id']}", f"  grid: {q['grid']}", f"  via: {q['via']}", f"  question: {json.dumps(q['question'])}",
                  f"  expected: {json.dumps(q['expected'])}", f"  tolerance: {q['tolerance']}", f"  text: {json.dumps(q['text'])}",
                  f"  tables: {json.dumps(q['tables'])}", f"  refuse: {'true' if q['refuse'] else 'false'}", f"  hold: {'true' if q['hold'] else 'false'}",
                  f"  count: {'true' if q['count'] else 'false'}", f"  note: {json.dumps(q['note'])}"]
    text = "\n".join(lines) + "\n"
    if chr(0x2014) in text or chr(0x2013) in text:
        raise SystemExit("a dash in the output")
    return text


def main(argv):
    at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    qs = build()
    if "--check" in argv:
        import yaml
        with open(OUT, encoding="utf-8") as f:
            stored = {q["id"]: q for q in yaml.safe_load(f)["questions"]}
        off = [q["id"] for q in qs if q["id"] not in stored or stored[q["id"]]["expected"] != q["expected"] or stored[q["id"]]["question"] != q["question"]]
        print("keys on disk differ from today's live set: " + ", ".join(off) if off else "keys on disk are today's live set's")
        return 1 if off else 0
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(yaml_text(qs, at))
    with open(KEYS_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"_about": "Session 3280: the keys of questions_trader.yaml as computed from the live set by scripts/ask_eval/trader_questions.py, not a run.",
                   "computed_at_utc": at, "source": f"{L.base_url().split('//')[1].split('.')[0]} catalogue and series views, anon key",
                   "keys": {q["id"]: {k: q[k] for k in ("expected", "tolerance", "text", "tables", "refuse", "hold", "count", "note")} for q in qs}}, f, indent=1)
        f.write("\n")
    print(f"wrote {os.path.relpath(OUT, ROOT)} and {os.path.relpath(KEYS_JSON, ROOT)}: {len(qs)} questions, keys computed at {at}")
    for q in qs:
        print(f"  {q['id']} {q['expected'] or q['text']}  {q['note'][:100]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
