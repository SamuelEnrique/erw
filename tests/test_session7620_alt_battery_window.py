"""Session 7620: the other choice of the ruling on test 178 (branch wip/alt-battery-1, not landed). The battery method
note follows the data: its default case is the page's own last twelve months on the table as it stands, not October 2025
to September 2026.

What is held to:
  the page's own library (site/lib/batterystack.ts, run by node) over the live set's rows of battery_stack_monthly for
    ERCOT HB_HUBAVG, 4 hours, perfect foresight, as read on 17 November 2026 (tests/fixtures/session7620/, the public
    table, read only by runs/c7620_battery_live.py) gives the window November 2025 to October 2026 and USD 80.34 per kW;
  the same rows held to September 2026 give the signed figure, USD 81.40, October 2025 to September 2026, so the fixture
    is the table the note was signed on, one month further;
  the note states the new default and the new window beside the signed ones.

No request, no model call. Skips when node is absent."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIXTURE = os.path.join(ROOT, "tests", "fixtures", "session7620", "battery_live_foresight_4h.json")
NOTE = os.path.join(ROOT, "docs", "methods", "battery_earns_algorithm.md")


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout)


def window(upto):
    js = """
import fs from "node:fs";
const B = await import("./lib/batterystack.ts");
const rows = JSON.parse(fs.readFileSync(%s, "utf-8"))["ercot:HB_HUBAVG"].filter((r) => r.ts_utc.slice(0, 7) <= %s);
const x = B.inputsOf({});
const ms = B.monthsOf(rows, "foresight", 4);
const l12 = B.lastTwelve(ms);
console.log(JSON.stringify({ first: l12[0].m, last: l12[11].m, kw: B.stat(rows, [], x, "l12_kw:total") }));
""" % (json.dumps(FIXTURE.replace("\\", "/")), json.dumps(upto))
    return node(js)


class TheNoteFollowsTheData(unittest.TestCase):
    def test_the_newest_window_is_november_2025_to_october_2026_at_80_34(self):
        w = window("9999-12")
        self.assertEqual((w["first"], w["last"]), ("2025-11", "2026-10"))
        self.assertEqual(f"{float(w['kw']):.2f}", "80.34")

    def test_held_to_september_2026_the_rows_give_the_signed_figure(self):
        w = window("2026-09")
        self.assertEqual((w["first"], w["last"]), ("2025-10", "2026-09"))
        self.assertEqual(f"{float(w['kw']):.2f}", "81.40")

    def test_the_note_states_the_new_default_beside_the_signed_one(self):
        with open(NOTE, encoding="utf-8") as f:
            t = f.read()
        self.assertIn("Default: 80.34 on the table of 17 November 2026 (81.40 when signed, October 2025 to September 2026).", t)
        self.assertIn("November 2025 to October 2026 on the table of 17 November 2026", t)
        self.assertIn("This note follows the data", t)
        self.assertNotIn(chr(0x2014), t)


if __name__ == "__main__":
    unittest.main()
