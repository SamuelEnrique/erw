#!/usr/bin/env python3
"""ERW, Research (/research, Automated Analysis): the replication a reader can run (session 3701, chain 208).

It reads only the page's public downloads (each finding card's CSV, served under /findings/, and the week's chart file,
served under /analysis-files/<week>/) and this folder's assumptions.json (the cards' default inputs and the rule's
constants), recomputes every figure /research prints (page_figures.json: the cards' callouts and the finding of this
week's chart) and prints each beside the page's figure with the difference and whether it is inside the tolerance (half
of the page's last shown digit). A figure the page prints as "license needed" is printed so here and not computed; a
figure the card prints that its download does not hold is said so.

    python replication/analysis/replicate.py [folder or URL of the CSVs] [folder or URL of the week's chart file]

The defaults are the repository's copies (site/public/findings/ and docs/analysis/<week>/) when they are there, else the
site's (https://erw-flame.vercel.app/findings/ and /analysis-files/<week>/). Exit 0 when every computed figure is
inside its tolerance or a difference page_figures.json or this file names as known, 1 when one is not, 2 when an input
cannot be read. Standard library and pandas only: the regressions' algebra is written out below (Gauss-Jordan on the
small cross-product matrices), so no other package is needed. Method: docs/methods/automated_analysis.md, "Replication".
"""
import io
import json
import math
import os
import sys
import urllib.request

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
LOCAL_CSV = os.path.join(ROOT, "site", "public", "findings")
LOCAL_WEEK = os.path.join(ROOT, "docs", "analysis")
SITE = "https://erw-flame.vercel.app"
UA = {"User-Agent": "ERW replication (github.com/SamuelEnrique/erw)"}


# ---------------------------------------------------------------- reading
def fetch_text(src):
    if src.startswith(("http://", "https://")):
        with urllib.request.urlopen(urllib.request.Request(src, headers=UA), timeout=120) as r:
            return r.read().decode("utf-8")
    with open(src, encoding="utf-8") as f:
        return f.read()


def join(base, name):
    return base.rstrip("/") + "/" + name if base.startswith(("http://", "https://")) else os.path.join(base, name)


def read_csv(base, name):
    """A card's CSV: its '#' header lines dropped, every column read as text, then each numeric column made a number
    (a text that is not a number becomes missing, as Stata's destring, force)."""
    lines = [ln for ln in fetch_text(join(base, name)).splitlines() if not ln.startswith("#")]
    df = pd.read_csv(io.StringIO("\n".join(lines)), dtype=str, keep_default_na=False)
    for c in df.columns:
        num = pd.to_numeric(df[c], errors="coerce")
        if num.notna().sum() == (df[c] != "").sum() and (df[c] != "").any():
            df[c] = num
    return df


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------- the algebra, without numpy
def inverse(a):
    """The inverse of a square matrix (a list of lists), by Gauss-Jordan elimination with partial pivoting."""
    n = len(a)
    m = [list(map(float, row)) + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(a)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[piv][col]) < 1e-300:
            raise ValueError("the cross-product matrix is singular")
        m[col], m[piv] = m[piv], m[col]
        p = m[col][col]
        m[col] = [v / p for v in m[col]]
        for r in range(n):
            if r != col and m[r][col] != 0.0:
                f = m[r][col]
                m[r] = [v - f * w for v, w in zip(m[r], m[col])]
    return [row[n:] for row in m]


def matmul(a, b):
    bt = list(zip(*b))
    return [[sum(x * y for x, y in zip(row, colm)) for colm in bt] for row in a]


def ols(y, X):
    """Least squares of y on the columns of X: the coefficients, the residuals, R2 and (X'X)^-1."""
    y = y.astype(float).reset_index(drop=True)
    X = X.astype(float).reset_index(drop=True)
    bread = inverse(X.T.dot(X).values.tolist())
    xty = X.T.dot(y).tolist()
    beta = [sum(b * v for b, v in zip(row, xty)) for row in bread]
    fitted = X.dot(pd.Series(beta, index=X.columns))
    e = y - fitted
    tot = float(((y - y.mean()) ** 2).sum())
    return {"beta": beta, "e": e, "fitted": fitted, "r2": 1 - float((e ** 2).sum()) / tot, "bread": bread, "n": len(y), "k": X.shape[1], "X": X}


def sandwich_se(f, meat, factor):
    v = matmul(matmul(f["bread"], meat), f["bread"])
    return [math.sqrt(factor * v[i][i]) for i in range(len(v))]


