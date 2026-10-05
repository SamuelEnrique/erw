"""Negative-price hours by month."""
import pandas as pd

from common import HISTORY, ISO_LABEL, RT, RT_MARKET, NoData, fetch, r2, render, result  # noqa: F401

NAME = "negative_price_hours"
TITLE = "Negative-price hours by month"
PUBLIC = True
COMPARE = "year"  # session 119: a monthly count with a season in it: compared with the same month a year earlier
ISOS = ["ercot", "caiso", "nyiso", "miso", "spp", "isone"]
PARAMS = {"iso": {"default": "ercot", "choices": ISOS},
          "hub": {"default": {**{i: RT[i][2] for i in ISOS}, "ercot": "HB_WEST"}, "choices": "nodes of the ISO's real-time table"},
          "months": {"default": 24, "choices": [12, 24]}}
TABLES = list(dict.fromkeys(RT[i][0] for i in ISOS)) + [HISTORY]
METHOD = """For one hub, the number of hours in each calendar month (local time) whose real-time price was below zero,
where an hour's price is the mean of the table's intervals in that hour. A month counts only when every hour of it is in
the warehouse, so the rolling 30-day tables give no complete month on most days; for ERCOT the yearly history tables
(ercot_rtm_hub_prices_<year>, 15-minute prices since 2015) are read with the live table when present. The chart shows
the last `months` complete months. The headline is the count in the latest complete month; its history is every earlier
complete month."""


def compute(iso="ercot", hub=None, months=24, history=True):
    table, tz, default = RT[iso]
    hub = hub or (default if iso != "ercot" else "HB_WEST")
    df = fetch(table, node=hub, market=RT_MARKET[iso])
    tables = [table]
    if iso == "ercot":
        import erw
        # session 30: the history's years are partitions of ercot_all_hub_prices_history (market ercot_rtm)
        years = sorted({int(n.rsplit("_", 1)[1]) for n, (t, _) in erw.migrations().items()
                        if t == HISTORY and n.startswith("ercot_rtm_hub_prices_20")})
        if not history:
            years = years[-3:]
        for y in years:
            try:
                df = pd.concat([df, fetch(HISTORY, node=hub, market="ercot_rtm", year=y)], ignore_index=True)
                if HISTORY not in tables:
                    tables.append(HISTORY)
            except Exception:
                pass
        df = df.drop_duplicates(["ts_utc"])
    h = df.assign(hour=df["ts_utc"].dt.floor("h")).groupby("hour")["value"].mean()
    loc = h.index.tz_convert(tz)
    hh = pd.DataFrame({"neg": (h.values < 0).astype(int), "month": loc.strftime("%Y-%m")})
    count = hh.groupby("month")["neg"].sum()
    n = hh.groupby("month").size()
    complete = []
    for m in count.index:
        s = pd.Timestamp(m + "-01").tz_localize(tz)
        e = (pd.Timestamp(m + "-01") + pd.offsets.MonthBegin(1)).tz_localize(tz)
        if n[m] == int((e - s) / pd.Timedelta(hours=1)):
            complete.append(m)
    if not complete:
        raise NoData(f"{table} {hub}: no complete month of hourly prices")
    use = complete[-months:]
    frame = pd.DataFrame({"month": use, "negative_hours": [int(count[m]) for m in use], "hours": [int(n[m]) for m in use],
                          "node": hub, "tables": ", ".join(sorted(set(tables)))})
    hist = [[m, int(count[m])] for m in complete]
    cur = hist[-1]
    label = ISO_LABEL[iso]
    top = max(use, key=lambda m: count[m])
    chart = {"kind": "bar", "x": use, "x_label": "Month (local)", "y_label": "Hours below zero",
             "series": [{"name": f"{hub} negative-price hours", "values": [int(count[m]) for m in use]}]}
    facts = [f"{label} {hub}: {int(count[top])} hours had a negative real-time price in {top}, the most of the months "
             f"{use[0]} to {use[-1]}.", f"Negative-price hours in {cur[0]}: {cur[1]} of {int(n[cur[0]])} hours."]
    return result(NAME, {"iso": iso, "hub": hub, "months": months}, f"{label} {hub}: hours with a negative real-time price",
                  f"Hours per month whose mean real-time price was below zero, {use[0]} to {use[-1]}", frame,
                  sorted(set(tables)), chart,
                  {"label": "negative-price hours in the latest complete month", "value": cur[1], "unit": "hours",
                   "period": cur[0], "history": hist[:-1]}, facts)
