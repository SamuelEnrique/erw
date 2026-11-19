"""Session 8013 (chain 505, part D3): "Forecast against actual" on the country view of /demand.

components/demand/CountryForecast.tsx reads forecast/<region>.json, forecast/ba/<code>.json (contract section 11) and
renewables_forecast.json (section 12); it is one new section of components/demand/Country.tsx, placed before the list
of every place, and the sections before it are not touched.
"""

import os
import re
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def src(*p):
    with open(os.path.join(REPO, "site", *p), encoding="utf-8") as f:
        return f.read()


class TheSection(unittest.TestCase):
    def test_one_new_section_before_the_list_of_places(self):
        s = src("components", "demand", "Country.tsx")
        i = s.index("{forecast && withFile.length ? <CountryForecast slots={withFile.map(")
        self.assertIn("fileOf={demandPlaceFile} forecast />", s)
        j = s.index('<ToolSection title="Every region and balancing authority" id="places"')
        self.assertLess(i, j)
        self.assertEqual(s.count("<CountryForecast"), 1)

    def test_it_reads_the_contract_files(self):
        c = src("components", "demand", "CountryForecast.tsx")
        self.assertIn("`forecast/${p.code.toLowerCase()}.json`", c)
        self.assertIn("`forecast/ba/${p.code.toLowerCase()}.json`", c)
        self.assertIn('readRegionFile<RenewFile>("renewables_forecast.json")', c)

    def test_every_figure_has_a_hover_and_a_missing_one_says_not_held(self):
        c = src("components", "demand", "CountryForecast.tsx")
        self.assertIn('title={`Not held. ${why}`}', c)
        # each figure goes through N, which carries the source as its title
        self.assertGreater(len(re.findall(r"<N key=", c)), 20)
        self.assertNotIn("—", c)


if __name__ == "__main__":
    unittest.main()
