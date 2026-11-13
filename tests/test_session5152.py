"""Session 5152: rows 8 and 9 of the security list (docs/reviews/security-faults-2026-11-13.md), the dependency audits
of 13 November 2026.

Energy Research Warehouse (ERW). No network, no model, no build: the pinned file and the two documents are read.

    row 8    certifi's bundle without the root whose intermediates' keys are compromised (PYSEC-2026-4320): the Python
             3.14 file pins 2026.10.18 or newer, and the pins session 312 and session 1503 made are still there
    row 9    the site's lockfile is as the audit found it: the linter's finding is ruled, not forced

    python -m unittest tests.test_session5152 -v
"""

import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def pins():
    out = {}
    for line in src("requirements-py314.txt").splitlines():
        m = re.match(r"^([A-Za-z0-9_.\-]+)==([^\s#]+)", line)
        if m:
            out[m.group(1).lower()] = m.group(2)
    return out


def version(v):
    return tuple(int(x) for x in re.findall(r"\d+", v))


class ThePythonPins(unittest.TestCase):
    def test_certifi_is_the_bundle_without_the_compromised_root(self):
        self.assertGreaterEqual(version(pins()["certifi"]), (2026, 10, 18))

    def test_the_earlier_security_pins_stand(self):
        p = pins()
        self.assertGreaterEqual(version(p["cryptography"]), (50, 0, 0))    # session 312
        self.assertGreaterEqual(version(p["setuptools"]), (84, 1, 0))      # session 1503
        self.assertGreaterEqual(version(p["lxml"]), (6, 1, 0))             # session 312

    def test_every_line_is_a_pin_or_a_comment(self):
        for line in src("requirements-py314.txt").splitlines():
            if line.strip() and not line.lstrip().startswith("#"):
                self.assertRegex(line, r"^[A-Za-z0-9_.\-]+==[^\s#]+(\s+#.*)?$", line)


class TheSitesLockfile(unittest.TestCase):
    def test_the_site_ships_the_versions_session_1503_set(self):
        pkg = json.loads(src("site", "package.json"))
        self.assertEqual(pkg["dependencies"]["next"], pkg["devDependencies"]["eslint-config-next"])
        self.assertGreaterEqual(version(pkg["dependencies"]["next"]), (16, 4, 5))

    def test_the_linters_finding_is_in_a_development_package_only(self):
        lock = json.loads(src("site", "package-lock.json"))["packages"]
        nested = [k for k in lock if k.endswith("/minimatch") and "@typescript-eslint" in k]
        for k in nested:
            self.assertTrue(lock[k].get("dev"), f"{k} is not a development package: the audit's ruling no longer holds")
        self.assertTrue(lock["node_modules/@typescript-eslint/typescript-estree"].get("dev"))


class TheRecords(unittest.TestCase):
    def test_the_list_and_the_state_file(self):
        rows = {line.split("|")[1].strip(): line for line in src("docs", "reviews", "security-faults-2026-11-13.md").splitlines() if re.match(r"^\| \d+ \|", line)}
        self.assertIn("certifi", rows["8"])
        self.assertIn("gridstatus 0.37.0", rows["8"])
        self.assertIn("**ruling**", rows["9"])
        s = src("docs", "security.md")
        self.assertIn("## Dependency audit, 13 November 2026 (session 5152, chain 237)", s)
        self.assertIn("PYSEC-2026-4320", s)

    def test_no_em_or_en_dash(self):
        for parts in (("tests", "test_session5152.py"), ("requirements-py314.txt",), ("docs", "security.md")):
            t = src(*parts)
            self.assertNotIn(chr(0x2014), t, parts)
            self.assertNotIn(chr(0x2013), t, parts)


if __name__ == "__main__":
    unittest.main()
