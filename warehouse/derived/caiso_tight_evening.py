#!/usr/bin/env python3
"""A day-ahead "tight evening" forecast for CAISO, backtested on past alert days (session 64). Internal only.

Energy Research Warehouse (ERW) derived table, tier internal: not in Supabase's live set, not on the site, not uploaded
to Redivis. It answers one question: had the Flex Alert scorecard's load model (warehouse/derived/flex_alert_scorecard.py,
session 60) been run the day before, how well would its predicted evening peak have told CAISO's tight evenings (the days
of a Flex Alert or a grid emergency notice, caiso_grid_emergencies) from the others?

    warehouse/output/caiso_tight_evening_backtest.csv
    python warehouse/derived/caiso_tight_evening.py

The forecast, per day D of the alert season (May to October):
- The model is the scorecard's: for each local hour, an ordinary least squares fit of CISO demand on the weather terms
  (cooling degree hours, their square, the 24 hours before and its square, the dew point, CDH x dew), Saturday, Sunday,
  holiday, month and year, on non-alert days only (so it predicts what the weather and the calendar call for, before any
  conservation).
- The evening peak is the highest predicted hour from 16:00 to 20:00 Pacific (the scorecard's default alert hours).
- A day is forecast tight when its predicted evening peak is at or above a threshold. The threshold is chosen on the
  training seasons alone: the value of the in-sample predicted peak that maximizes F1 (the harmonic mean of precision
  and recall) for the training seasons' alert days.
- The backtest is season by season, expanding: season Y (2020 to 2025) is forecast by the model fitted on the seasons
  before Y only, with year Y's level taken as year Y-1's (the last year it has seen). 2018 (from July) and 2019 are
  training only.
- Two weather inputs, both stated: "observed" uses day D's own observed weather (a perfect weather forecast: an upper
  bound on what a real forecast could do; no weather forecast is held), and "persistence" uses the weather of the day
  before, hour by hour (what is known without any forecast, by the end of D-1). Each is trained on its own inputs.
Measures per season and pooled: alert days, days forecast tight, hits, misses, false alarms, precision and recall
(percent), the AUC of the predicted peak as a ranking of alert days (the chance an alert day's predicted peak exceeds a
non-alert day's, ties half), and the evening-peak error on non-alert days (mean absolute error, MW).
"""

import datetime as dt
import os
import sys
import traceback

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402
import flex_alert_scorecard as fa  # noqa: E402

NAME = "caiso_tight_evening_backtest"
SOURCE = "erw:tight_evening"
METHOD = "https://github.com/SamuelEnrique/erw/blob/main/warehouse/derived/caiso_tight_evening.py"  # the method: its docstring
ENTITY = "eia930:CISO"
EVENING = (16, 17, 18, 19, 20)
TEST = list(range(2020, 2026))
WX_TERMS = fa.TERMS[1:10]  # cdh ... holiday, as the scorecard's chosen variant


def design(p, years):
    """Intercept, the weather and calendar terms, month indicators (May the base) and year indicators for years[1:]
    (years[0] the base), each row's year taken from its column "yr"."""
    cols = [np.ones(len(p))] + [p[t].to_numpy(float) for t in WX_TERMS]
    cols += [(p["month"].to_numpy() == m).astype(float) for m in fa.MONTHS[1:]]
    cols += [(p["yr"].to_numpy() == y).astype(float) for y in years[1:]]
    return np.column_stack(cols)


def fit(p, days, years):
    sub = p[p["day"].isin(days)]
    return {h: np.linalg.lstsq(design(g, years), g["y"].to_numpy(float), rcond=None)[0] for h, g in sub.groupby("hour")}


def predict(p, betas, years):
    out = np.full(len(p), np.nan)
    X = design(p, years)
    for h, b in betas.items():
        i = (p["hour"] == h).to_numpy()
        out[i] = X[i] @ b
    return out


def evening_peaks(p):
    e = p[p["hour"].isin(EVENING)]
    return e.groupby("day").agg(pred=("pred", "max"), actual=("y", "max"))


def best_threshold(peaks, alert):
    """The predicted peak at or above which a day is called tight, maximizing F1 on these days (the lowest on a tie)."""
    best = (-1.0, None)
    for t in np.unique(peaks):
        flag = peaks >= t
        tp = int((flag & alert).sum())
        fp, fn = int((flag & ~alert).sum()), int((~flag & alert).sum())
        f1 = 2 * tp / (2 * tp + fp + fn) if tp else 0.0
        if f1 > best[0]:
            best = (f1, float(t))
    return best[1], best[0]


