"""Session 1422 (chain 111): the older blocks' render cases.

Session 1404's render test (site/scripts/test-grid-render.mjs) drew the Grid tool's older blocks only inside the tab
around them, where a pinned test read them. Every block of /grid that stood before chain 077 and had no case of its own
now has one, a case a grid kind where it is drawn differently (ERCOT, CAISO, ISO-NE as the held grid, the Lower 48), on
the committed fixtures: its name, its own figures by kind and count, its words, its held line, its anchors, its method
links and its files. The page is unchanged: the older blocks are named in the stand-in only (site/scripts/
grid-render-standin.mjs OLDER_MARKS, OLDER_COMPONENTS, a Section by its title, a <section> by its id, older_<name>),
each counting as its own what is not inside a named panel within it. One fixture is new, site/scripts/fixtures/
grid_mix_now.json (eia930_generation_latest for ERCOT, ISO-NE and the Lower 48, state_generation_mix_monthly for the
United States, read once with the anon key). The pinned python assertions the new cases cover carry session 1404's
comment line.

    python -m unittest tests.test_session1422 -v
"""

import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
MODULES = all(os.path.isdir(os.path.join(SITE, "node_modules", p)) for p in ("typescript", "react"))
EM = chr(0x2014)
TAG = "# also covered by " + "site/scripts/test-grid-render.mjs: "   # in two parts: tests/test_session1404.py reads every line holding it whole
CHANGED = [("site", "scripts", "grid-render-standin.mjs"), ("site", "scripts", "test-grid-render.mjs"), ("site", "scripts", "fixtures", "grid_mix_now.json"),
           ("docs", "methods", "grid_network.md"), ("tests", "test_session1422.py")]
KINDS = ("an ISO with prices (ERCOT)", "CAISO", "a held grid (ISO-NE)", "the Lower 48")
# the older blocks a case now names, each with the grid kinds it is drawn for
OLDER = {
    "older_the sentence": KINDS, "older_the headline numbers": KINDS, "older_#today": KINDS, "older_#hourly": KINDS,
    "older_the Ask aside": KINDS, "older_the network's server lines": KINDS, "mixview_forecast": KINDS,
    "older_parts_now": KINDS[:3], "older_Who runs this grid": KINDS[:3], "older_Where the power comes from": KINDS[:3], "older_How clean": KINDS[:3],
    "mixview_records": KINDS[:3], "mixview_now": KINDS[1:], "older_In the news": (KINDS[0], KINDS[2]),
    "older_#monthly": KINDS[:1], "older_the source line": KINDS[:1], "older_the decisions": KINDS[:1], "older_The last 24 hours": KINDS[:1],
    "older_CAISO's break note": KINDS[:2], "older_the header": (KINDS[0], KINDS[3]),
}
ANNOTATED = {"test_session54.py": "older_the network's server lines on /grid?grid=ercot&view=network",
             "test_session133.py": "mixview_forecast on /grid?grid=us48&view=mix&mix=forecast",
             "test_session157_page.py": "mixview_forecast on /grid?grid=us48&view=mix&mix=forecast",
             "test_session266.py": "older_the sentence on /grid?grid=ercot&view=mix",
             "test_session502.py": "older_the Ask aside on /grid?grid=ercot&view=mix"}


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def cases():
    return [json.loads(line.strip().rstrip(",")) for line in src("site", "scripts", "test-grid-render.mjs").split("\n") if line.startswith('  {"name": ')]


def node_env():
    return {k: v for k, v in os.environ.items()
            if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY", "NEXT_PHASE", "NEXT_RUNTIME", "ERW_PAGES_TOGETHER", "ERW_READ_TIMING",
                         "GRID_FILES_OUT", "ERW_SIZES")}


