"""wip/ready-datacenter-gpu (session 11406, chain 770, part C): the first other choice of the datacenter audit of
26 November, finding 7 (docs/reviews/datacenter-model-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main the power per GPU is 1.3 kW, the datasheet's 10.2 kW for 8 GPUs (1.275) rounded up. On this branch it is
1.275 kW: every power per GPU-hour is 1.9 percent lower (default case 0.0691 to 0.0678 on the page's files of today)
and 100 MW powers 50,277 GPUs, not 49,310. The overhead ratio stays 1.56 (its other choice is wip/ready-datacenter-pue).
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
console.log(JSON.stringify({ gpu: L.ASSUMED.gpu.value, pue: L.ASSUMED.pue.value, gs: L.ASSUMED.gpu.source, per: s.per,
  h: L.gpuHour(s.per, L.DEFAULTS.gpu, L.DEFAULTS.pue), h13: L.gpuHour(s.per, 1.3, 1.56), n: L.gpus(100, L.DEFAULTS.gpu, L.DEFAULTS.pue), n13: L.gpus(100, 1.3, 1.56) }));
"""


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheDatasheetsPowerPerGpu(unittest.TestCase):
    def test_default_is_the_datasheets_1275(self):
        out = subprocess.run(["node", "--input-type=module", "-e", JS, URL("site", "lib", "datacenter.ts"), URL("site", "lib", "datacenter", "finance.ts"),
                              os.path.join(ROOT, "site", "data", "datacenter")], capture_output=True, text=True, timeout=300)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        print(json.dumps(r))
        self.assertEqual((r["gpu"], r["pue"]), (1.275, 1.56))
        self.assertIn("8 H100 GPUs and a maximum system power of 10.2 kW, so 1.275 kW per GPU", r["gs"])
        self.assertNotIn("about 1.3", r["gs"])
        self.assertAlmostEqual(r["h"] / r["h13"] - 1, -0.01923, places=4)   # 1.9 percent lower on every GPU-hour
        self.assertEqual(round(r["n"]), 50277)
        self.assertEqual(round(r["n13"]), 49310)

    def test_the_replication_carries_the_same_input(self):
        self.assertIn("scalar s_gpu_kw = 1.275\n", src("site", "public", "datacenter", "erw_2026_datacenter_replication.do"))
        self.assertIn("MW, GPU_KW, PUE = 100, 1.275, 1.56", src("site", "public", "datacenter", "erw_2026_datacenter_replication.py"))
        self.assertIn("MW, GPU_KW, PUE = 100, 1.275, 1.56", src("warehouse", "derived", "datacenter_hourly_export.py"))
        self.assertIn("| Power per GPU | 1.275 kW |", src("docs", "methods", "datacenter_pays_algorithm.md"))


if __name__ == "__main__":
    unittest.main()
