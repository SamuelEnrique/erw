"""Session 10214 (demand audit): a state's retail sales by sector, month by month, with each month's change on the same
month a year before, to see whether a sector's growth is a step (customers moved between classes) or a trend.
Standard library; the table is streamed.

Usage: python sector_months.py <eia_retail_sales_monthly.csv> <from YYYY-MM> <state> [<state> ...]
"""
import csv
import sys


def main(path, start, states):
    v = {}
    with open(path, newline="", encoding="utf-8") as f:
        rd = csv.reader(line for line in f if not line.startswith("#"))
        head = next(rd)
        e, var, t, val = head.index("entity"), head.index("variable"), head.index("ts_utc"), head.index("value")
        for r in rd:
            if r[var] != "retail_sales":
                continue
            _, _, st, sec = r[e].split(":")
            if st in states:
                v[(st, sec, r[t][:7])] = float(r[val])
    for st in states:
        print(f"== {st}: month, industrial GWh (change on a year before), commercial GWh (change), all sectors GWh (change), industrial share of all, percent")
        ms = sorted({m for (s, _, m) in v if s == st and m >= start})
        for m in ms:
            p = f"{int(m[:4]) - 1}{m[4:]}"
            def cell(sec):
                a, b = v.get((st, sec, m)), v.get((st, sec, p))
                if a is None:
                    return "none"
                return f"{a / 1000:,.0f} ({(a - b) / 1000:+,.0f})" if b is not None else f"{a / 1000:,.0f}"
            share = 100 * v[(st, "IND", m)] / v[(st, "ALL", m)] if (st, "IND", m) in v and (st, "ALL", m) in v else float("nan")
            print(f"{m}  IND {cell('IND')}  COM {cell('COM')}  ALL {cell('ALL')}  IND share {share:.1f}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
