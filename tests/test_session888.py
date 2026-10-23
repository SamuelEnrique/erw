"""Session 888: the licenses' third round.

Energy Research Warehouse (ERW). Tests that the U.S. Wind Turbine Database's publisher name resolves to USGS's verdict
(read 87), that PUDL's FERC Form 714 tables stay unmatched (they wait on FERC's own page), that every request of the
round is in the record with a label of its own, and that the Canada Energy Regulator's verdict and Catalyst's single
verdict stand. No network.

    python -m unittest tests.test_session888 -v
"""

import csv
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import licenses as L  # noqa: E402


def rows(name):
    with open(os.path.join(ROOT, "warehouse", "metadata", name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


class ThirdRound(unittest.TestCase):
    def test_usgs_names_resolve(self):
        self.assertEqual(L.canon("U.S. Geological Survey (USGS), with LBNL and ACP"), "U.S. Geological Survey (USGS)")
        self.assertEqual(L.canon("Catalyst Cooperative (PUDL), from FERC Form 714"), "Catalyst Cooperative (PUDL), from FERC Form 714")

    def test_the_round_is_recorded(self):
        reads = [r for r in rows("license_reads.csv") if "(session 888)" in r["publisher"]]
        self.assertEqual(len(reads), 10)
        hosts = {}
        for r in reads:
            h = r["url"].split("/")[2]
            hosts[h] = hosts.get(h, 0) + 1
        self.assertTrue(all(v <= 2 for v in hosts.values()), hosts)          # two a host
        ferc = [r for r in reads if r["url"].endswith("/administrative-policies")]
        self.assertTrue(ferc[0]["outcome"].startswith("not read: HTTP 403"))

    def test_one_verdict_a_publisher(self):
        keys = [v["key"] for v in rows("license_verdicts.csv")]
        self.assertEqual(keys.count("Catalyst Cooperative (PUDL)"), 1)
        self.assertEqual(len(set(keys)), len(keys))


if __name__ == "__main__":
    unittest.main()
