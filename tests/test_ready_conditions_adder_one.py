"""Session 11407 (chain 770, part C), carried over from wip/audit-conditions-7 (session 10219, the conditions audit of
26 November, finding 7). /conditions counted ERCOT's online reserve adder as scarcity whenever its hourly mean was above
zero, however small: the COVID window's glance printed 20 such hours on 16 March 2020, a day of cents. On this branch
the builder (warehouse/derived/conditions_page.py) counts the hours at USD 1 or more (ADDER_LEVEL), the page's words say
so, and the window's most is 6 (8 April 2020). The committed page files are rebuilt at landing by the desk.
"""
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "conditions")
OUT = os.path.join(ROOT, "warehouse", "output", "ercot_rtm_price_adders.csv")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


def builder():
    sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
    sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
    import conditions_page
    return conditions_page


class AtOneDollarIsTheCount(unittest.TestCase):
    def test_the_builder_counts_at_one_dollar(self):
        s = src("warehouse", "derived", "conditions_page.py")
        self.assertIn('int((g["adder"] >= ADDER_LEVEL).sum())', s)
        self.assertNotIn('int((g["adder"] > 0).sum())', s)
        self.assertEqual(builder().ADDER_LEVEL, 1.0)

    def test_the_page_says_so(self):
        s = src("site", "app", "conditions", "page.tsx")
        self.assertIn("Most hours with the adder at USD 1 or more in a day", s)
        self.assertIn('title="Hours the adder was USD 1/MWh or more, a day"', s)
        self.assertNotIn("with the adder above zero", s)
        self.assertNotIn("Hours the adder was above zero", s)
        self.assertIn("8. **The adder's level.**", src("docs", "methods", "grid_conditions.md"))

    def test_a_day_of_cents_counts_no_hour(self):
        import pandas as pd
        cp = builder()
        ts = [f"2020-03-16T{h:02d}:00:00Z" for h in range(5, 24)]
        w = pd.DataFrame({"ts_utc": ts, "adder": [0.02] * 17 + [1.0, 3.5]})
        w["day"] = cp.local(w["ts_utc"], "America/Chicago").dt.strftime("%Y-%m-%d")
        cols, rows = cp.daily_rows(w, "ercot", None)
        self.assertEqual(rows[0][cols.index("adder_hours")], 2)


@unittest.skipUnless(os.path.exists(OUT) and os.path.exists(os.path.join(DIR, "ercot.json")), "ercot_rtm_price_adders or the page files are not in this checkout")
class TheCovidWindowFrom20To6(unittest.TestCase):
    def test_the_builder_on_the_adder_table(self):
        import pandas as pd
        cp = builder()
        scar = cp.read("ercot_rtm_price_adders", ["variable", "ts_utc", "value"], keep=lambda d: d["variable"] == "rtorpa_mean")
        scar = scar[(scar["ts_utc"] >= "2020-02-29") & (scar["ts_utc"] <= "2020-06-02")]
        dem = pd.DataFrame({c: pd.Series(dtype=str) for c in ("variable", "ts_utc", "value", "ba")})
        w = cp.hourly_frame("ercot", cp.OPS["ercot"], dem, None, None, scar)
        cols, rows = cp.daily_rows(w, "ercot", None)
        with open(os.path.join(DIR, "ercot.json"), encoding="utf-8") as fh:
            win = [x for x in json.load(fh)["windows"] if x["id"] == "covid_2020"][0]
        i = cols.index("adder_hours")
        days = [r for r in rows if win["start"] <= r[0] <= win["end"] and r[i] is not None]
        top = max(days, key=lambda r: r[i])
        self.assertEqual((top[0], top[i]), ("2020-04-08", 6))


if __name__ == "__main__":
    unittest.main()
