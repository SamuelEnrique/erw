"""Session 10223 (the states audit, finding 1): net interstate trade in EIA's state profile is out less in.

The page printed "Net interstate trade (in less out)" and the files' note said "positive where the state took in more
electricity from other states than it sent out". EIA lists the trade among the disposition: read out less in, each
place's net generation and international imports less the trade equal its sales, losses and exports to within EIA's
direct use; read in less out, many places fall far below zero. Words only: no figure moves.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "states")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def rests():
    """{place: (rest read in less out, rest read out less in), each as a share of the disposition}, newest year."""
    with open(os.path.join(DIR, "index.json"), encoding="utf-8") as f:
        idx = json.load(f)
    out = {}
    for r in idx["states"]:
        with open(os.path.join(DIR, r["file"]), encoding="utf-8") as f:
            d = json.load(f)["disposition"]
        if not d.get("years"):
            continue
        i = len(d["years"]) - 1
        v = {k: ((a[i] if a else None) or 0) for k, a in d["values"].items()}
        dis = v["full_service_providers"] + v["energy_only_providers"] + v["estimated_losses"] + v["total_international_exports"]
        base = v["total_net_generation"] + v["total_international_imports"]
        out[r["state"]] = ((base + v["net_interstate_trade"] - dis) / dis, (base - v["net_interstate_trade"] - dis) / dis)
    return out


@unittest.skipUnless(os.path.exists(os.path.join(DIR, "index.json")), "the states' page files are not on this machine")
class TheSign(unittest.TestCase):
    def test_out_less_in_balances_the_profile(self):
        r = rests()
        self.assertEqual(len(r), 52)
        below_out = [st for st, (_, b) in r.items() if b < -0.02]
        below_in = [st for st, (a, _) in r.items() if a < -0.02]
        self.assertLessEqual(len(below_out), 1, below_out)       # Hawaii, trade 0, -1.5 percent
        self.assertGreaterEqual(len(below_in), 20, below_in)
        med = sorted(abs(b) for _, b in r.values())[len(r) // 2]
        self.assertLess(med, 0.05)

    def test_virginia_takes_in_more_than_it_sends(self):
        with open(os.path.join(DIR, "va.json"), encoding="utf-8") as f:
            d = json.load(f)["disposition"]
        trade = d["values"]["net_interstate_trade"][-1]
        gen = d["values"]["total_net_generation"][-1]
        sales = d["values"]["full_service_providers"][-1] + d["values"]["energy_only_providers"][-1]
        self.assertLess(trade, 0)
        self.assertGreater(sales, gen)            # Virginia sells more than it makes: it takes in the rest


class TheWords(unittest.TestCase):
    def test_the_page_says_out_less_in(self):
        page = src("site", "app", "states", "page.tsx")
        self.assertIn("Net interstate trade (out less in)", page)
        self.assertNotIn("(in less out)", page)
        self.assertIn("positive where the state sent more electricity to other states than it took in", page)

    def test_the_builder_note_says_the_same(self):
        b = src("warehouse", "derived", "states_page.py")
        self.assertNotIn("positive where the state took in more electricity", b)
        self.assertIn("positive where the state sent more electricity to other states than it took in", b)
        self.assertIn("out less in", src("docs", "methods", "states_page.md"))


if __name__ == "__main__":
    unittest.main()
