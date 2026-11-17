"""Session 7626: the other choice of the ruling on Michigan's law in the large-load laws table (branch wip/alt-policy-2,
not landed). Michigan's one law, Enrolled H.B. 4906 (Public Act 207 of 2024), is a sales tax exemption for enterprise
data centers with no smallest load; under the other choice it is taken out of the table's scope.

What is held to (lib/largeloadrules.ts, run by node, on site/data/siting/large_load_rules.json built 16 November 2026):
  the laws shown 27 to 26 (-3.7 percent); the laws in effect 10 to 9; the states with a public law 25 to 24 (26 to 25
    with the held law's state); the check key largeload|laws|public reads 26; Michigan is no longer a state with a law;
  one law is out of scope, by its id, with its reason; every reader of the laws takes the same list (the policy page,
    the siting files, the check keys' function).

No request, no model call. Skips when node is absent."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class MichigansLawTakenOut(unittest.TestCase):
    def test_the_counts(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        js = """
import fs from "node:fs";
const L = await import("./lib/largeloadrules.ts");
const f = JSON.parse(fs.readFileSync("data/siting/large_load_rules.json", "utf-8"));
const ls = L.inScopeLaws(f.laws);
console.log(JSON.stringify({ before: f.laws.length, after: ls.length, inEffect: [f.laws.filter((l) => l.status === "in effect").length, ls.filter((l) => l.status === "in effect").length],
  states: [new Set(f.laws.map((l) => l.state)).size, new Set(ls.map((l) => l.state)).size], stat: L.largeLoadStat(f, "largeload|laws|public"), mi: L.lawStates(f).includes("MI") }));
"""
        r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr[-1500:])
        got = json.loads(r.stdout)
        self.assertEqual(got, {"before": 27, "after": 26, "inEffect": [10, 9], "states": [25, 24], "stat": 26, "mi": False})
        self.assertEqual(f"{100 * (26 - 27) / 27:.1f}", "-3.7")

    def test_every_reader_takes_the_same_list(self):
        self.assertIn('"laws_midwest_northeast-05": "a sales tax exemption for enterprise data centers', src("site", "lib", "largeloadrules.ts"))
        self.assertIn("laws: inScopeLaws((largeLoadJson as unknown as LargeLoadFile).laws)", src("site", "lib", "sitingdata.ts"))
        self.assertIn("laws={{ laws: inScopeLaws(ll.laws), held: ll.held_laws,", src("site", "app", "policy", "page.tsx"))
        for t in (src("site", "lib", "largeloadrules.ts"), src("site", "lib", "sitingdata.ts")):
            self.assertNotIn(chr(0x2014), t)


if __name__ == "__main__":
    unittest.main()