class TheCases(unittest.TestCase):
    def test_every_older_block_has_its_cases(self):
        cs = cases()
        for block, kinds in OLDER.items():
            got = {c["grid"] for c in cs if c["block"] == block}
            for k in kinds:
                self.assertIn(k, got, f"{block}: {k}")
        abouts = {c["grid"] for c in cs if c["block"].startswith("older_About ")}
        self.assertEqual(abouts, set(KINDS[:3]))

    def test_a_new_case_checks_what_a_chain_case_checks(self):
        new = [c for c in cases() if c["block"].startswith("older_") or (c["block"].startswith("mixview_") and c["grid"] != "an older block"
                                                                         and c["block"] in ("mixview_now", "mixview_records", "mixview_forecast"))]
        self.assertGreaterEqual(len(new), 60)
        for c in new:
            self.assertIn(c["grid"], KINDS, c["name"])
            self.assertTrue(c["words"], c["name"])
            for k in ("figures", "kinds", "keys", "anchors", "methods", "files", "held"):
                self.assertIn(k, c, c["name"])
            self.assertEqual(sum(c["kinds"].values()), c["figures"], c["name"])
            self.assertFalse(any("page was drawn" in w for w in c["words"]), c["name"])   # the clock is not a fixture
        # the held grid's own held lines, and a figure of the new fixture
        self.assertTrue(any(c["held"] and c["grid"] == "a held grid (ISO-NE)" for c in new))
        self.assertTrue(any(c["kinds"].get("series_esum") for c in new))
        self.assertIn('"name": "mixview_now on /grid?grid=ercot&view=mix", "q": "grid=ercot&view=mix", "block": "mixview_now", "grid": "an older block", "figures": 9, "kinds": {"series": 8, "series_esum": 1}',
                      src("site", "scripts", "test-grid-render.mjs"))

    def test_the_stand_in_names_them_without_moving_the_page(self):
        s = src("site", "scripts", "grid-render-standin.mjs")
        self.assertIn("export const OLDER_MARKS = [", s)
        self.assertIn("export const OLDER_COMPONENTS = { ToolHeader: ", s)
        self.assertIn('if (type === "section" && props.id !== undefined && !SECTIONS.has(node)) opens.push(`older_#${props.id}`);', s)
        self.assertIn('const nm = OLDER_COMPONENTS[type.name]?.() ?? (SECTION_FNS.has(type.name) && typeof props.title === "string" ? `older_${props.title}` : null);', s)
        self.assertIn('const mixNow = fx("grid_mix_now.json");', s)
        # the blocks the page names are as they were (sessions 1404 and 1412)
        self.assertIn('["data-alerts-days", () => "alerts_days"]', s)
        self.assertIn('export const BLOCKS = [["data-grid-panel", (v) => v],', s)


class TheFixture(unittest.TestCase):
    def test_real_rows_with_their_read(self):
        f = json.loads(src("site", "scripts", "fixtures", "grid_mix_now.json"))
        self.assertIn("read once with the anon key", f["about"])
        self.assertRegex(f["read_at"], r"^2026-10-\d\dT\d\d:\d\d:\d\dZ$")
        lat, mon = f["eia930_generation_latest"], f["state_generation_mix_monthly"]
        self.assertEqual({k.split("|")[0] for k in lat}, {"eia930:ERCO", "eia930:ISNE", "eia930:US48"})   # CAISO's mix is not drawn (session 118)
        self.assertEqual({k.split("|")[0] for k in mon}, {"eia:US"})
        for k in ("eia930:ERCO|net_generation_mw", "eia930:ISNE|net_generation_mw", "eia930:US48|net_generation_mw"):
            self.assertGreater(len(lat[k]), 0, k)
        self.assertGreaterEqual(len(mon["eia:US|net_generation_coal_mwh"]), 300)
        for rows in list(lat.values()) + list(mon.values()):
            for ts, v in rows:
                self.assertTrue(re.match(r"^\d{4}-\d\d-\d\d", ts))
                self.assertIsInstance(v, (int, float))


class TheComments(unittest.TestCase):
    def test_the_pins_the_cases_cover_are_annotated(self):
        names = {c["name"] for c in cases()}
        for fn, case in ANNOTATED.items():
            lines = src("tests", fn).split("\n")
            at = [i for i, line in enumerate(lines) if line.strip() == TAG + case]
            self.assertEqual(len(at), 1, fn)
            self.assertIn("self.assert", lines[at[0] + 1], fn)
            self.assertIn(case, names)


class TheNoteAndTheLetter(unittest.TestCase):
    def test_the_method_note(self):
        m = src("docs", "methods", "grid_network.md")
        sec = m[m.index("## The older blocks' files, anchors"):m.index("## Not here")]
        self.assertIn("Session 1422, each older block's render case.", sec)
        self.assertIn("Decisions (chain 111, session 1422): **the older blocks are named in the test's walk, not on the page**", sec)

    def test_no_em_dash(self):
        for parts in CHANGED:
            self.assertNotIn(EM, src(*parts), parts)
        if os.path.exists(os.path.join(ROOT, "archive", "sessions", "SESSION_1422_REPORT.md")):
            self.assertNotIn(EM, src("archive", "sessions", "SESSION_1422_REPORT.md"))


@unittest.skipUnless(NODE and MODULES, "node and site/node_modules (typescript, react) are needed")
class TheRender(unittest.TestCase):
    def test_every_new_case_holds(self):
        r = subprocess.run([NODE, "--import", "./scripts/alias-register.mjs", "--import", "./scripts/tsx-register.mjs", os.path.join("scripts", "test-grid-render.mjs")],
                           cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=600, env=node_env())
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-2000:])
        for c in cases():
            if c["block"].startswith("older_"):
                self.assertIn(f"ok   {c['name']} (", r.stdout)


if __name__ == "__main__":
    unittest.main()
