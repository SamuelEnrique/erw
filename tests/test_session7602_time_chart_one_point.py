"""Session 7602 (chain 305, the portable laptop): row 63 of docs/state/browser_reads_wanted.md, read in a browser on a
build of the old laptop's branches. The interconnection explorer's one-year view (`?queue=spp&from=2018&to=2018`) drew
its withdrawn share on an axis of 0.6 to 1.8: the shared chart (site/components/TimeChart.tsx, bounds) gave a value
alone one whole unit above it. A value alone is now padded by a tenth of its size on each side; a zero alone keeps its
axis of 0 to 1; a chart of more than one value is as it was.
Energy Research Warehouse (ERW)."""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
DASHES = (chr(0x2014), chr(0x2013))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def bounds_js():
    """STEPS, nice and bounds as the file holds them, their type notes taken out so that node runs them."""
    s = src("site", "components", "TimeChart.tsx")
    steps = re.search(r"const STEPS = \[[^\]]*\];", s).group(0)
    nice = re.search(r"const nice = \(span: number\) => [^\n]*", s).group(0).replace("(span: number)", "(span)")
    body = re.search(r"function bounds\(vs: number\[\], fromZero: boolean\): Bounds \{.*?\n\}", s, re.S).group(0)
    body = body.replace("function bounds(vs: number[], fromZero: boolean): Bounds", "function bounds(vs, fromZero)")
    return "\n".join([steps, nice, body])


def run(cases):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on the path")
    code = bounds_js() + f"\nconst cases = {json.dumps(cases)};\nconsole.log(JSON.stringify(cases.map(([vs, z]) => bounds(vs, z))));"
    out = subprocess.run([exe, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError(out.stderr[-2000:])
    return json.loads(out.stdout)


class OneValueAlone(unittest.TestCase):
    def test_a_share_alone_stays_near_itself(self):
        share, wait, zero, zero_from, neg = run([[[0.75], False], [[7.0], False], [[0], False], [[0], True], [[-4.0], False]])
        self.assertLessEqual(share["hi"], 0.9, share)       # the case of row 63: no tick of 1.2, 1.4, 1.6, 1.8
        self.assertGreaterEqual(share["lo"], 0.6, share)
        self.assertLess(share["lo"], 0.75)
        self.assertGreater(share["hi"], 0.75)
        self.assertLessEqual(wait["hi"] - wait["lo"], 2, wait)
        self.assertTrue(wait["lo"] < 7 < wait["hi"], wait)
        self.assertEqual((zero["lo"], zero["hi"]), (0, 1))
        self.assertEqual((zero_from["lo"], zero_from["hi"]), (0, 1))
        self.assertTrue(neg["lo"] < -4 < neg["hi"], neg)

    def test_more_than_one_value_is_as_it_was(self):
        a, b = run([[[0.2, 0.9], False], [[3, 12], True]])
        self.assertLessEqual(a["lo"], 0.2)
        self.assertGreaterEqual(a["hi"], 0.9)
        self.assertEqual(b["lo"], 0)
        self.assertGreaterEqual(b["hi"], 12)

    def test_the_comment_names_the_row_and_no_dash(self):
        s = src("site", "components", "TimeChart.tsx")
        self.assertIn("browser read row 63", s)
        for ch in DASHES:
            self.assertNotIn(ch, s)


if __name__ == "__main__":
    unittest.main()
