"""Session 7630: the other choice of the ruling on storage in the queue on /queues (branch wip/alt-queues-2, not landed).
The page gave storage as the file's parts; under the other choice the US storage figure is reconciled to Berkeley Lab's
own summary ("approximately 749 GW").

What is held to:
  the file's parts for the US (site/data/queues.json, built 17 November 2026: active MW of the battery parts and the other
    storage parts, hybrids' storage parts included) sum to 552.7 GW; the summary's 749 GW is +196.3 GW, +35.5 percent;
  the page draws the reconciled figure for the US view only, beside the parts' sum, saying the grids do not add up to it.

No request, no model call."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class StorageReconciled(unittest.TestCase):
    def test_the_figures(self):
        with open(os.path.join(ROOT, "site", "data", "queues.json"), encoding="utf-8") as f:
            w = json.load(f)["views"]["us|all"]["whole"]
        parts = (w["active_mw_parts_battery"] + w["active_mw_parts_other_storage"]) / 1000
        self.assertEqual(f"{parts:.1f}", "552.7")
        self.assertEqual((f"{749 - parts:.1f}", f"{100 * (749 / parts - 1):.1f}"), ("196.3", "35.5"))

    def test_the_page(self):
        with open(os.path.join(ROOT, "site", "app", "queues", "page.tsx"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn("const STORAGE_SUMMARY_GW = 749;", s)
        self.assertIn('{grid.slug === "us" && viewOf(file, "us", "all") ? (() => {', s)
        self.assertIn("data-storage-reconciled={STORAGE_SUMMARY_GW}", s)
        self.assertNotIn(chr(0x2014), s)


if __name__ == "__main__":
    unittest.main()
