"""Session 252: verify the daily scanner's drafts (rules record, spike, weekly) as they stand in public.scanner_drafts.

A scanner draft carries no file: its data is the warehouse table it names. For each draft kept by fetch_drafts.py:
  1. the series is read again from today's table by the scanner's own reader, cut at the draft's own scan date, and
     its rule is run again; every stored number (value, strength, the threshold, the compared block, the history
     block) is compared exactly with what comes out;
  2. tests the scanner does not run, by rule, on today's table: what the table holds after the flagged point, the
     margin in plain standard deviations, the season (records), other windows (spikes, weekly changes).
No row of the review list is written, and no publisher is asked. Output: runs/session252/verify_scanner.json.
"""
import collections
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.exists(os.path.join(ROOT, "ARCHITECTURE.md")):   # the repository root, from runs/ or from docs/
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
import findings_common as common  # noqa: E402
import findings_scanner as fs  # noqa: E402

DRAFTS = os.path.join(ROOT, "runs", "session252", "drafts")
RULE = {"record": fs.rule_record, "spike": fs.rule_spike, "weekly": fs.rule_weekly, "negative": fs.rule_negative}
D = "datetime64[D]"
_tables = {}


def series_of(table, key_str, cfg):
    if table not in _tables:
        p = os.path.join(common.DEFAULT_IN_DIR, table + ".csv")
        stats = collections.defaultdict(int)
        _tables[table] = {s.key_str: s for s in fs.read_series(table, fs.table_columns(p), common.DEFAULT_IN_DIR, cfg, stats)}
    return _tables[table].get(key_str)


def same(a, b):
    if isinstance(a, float) or isinstance(b, float):
        return a is not None and b is not None and float(a) == float(b)
    return a == b


def compare(stored, fresh, path, problems, counted):
    for k, v in stored.items():
        if isinstance(v, dict):
            compare(v, (fresh or {}).get(k) or {}, f"{path}{k}.", problems, counted)
            continue
        counted[0] += 1
        if not same(v, (fresh or {}).get(k)):
            problems.append(f"{path}{k}: stored {v!r}, recomputed {(fresh or {}).get(k)!r}")


def more_record(s, fl, i):
    v, days = s.v, s.days
    high = fl["direction"] == "high"
    val, old = float(v[i]), fl["compared"]["old_record"]
    prior = v[:i]
    after = v[i + 1:]
    month = days.astype("datetime64[M]").astype(int) % 12
    same_month = prior[month[:i] == month[i]]
    out = {"value_today": val, "points_after": int(len(after)), "after_dates": [str(x) for x in days[i + 1:]], "after_values": [float(x) for x in after],
           "still_the_record_today": bool(val == (v.max() if high else v.min())),
           "pct_past_old_record": (val - old) / abs(old) * 100,
           "margin_plain_sd": abs(val - old) / float(np.std(prior)) if float(np.std(prior)) > 0 else None,
           "same_month_points": int(len(same_month)),
           "same_month_old_record": float(same_month.max() if high else same_month.min()) if len(same_month) else None,
           "record_for_its_month_too": bool(len(same_month) and (val > same_month.max() if high else val < same_month.min())),
           "pct_vs_same_month_last_year": (val - float(same_month[-1])) / abs(float(same_month[-1])) * 100 if len(same_month) else None,
           "previous_point": float(v[i - 1]), "previous_point_date": str(days[i - 1]),
           "pct_vs_previous_point": (val - float(v[i - 1])) / abs(float(v[i - 1])) * 100,
           "previous_point_past_old_record": bool(v[i - 1] > old if high else v[i - 1] < old)}
    # the record without the season: the value against the mean of the 12 points before it, and the same ratio's own history
    if i >= 24:
        ratio = np.array([v[j] / np.mean(v[j - 12:j]) for j in range(12, i + 1) if np.mean(v[j - 12:j]) != 0])
        out["ratio_to_prior_12_mean"] = float(ratio[-1])
        out["ratio_rank_from_top"] = int((ratio > ratio[-1]).sum()) + 1 if high else int((ratio < ratio[-1]).sum()) + 1
        out["ratio_points"] = int(len(ratio))
    return out