def hc1(y, X):
    """OLS with heteroskedasticity-robust errors, Stata's regress, vce(robust)."""
    f = ols(y, X)
    meat = f["X"].mul(f["e"] ** 2, axis=0).T.dot(f["X"]).values.tolist()
    f["se"] = sandwich_se(f, meat, f["n"] / (f["n"] - f["k"]))
    return f


def newey(y, X):
    """OLS with Newey-West errors, Stata's newey, lag(L): L = floor(4 (n / 100) ^ (2 / 9)), Bartlett weights."""
    f = ols(y, X)
    n = f["n"]
    lags = int(math.floor(4 * (n / 100.0) ** (2.0 / 9.0)))
    Z = f["X"].mul(f["e"], axis=0)
    S = Z.T.dot(Z)
    for j in range(1, min(lags, n - 1) + 1):
        G = Z.iloc[j:].reset_index(drop=True).T.dot(Z.iloc[:-j].reset_index(drop=True))
        S = S + (1.0 - j / (lags + 1.0)) * (G + G.T)
    f["se"] = sandwich_se(f, S.values.tolist(), n / (n - f["k"]))
    f["lags"] = lags
    return f


def dummies(values, levels, prefix):
    return pd.DataFrame({f"{prefix}{lv}": (values == lv).astype(float) for lv in levels})


# ---------------------------------------------------------------- the cards' figures, from their downloads
def batteries_lunch_grids(df, a):
    """Each grid's worst-interval multiple in its first and last full year (ERCOT: its first year and the last before
    the newest, as the first card read it), and its battery fleet in the newest month that holds one."""
    n = {}
    for grid in ("ercot", "caiso", "nyiso", "isone", "spp"):
        g = df[df["grid"] == grid]
        years = g[g["kind"] == "year"].set_index("period")
        ys = sorted(years.index)
        if not ys:
            continue
        if grid == "ercot":
            first, last = ys[0], max(y for y in ys if y < ys[-1])
        else:
            full = [y for y in ys if str(years.loc[y, "full_year"]) == "True"]
            first, last = (full[0], full[-1]) if full else (None, None)
        n[f"{grid}_multiple_first"] = float(years.loc[first, "worst_interval_multiple"]) if first else None
        n[f"{grid}_multiple_last"] = float(years.loc[last, "worst_interval_multiple"]) if last else None
        months = g[(g["kind"] == "month")].sort_values("period")
        fl = months[months["battery_mw"].notna() & (months["battery_mw"].astype(str) != "")]
        n[f"{grid}_fleet_last_mw"] = float(fl["battery_mw"].iloc[-1]) if len(fl) else None
    return n


def batteries_curtailment(df, a):
    """Daily curtailment (MWh) on charging (GWh), alone and with solar (GWh) and the month fixed; HC1 errors. The days
    at or below the median charging against those above it."""
    y = df["curtailed_mwh"]
    one = pd.Series(1.0, index=df.index, name="const")
    ch, so = (df["charging_mwh"] / 1000.0).rename("charging"), (df["solar_mwh"] / 1000.0).rename("solar")
    months = sorted(df["month"].unique())
    md = dummies(df["month"], months[1:], "m_").set_index(df.index)
    f1 = hc1(y, pd.concat([one, ch], axis=1))
    f3 = hc1(y, pd.concat([one, ch, so, md], axis=1))
    med = float(df["charging_mwh"].median())
    low, high = df["charging_mwh"] <= med, df["charging_mwh"] > med
    return {"curtailed_low_charging_days": float(y[low].mean()), "curtailed_high_charging_days": float(y[high].mean()),
            "charging_coef": f1["beta"][1], "charging_solar_month_coef": f3["beta"][1], "charging_solar_month_se": f3["se"][1],
            "charging_solar_month_r2": f3["r2"]}


def batteries_curtailment_hourly(df, a):
    """Hourly curtailment against charging; what net load alone (with the hour and the month fixed) predicts in the
    charging hours of each year; and the hours at the charging ceiling with curtailment on."""
    pct = float(a["batteries_curtailment_hourly_ceiling_pct"]["value"])
    on_mw = float(a["batteries_curtailment_hourly_curtailed_on_mw"]["value"])
    df = df.reset_index(drop=True)
    y, ch = df["curtailed_mw"].astype(float), df["charging_mw"].astype(float)
    nl = (df["net_load_mw"] / 1000.0).rename("net_load_gw")
    month = df["day"].str[:7]
    months = sorted(month.unique())
    X = pd.concat([pd.Series(1.0, index=df.index, name="const"), nl, (nl ** 2).rename("net_load_gw2"),
                   dummies(df["hour"], range(1, 24), "h"), dummies(month, months[1:], "m_")], axis=1)
    pred = ols(y, X)["fitted"]
    r = float(y.corr(ch))
    is_ch = ch > 0
    on = y >= on_mw
    trail = df["trail_max_charging_mw"]
    at_trail = is_ch & trail.notna() & (ch >= pct / 100.0 * trail.fillna(float("inf")))
    year = df["day"].str[:4]
    n = {"corr_curtailed_charging": r, "charging_r2": r * r}
    for yr in sorted(year.unique()):
        sel = year == yr
        c = sel & is_ch
        n[f"y{yr}_obs_charging_mw"] = float(y[c].mean()) if c.any() else None
        n[f"y{yr}_pred_charging_mw"] = float(pred[c].mean()) if c.any() else None
        n[f"y{yr}_sat_curt_hours"] = int((sel & at_trail & on).sum())
    return n