def auc(score, alert):
    """P(an alert day's score > a non-alert day's), ties half (the Mann-Whitney statistic)."""
    a, n = score[alert], score[~alert]
    if not len(a) or not len(n):
        return None
    r = pd.Series(np.concatenate([a, n])).rank().to_numpy()
    return float((r[:len(a)].sum() - len(a) * (len(a) + 1) / 2) / (len(a) * len(n)))


def measures(d):
    flag, alert = d["tight"].to_numpy(bool), d["alert"].to_numpy(bool)
    tp, fp, fn = int((flag & alert).sum()), int((flag & ~alert).sum()), int((~flag & alert).sum())
    na = ~alert
    return dict(days=len(d), alert_days=int(alert.sum()), tight_days=int(flag.sum()), hits=tp, misses=fn, false_alarms=fp,
                precision_pct=100 * tp / (tp + fp) if tp + fp else None, recall_pct=100 * tp / (tp + fn) if tp + fn else None,
                auc=auc(d["pred"].to_numpy(float), alert),
                mae_mw=float((d.loc[na, "pred"] - d.loc[na, "actual"]).abs().mean()) if na.any() else None,
                bias_mw=float((d.loc[na, "pred"] - d.loc[na, "actual"]).mean()) if na.any() else None)


def backtest(p, full, alert_set, log):
    """Season by season: the per-day frame (day, pred, actual, alert, tight, season, threshold) and the season measures."""
    p = p[p["day"].isin(full)].copy()
    p["season"] = p["year"]
    days_all, rows, seasons = sorted(full), [], []
    for Y in TEST:
        train_years = sorted(y for y in p["season"].unique() if y < Y)
        tr_days = [d for d in days_all if int(d[:4]) < Y and d not in alert_set]
        tr = p[p["season"] < Y].assign(yr=lambda q: q["year"])
        betas = fit(tr, tr_days, train_years)
        tr = tr.assign(pred=predict(tr, betas, train_years))
        tp = evening_peaks(tr)
        t_alert = tp.index.isin(alert_set)
        thr, f1 = best_threshold(tp["pred"].to_numpy(float), t_alert)
        te = p[p["season"] == Y].assign(yr=Y - 1)  # the test year's level: the last year the model has seen
        te = te.assign(pred=predict(te, betas, train_years))
        ep = evening_peaks(te).dropna()
        ep["alert"] = ep.index.isin(alert_set)
        ep["tight"] = ep["pred"] >= thr
        ep["season"], ep["threshold"] = Y, thr
        rows.append(ep)
        m = measures(ep)
        seasons.append(dict(season=Y, threshold_mw=thr, train_f1=f1, train_days=len(tr_days), **m))
        log(f"  {Y}: threshold {thr:,.0f} MW (training F1 {f1:.3f}); {m['alert_days']} alert days, {m['tight_days']} forecast tight, "
            f"{m['hits']} hits, {m['misses']} misses, {m['false_alarms']} false alarms; AUC {m['auc'] if m['auc'] is None else round(m['auc'], 3)}; "
            f"non-alert evening peak MAE {m['mae_mw']:,.0f} MW")
    d = pd.concat(rows)
    return d, seasons, measures(d)


