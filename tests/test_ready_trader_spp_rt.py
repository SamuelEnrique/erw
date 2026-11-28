"""wip/ready-trader-spp-rt (session 11406, chain 770, part C): the other choice of the trader view audit of
26 November, finding 1 (docs/reviews/trader-model-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main warehouse/derived/trader_view.py gives SPP no real-time table, so the board's week has no SPP real-time
figures though the board draws SPP's real-time prices. On this branch ISOS["spp"] reads spp_rtm_hub_prices: the
week's SPP rows gain real time less day-ahead, the largest spread and the hours over 50. Measured from the page's own
hourly files: on the board of 25 November SPP North -3.73 and SPP South -3.66 (the audit); this test measures the file
on disk and prints it. iso_trader_daily is rebuilt at landing by the desk (no SPP price table is on this machine)."""
import collections
import datetime as dt
import json
import os
import unittest
from zoneinfo import ZoneInfo

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def whole_days(hf, market):
    tz = ZoneInfo(hf["tz"])
    by = collections.defaultdict(list)
    for i, v in enumerate(hf.get(market) or []):
        if v is None:
            continue
        u = dt.datetime.fromtimestamp((hf["t0"] + i) * 3600, tz=dt.timezone.utc)
        by[u.astimezone(tz).date()].append((u, v))
    out = {}
    for d, hv in by.items():
        a = dt.datetime(d.year, d.month, d.day, tzinfo=tz).astimezone(dt.timezone.utc)
        n = d + dt.timedelta(days=1)
        want = round((dt.datetime(n.year, n.month, n.day, tzinfo=tz).astimezone(dt.timezone.utc) - a).total_seconds() / 3600)
        if len(hv) == want:
            out[d] = sorted(hv)
    return out


class SppRealTimeIsRead(unittest.TestCase):
    def test_the_code_reads_it(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "trader_view.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn('"spp": ("spp_dam_hub_prices", "spp_rtm_hub_prices", "America/Chicago"),', src)
        with open(os.path.join(ROOT, "warehouse", "connectors", "iso_prices.py"), encoding="utf-8") as f:
            self.assertIn('file="spp_rtm_hub_prices"', f.read())
        with open(os.path.join(SITE, "components", "board", "BoardView.tsx"), encoding="utf-8") as f:
            self.assertNotIn("the trader view does not read them", f.read())

    def test_the_week_it_would_hold(self):
        with open(os.path.join(SITE, "data", "board.json"), encoding="utf-8") as f:
            built = json.load(f)["built"]
        for hid in ("spp-sppnorth-hub", "spp-sppsouth-hub"):
            with open(os.path.join(SITE, "public", "board", "h", hid + ".json"), encoding="utf-8") as f:
                hf = json.load(f)
            da, rt = whole_days(hf, "da"), whole_days(hf, "rt")
            both = sorted(d for d in da if d in rt and [u for u, _ in rt[d]] == [u for u, _ in da[d]])
            wk = both[-7:]
            self.assertEqual(len(wk), 7, hid)
            means = [sum(r - a for (_, a), (_, r) in zip(da[d], rt[d])) / len(da[d]) for d in wk]
            v = sum(means) / 7
            print(f"board {built[:10]} {hid}: real time less day-ahead, the 7 days {wk[0]} to {wk[-1]}: {v:.2f}")
            if built.startswith("2026-11-25"):
                self.assertAlmostEqual(v, {"spp-sppnorth-hub": -3.73, "spp-sppsouth-hub": -3.66}[hid], delta=0.005)


if __name__ == "__main__":
    unittest.main()
