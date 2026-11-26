"""Session 10214 (demand audit): every figure the default view of /demand prints (ERCOT, ranked by average demand), as
the site's own code drew it (draw_demand.mjs: data-n keys), set beside the restatement (restate.py) formatted as the page
formats a figure (MW whole with separators, a growth signed to two decimals). Standard library only.

The year so far of ERCOT, CAISO and PJM needs October 2026 hours the workbook of 3 October lacks and the API table holds
only in part (two days short); for those the restatement is formed a second way, from the page file's own ten months,
each weighted by its local hours (ERCOT used every hour of the window, 7,295 of 7,295), and that second way is named.

Usage: python compare.py <drawn figures json> <restated json> <site demand_growth.json> <hours dir> <out>
"""
import calendar
import csv
import json
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

H = timedelta(hours=1)
NAMES = {"ERCO": "ERCOT", "CISO": "CAISO", "PJM": "PJM", "MISO": "MISO", "SWPP": "SPP", "NYIS": "NYISO", "ISNE": "ISO-NE", "US48": "Lower 48"}
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def whole(v):
    return f"{int(round_half_up(v)):,}"


def round_half_up(v):
    import decimal
    return decimal.Decimal(repr(v)).quantize(decimal.Decimal("1"), rounding=decimal.ROUND_HALF_UP)


def signed(v):
    s = f"{abs(v):,.2f}"
    return ("+" if v > 0 else "-" if v < 0 else "") + s


def local_hours(y, m, tz):
    a = datetime(y, m, 1, tzinfo=tz).astimezone(timezone.utc)
    b = datetime(y + (m == 12), m % 12 + 1, 1, tzinfo=tz).astimezone(timezone.utc)
    return int((b - a) / H)


