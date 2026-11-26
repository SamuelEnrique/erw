"""Audit of "What a datacenter pays", finding 7 (session 10203, docs/reviews/datacenter-model-audit-2026-11-26.md): the two
GPU defaults (ASSUMED in site/lib/datacenter.ts). Power per GPU is 1.3 kW, from NVIDIA's DGX H100 datasheet as the hover
quotes it: 8 GPUs and 10.2 kW of maximum system power, which is 1.275 kW; 1.3 rounds it up by 1.96 percent, so every
power per GPU-hour is 1.96 percent high and the GPU count 1.9 percent low (49,310 against 50,277 for 100 MW). The
overhead ratio is the industry's average, 1.56; the same hover gives Google's fleet at 1.09, the kind of figure a lab's
own new site would be built to: at 1.09 every power per GPU-hour is 30.1 percent lower and 100 MW powers 70,572 GPUs.

This branch makes no fix: a fix moves printed figures, which is Samuel's ruling. The test shows both through the page's
own library (run by Node), and that the hover's own words hold the figures the defaults leave aside."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "datacenter.ts").replace("\\", "/")
JS = """
const L = await import(process.argv[1]);
console.log(JSON.stringify({ gpu: L.ASSUMED.gpu.value, pue: L.ASSUMED.pue.value, gs: L.ASSUMED.gpu.source, ps: L.ASSUMED.pue.source,
  h0: L.gpuHour(34.07, 1.3, 1.56), h1: L.gpuHour(34.07, 10.2 / 8, 1.56), h2: L.gpuHour(34.07, 1.3, 1.09),
  n0: L.gpus(100, 1.3, 1.56), n1: L.gpus(100, 10.2 / 8, 1.56), n2: L.gpus(100, 1.3, 1.09) }));
"""


class GpuDefaults(unittest.TestCase):
    def test_defaults_and_what_the_hover_holds(self):
        out = subprocess.run(["node", "--input-type=module", "-e", JS, LIB], capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertEqual((r["gpu"], r["pue"]), (1.3, 1.56))
        self.assertIn("8 H100 GPUs and a maximum system power of 10.2 kW", r["gs"])
        self.assertIn("Google reports 1.09", r["ps"])
        self.assertAlmostEqual(r["h0"] / r["h1"] - 1, 0.0196, places=4)       # 1.3 against the datasheet's 1.275
        self.assertAlmostEqual(round(r["n0"]), 49310)
        self.assertAlmostEqual(round(r["n1"]), 50277)
        self.assertAlmostEqual(r["h2"] / r["h0"] - 1, -0.3013, places=4)      # the hover's own 1.09
        self.assertAlmostEqual(round(r["n2"]), 70572)


if __name__ == "__main__":
    unittest.main()
