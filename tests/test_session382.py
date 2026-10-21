"""Session 382: the trader path, click by click (docs/reviews/trader-path.md), and the one fault the walk found.

The fault: from 21 October 2026 (the license hold of the owner's ruling of 12 October, lib/license.ts) the generator
page's model figures (check keys mr|iso=<grid>&...|<stat> and ms|iso=<grid>&...|<span>|<stat>, table
merchant_revenue_monthly, decided by ISO-NE, MISO and NYISO and so held grid by grid) were drawn as "license needed" on
every grid, ERCOT's, CAISO's and SPP's included: components/Num.tsx looked for the grid only as an entity
("iso:ercot") and the keys name it as an input ("iso=ercot"). gridEntityOfKey reads it; a held grid's figures stay held.
"""

import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
DOC = os.path.join(ROOT, "docs", "reviews", "trader-path.md")
SHOTS = os.path.join(ROOT, "docs", "brand", "review-382")

PROBE = r"""
const L = await import("@/lib/license");
const on = new Date("2026-10-21T03:00:00Z"), before = new Date("2026-10-19T12:00:00Z");
const inputs = (g) => `iso=${g}&asset=solar&mw=100&mwh=0&ds=0&hr=0&vom=0&fom=0`;
const keys = (g) => [`mr|${inputs(g)}|l12_kw`, `ms|${inputs(g)}&hub=HB_WEST&market=rt|twelve|revenue`];
const out = {};
for (const g of ["ercot", "caiso", "spp", "isone", "nyiso", "miso"]) {
  out[g] = keys(g).map((k) => {
    const p = k.split("|").slice(1);
    const e = L.gridEntityOfKey(p);
    return [e ?? null, L.licenseHeldRow("merchant_revenue_monthly", e, on), L.licenseHeldRow("merchant_revenue_monthly", e, before)];
  });
}
out.none = [L.gridEntityOfKey(["asset=solar", "l12"]) ?? null, L.gridEntityOfKey(["xiso=ercot"]) ?? null, L.gridEntityOfKey(["iso=texas&mw=1"]) ?? null];
console.log(JSON.stringify(out));
"""


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(shutil.which("node"), "node is not installed")
class TheHoldIsByGrid(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = subprocess.run(["node", "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", PROBE],
                           cwd=SITE, capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            raise AssertionError(f"node failed ({r.returncode}): {r.stderr[-800:]}")
        cls.out = json.loads(r.stdout.strip().splitlines()[-1])

    def test_ercot_caiso_spp_are_not_held(self):
        for g in ("ercot", "caiso", "spp"):
            for entity, held_on, held_before in self.out[g]:
                self.assertEqual(entity, f"iso:{g}")
                self.assertFalse(held_on, g)
                self.assertFalse(held_before, g)

    def test_isone_nyiso_miso_are_held_from_the_day(self):
        for g in ("isone", "nyiso", "miso"):
            for entity, held_on, held_before in self.out[g]:
                self.assertEqual(entity, f"iso:{g}")
                self.assertTrue(held_on, g)
                self.assertFalse(held_before, g)

    def test_a_key_naming_no_grid_names_none(self):
        self.assertEqual(self.out["none"], [None, None, None])


class TheComponent(unittest.TestCase):
    def test_num_falls_back_to_the_grid_an_input_names(self):
        t = src("site", "components", "Num.tsx")
        self.assertIn('const entity = p.slice(1).find((x) => gridOfEntity(x) !== "") ?? gridEntityOfKey(p.slice(1));', t)
        self.assertRegex(t, r"import \{[^}]*\bgridEntityOfKey\b[^}]*\} from \"@/lib/license\"")
        # the map of 14 October stands: both model prefixes are the merchant table
        self.assertIn('mr: "merchant_revenue_monthly", ms: "merchant_revenue_monthly"', t)

    def test_the_function_is_in_the_license_module(self):
        t = src("site", "lib", "license.ts")
        self.assertIn("export function gridEntityOfKey(parts: string[]): string | undefined", t)


class TheDocument(unittest.TestCase):
    def test_every_step_has_its_address_its_two_shots_and_its_questions(self):
        t = src("docs", "reviews", "trader-path.md")
        steps = re.findall(r"^### Step (\d\d)", t, flags=re.M)
        self.assertGreaterEqual(len(steps), 12)
        self.assertEqual(steps, sorted(steps))
        for block in re.split(r"^### Step ", t, flags=re.M)[1:]:
            n = block[:2]
            self.assertRegex(block, r"Address: `/(cost-of-power/seller|cost-of-power/battery|board)", n)
            self.assertIn("Does:", block, n)
            self.assertIn("Sees:", block, n)
            self.assertIn("A trader would ask", block, n)
            shots = re.findall(r"\((?:\.\./brand/review-382/)?([0-9]{2}-[a-z0-9-]+_(?:1280|390)\.png)\)", block)
            self.assertEqual({s.rsplit("_", 1)[1] for s in shots}, {"1280.png", "390.png"}, n)
            for s in shots:
                self.assertTrue(os.path.isfile(os.path.join(SHOTS, s)), s)
                self.assertTrue(s.startswith(n), s)

    def test_the_on_energy_section_says_what_is_needed(self):
        t = src("docs", "reviews", "trader-path.md")
        self.assertIn("## The On.Energy walkthrough: what is needed to write it", t)

    def test_no_em_dash(self):
        for p in (DOC, os.path.join(SHOTS, "walk-382.mjs"), os.path.join(SHOTS, "explore-382.mjs"), os.path.abspath(__file__)):
            with open(p, encoding="utf-8") as f:
                self.assertNotIn(chr(0x2014), f.read(), p)


if __name__ == "__main__":
    unittest.main()
