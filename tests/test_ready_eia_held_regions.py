"""Session 11405 (chain 770, part C): decision 8 of the weekend page of 28 November, the "yes" readied.

The question: does the owner's hold on NYISO and SPP (12 October) reach EIA's own published rows for New York, New
England and the Midwest? On origin/main (the default "no") the three regions sections draw them: "The whole country"
on the nine event pages (app/events/WholeCountry.tsx), /supply's (components/supply/Country.tsx) and /demand's view of
the country (components/demand/Country.tsx). This branch holds the three regions (MIDW, NE, NY) in each, their
balancing authorities with them on /supply and /demand, drawn "license needed" as a held file is.

Measured on the files in site/data/regions/ (runs/c770/11405/measure_regions.mjs): the nine event sections as they
open 2,439 checked figures, 1,785 on the branch (654 become "license needed", 78 cells a page); /supply as it opens
1,387 to 1,216; /demand as it opens 160 to 160 (it opens on regions that are not held), and with New York, New England
or the Midwest chosen every figure of the place (85 to 113) reads "license needed".

The "license needed MW" mend of the event pages is on its own branch (wip/ready-events-mw-mend), as it lands under
either answer.
"""
import os
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
HELD = '["MIDW", "NE", "NY"]'


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheThreeLists(unittest.TestCase):
    def test_events_section_holds_the_three(self):
        self.assertIn(f"export const REGIONS_HELD: string[] = {HELD};", src("site", "app", "events", "WholeCountry.tsx"))

    def test_supply_section_holds_the_three(self):
        self.assertIn(f"export const REGIONS_HELD: string[] = {HELD};", src("site", "components", "supply", "Country.tsx"))

    def test_demand_view_holds_the_three_and_their_authorities(self):
        s = src("site", "components", "demand", "Country.tsx")
        self.assertIn(f"export const REGIONS_HELD: string[] = {HELD};", s)
        self.assertIn('place.level === "region" ? place.code : baOf(index, place.code)?.region', s)
        self.assertIn("const why = heldWhyOf(file) ?? regionHeldWhy(place, index);", s)


SCRIPT = r"""
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
const W = await import("../app/events/WholeCountry.tsx");
const S = await import("../components/supply/Country.tsx");
const D = await import("../components/demand/Country.tsx");
const CD = await import("../lib/countrydemand.ts");
const C = await import("../lib/countryfiles.ts");
const keys = (html) => [...html.matchAll(/<span data-c?n="([^"]+)">/g)].map((m) => m[1]);
const held = (html) => (html.match(/data-license-held=/g) ?? []).length;
const out = {};
const ev = renderToStaticMarkup(createElement(W.WholeCountry, { event: "elliott_2022", path: "/events/elliott-2022", file: C.eventRegionsFile("elliott_2022"), q: {}, first: "TEN", second: "CAR", firstWhy: "x" }));
out.events = { held: held(ev), keys: keys(ev) };
const su = renderToStaticMarkup(createElement(S.Country, { q: { region: "ny" } }));
out.supply = { held: held(su), keys: keys(su) };
const index = CD.regionsIndex();
for (const a of ["ny", "ne", "midw", "ba-isne", "tex"]) {
  const h = renderToStaticMarkup(createElement(D.Country, { q: { a, b: "none" }, index, fileOf: CD.demandPlaceFile }));
  out["demand_" + a] = { held: held(h), n: keys(h).length };
}
console.log(JSON.stringify(out));
"""


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
@unittest.skipUnless(os.path.isfile(os.path.join(SITE, "data", "regions", "events", "elliott_2022.json")), "the regions files are not on this copy")
class TheSectionsDrawn(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import json
        fd, path = tempfile.mkstemp(prefix="zz-ready-eia-", suffix=".mjs", dir=os.path.join(SITE, "scripts"))
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(SCRIPT)
        try:
            r = subprocess.run([NODE, "--import", "./scripts/battery-awards-page-register.mjs", os.path.relpath(path, SITE).replace(os.sep, "/")], cwd=SITE,
                               capture_output=True, text=True, encoding="utf-8", timeout=900)
        finally:
            os.remove(path)
        if r.returncode != 0:
            raise AssertionError(r.stdout[-2000:] + r.stderr[-2000:])
        cls.out = json.loads(r.stdout.strip().splitlines()[-1])

    def test_events_no_figure_of_the_three(self):
        k = self.out["events"]["keys"]
        self.assertFalse([x for x in k if re.match(r"wc\|(MIDW|NE|NY)\|", x)])
        self.assertTrue([x for x in k if x.startswith("wc|TEN|")])
        self.assertGreaterEqual(self.out["events"]["held"], 3 * 17)

    def test_supply_new_york_held(self):
        k = self.out["supply"]["keys"]
        self.assertFalse([x for x in k if re.match(r"(trade|mix)\|NY\|", x)])
        self.assertGreater(self.out["supply"]["held"], 100)

    def test_demand_the_three_and_an_authority_held_texas_drawn(self):
        for a in ("ny", "ne", "midw", "ba-isne"):
            self.assertEqual(self.out["demand_" + a]["n"], 0, a)
            self.assertGreater(self.out["demand_" + a]["held"], 0, a)
        self.assertGreater(self.out["demand_tex"]["n"], 0)
        self.assertEqual(self.out["demand_tex"]["held"], 0)


if __name__ == "__main__":
    unittest.main()
