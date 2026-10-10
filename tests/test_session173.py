"""Session 173: Automated Analysis finished. What is held to: the two fonts and their license texts are bundled under
site/public/fonts/ byte for byte as Google Fonts' repository ships them (sha256 pinned here, recorded in the folder's
README with the pull's accounting); the Roundup's runner restores the templates' own tables too (warehouse/analysis/run.py
--tables prints them as one pattern, and roundup.yml syncs it after the watch list's and the findings' patterns and before
the Roundup is written); the pattern covers every template's tables; the three cards on disk are the ones recomputed on
the data machine. No request and no model call is made here; the environment is read, never set."""
import hashlib
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FONTS = os.path.join(ROOT, "site", "public", "fonts")
EM = chr(0x2014)
SHA = {
    "SourceSerif4-Variable.ttf": ("97b2d4da6e3cb494b5a1e66ae176914d852ccabef49e0c02c0df25f3e39aca0b", 1209508),
    "SourceSerif4-Italic-Variable.ttf": ("15fbc7e4679489a501998c3669272637a6646388ef7e4bd77eebb5bf967a1f42", 855432),
    "Inter-Variable.ttf": ("29160a80ff49ddcab2c97711247e08b1fab27a484a329ce8b813d820dc559031", 876576),
    "OFL-SourceSerif4.txt": ("5f94c3fd3a23131a417ab5a0c8452de57e70c3cfb9f604d88241f7065ebf9fd9", 4400),
    "OFL-Inter.txt": ("5b9321a4298cfeb6b34354164a1c3afc3db114569984c502b9b35d988fd58c57", 4377),
}
FILES = ("site/public/fonts/README.md", ".github/workflows/roundup.yml", "warehouse/analysis/run.py", "tests/test_session173.py",
         "archive/sessions/SESSION_173_REPORT.md")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheFonts(unittest.TestCase):
    def test_the_five_files_are_the_repositorys_byte_for_byte(self):
        for name, (sha, size) in SHA.items():
            p = os.path.join(FONTS, name)
            self.assertTrue(os.path.exists(p), name)
            with open(p, "rb") as f:
                b = f.read()
            self.assertEqual(len(b), size, name)
            self.assertEqual(hashlib.sha256(b).hexdigest(), sha, name)

    def test_the_licenses_are_the_open_font_license(self):
        for name, who in (("OFL-SourceSerif4.txt", "Source Serif 4 Project Authors"), ("OFL-Inter.txt", "Inter Project Authors")):
            t = src("site", "public", "fonts", name)
            self.assertIn(who, t)
            self.assertIn("SIL Open Font License", t)
            self.assertIn("Version 1.1", t)

    def test_the_readme_records_the_pull(self):
        r = src("site", "public", "fonts", "README.md")
        for sha, _ in SHA.values():
            self.assertIn(sha, r)
        for word in ("google/fonts", "Nine requests", "ERW research project, github.com/SamuelEnrique/erw", "robots"):
            self.assertIn(word, r, word)

    def test_the_render_frame_hides_the_site_header_and_fits_the_wide_frame(self):
        css = src("site", "app", "analysis", "card", "render.css")
        self.assertIn("body:has(.finding-render) > header", css)
        self.assertIn("body:has(.finding-render) > footer", css)
        self.assertIn("@media (min-aspect-ratio: 3/2)", css)
        self.assertIn("[data-finding-chart] { height: 280px !important; }", css)
        for name in ("batteries_lunch", "gas_sets_price", "queue_divorce"):
            for size in ("1080x1350", "1600x900"):
                p = os.path.join(ROOT, "site", "public", "findings", f"{name}_{size}.png")
                self.assertTrue(os.path.exists(p), p)
                with open(p, "rb") as f:
                    head = f.read(24)
                self.assertEqual(head[:8], bytes([137, 80, 78, 71, 13, 10, 26, 10]), "a PNG")
                w, h = int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")
                self.assertEqual((w, h), tuple(int(x) for x in size.split("x")), (name, size))
            self.assertTrue(os.path.exists(os.path.join(ROOT, "docs", "analysis", "findings", f"{name}_1600x900.png")), name)

    def test_the_render_frame_and_the_renderer_name_these_files(self):
        css = src("site", "app", "analysis", "card", "render.css")
        mjs = src("site", "scripts", "render-cards.mjs")
        for name in ("SourceSerif4-Variable.ttf", "SourceSerif4-Italic-Variable.ttf", "Inter-Variable.ttf"):
            self.assertIn(name, css, name)
            self.assertIn(name, mjs, name)