def more_spike(s, fl, i, cfg):
    v, days = s.v, s.days
    val = float(v[i])
    out = {"value_today": val, "day_max_interval": float(s.hi[i]), "day_min_interval": float(s.lo[i]), "held_days_before": int(i),
           "history_first_day": str(days[0]), "years_held_before": round(float((days[i] - days[0]).astype(int)) / 365.25, 2)}
    for name, yrs in (("1y", 1), ("3y", 3), ("all", 100)):
        a = days[i] - np.timedelta64(int(round(365.25 * yrs)), "D")
        prior = v[int(np.searchsorted(days, a, side="left")):i]
        p = float(np.percentile(prior, cfg["spike_percentile"]))
        out[f"p99_{name}"], out[f"multiple_{name}"], out[f"points_{name}"] = p, val / p if p else None, int(len(prior))
        out[f"prior_max_{name}"] = float(prior.max())
    out["rank_from_top_all_days"] = int((v > val).sum()) + 1
    out["days_above_line_before"] = int((v[:i] > fl["threshold"]["value"]).sum())
    after = v[i + 1:]
    out["days_after"] = int(len(after))
    out["days_after_above_line"] = int((after > fl["threshold"]["value"]).sum())
    out["days_after_above_value"] = int((after > val).sum())
    out["after_max"] = float(after.max()) if len(after) else None
    out["after_max_date"] = str(days[i + 1 + int(np.argmax(after))]) if len(after) else None
    w = slice(max(0, i - 7), min(len(v), i + 8))
    out["around"] = [[str(d), round(float(x), 4)] for d, x in zip(days[w], v[w])]
    return out


def more_weekly(s, fl, i):
    v, days = s.v, s.days
    c = np.where(np.diff(days[:i + 1]).astype(int) <= 8, np.diff(v[:i + 1]), np.nan)
    now = float(c[-1])
    hist = c[:-1][~np.isnan(c[:-1])]
    high = fl["direction"] == "high"
    out = {"change_today": now, "level": float(v[i]), "level_before": float(v[i - 1]), "pct_change": now / abs(float(v[i - 1])) * 100,
           "all_history_points": int(len(hist)), "all_history_first": str(days[1]),
           "all_history_low": float(hist.min()), "all_history_high": float(hist.max()),
           "outside_all_history": bool(now > hist.max() if high else now < hist.min()),
           "rank_in_all_history": int((hist > now).sum()) + 1 if high else int((hist < now).sum()) + 1,
           "z_plain_sd": (now - float(hist.mean())) / float(hist.std()) if float(hist.std()) > 0 else None}
    after_d, after_v = days[i + 1:], v[i + 1:]
    out["weeks_after"] = int(len(after_v))
    out["after"] = [[str(d), float(x)] for d, x in zip(after_d, after_v)]
    out["change_next_week"] = float(after_v[0] - v[i]) if len(after_v) else None
    out["level_now_vs_before_the_move"] = float(after_v[-1] - v[i - 1]) if len(after_v) else None
    # the percent change against its own history (a change in units grows with the level)
    pc = np.diff(v[:i + 1]) / np.abs(v[:i])
    pc = pc[np.isfinite(pc)]
    out["pct_change_rank"] = int((pc[:-1] > pc[-1]).sum()) + 1 if high else int((pc[:-1] < pc[-1]).sum()) + 1
    out["pct_change_points"] = int(len(pc) - 1)
    return out


