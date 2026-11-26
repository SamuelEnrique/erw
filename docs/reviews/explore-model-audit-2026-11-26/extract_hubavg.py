"""Session 10231 (audit of the signature explorers): stream ERCOT's hub price history (read only, from the main copy)
and keep HB_HUBAVG's real-time (spp_rtm, 15-minute) and day-ahead (spp_dam, hourly) prices, one line each:
market, ts_utc, value. Standard library only; nothing of the warehouse's code is imported.

    python extract_hubavg.py <ercot_all_hub_prices_history.csv> <out.csv> [<iso_rtm_hub_prices.csv> <iso_dam_hub_prices.csv>]
"""
import csv
import sys

HUB = "ercot:HB_HUBAVG"


def stream(path, out, seen):
    n = 0
    with open(path, newline="", encoding="utf-8") as f:
        rows = (l for l in f if not l.startswith("#"))
        r = csv.reader(rows)
        head = next(r)
        ix = {k: i for i, k in enumerate(head)}
        for c in r:
            if c[ix["entity"]] != HUB:
                continue
            var = c[ix["variable"]]
            if var not in ("spp_rtm", "spp_dam"):
                continue
            key = (var, c[ix["ts_utc"]])
            if key in seen:
                if seen[key] != c[ix["value"]]:
                    print("two prices for", key, seen[key], c[ix["value"]])
                continue
            seen[key] = c[ix["value"]]
            out.writerow([var, c[ix["ts_utc"]], c[ix["value"]]])
            n += 1
    print(path, n, "rows kept")


def main():
    hist, dst = sys.argv[1], sys.argv[2]
    seen = {}
    with open(dst, "w", newline="", encoding="utf-8") as g:
        w = csv.writer(g)
        w.writerow(["variable", "ts_utc", "value"])
        stream(hist, w, seen)
        for extra in sys.argv[3:]:
            stream(extra, w, seen)


if __name__ == "__main__":
    main()