def main():
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    retrieved = f"{run_id[:4]}-{run_id[4:6]}-{run_id[6:8]}T{run_id[9:11]}:{run_id[11:13]}:{run_id[13:15]}Z"
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"tight_evening_{run_id}.log"))
    status = dict(table=NAME, market="derived", status="ok", detail="")
    try:
        emr = fa.read_table("caiso_grid_emergencies")
        alerts = fa.alert_days(emr)
        alert_set = set(alerts["day"])
        load, dsrc = fa.demand(log)
        wx, wsrc = fa.weather(log)
        # persistence: each hour takes the weather of the same hour the day before
        wx_p = wx.shift(24)
        out, summary = [], {}
        for name, w in (("observed", wx), ("persistence", wx_p)):
            p = fa.panel(load, w)
            full = fa.complete_days(p)
            log(f"{name} weather: {len(full)} complete season days, {len(alert_set & full)} of them alert days")
            d, seasons, pooled = backtest(p, full, alert_set, log)
            summary[name] = (seasons, pooled)
            log(f"  pooled 2020 to 2025: {pooled}")
            base = dict(unit="MW", freq="P1D", geo="US-CA", market="", node="", source=SOURCE, source_url=METHOD,
                        retrieved_at=retrieved, vintage="", entity=ENTITY)
            for day, r in d.iterrows():
                ts = f"{day}T00:00:00Z"
                out += [dict(base, variable=f"pred_evening_peak_mw_{name}", ts_utc=ts, value=round(float(r["pred"]), 4)),
                        dict(base, variable=f"tight_forecast_{name}", ts_utc=ts, value=int(r["tight"]), unit="count")]
                if name == "observed":
                    out += [dict(base, variable="actual_evening_peak_mw", ts_utc=ts, value=round(float(r["actual"]), 4)),
                            dict(base, variable="alert_day", ts_utc=ts, value=int(r["alert"]), unit="count")]
            units = dict(threshold_mw="MW", train_f1="ratio", train_days="count", days="count", alert_days="count",
                         tight_days="count", hits="count", misses="count", false_alarms="count", precision_pct="pct",
                         recall_pct="pct", auc="ratio", mae_mw="MW", bias_mw="MW")
            for s in seasons + [dict(season="2020-2025", **pooled)]:
                ts = f"{s['season']}-05-01T00:00:00Z" if s["season"] != "2020-2025" else "2020-05-01T00:00:00Z"
                freq = "P1Y" if s["season"] != "2020-2025" else "P6Y"
                for k, u in units.items():
                    if k in s and s[k] is not None:
                        v = f"{k}_{name}" + ("_pooled" if s["season"] == "2020-2025" else "")
                        out.append(dict(base, variable=v, ts_utc=ts, value=round(float(s[k]), 4), unit=u, freq=freq))
        df = pd.DataFrame(out)[ip.SERIES_COLS]
        if df.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("two rows share an (entity, variable, ts_utc) key")
        header = [
            "Energy Research Warehouse (ERW): a day-ahead tight-evening forecast for CAISO, backtested on past alert days (derived, session 64)",
            "License: internal. Not in Supabase's live set, not on the site, not uploaded to Redivis.",
            "Shape: series (docs/datastandard.md v0). entity eia930:CISO; P1D rows at the Pacific day (00:00:00Z); P1Y rows per alert "
            "season (ts_utc May 1), P6Y the pooled 2020 to 2025 seasons (variables ending _pooled). Variables end _observed (day D's observed weather, a perfect "
            "weather forecast, an upper bound) or _persistence (the day before's weather, hour by hour).",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/caiso_tight_evening.py",
            f"Run log: warehouse/output/logs/tight_evening_{run_id}.log",
            f"Source: {SOURCE} ERW derived internal table, tight-evening backtest, {METHOD}",
            "Derived from: caiso_grid_emergencies (alert days, as flex_alert_scorecard.alert_days reads them); EIA-930 CISO hourly "
            f"demand, {dsrc}; {wsrc}",
            "Model: warehouse/derived/flex_alert_scorecard.py's per-hour OLS (chosen variant), fitted on non-alert days of the seasons "
            "before the test season; the test season's year level is the last training year's; threshold maximizing F1 on the training "
            "seasons' in-sample evening peaks (16:00 to 20:00 Pacific).",
        ]
        _write(df, header, log)
        ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                report="Tight-evening forecast backtest (warehouse/derived/caiso_tight_evening.py)", report_url=METHOD,
                                document_list="", license="internal", tables=[NAME])])
        status["detail"] = f"{len(df)} rows"
        for name, (seasons, pooled) in summary.items():
            print(f"{name}: pooled {pooled}")
    except Exception:
        tb = traceback.format_exc()
        log(tb)
        status.update(status="failed", detail=tb.strip().splitlines()[-1][:300])
        print(f"{NAME} FAILED: {status['detail']}", file=sys.stderr)
    ip.write_status("tight_evening", run_id, [status])
    log.close()
    return 0 if status["status"] == "ok" else 1


def _write(df, header, log):
    """The table rewritten whole (a derived backtest: every run replaces it)."""
    path = os.path.join(ip.OUT_DIR, NAME + ".csv")
    with open(path + ".tmp", "w", encoding="utf-8", newline="") as f:
        f.writelines("# " + h + "\n" for h in header)
        df.to_csv(f, index=False, lineterminator="\n")
    os.replace(path + ".tmp", path)
    log(f"wrote {path}: {len(df)} rows")


if __name__ == "__main__":
    sys.exit(main())
