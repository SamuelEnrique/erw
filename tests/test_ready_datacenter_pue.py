"""wip/ready-datacenter-pue (session 11406, chain 770, part C): the second other choice of the datacenter audit of
26 November, finding 7 (docs/reviews/datacenter-model-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main the facility overhead ratio is the industry's average, 1.56. On this branch it is the hover's own Google
fleet figure, 1.09: every power per GPU-hour is 30.1 percent lower (default case 0.0691 to 0.0483 on today's files)
and 100 MW powers 70,572 GPUs, not 49,310. The power per GPU stays 1.3 (its other choice is wip/ready-datacenter-gpu).
The audit's test (tests/test_audit_datacenter_7.py on wip/audit-datacenter-7) is carried here, asserting the new
default; the replication's do-file, its Python mirror and the exporter carry the same input."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
URL = lambda *p: "file:///" + os.path.join(ROOT, *p).replace("\\", "/")  # noqa: E731
JS = """
const [L, F] = await Promise.all([import(process.argv[1]), import(process.argv[2])]);
const fs = await import("node:fs");
const dir = process.argv[3];
const index = JSON.parse(fs.readFileSync(dir + "/index.json", "utf-8"));
const files = index.grids.ercot.years.map((y) => JSON.parse(fs.readFileSync(dir + "/ercot_" + y + ".json", "utf-8")));
const s = L.span(L.lastTwelve(L.monthsRuled(files, "LZ_NORTH", "rt", { run: "flat", n: 0, pct: 0, shift: 0 }, "forecast").months));
console.log(JSON.stringify({ gpu: L.ASSUMED.gpu.value, pue: L.ASSUMED.pue.value, gs: L.ASSUMED.gpu.source, ps: L.ASSUMED.pue.source, per: s.per,
  h: L.gpuHour(s.per, L.DEFAULTS.gpu, L.DEFAULTS.pue), h13: L.gpuHour(s.per, 1.3, 1.56), n: L.gpus(100, L.DEFAULTS.gpu, L.DEFAULTS.pue), n13: L.gpus(100, 1.3, 1.56) }));
"""


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class GooglesOverheadRatio(unittest.TestCase):
    def test_default_is_googles_109(self):
        out = subprocess.run(["node", "--input-type=module", "-e", JS, URL("site", "lib", "datacenter.ts"), URL("site", "lib", "datacenter", "finance.ts"),
                              os.path.join(ROOT, "site", "data", "datacenter")], capture_output=True, text=True, timeout=300)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        print(json.dumps(r))
        self.assertEqual((r["gpu"], r["pue"]), (1.3, 1.09))
        self.assertIn("Google reports 1.09 for its fleet over twelve months", r["ps"])
        self.assertIn("Uptime Institute, Global Data Center Survey 2024, 1.56", r["ps"])
        self.assertAlmostEqual(r["h"] / r["h13"] - 1, -0.30128, places=4)   # 30.1 percent lower on every GPU-hour
        self.assertEqual(round(r["n"]), 70572)
        self.assertEqual(round(r["n13"]), 49310)

    def test_the_replication_carries_the_same_input(self):
        self.assertIn("scalar s_pue = 1.09\n", src("site", "public", "datacenter", "erw_2026_datacenter_replication.do"))
        self.assertIn("MW, GPU_KW, PUE = 100, 1.3, 1.09", src("site", "public", "datacenter", "erw_2026_datacenter_replication.py"))
        self.assertIn("MW, GPU_KW, PUE = 100, 1.3, 1.09", src("warehouse", "derived", "datacenter_hourly_export.py"))
        self.assertIn("| Facility overhead ratio | 1.09 |", src("docs", "methods", "datacenter_pays_algorithm.md"))


if __name__ == "__main__":
    unittest.main()
