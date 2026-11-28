"""Session 11408, readied for the owner's ruling (weekend page part 3.4, battery choice 7; the battery audit of 20
November, finding 7, docs/reviews/battery-model-audit-2026-11-20.md): the size field stops at 500 MW, where the
price-taker model's regulation awards begin to pass what ERCOT buys (5,000 MW until now).

Through site/lib/batterystack.ts (run by Node): the default stays 100 MW, 500 MW is read as given, 5,000 MW is brought
to 500 with a line that says why; the form's field and the note say 500. Nothing moves at the default."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "batterystack.ts").replace("\\", "/")


class SizeCap(unittest.TestCase):
    def test_the_size_stops_at_500(self):
        js = ("const L = await import(process.argv[1]);"
              "const at = (mw) => L.inputsOf(mw === null ? {} : { mw: String(mw) }).mw;"
              "console.log(JSON.stringify({ max: L.MAX_MW, d: at(null), a: at(500), b: at(5000),"
              " notes: L.typedNotes({ mw: '5000' }, L.inputsOf({ mw: '5000' })) }));")
        out = subprocess.run(["node", "--input-type=module", "-e", js, LIB], capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertEqual((r["max"], r["d"], r["a"], r["b"]), (500, 100, 500, 500))
        self.assertEqual(r["notes"], ["5,000 MW is outside the size field's bounds, 1 to 500 MW (past about 500 MW the battery would hold more regulation than ERCOT buys): 500 MW is shown."])

    def test_the_form_and_the_note_say_500(self):
        with open(os.path.join(ROOT, "site", "app", "cost-of-power", "battery", "BatteryForm.tsx"), encoding="utf-8") as f:
            self.assertIn('max={500} step="any"', f.read())
        with open(os.path.join(ROOT, "docs", "methods", "battery_earns_algorithm.md"), encoding="utf-8") as f:
            self.assertIn("| `mw` | 100 | 1 to 500 (session 11408: 5,000 until then) |", f.read())


if __name__ == "__main__":
    unittest.main()
