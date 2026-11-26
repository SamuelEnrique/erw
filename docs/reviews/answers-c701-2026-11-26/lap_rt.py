"""Data request 7 of docs/state/data_requests_five_tools.md, real time (the datacenter audit, finding 8): CAISO's three
default load aggregation points against their trading hubs in the real-time market, November 2025 to October 2026.

OASIS PRC_INTVL_LMP (version 3, RTM), one calendar month a request a node, 5 seconds between requests (oasis.caiso.com
has no robots file: 404, request 47 of runs/c701/probe/probe.csv); each zip kept under runs/c701/oasis/. The 5-minute
prices become 15-minute means and hourly means by zone_price_history.py's rules (a quarter hour only with its three
prices; an hour only with its four quarters). The hubs' real-time hours are iso_hub_prices_history's own (caiso_rtm).
A flat load: every hour weighs the same, over the hours both are held. Prints the result and writes lap_gap_rtm.csv."""
import io
import os
import sys
import time
import zipfile

import pandas as pd
import requests

sys.path.insert(0, "warehouse/connectors")
import iso_prices as ip  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
URL = ("https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=PRC_INTVL_LMP&version=3&market_run_id=RTM"
       "&node={node}&startdatetime={a}&enddatetime={b}")
PAIRS = {"DLAP_PGAE-APND": "TH_NP15_GEN-APND", "DLAP_SCE-APND": "TH_SP15_GEN-APND", "DLAP_SDGE-APND": "TH_SP15_GEN-APND"}
KEEP = "runs/c701/oasis"
os.makedirs(KEEP, exist_ok=True)
PT = "America/Los_Angeles"


def month_starts():
    return [pd.Timestamp(f"{y}-{m:02d}-01", tz=PT) for y, m in [(2025, 11), (2025, 12)] + [(2026, k) for k in range(1, 11)]]


def hourly(content, node):
    z = zipfile.ZipFile(io.BytesIO(content))
    names = [n for n in z.namelist() if n.lower().endswith(".csv")]
    if not names:
        raise RuntimeError(f"{node}: no CSV in the zip: {z.namelist()} {content[:200]!r}")
    df = pd.concat([pd.read_csv(io.BytesIO(z.read(n)), dtype=str, keep_default_na=False) for n in names], ignore_index=True)
    col = next(c for c in ("MW", "VALUE", "PRC") if c in df.columns)
    df = df[(df["LMP_TYPE"] == "LMP") & (df["NODE"] == node)]
    a = pd.to_datetime(df["INTERVALSTARTTIME_GMT"], utc=True)
    p = pd.DataFrame({"ts": a.dt.tz_convert("UTC").values, "v": pd.to_numeric(df[col], errors="coerce").values}).dropna().drop_duplicates()
    p["ts"] = pd.to_datetime(p["ts"], utc=True)  # .values drops the zone
    p = p.drop_duplicates("ts", keep=False)
    g = p.groupby(p["ts"].dt.floor("15min"))["v"]
    q = g.mean()[g.size() == 3]
    h = q.groupby(q.index.floor("h"))
    return h.mean()[h.size() == 4]


def main():
    series = {}
    n = 0
    for node in PAIRS:
        parts = []
        for start in month_starts():
            end = start + pd.offsets.MonthBegin(1)
            fn = os.path.join(KEEP, f"{node}_{start:%Y-%m}.zip")
            if os.path.exists(fn):
                content = open(fn, "rb").read()
            else:
                url = URL.format(node=node, a=start.tz_convert("UTC").strftime("%Y%m%dT%H:%M-0000"), b=end.tz_convert("UTC").strftime("%Y%m%dT%H:%M-0000"))
                if n:
                    time.sleep(5)
                r = requests.get(url, headers=UA, timeout=180)
                n += 1
                if r.status_code != 200:
                    raise RuntimeError(f"{node} {start:%Y-%m}: HTTP {r.status_code}")
                content = r.content
                open(fn, "wb").write(content)
            parts.append(hourly(content, node))
            print(f"{node} {start:%Y-%m}: {len(parts[-1])} hours", flush=True)
        series[node] = pd.concat(parts)
    p = "warehouse/output/iso_hub_prices_history.csv"
    hubs = pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str, keep_default_na=False)
    hubs = hubs[(hubs["market"] == "caiso_rtm") & hubs["entity"].isin(["caiso:" + h for h in set(PAIRS.values())])]
    hubs["ts"] = pd.to_datetime(hubs["ts_utc"], utc=True)
    hubs["v"] = hubs["value"].astype(float)
    hub_h = {}
    for e, g in hubs.groupby("entity"):
        s = g.set_index("ts")["v"].sort_index()
        hh = s.groupby(s.index.floor("h"))
        sizes = hh.size()
        full = sizes[sizes == sizes.mode().iloc[0]].index      # the hour's own count of intervals in the table (4 quarters, or 1 hourly)
        hub_h[e.split(":", 1)[1]] = hh.mean().loc[full]
    rows = []
    lo, hi = month_starts()[0].tz_convert("UTC"), (month_starts()[-1] + pd.offsets.MonthBegin(1)).tz_convert("UTC")
    for lap, hub in PAIRS.items():
        both = pd.concat([series[lap].rename("lap"), hub_h[hub].rename("hub")], axis=1).dropna()
        both = both[(both.index >= lo) & (both.index < hi)]
        rows.append(dict(lap=lap, hub=hub, market="real-time", hours=len(both), lap_mean=round(both["lap"].mean(), 4),
                         hub_mean=round(both["hub"].mean(), 4), gap_usd_mwh=round((both["lap"] - both["hub"]).mean(), 4),
                         first=both.index.min().isoformat(), last=both.index.max().isoformat()))
    out = pd.DataFrame(rows)
    print(out.to_string(index=False))
    print("requests made:", n)
    out.to_csv("runs/c701/lap_gap_rtm.csv", index=False)


if __name__ == "__main__":
    main()
