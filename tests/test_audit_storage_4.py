"""Session 10212 (storage audit, finding 4): the build-out's early years are understated by more than "slightly".

/storage?tab=buildout rebuilds every year end from one EIA-860M inventory; a battery retired before the retired table's
window (the inventory year and the year before) is in no year, and the fold said "so early years are slightly
understated". Measured with EIA's full list of retired generators (eia860m_retired_generators_all, August 2026: 50
battery units, 524.3 MW, of which 42 units and 185.8 MW retired before 2025) against the September 2026 inventory
(docs/reviews/storage-model-audit-2026-11-26/measures.json, "buildout_year_ends_with_retired"): the United States' year
end lacks 112.7 of 362.9 MW in 2015 (31 percent), 125.6 of 587.0 in 2016, 111.4 of 1,115.4 in 2019 (10 percent) and 106.0
of 1,695.0 in 2020; from 2022 under half a percent.

Words only (site/app/storage/buildout/view.tsx, the fold "What EIA-860M covers and misses"): no figure moves. Putting the
retired batteries back would move the bars; that is finding 5, for the owner.
"""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class EarlyYears(unittest.TestCase):
    def test_the_builder_reads_only_the_retired_window(self):
        b = read("warehouse", "derived", "storage_buildout.py")
        self.assertIn('"retired": "eia860m_retired_generators"}', b)
        # session 11408 (wip/ready-storage-retired): the full list is read for batteries retired before the window
        self.assertIn("RETIRED_ALL = \"eia860m_retired_generators_all\"", b)

    def test_the_fold_says_how_much(self):
        v = read("site", "app", "storage", "buildout", "view.tsx")
        self.assertNotIn("slightly understated", v)
        self.assertIn("is read from EIA&apos;s full list of retired generators and counts in every year it operated, its MWh not reported",
                      " ".join(v.split()))
        self.assertNotIn(chr(0x2014), v)


if __name__ == "__main__":
    unittest.main()
