"""Session 664: release v1's package for the Stanford dataset (chain 043).

Energy Research Warehouse (ERW). `release_v1.py --target stanford` writes docs/redivis/release-v1-stanford/: every table whose
ERW verdict is public, "yes" when the uploader's Stanford manifest holds it and "held" otherwise; no other verdict is
listed. The old package (docs/redivis/release-v1/) is untouched. No network.

    python -m unittest tests.test_session664 -v
"""

import importlib
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))

import release_v1  # noqa: E402
import upload  # noqa: E402


class StanfordPackage(unittest.TestCase):
    def tearDown(self):
        importlib.reload(release_v1)  # use_stanford() rebinds the module's globals

    def test_plan_holds_public_verdicts_only(self):
        verdicts = upload.erw_verdicts()
        plan = release_v1.plan_stanford()
        names = {t for t, _, _ in plan}
        self.assertEqual(names, {t for t, v in verdicts.items() if v == "public"})
        self.assertTrue(all(v in ("yes", "held") for _, v, _ in plan))
        self.assertNotIn("ai_power_regions", names)  # flagged public in coverage.csv, unsettled by its verdict

    def test_yes_means_in_the_stanford_manifest(self):
        man = os.path.join(ROOT, upload.CONFIG["targets"]["stanford"]["manifest"])
        sent = {r["table"] for r in release_v1.rows(man)} if os.path.exists(man) else set()
        for t, v, _ in release_v1.plan_stanford():
            self.assertEqual(v == "yes", t in sent, t)

    def test_use_stanford_writes_elsewhere_and_names_the_dataset(self):
        old = release_v1.DOCS
        release_v1.use_stanford()
        self.assertNotEqual(release_v1.DOCS, old)
        self.assertTrue(release_v1.DOCS.replace(os.sep, "/").endswith("docs/redivis/release-v1-stanford"))
        self.assertEqual(release_v1.DATASET, "datapages.erw")
        self.assertIn("datapages.erw", release_v1.citation("eia_fuel_spot_prices", [], "EIA"))


if __name__ == "__main__":
    unittest.main()