def main(drawn, restated, site, hours, out):
    page = dict(json.load(open(drawn, encoding="utf-8")))
    R = json.load(open(restated, encoding="utf-8"))["areas"]
    S = json.load(open(site, encoding="utf-8"))
    tz = ZoneInfo("America/Chicago")
    e = R["ERCO"]["years"]
    mine = {}
    # the summary and the headlines
    mine["sum|avg0"] = mine["head|avg0"] = whole(e["2019"]["avg_demand_mw"])
    mine["sum|avg1"] = mine["head|avg1"] = whole(e["2025"]["avg_demand_mw"])
    g = round(100 * (e["2025"]["avg_demand_mw"] - e["2019"]["avg_demand_mw"]) / e["2019"]["avg_demand_mw"], 2)
    mine["sum|avg_growth"] = mine["head|avg_growth"] = signed(g)
    mine["sum|peak0"] = mine["head|peak0"] = whole(e["2019"]["peak_demand_mw"])
    mine["sum|peak1"] = mine["head|peak1"] = whole(e["2025"]["peak_demand_mw"])
    mine["sum|peak_growth"] = mine["head|peak_growth"] = signed(round(100 * (e["2025"]["peak_demand_mw"] - e["2019"]["peak_demand_mw"]) / e["2019"]["peak_demand_mw"], 2))
    # the year so far, from the page file's own ten months of 2026 and of 2019 weighted by their local hours
    def ytd_from_months(f, ba, y):
        yr = f["areas"][ba]["years"][str(y)]
        s = sum(yr[f"avg_demand_mw_m{m:02d}"] * local_hours(y, m, ZoneInfo(f["areas"][ba]["tz"])) for m in range(1, 11))
        n = sum(local_hours(y, m, ZoneInfo(f["areas"][ba]["tz"])) for m in range(1, 11))
        return s / n, n
    y26, n26 = ytd_from_months(S, "ERCO", 2026)
    y19 = e["2019"]["ytd_avg_demand_mw"]
    mine["head|ytd1"] = mine["ytd|avg"] = whole(round(y26, 1))
    mine["head|ytd0"] = whole(y19)
    mine["sum|ytd_growth"] = mine["head|ytd_growth"] = mine["ytd|avg_growth"] = signed(round(100 * (round(y26, 1) - y19) / y19, 2))
    mine["ytd|peak"] = whole(e["2026"]["ytd_peak_demand_mw"])
    mine["ytd|peak_growth"] = signed(round(100 * (e["2026"]["ytd_peak_demand_mw"] - e["2019"]["ytd_peak_demand_mw"]) / e["2019"]["ytd_peak_demand_mw"], 2))
    mine["ytd|hours"] = f"{n26:,}"
    # year by year
    for y in range(2019, 2026):
        r = e[str(y)]
        mine[f"y|{y}|avg"] = whole(r["avg_demand_mw"])
        mine[f"y|{y}|peak"] = whole(r["peak_demand_mw"])
        mine[f"y|{y}|hours"] = f"{r['hours_used']:,}"
        if y > 2019:
            mine[f"y|{y}|avg_growth"] = signed(r["avg_demand_growth_since_2019_pct"])
            mine[f"y|{y}|yoy"] = signed(r["avg_demand_growth_yoy_pct"])
            mine[f"y|{y}|peak_growth"] = signed(r["peak_demand_growth_since_2019_pct"])
    mine["screen|jumps"] = str(R["ERCO"]["screened"]["jumps"])
    mine["screen|zero"] = str(R["ERCO"]["screened"]["not_positive"])
    mine["screen|blank"] = str(R["ERCO"]["screened"]["blank"])
    # the cells: the largest and smallest growth by percent, first in month-then-hour order on a tie
    cells = []
    for m in range(1, 13):
        for h in range(24):
            k = f"m{m:02d}_h{h:02d}"
            if f"growth_pct_{k}" in e["2025"]:
                cells.append((m, h, e["2025"][f"growth_pct_{k}"], e["2025"][f"growth_mw_{k}"]))
    most = max(cells, key=lambda c: c[2])
    most = [c for c in cells if c[2] == most[2]][0]
    least = min(cells, key=lambda c: c[2])
    least = [c for c in cells if c[2] == least[2]][0]
    mine["sum|cell_most"] = mine["cell|most|pct"] = signed(most[2])
    mine["cell|most|mw"] = whole(most[3])
    mine["cell|least|pct"] = signed(least[2])
    mine["cell|least|mw"] = whole(least[3])
    # the ranking: every area's growth to 2025 and the year so far
    for ba, r in R.items():
        a = r["years"]
        mine[f"rank|{ba}|avg"] = signed(a["2025"]["avg_demand_growth_since_2019_pct"])
        if "peak_demand_growth_since_2019_pct" in a["2025"]:
            mine[f"rank|{ba}|peak"] = signed(a["2025"]["peak_demand_growth_since_2019_pct"])
        if ba in ("ERCO",):
            mine[f"rank|{ba}|ytd"] = mine["head|ytd_growth"]
        elif "ytd_avg_demand_growth_since_2019_pct" in a.get("2026", {}):
            mine[f"rank|{ba}|ytd"] = signed(a["2026"]["ytd_avg_demand_growth_since_2019_pct"])
    for ba in ("CISO", "PJM", "US48"):
        v26, _ = ytd_from_months(S, ba, 2026)
        b19 = R[ba]["years"]["2019"]["ytd_avg_demand_mw"]
        mine[f"rank|{ba}|ytd (from the file's months)"] = signed(round(100 * (round(v26, 1) - b19) / b19, 2))
    lines, eq, ne, missing = [], 0, 0, 0
    for k, v in page.items():
        if k in mine:
            ok = mine[k] == v
            eq += ok
            ne += not ok
            lines.append(f"{'=' if ok else 'X'} {k}: page {v}, restated {mine[k]}")
        else:
            missing += 1
            lines.append(f"? {k}: page {v}, not restated here (see the note below)")
    for k in mine:
        if k not in page:
            lines.append(f"+ {k}: restated {mine[k]} (not a marked figure of this view)")
    # the ranking's order
    order = sorted([ba for ba in R], key=lambda b: -R[b]["years"]["2025"]["avg_demand_growth_since_2019_pct"])
    lines.append("ranking order restated (average demand): " + ", ".join(NAMES[b] for b in order))
    # the peaks' local hours as the page writes them
    for y in ("2019", "2025"):
        t = datetime.strptime(R["ERCO"]["at"][y]["peak_demand_mw"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).astimezone(tz)
        lines.append(f"ERCOT peak {y}: {t.day} {MONTHS[t.month - 1]} {t.year}, {t.hour:02d}:00 local")
    lines.append(f"cells held for ERCOT 2025: {len(cells)} of 288; largest {MONTHS[most[0] - 1]} {most[1]:02d}:00, smallest {MONTHS[least[0] - 1]} {least[1]:02d}:00")
    # the hover of "On the year before": the All grids tab's last twelve months over the twelve before (lib/siting.ts)
    def mean12(end_y, end_m):
        s = h = 0
        for k in range(12):
            y, m = end_y, end_m - k
            while m < 1:
                m += 12
                y -= 1
            v = S["areas"]["ERCO"]["years"][str(y)][f"avg_demand_mw_m{m:02d}"]
            d = calendar.monthrange(y, m)[1] * 24
            s += v * d
            h += d
        return s / h
    lines.append(f"the hover's All grids figure, ERCOT, November 2025 to October 2026 on the twelve before: {signed(100 * (mean12(2026, 10) / mean12(2025, 10) - 1))} percent")
    head = f"/demand (ERCOT, average demand): {eq} of {eq + ne} marked figures restated equal, {ne} differ, {missing} not restated"
    open(out, "w", encoding="utf-8").write("\n".join([head, ""] + lines) + "\n")
    print(head)


if __name__ == "__main__":
    main(*sys.argv[1:6])
