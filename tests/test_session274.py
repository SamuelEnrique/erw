"""Session 274: the Roundup's motion video.

Energy Research Warehouse (ERW). A Remotion pipeline (motion/) that takes a chart's own rows and renders a silent video
of 10 to 20 seconds at 1080x1350 and 1080x1080, choosing among four motion types by the chart's kind. Held here: every
number of a spec is the source file's; the four strongest findings are the rule's; every proof is on disk in both
sizes and lasts 10 to 20 seconds; the versions are exact; nothing is posted (no network call in the code but the fonts).
No video is rendered by the test.
"""

import glob
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MOTION = os.path.join(ROOT, "motion")
PROOFS = os.path.join(ROOT, "docs", "research", "motion")
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def specs():
    out = {}
    for p in sorted(glob.glob(os.path.join(MOTION, "specs", "*.json"))):
        with open(p, encoding="utf-8") as f:
            s = json.load(f)
        out[s["id"]] = s
    return out


def finding(name):
    with open(os.path.join(ROOT, "site", "data", "findings", name + ".json"), encoding="utf-8") as f:
        return json.load(f)


class TheSpecs(unittest.TestCase):
    def setUp(self):
        self.s = specs()

    def test_the_proofs_and_their_motion_types(self):
        self.assertEqual({k: v["type"] for k, v in self.s.items()}, {
            "chart_of_the_week_2026-W41": "draw-on", "batteries_curtailment_hourly": "draw-on", "batteries_curtailment": "count-up",
            "batteries_lunch": "draw-on", "impact_study": "draw-on", "who_rescues_whom": "reorder", "queue_divorce": "roll-call"})
        for s in self.s.values():
            self.assertTrue(10 * 30 <= s["frames"] <= 20 * 30, s["id"])

    def test_the_four_strongest_are_the_rules(self):
        rows = []
        for p in glob.glob(os.path.join(ROOT, "site", "data", "findings", "*.json")):
            if p.endswith("catalogue.json"):
                continue
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
            et = d.get("effect_table") or {}
            if et.get("rows"):
                rows.append((float(et["rows"][0]["p"]), d["id"], re.sub(r"_grids$", "", d["id"].split("__")[0])))
        seen, top = set(), []
        for p, i, fam in sorted(rows):
            if fam not in seen:
                seen.add(fam)
                top.append(i)
        self.assertEqual(top[:4], ["batteries_curtailment_hourly", "batteries_curtailment", "batteries_lunch", "impact_study"])
        self.assertLessEqual(set(top[:4]), set(self.s))

    def test_every_number_is_the_charts(self):
        with open(os.path.join(ROOT, "docs", "analysis", "2026-W41", "chart_of_the_week.json"), encoding="utf-8") as f:
            week = json.load(f)
        s = self.s["chart_of_the_week_2026-W41"]
        self.assertEqual(s["x"], [str(x) for x in week["chart"]["x"]])
        self.assertEqual(s["series"][0]["values"], week["chart"]["series"][0]["values"])
        for name in ("batteries_curtailment_hourly", "batteries_lunch", "impact_study"):
            c, sp = finding(name)["chart"], self.s[name]
            kept = [x for x in c["series"] if x["name"] not in sp["leftOut"]]
            self.assertEqual([x["values"] for x in sp["series"]], [x["values"] for x in kept], name)
        self.assertEqual(self.s["batteries_lunch"]["leftOut"], ["Hours at or above USD 1,000/MWh"])
        et = finding("batteries_curtailment")["effect_table"]
        self.assertEqual(self.s["batteries_curtailment"]["value"], et["rows"][-1]["coef_per_gw"])
        c = finding("who_rescues_whom")["chart"]
        self.assertEqual((self.s["who_rescues_whom"]["before"]["values"], self.s["who_rescues_whom"]["after"]["values"]),
                         (c["series"][0]["values"], c["series"][1]["values"]))
        c = finding("queue_divorce")["chart"]
        self.assertEqual([r["value"] for r in self.s["queue_divorce"]["rows"]], c["series"][0]["values"])


class TheProofs(unittest.TestCase):
    def test_each_in_both_sizes_with_its_still(self):
        for sid in specs():
            for size in ("1080x1350", "1080x1080"):
                for tail in (".mp4", "_last.png"):
                    p = os.path.join(PROOFS, f"{sid}_{size}{tail}")
                    self.assertTrue(os.path.exists(p) and os.path.getsize(p) > 10_000, p)
        self.assertIn("**Nothing here is posted anywhere.**", src("docs", "research", "motion", "README.md"))


class TheCode(unittest.TestCase):
    def test_exact_versions_and_the_packages_never_committed(self):
        with open(os.path.join(MOTION, "package.json"), encoding="utf-8") as f:
            deps = json.load(f)["dependencies"]
        for k, v in deps.items():
            self.assertRegex(v, r"^\d+\.\d+\.\d+$", k)
        self.assertIn("node_modules/", src("motion", ".gitignore"))

    def test_no_post_and_no_em_dash(self):
        files = glob.glob(os.path.join(MOTION, "src", "*.ts*")) + [os.path.join(MOTION, f) for f in ("specs.mjs", "render.mjs")]
        for p in files:
            with open(p, encoding="utf-8") as f:
                t = f.read()
            self.assertNotIn(EM, t, p)
            self.assertNotRegex(t, r"fetch\(|https?://", p)   # the code asks nothing of any host itself (the fonts' package does)
        self.assertNotIn(EM, src("docs", "research", "motion", "README.md"))


if __name__ == "__main__":
    unittest.main()
