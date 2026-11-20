"""Session 9601 (chain 620, 20 November 2026): the resource problem set gives the legend a student reads on the map.

Energy Research Warehouse (ERW). Row 434 of `docs/state/browser_reads_wanted.md`, read on production: the worked
example of "What is under the ground and in the wind" tells a student to switch on Global Horizontal Irradiance and
read its legend, and answered 2.81 to 6.50 kWh/m2/day; the map's legend ran from 1.6 to 6.9. The map draws one legend
over every part of a layer (`legendOf` in `site/lib/resources.ts`: the contiguous states' range widened to Alaska's
and Hawaii's); the set read the contiguous states' range alone.

Held here:
- the set takes each end of a legend the way the map does, and each figure still names the part it is read from;
- on the committed list of layers the sun's legend runs from Alaska's low to Hawaii's high, and those are the map's
  own ends (the map's rule applied to the same file);
- the replication reads the legend the same way, by its own code;
- the decision's words and the method note say so; no em dash.
Nothing here sets the environment, reads a table or makes a request.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def layer(i):
    m = json.loads(src("site", "data", "resources", "manifest.json"))
    hits = [x for x in m["layers"] if x["id"] == i]
    assert len(hits) == 1, i
    return hits[0]


def map_legend(i):
    """The map's rule (legendOf): the layer's own range widened to hold every other extent's range."""
    lay = layer(i)
    lo, hi = lay["legend"]["min"], lay["legend"]["max"]
    for x in lay.get("other_extents") or []:
        g = x.get("legend") or {}
        if isinstance(g.get("min"), (int, float)) and isinstance(g.get("max"), (int, float)) and g["max"] > g["min"]:
            lo, hi = min(lo, g["min"]), max(hi, g["max"])
    return lo, hi


class TheSet(unittest.TestCase):
    def setUp(self):
        self.s = src("site", "lib", "problemsets", "under-the-ground-and-in-the-wind.ts")

    def test_each_legends_end_is_taken_over_every_part_of_the_layer(self):
        self.assertIn("const legendEnd = (id: string, end: \"min\" | \"max\", u: string) =>", self.s)
        self.assertIn("for (const x of l.other_extents ?? [])", self.s)
        self.assertIn('path: ["other_extents", { extent: x.extent }, "legend", end]', self.s)
        for line in ('legendEnd("solar_ghi", "min"', 'legendEnd("solar_ghi", "max"', 'legendEnd("wind_speed_100m", "max"', 'legendEnd("solar_dni", "max"'):
            self.assertIn(line, self.s)

    def test_no_legend_is_read_from_the_contiguous_states_alone(self):
        self.assertNotIn('["legend", "min"]', self.s)
        self.assertNotIn('["legend", "max"]', self.s)

    def test_the_steps_say_where_the_two_ends_come_from(self):
        self.assertIn("over every part of the layer", self.s)
        self.assertIn("the lowest of their lows (${gLow.where}) to the highest of their highs (${gHigh.where})", self.s)

    def test_the_map_still_widens_a_layers_legend_the_same_way(self):
        r = src("site", "lib", "resources.ts")
        self.assertIn("for (const x of l.other_extents ?? []) if (ok(x.legend)) { min = Math.min(min, x.legend.min); max = Math.max(max, x.legend.max); }", r)


class TheListOfLayers(unittest.TestCase):
    def test_the_suns_legend_runs_from_alaskas_low_to_hawaiis_high(self):
        lay = layer("solar_ghi")
        lo, hi = map_legend("solar_ghi")
        parts = {x["extent"].split(",")[0]: x["legend"] for x in lay["other_extents"]}
        self.assertLess(lo, lay["legend"]["min"], "the contiguous states' low is not the legend's low")
        self.assertGreater(hi, lay["legend"]["max"], "the contiguous states' high is not the legend's high")
        self.assertEqual(lo, min(g["min"] for g in parts.values()))
        self.assertEqual(hi, parts["Hawaii"]["max"])

    def test_the_wind_layer_has_one_part_so_its_legend_is_its_own(self):
        lay = layer("wind_speed_100m")
        self.assertEqual(map_legend("wind_speed_100m"), (lay["legend"]["min"], lay["legend"]["max"]))


class TheReplicationAndTheWords(unittest.TestCase):
    def test_the_replication_reads_the_legend_over_every_part(self):
        r = src("replication", "problem_sets", "replicate_country.py")
        self.assertIn("def legend_end(q, name, i, end):", r)
        for line in ('legend_end("rx", "min", "solar_ghi", "min")', 'legend_end("rx", "max", "solar_ghi", "max")', 'legend_end("r1", "legend_max", "wind_speed_100m", "max")', 'legend_end("r2", "dni", "solar_dni", "max")'):
            self.assertIn(line, r)

    def test_the_decision_and_the_method_note_say_so(self):
        d = src("site", "app", "learn", "problems", "Decisions.tsx")
        self.assertIn("its legend's range is the one the map draws, from the lowest low to the highest high over the layer's parts", d)
        n = src("docs", "methods", "problem_sets.md")
        self.assertIn("the legend's range as the map draws it, from the lowest low to the highest high over the layer's parts", n)

    def test_no_em_dash(self):
        for parts in (("site", "lib", "problemsets", "under-the-ground-and-in-the-wind.ts"), ("tests", "test_session9601_resource_set_legend.py")):
            self.assertNotIn(EM, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