def gas_sets_price(df, a):
    """The share of each grid's hours priced below gas's fuel cost at a 7.0 heat rate (and 6.5 and 8.0 for ERCOT), in
    the first year and the last full year."""
    years = sorted(df["year"].astype(int).unique())
    first, last = years[0], max(y for y in years if y < years[-1])
    at = df.assign(year=df["year"].astype(int)).set_index(["grid", "year"])
    k = "share_below_hr7"
    n = {}
    for grid in ("ercot", "isone"):
        n[f"{grid}_first"], n[f"{grid}_last"] = float(at.loc[(grid, first), k]), float(at.loc[(grid, last), k])
    n["ercot_last_hr6p5"], n["ercot_last_hr8"] = float(at.loc[("ercot", last), "share_below_hr6p5"]), float(at.loc[("ercot", last), "share_below_hr8"])
    return n


def impact_study(df, a):
    """The mean of the series and the control in the days before and from the event, the difference in differences,
    and the Newey-West error of the regression of the daily difference on the after dummy."""
    win = df[(df["in_window"] == 1) & df["diff"].notna()]
    pre, post = win[win["after"] == 0], win[win["after"] == 1]
    n = {"series_pre": float(pre["series_value"].mean()), "series_post": float(post["series_value"].mean()),
         "control_pre": float(pre["control_value"].mean()), "control_post": float(post["control_value"].mean())}
    n["did"] = (n["series_post"] - n["series_pre"]) - (n["control_post"] - n["control_pre"])
    X = pd.DataFrame({"const": 1.0, "after": win["after"].astype(float)})
    f = newey(win["diff"], X)
    n["reg_did_se"] = f["se"][1]
    return n


def negative_prices_west(df, a):
    years = sorted(df["year"].astype(int).unique())
    first, this = years[0], years[-1]
    last = max(y for y in years if y < this)
    at = df.assign(year=df["year"].astype(int)).set_index(["hub", "year"])
    n = {}
    for hub in ("ercot_west", "ercot_houston"):
        for tag, yr in (("first", first), ("last", last)):
            n[f"{hub}_{tag}"] = float(at.loc[(hub, yr), "negative_hours"])
            n[f"{hub}_{tag}_share"] = float(at.loc[(hub, yr), "share_pct"])
    return n


def peak_hour_grids(df, a):
    """Each grid's share of days peaking 17:00 to 21:59 in its first year held and its last full year held, and its
    solar fleet at the end of that last year (the rows of hour 0 hold each year's figures)."""
    df = df.assign(year=df["year"].astype(int), hour=df["hour"].astype(int))
    this = int(df["year"].max())
    h0 = df[df["hour"] == 0].set_index(["grid", "year"])
    n = {}
    for grid in df["grid"].unique():
        held = sorted(y for (g, y), r in h0.iterrows() if g == grid and pd.notna(r["n_days"]) and r["n_days"] != 0)
        if not held:
            continue
        first, last = held[0], max((y for y in held if y < this), default=None)
        n[f"{grid}_first_evening_pct"] = float(h0.loc[(grid, first), "share_evening_pct"])
        if last is not None:
            n[f"{grid}_last_evening_pct"] = float(h0.loc[(grid, last), "share_evening_pct"])
            n[f"{grid}_last_solar_mw"] = float(h0.loc[(grid, last), "solar_mw_yearend"])
    return n


def queue_divorce(df, a):
    allr = df[df["technology"] == "All technologies"].iloc[0]
    rest = df[df["technology"] != "All technologies"]
    return {"withdrawn_pct": float(allr["withdrawn_pct"]), "requested_gw": float(allr["requested_gw"]), "operational_pct": float(allr["operational_pct"]),
            "worst_withdrawn_pct": float(rest["withdrawn_pct"].max()), "best_withdrawn_pct": float(rest["withdrawn_pct"].min()),
            "cdc_divorce_rate": float(allr["cdc_divorce_rate_per_1000"]), "cdc_marriage_rate": float(allr["cdc_marriage_rate_per_1000"]),
            "cdc_ratio_pct": float(allr["cdc_divorce_rate_per_1000"]) / float(allr["cdc_marriage_rate_per_1000"]) * 100.0}