class TheRoundupsTables(unittest.TestCase):
    def test_run_py_prints_every_templates_tables_as_one_pattern(self):
        p = subprocess.run([sys.executable, os.path.join(ROOT, "warehouse", "analysis", "run.py"), "--tables"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=ROOT)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        pat = p.stdout.strip().splitlines()[-1]
        self.assertTrue(pat.startswith("^(") and pat.endswith(")$"), pat)
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis"))
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "templates"))
        import templates
        tabs = {t for m in templates.load_all() for t in m.TABLES}
        self.assertGreater(len(tabs), 30)
        for t in sorted(tabs):
            self.assertTrue(re.match(pat, t), t)
        self.assertIn("portwatch_chokepoint_transits", pat, "the table no restore brought before session 173")
        self.assertIsNone(re.match(pat, "news_stories"))

    def test_the_workflow_restores_the_templates_tables_before_the_roundup(self):
        y = src(".github", "workflows", "roundup.yml")
        line = next(l for l in y.splitlines() if "warehouse/news/roundup.py;" in l)
        # session 176: the analysis and the Roundup each ask the daily model budget first (warehouse/health.py budget), so
        # the two commands are no longer joined by one "&&"; the order is what this test holds: restore, analysis, Roundup
        for step in ("upload.py --restore", "watch.py --tables", "run_finding.py --tables", "run.py --tables", "eia_fuels.py",
                     "then python warehouse/analysis/run.py;", "then python warehouse/news/roundup.py;"):
            self.assertIn(step, line, step)
        self.assertLess(line.find("run_finding.py --tables"), line.find("analysis/run.py --tables"))
        self.assertLess(line.find("analysis/run.py --tables"), line.find("then python warehouse/analysis/run.py;"))
        self.assertLess(line.find("then python warehouse/analysis/run.py;"), line.find("then python warehouse/news/roundup.py;"))
        self.assertIn("|| echo 'the templates, not every table could be restored", line, "a failed restore never stops the Roundup")
        self.assertIn("Session 173", y)


class TheCards(unittest.TestCase):
    def test_the_three_cards_were_computed_on_the_data_machine_on_10_october(self):
        import json
        for name in ("batteries_lunch", "gas_sets_price", "queue_divorce"):
            card = json.load(open(os.path.join(ROOT, "site", "data", "findings", f"{name}.json"), encoding="utf-8"))
            self.assertTrue(card["computed_at"].startswith("2026-10-10T"), (name, card["computed_at"]))
            csv_name = card.get("downloads", {}).get("csv") or next((v for k, v in card.items() if isinstance(v, str) and v.endswith(".csv")), None)
            if csv_name and os.path.exists(os.path.join(ROOT, "site", "public", "findings", os.path.basename(csv_name))):
                with open(os.path.join(ROOT, "site", "public", "findings", os.path.basename(csv_name)), "rb") as f:
                    self.assertEqual(hashlib.sha256(f.read()).hexdigest(), card["csv_sha256"], name)

    def test_no_em_dash_in_this_sessions_files(self):
        for rel in FILES:
            p = os.path.join(ROOT, *rel.split("/"))
            if os.path.exists(p):
                self.assertNotIn(EM, src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