def main():
    cfg = fs.load_config()
    index = json.load(open(os.path.join(DRAFTS, "index.json"), encoding="utf-8"))
    results = []
    for x in index:
        if x["rule"] == "hunt":
            continue
        row = json.load(open(os.path.join(DRAFTS, x["id"], "row.json"), encoding="utf-8"))
        fl = row["flag"]
        res = {"id": x["id"], "rule": x["rule"], "state": row["state"], "table": fl["table"], "series_key": fl["series_key"], "label": fl["label"], "unit": fl["unit"],
               "date": fl["date"], "value": fl["value"], "strength": fl["strength"], "direction": fl["direction"], "scan_date": fl["scan_date"],
               "fact": row["card"]["subtitle"], "source": fl["source"], "stored": {"compared": fl["compared"], "history": fl["history"], "threshold": fl["threshold"]},
               "problems": [], "config_changed": []}
        for k, v in fl["threshold"]["config"].items():
            now = cfg[k][fs.grain_of(fl["series"].get("freq"))[0]] if isinstance(cfg.get(k), dict) else cfg.get(k)
            if now != v:
                res["config_changed"].append(f"{k}: {v} when raised, {now} today")
        s = series_of(fl["table"], fl["series_key"], cfg)
        if s is None:
            res["problems"].append("the series is not read from today's table (its key is not there, or a guard leaves it out)")
            results.append(res)
            print(f"{x['id']}: SERIES NOT FOUND")
            continue
        n, f = fs.settled(s, cfg, fl["scan_date"])
        fresh = [g for g in (RULE[fl["rule"]](s, cfg, fl["scan_date"], n, f) if f is not None else []) if g["id"] == fl["id"]]
        counted = [0]
        if not fresh:
            # The table may hold points it did not hold at the scan (a weekly table gains a week). The rule is run again
            # on the series as it stood: cut after the flagged point. Said in the result, not hidden.
            at = np.nonzero(s.days == np.datetime64(fl["date"], "D"))[0]
            if len(at) and int(at[0]) + 1 < n:
                cut = int(at[0]) + 1
                n2, f2 = fs.settled(s, cfg, fl["scan_date"])
                f2 = min(f2, cut - 1) if f2 is not None else None
                fresh = [g for g in (RULE[fl["rule"]](s, cfg, fl["scan_date"], cut, f2) if f2 is not None else []) if g["id"] == fl["id"]]
                if fresh:
                    res["cut_note"] = (f"today's table holds {n - cut} settled point(s) after the flagged one ({', '.join(str(d) for d in s.days[cut:n])}) that it did not hold "
                                       f"at the scan; the rule was run on the series cut after {fl['date']}")
        if not fresh:
            res["problems"].append(f"the rule run again at the scan date {fl['scan_date']} on today's table does not raise this flag")
            # say why: the value at the date today against the stored one
            at = np.nonzero(s.days == np.datetime64(fl["date"], "D"))[0]
            res["value_at_date_today"] = float(s.v[at[0]]) if len(at) else None
        else:
            g = fresh[0]
            for k in ("date", "value", "strength", "direction", "unit", "statistic", "label", "source"):
                counted[0] += 1
                if not same(fl[k], g[k]):
                    res["problems"].append(f"{k}: stored {fl[k]!r}, recomputed {g[k]!r}")
            compare(fl["compared"], g["compared"], "compared.", res["problems"], counted)
            compare(fl["history"], g["history"], "history.", res["problems"], counted)
            compare({"value": fl["threshold"]["value"], "name": fl["threshold"]["name"]}, g["threshold"], "threshold.", res["problems"], counted)
            for k, v in row["card"]["numbers"].items():
                src = {**g["compared"], "value": g["value"], "strength": g["strength"], "threshold": g["threshold"]["value"],
                       "history_years": g["history"]["years"], "history_points": g["history"]["points"]}
                if k in src:
                    counted[0] += 1
                    if not same(v, src[k]):
                        res["problems"].append(f"card.numbers.{k}: stored {v!r}, recomputed {src[k]!r}")
        res["numbers_compared"] = counted[0]
        res["reproduced"] = not res["problems"]
        at = np.nonzero(s.days == np.datetime64(fl["date"], "D"))[0]
        if len(at):
            i = int(at[0])
            res["table_last_point"] = str(s.days[-1])
            res["more"] = (more_record(s, fl, i) if fl["rule"] == "record" else more_spike(s, fl, i, cfg) if fl["rule"] == "spike" else more_weekly(s, fl, i))
        results.append(res)
        print(f"{x['id']}  {fl['rule']} {fl['label']} {fl['date']}: {'EXACT' if res['reproduced'] else 'DIFFERS'} ({counted[0]} values compared)")
        for p in res["problems"]:
            print(f"    PROBLEM: {p}")
        for p in res["config_changed"]:
            print(f"    config: {p}")
        print(f"    more: {json.dumps(res.get('more'), default=str)}")
    with open(os.path.join(ROOT, "runs", "session252", "verify_scanner.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(results, fh, indent=1, ensure_ascii=False, default=str)
        fh.write("\n")
    bad = [r for r in results if r["problems"]]
    print(f"{len(results)} scanner drafts; {len(results) - len(bad)} reproduce exactly from today's table at their own scan date")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
