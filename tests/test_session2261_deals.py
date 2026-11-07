"""Session 2261 (chain 159): a facility's company field with two names the model joined.

The second read (session 2249) found 3 of 60 sampled facilities with the operator missed. One (F014) was the check:
the model gave the developer as "Colt DCS, RMZ" for "Colt DCS and RMZ start work on third facility at Mumbai
campus", and the joined string is not in the story, so warehouse/datacenters/extract.py refused it. A company field
now passes when each of its names is in the story (names_named). The two others stay by the rule: "TikTok owner" is a
description, not a name (F050), and "Balearic Islands launches new data center" names a government by its place,
left empty by the model (F036).
"""

import importlib.util
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "datacenters", "eval"))
import dc_fixture  # noqa: E402


def extract():
    sys.path.insert(0, os.path.join(ROOT, "warehouse", "datacenters"))
    sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
    sys.path.insert(0, os.path.join(ROOT, "warehouse"))
    spec = importlib.util.spec_from_file_location("erw_dc_extract_2261", os.path.join(ROOT, "warehouse", "datacenters", "extract.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TheCheck(unittest.TestCase):
    def test_each_name_in_the_story(self):
        ex = extract()
        text = ex.norm("Colt DCS and RMZ start work on third facility at Mumbai campus, India")
        self.assertTrue(ex.names_named("Colt DCS, RMZ", text))
        self.assertTrue(ex.names_named("Colt DCS and RMZ", text))
        self.assertFalse(ex.names_named("Colt DCS, Equinix", text))   # a name not in the story
        self.assertFalse(ex.names_named("Colt DCS", text))             # one name is the ordinary check's
        out, why = ex.checked_fields({"developer": "Colt DCS, RMZ", "site_name": "Colt DCS, RMZ"}, text)
        self.assertEqual(out["developer"], "Colt DCS, RMZ")
        self.assertEqual(out["site_name"], "")   # only the two company fields take joined names


class TheSample(unittest.TestCase):
    def test_f014_keeps_its_developers(self):
        with open(os.path.join(ROOT, "tests", "fixtures", "datacenters", "stories_2249.json"), encoding="utf-8") as f:
            fx = {s["event_id"]: s.get("fixture") for s in json.load(f)}
        rows, log = dc_fixture.replay("2249")
        got = [r for r in rows.to_dict("records") if "F014" in {fx.get(i) for i in str(r["story_ids"]).split(";")}]
        self.assertEqual([r["developer"] for r in got], ["Colt DCS, RMZ"])
        self.assertIn("'TikTok owner' is a description", log)


if __name__ == "__main__":
    unittest.main()