def who_rescues_whom(df, a):
    to_exp, to_imp = df[df["flip"] == "import_to_export"], df[df["flip"] == "export_to_import"]
    grid = df[df["event_grid"] == 1].iloc[0]
    big = to_exp.loc[to_exp["event_net_mwh_day"].idxmax()] if len(to_exp) else None
    return {"n_to_export": len(to_exp), "n_to_import": len(to_imp), "grid_baseline_abs": abs(float(grid["baseline_net_mwh_day"])),
            "grid_event_abs": abs(float(grid["event_net_mwh_day"])),
            "big_exp_baseline_abs": abs(float(big["baseline_net_mwh_day"])) if big is not None else None,
            "big_exp_event_abs": abs(float(big["event_net_mwh_day"])) if big is not None else None}


def siting_battery_swing(df, a):
    """ERCOT's storage nodes holding at least 90 percent of the days, by their mean day-ahead intraday swing."""
    s = df[df["days"] >= float(a["siting_battery_swing_min_days"]["value"])].sort_values(["swing_mean_usd_mwh", "node"]).reset_index(drop=True)
    k = len(s)
    med = float(s["swing_mean_usd_mwh"].iloc[(k - 1) // 2]) if k % 2 else float((s["swing_mean_usd_mwh"].iloc[k // 2 - 1] + s["swing_mean_usd_mwh"].iloc[k // 2]) / 2)
    return {"narrowest": float(s["swing_mean_usd_mwh"].iloc[0]), "widest": float(s["swing_mean_usd_mwh"].iloc[-1]), "median": med, "nodes": k,
            "widest_p10": float(s["swing_p10_usd_mwh"].iloc[-1]), "widest_p90": float(s["swing_p90_usd_mwh"].iloc[-1])}


def siting_flexible(df, a):
    """A 1 GW load at each ERCOT row, flat against flexible: the saving all-in (flat less flexible), the hours given
    up, and both all-in figures at the hub average."""
    d = df.assign(saved=df["allin_flat_usd_mwh"] - df["allin_flexible_usd_mwh"])
    by_saved = d.sort_values(["saved", "row"]).reset_index(drop=True)
    by_lost = d.sort_values(["hours_given_up", "row"]).reset_index(drop=True)
    hub = d[d["row"] == a["siting_flexible_hub_row"]["value"]].iloc[0]
    return {"saved_least": float(by_saved["saved"].iloc[0]), "saved_most": float(by_saved["saved"].iloc[-1]),
            "lost_fewest": float(by_lost["hours_given_up"].iloc[0]), "lost_most": float(by_lost["hours_given_up"].iloc[-1]),
            "hub_flat": float(hub["allin_flat_usd_mwh"]), "hub_flex": float(hub["allin_flexible_usd_mwh"])}


def siting_gigawatt(df, a):
    """A 1 GW datacenter load at every row holding each cost part: all-in is energy, transmission and capacity, and a
    year is all-in times the MWh of a year at 0.90 of 1,000 MW in each of 8,760 hours."""
    d = df.assign(allin=df["energy_usd_mwh"] + df["transmission_usd_mwh"] + df["capacity_usd_mwh"]).sort_values(["allin", "row"]).reset_index(drop=True)
    year_mwh = float(a["siting_gigawatt_mw"]["value"]) * float(a["siting_gigawatt_load_factor"]["value"]) * float(a["siting_gigawatt_hours"]["value"])
    return {"least_allin": float(d["allin"].iloc[0]), "most_allin": float(d["allin"].iloc[-1]),
            "least_year_usd": float(d["allin"].iloc[0]) * year_mwh, "most_year_usd": float(d["allin"].iloc[-1]) * year_mwh}


def chart_of_the_week(chart, a):
    """The rule's figures from the chart the page draws: the newest period's value, the one before, the change, and the
    share of the earlier changes the file holds whose size was smaller."""
    vals = [float(v) for v in chart["chart"]["series"][0]["values"]]
    delta = vals[-1] - vals[-2]
    earlier = [vals[i] - vals[i - 1] for i in range(1, len(vals) - 1)]
    smaller = sum(1 for e in earlier if round(abs(e), 6) < round(abs(delta), 6))
    return {"value": vals[-1], "previous": vals[-2], "delta": delta, "score": 100.0 * smaller / len(earlier) if earlier else None,
            "_earlier_held": len(earlier)}


CARDS = {"batteries_lunch_grids": batteries_lunch_grids, "batteries_curtailment": batteries_curtailment,
         "batteries_curtailment_hourly": batteries_curtailment_hourly, "gas_sets_price": gas_sets_price, "impact_study": impact_study,
         "negative_prices_west": negative_prices_west, "peak_hour_grids": peak_hour_grids, "queue_divorce": queue_divorce,
         "who_rescues_whom": who_rescues_whom, "siting_battery_swing": siting_battery_swing, "siting_flexible": siting_flexible,
         "siting_gigawatt": siting_gigawatt}


# ---------------------------------------------------------------- the run
def compute(csv_base, week_base, page, assumptions):
    """{card: {field: value}}, every card's figures from its download; the week's from its chart file."""
    out = {}
    for card in dict.fromkeys(f["card"] for f in page["figures"]):
        if card == "chart_of_the_week":
            src = join(join(week_base, page["week"]), "chart_of_the_week.json")
            out[card] = chart_of_the_week(json.loads(fetch_text(src)), assumptions)
        else:
            name = next(f["download"] for f in page["figures"] if f["card"] == card)
            out[card] = CARDS[card](read_csv(csv_base, name), assumptions)
    return out


def compare(numbers, page):
    """[(figure, status, replicated, difference)] for every figure of page_figures.json. status: "yes" inside the
    tolerance; "license needed"; "not in the download: ..."; "no: a known difference ..."; "NO"."""
    rows = []
    for f in page["figures"]:
        if f["held"]:
            rows.append((f, "license needed", None, None))
            continue
        if f["not_in_download"]:
            rows.append((f, f"not in the download: {f['not_in_download']}", None, None))
            continue
        got = numbers.get(f["card"], {}).get(f["field"])
        if got is None:
            rows.append((f, "NO: not computed", None, None))
            continue
        shown = float(got) if f["decimals"] or f["page"] >= 0 else float(got)
        diff = round(shown, 10) - f["page"]
        if abs(diff) <= f["tolerance"] + 1e-9:
            rows.append((f, "yes", shown, diff))
        elif f["field"] == "score" and numbers[f["card"]].get("_earlier_held", 0) < f.get("earlier_changes", 0):
            held = numbers[f["card"]]["_earlier_held"]
            rows.append((f, f"no: a known difference (the file holds {held} of the {f['earlier_changes']} earlier changes the rule ranked it among)", shown, diff))
        else:
            rows.append((f, "NO", shown, diff))
    return rows


def default_bases():
    csv_base = LOCAL_CSV if os.path.isdir(LOCAL_CSV) else SITE + "/findings"
    week_base = LOCAL_WEEK if os.path.isdir(LOCAL_WEEK) else SITE + "/analysis-files"
    return csv_base, week_base


def main(argv):
    csv_base, week_base = default_bases()
    if len(argv) > 1:
        csv_base = argv[1]
    if len(argv) > 2:
        week_base = argv[2]
    try:
        assumptions = load_json(os.path.join(HERE, "assumptions.json"))
        page = load_json(os.path.join(HERE, "page_figures.json"))
        numbers = compute(csv_base, week_base, page, assumptions)
    except (OSError, ValueError, KeyError, IndexError) as exc:
        print(f"the inputs could not be read: {type(exc).__name__}: {exc}")
        return 2
    rows = compare(numbers, page)
    print(f"Research (/research), its figures from the downloads: the cards' CSVs from {csv_base}, the chart of {page['week']} from {week_base}")
    print("figure | key | replication | the page | difference | inside the tolerance")
    for f, status, got, diff in rows:
        g = "" if got is None else f"{got:,.{max(f['decimals'], 2) + 2}f}"
        d = "" if diff is None else f"{diff:+.{max(f['decimals'], 2) + 2}f}"
        print(f"{f['card']}: {f['name']} | {f['key']} | {g} | {f['page_text']} | {d} | {status}")
    n_yes = sum(1 for r in rows if r[1] == "yes")
    n_held = sum(1 for r in rows if r[1] == "license needed")
    n_out = sum(1 for r in rows if r[1].startswith("not in the download"))
    n_known = sum(1 for r in rows if r[1].startswith("no: a known"))
    bad = [r for r in rows if r[1].startswith("NO")]
    print(f"{n_yes} of {len(rows) - n_held - n_out} computed figures inside the tolerance, {n_known} a known difference; "
          f"{n_held} license needed; {n_out} not in a download; not replicated here: {page['not_replicated']}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
