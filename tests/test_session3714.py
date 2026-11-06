"""Session 3714 (chain 208): the thin page-file rebuild of 6 November 2026, root-caused in the runner's restore step
(warehouse/scheduled.py did not name caiso_fuel_supply_history among mix_profile's inputs, so the runner never restored
it and the builder wrote CAISO's mix without its hydro-gap months), and the guard of the runner's commit step
(scripts/never_thinner.py): a page file is never committed with less history than main holds. The test fails on a
shorter history: the thinned copy of 6 November is refused against the copy before it. No network, no model.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THINNED = "e2794ff06"   # "Daily prices 2026-11-06": the runner's catch-up run that thinned CAISO's mix


def module(name, *parts):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, *parts))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def git(args, cwd=ROOT):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL)


def months(first, last, skip=()):
    out, (y, m) = {}, (int(first[:4]), int(first[5:]))
    while f"{y:04d}-{m:02d}" <= last:
        k = f"{y:04d}-{m:02d}"
        if k not in skip:
            out[k] = {"avg": {}}
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


class TheRule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.n = module("never_thinner", "scripts", "never_thinner.py")

    def test_a_shorter_history_is_refused(self):
        old = {"first": "2019-01", "months": months("2019-01", "2026-09")}
        gap = [f"2019-{m:02d}" for m in range(10, 13)] + [f"2020-{m:02d}" for m in range(1, 9)]
        new = {"first": "2019-01", "months": months("2019-01", "2026-09", skip=gap)}
        why = self.n.thinner(new, old)
        self.assertIsNotNone(why)
        self.assertIn("11 months HEAD holds are gone (2019-10 to 2020-08)", why)

    def test_a_later_start_is_refused(self):
        self.assertIsNotNone(self.n.thinner({"first": "2021-01", "months": months("2021-01", "2026-09")},
                                            {"first": "2019-01", "months": months("2019-01", "2026-09")}))
        self.assertIsNotNone(self.n.thinner({"t0": 470000, "n": 20000}, {"t0": 469255, "n": 28920}))

    def test_a_longer_or_equal_history_passes(self):
        old = {"first": "2019-01", "months": months("2019-01", "2026-09")}
        self.assertIsNone(self.n.thinner({"first": "2019-01", "months": months("2019-01", "2026-10")}, old))
        self.assertIsNone(self.n.thinner(old, old))
        self.assertIsNone(self.n.thinner({"t0": 469255, "n": 29000}, {"t0": 469255, "n": 28920}))
        # the newest month may be withdrawn (a month rebuilt as not yet whole)
        self.assertIsNone(self.n.thinner({"first": "2019-01", "months": months("2019-01", "2026-08")}, old))


class TheSixthOfNovember(unittest.TestCase):
    def test_the_thinned_caiso_mix_is_refused(self):
        n = module("never_thinner_6", "scripts", "never_thinner.py")
        new, old = git(["show", f"{THINNED}:site/data/mix/caiso.json"]), git(["show", f"{THINNED}^:site/data/mix/caiso.json"])
        if new.returncode or old.returncode:
            self.skipTest("the commit of 6 November is not in this clone's history (a shallow checkout)")
        new, old = json.loads(new.stdout), json.loads(old.stdout)
        self.assertLess(len(new["months"]), len(old["months"]))
        self.assertIsNotNone(n.thinner(new, old))


class TheStagedGuard(unittest.TestCase):
    def test_a_thinner_staged_file_is_put_back(self):
        tmp = tempfile.mkdtemp(prefix="erw-s3714-")
        try:
            git(["init", "--quiet", tmp], cwd=tmp)
            git(["config", "user.email", "t@example.org"], cwd=tmp)
            git(["config", "user.name", "t"], cwd=tmp)
            os.makedirs(os.path.join(tmp, "site", "data", "mix"))
            os.makedirs(os.path.join(tmp, "scripts"))
            shutil.copy(os.path.join(ROOT, "scripts", "never_thinner.py"), os.path.join(tmp, "scripts"))
            path = os.path.join(tmp, "site", "data", "mix", "caiso.json")
            full = {"first": "2019-01", "months": months("2019-01", "2026-09")}
            with open(path, "w", encoding="utf-8") as f:
                json.dump(full, f)
            git(["add", "."], cwd=tmp)
            git(["commit", "--quiet", "-m", "full"], cwd=tmp)
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"first": "2021-01", "months": months("2021-01", "2026-09")}, f)
            git(["add", "site/data/mix/caiso.json"], cwd=tmp)
            p = subprocess.run([sys.executable, os.path.join(tmp, "scripts", "never_thinner.py"), "--staged"], cwd=tmp,
                               capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("site/data/mix/caiso.json", p.stdout)
            self.assertEqual(git(["diff", "--cached", "--name-only"], cwd=tmp).stdout.strip(), "")
            with open(path, encoding="utf-8") as f:
                self.assertEqual(json.load(f), full)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TheRestoreStep(unittest.TestCase):
    def test_mix_profile_names_every_table_it_reads(self):
        # named as an input, never asked of the archive (session 114's rule for this builder): without it the step skips
        s = module("scheduled", "warehouse", "scheduled.py")
        job = s.JOBS["mix_profile"]
        self.assertIn("caiso_fuel_supply_history", job["tables"])
        self.assertNotIn("caiso_fuel_supply_history", job.get("restore", []))
        with open(os.path.join(ROOT, "warehouse", "derived", "mix_profile.py"), encoding="utf-8") as f:
            self.assertIn('HISTORY = "caiso_fuel_supply_history"', f.read())


if __name__ == "__main__":
    unittest.main()
