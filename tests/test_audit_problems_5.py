"""Session 10229 (the problems audit, finding 6): two sentences of the sets of the whole country against their files.
A storm across the country, question 3's "why": at Tennessee's highest hour of Elliott the extra demand over the baseline
hour was met by natural gas, hydro and imports; coal ran little above its baseline hour (the sentence named coal among the
plants turned up and left out the imports). Your own balancing authority, question 7: the growth is of the year's average
demand (docs/methods/authority_facts.md), asked beside the peak. Facts from site/data/regions/events/elliott_2022.json and
the method note; words from the two modules.
"""
import json
import os
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
EVENT = os.path.join(ROOT, "site", "data", "regions", "events", "elliott_2022.json")
STORM = os.path.join(ROOT, "site", "lib", "problemsets", "storm-across-the-country.ts")
AUTH = os.path.join(ROOT, "site", "lib", "problemsets", "your-own-balancing-authority.ts")
NOTE = os.path.join(ROOT, "docs", "methods", "authority_facts.md")


class TheStormHour(unittest.TestCase):
    def test_what_met_the_extra_demand(self):
        e = json.load(open(EVENT, encoding="utf-8"))["regions"]["TEN"]
        d = e["demand_mw"]
        k = max(range(len(d)), key=lambda j: (d[j] if isinstance(d[j], (int, float)) else float("-inf"), -j))
        rise = lambda s: e["gen"][s][k] - e["baseline"]["gen"][s][k]
        extra = d[k] - e["baseline"]["demand_mw"][k]
        imports = e["net_imports_mw"][k] - e["baseline"]["net_imports_mw"][k]
        self.assertEqual((extra, rise("natural_gas"), rise("hydro"), rise("coal"), imports), (13395, 5374, 2509, 116, 5415))
        self.assertLess(rise("coal"), 0.02 * extra)
        self.assertGreater(imports / extra, 0.35)
        self.assertGreater(max(x for x in e["gen"]["coal"] if isinstance(x, (int, float))) - e["gen"]["coal"][k], 2000)


class TheWords(unittest.TestCase):
    def test_the_storm(self):
        src = open(STORM, encoding="utf-8").read()
        self.assertNotIn('such as gas, coal and hydro."', src)
        self.assertIn("in this hour natural gas and hydro rose most above the baseline and imports carried much of the rest (the question on the flows into Tennessee)", src)
        self.assertNotIn(chr(0x2014), src)

    def test_the_authority(self):
        self.assertIn("average demand against 2019", open(NOTE, encoding="utf-8").read())
        src = open(AUTH, encoding="utf-8").read()
        self.assertIn("how much did its average demand grow from 2019 to ${a.size.growth_year}", src)
        self.assertIn("the newest whole year's average demand against 2019's", src)
        self.assertNotIn(chr(0x2014), src)


if __name__ == "__main__":
    unittest.main()
