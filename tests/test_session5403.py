"""Session 5403 (chain 255, portable laptop window P1): Grid faults row 4. MISO's local hour read "6:00 PM GMT-5" on its
grid page (the Mix sentence, the hour cards, the conditions) beside the other grids' "EST" and "CST": MISO keeps
Eastern Standard Time all year, the zone Etc/GMT+5, which Intl names "GMT-5". site/lib/gridtool.ts zoneWords gives it
MISO's own name, "EST", in every season, and leaves every other zone as Intl names it; the three formatters use it.
Node runs the function on Intl's own output (no build, no network).
"""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
FILES = {"components/grid/NowView.tsx": 1, "components/grid/YourGrid.tsx": 1, "components/grid/Conditions.tsx": 1}


def src(rel):
    with open(os.path.join(SITE, *rel.split("/")), encoding="utf-8") as f:
        return f.read()


class ZoneWords(unittest.TestCase):
    def test_every_formatter_of_a_short_zone_name_uses_it(self):
        for rel, n in FILES.items():
            text = src(rel)
            self.assertEqual(text.count('timeZoneName: "short" }).format('), n, rel)
            self.assertEqual(len(re.findall(r'zoneWords\(new Intl\.DateTimeFormat\("en-US", \{ timeZone: tz,[^\n]*timeZoneName: "short" \}\)\.format\(new Date\(\w+\)\), tz\)', text)), n, rel)
            self.assertRegex(text, r'import \{[^}]*\bzoneWords\b[^}]*\} from "@/lib/gridtool"', rel)

    def test_miso_is_named_est_in_every_season_and_no_other_zone_moves(self):
        node = shutil.which("node")
        if not node or not os.path.exists(os.path.join(SITE, "scripts", "alias-register.mjs")):
            self.skipTest("node or the site's alias loader is not here")
        script = """
import { zoneWords } from "@/lib/gridtool";
const f = (tz, t) => new Intl.DateTimeFormat("en-US", { timeZone: tz, month: "short", day: "numeric", hour: "numeric", minute: "2-digit", timeZoneName: "short" }).format(new Date(t));
const out = {};
for (const [tz, t] of [["Etc/GMT+5", "2026-11-12T23:00:00Z"], ["Etc/GMT+5", "2026-07-12T23:00:00Z"], ["America/New_York", "2026-11-12T23:00:00Z"],
                       ["America/New_York", "2026-07-12T23:00:00Z"], ["America/Chicago", "2026-11-12T23:00:00Z"]]) {
  out[tz + " " + t] = [f(tz, t), zoneWords(f(tz, t), tz)];
}
out["null"] = zoneWords("Nov 12, 6:00 PM GMT-5", null);
console.log(JSON.stringify(out));
"""
        r = subprocess.run([node, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", script], cwd=SITE,
                           capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr[-1500:])
        out = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual(out["Etc/GMT+5 2026-11-12T23:00:00Z"], ["Nov 12, 6:00 PM GMT-5", "Nov 12, 6:00 PM EST"])
        self.assertEqual(out["Etc/GMT+5 2026-07-12T23:00:00Z"], ["Jul 12, 6:00 PM GMT-5", "Jul 12, 6:00 PM EST"])
        for k in ("America/New_York 2026-11-12T23:00:00Z", "America/New_York 2026-07-12T23:00:00Z", "America/Chicago 2026-11-12T23:00:00Z"):
            self.assertEqual(out[k][0], out[k][1], k)
        self.assertEqual(out["America/New_York 2026-07-12T23:00:00Z"][0], "Jul 12, 7:00 PM EDT")
        self.assertEqual(out["null"], "Nov 12, 6:00 PM GMT-5")

    def test_the_faults_file_has_the_row(self):
        with open(os.path.join(ROOT, "docs", "reviews", "grid-faults-2026-11-13.md"), encoding="utf-8") as f:
            self.assertRegex(f.read(), r"\| 4 \|.*GMT-5.*\| fixed \(session 5403\) \|")


if __name__ == "__main__":
    unittest.main()
