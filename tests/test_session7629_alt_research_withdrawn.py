"""Session 7629: the other choice of the ruling on the findings cards built from internal tables (branch
wip/alt-research-1, not landed). Three cards (gas_sets_price from ISO-NE's prices; siting_flexible and siting_gigawatt
from the PUCT's transmission matrices) were left in the library and served by address; under the other choice they are
withdrawn.

What is held to:
  the library (lib/findings.ts, loadCards) holds 11 of the 14 card files (-21.4 percent); the three withdrawn are not
    among them, and a withdrawn card's address loads no card (loadCard returns null, so the page answers not found);
  the catalogue a reader may ask from leaves gas_sets_price out (it was 1 of its 11 entries);
  the files stay on disk (not deleted), each withdrawn card with its reason.

No request, no model call."""
import glob
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "findings")
WITHDRAWN = {"gas_sets_price", "siting_flexible", "siting_gigawatt"}


class TheThreeCardsWithdrawn(unittest.TestCase):
    def test_the_library_counts(self):
        files = [os.path.basename(p)[:-5] for p in glob.glob(os.path.join(DIR, "*.json")) if not p.endswith("catalogue.json")]
        self.assertEqual(len(files), 14)
        kept = [f for f in files if f not in WITHDRAWN]
        self.assertEqual(len(kept), 11)
        self.assertEqual(f"{100 * (11 - 14) / 14:.1f}", "-21.4")
        with open(os.path.join(DIR, "catalogue.json"), encoding="utf-8") as f:
            cat = json.load(f)
        self.assertEqual((len(cat), len([e for e in cat if e.get("id") not in WITHDRAWN])), (11, 10))
        for w in WITHDRAWN:
            self.assertTrue(os.path.exists(os.path.join(DIR, f"{w}.json")), w)

    def test_the_loader(self):
        with open(os.path.join(ROOT, "site", "lib", "findings.ts"), encoding="utf-8") as f:
            s = f.read()
        block = re.search(r"export const WITHDRAWN: Record<string, string> = \{(.*?)\};", s, re.S).group(1)
        self.assertEqual(set(re.findall(r"(\w+):", block)), WITHDRAWN)
        self.assertIn('!(f.replace(/\\.json$/, "") in WITHDRAWN)', s)
        self.assertIn("|| cardId in WITHDRAWN) return null;", s)
        self.assertIn('.filter((e) => !(String((e as { id?: string }).id ?? "") in WITHDRAWN))', s)
        self.assertNotIn(chr(0x2014), s)


if __name__ == "__main__":
    unittest.main()
