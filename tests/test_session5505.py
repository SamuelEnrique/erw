"""Session 5505 (chain 269, portable laptop window P1): Grid faults row 7, found in the last fresh read of the five.

Each grid's own page (/grid?grid=<grid>) ended with "Reads that failed: dcs: license needed: Amazon Web Services;
Bloomberg; ... news: license needed: ...", about thirty publishers a table: the two reads of tables held for a license
(datacenter_facilities, news_index) were listed as failures, though lib/supabase.ts says a held read is not one
(LicenseNeeded: "nothing was asked") and both sections already say "license needed" in place. lib/grid.ts load() now
leaves a held read out of its errors; a read that does fail is still listed.

Node runs load() with no database named (no network): every unheld read fails as NotConfigured and is listed; the two
held reads are not.
"""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class HeldIsNotFailed(unittest.TestCase):
    def test_the_source(self):
        src = read("site", "lib", "grid.ts")
        self.assertIn('import { HOURLY, LicenseNeeded, rest } from "@/lib/supabase";', src)
        self.assertIn("if (!(e instanceof LicenseNeeded)) errors[what] = (e as Error).message;", src)
        page = read("site", "components", "grid", "YourGrid.tsx")
        self.assertIn('Reads that failed: {Object.entries(d.errors)', page)

    def test_load_leaves_the_held_reads_out_and_lists_the_failed(self):
        status = json.loads(read("site", "data", "license_status.json"))
        tables = status.get("tables", status)
        for t in ("datacenter_facilities", "news_index"):
            if t not in tables or tables[t].get("status") != "license needed":
                self.skipTest(f"{t} is not held in site/data/license_status.json today")
        node = shutil.which("node")
        if not node or not os.path.exists(os.path.join(SITE, "scripts", "alias-register.mjs")) or not os.path.exists(os.path.join(SITE, "content", "docs.json")):
            self.skipTest("node, the site's alias loader or site/content/docs.json is not here")
        script = """
import { load } from "@/lib/grid";
import { DOCS } from "@/lib/markdown";
const g = DOCS.grid_config.find((x) => x.slug === "caiso");
const d = await load(g);
console.log(JSON.stringify(Object.keys(d.errors).sort()));
"""
        env = {k: v for k, v in os.environ.items() if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY")}
        env["SUPABASE_URL"] = ""
        env["SUPABASE_ANON_KEY"] = ""
        r = subprocess.run([node, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", script], cwd=SITE, env=env,
                           capture_output=True, text=True, timeout=180, stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 0, r.stderr[-1500:])
        keys = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertNotIn("dcs", keys)
        self.assertNotIn("news", keys)
        for k in ("demand", "gen", "ci", "queue"):
            self.assertIn(k, keys)

    def test_the_faults_row_and_no_dash(self):
        faults = read("docs", "reviews", "grid-faults-2026-11-13.md")
        self.assertRegex(faults, r"\n\| 7 \|[^\n]*found in session 5505[^\n]*\| fixed \(session 5505\) \|")
        for rel in (("tests", "test_session5505.py"), ("site", "lib", "grid.ts"), ("docs", "reviews", "grid-faults-2026-11-13.md")):
            text = read(*rel)
            self.assertNotIn(chr(0x2014), text, rel)
            self.assertNotIn(chr(0x2013), text, rel)


if __name__ == "__main__":
    unittest.main()
