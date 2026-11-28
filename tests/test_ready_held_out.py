"""Session 11405 (chain 770, part C), decision 1 of docs/reviews/weekend-2026-11-28.md: every held figure the line names
taken out of the site's public files and the repository's current files in one batch. For Samuel's ruling: this branch
(wip/ready-held-out) lands only on his word. The repository's history is not rewritten (a person's act).

The line's items, and where each is counted (the count of held values left in each place):
  the site's pages (tests/test_ready_held_out_site.py, PLACES): /curtailment's two hour counts of ISO-NE and NYISO; the
    generator tool's NYISO and ISO-NE choices; the policy monitor's rows of the Texas PUC; ISO-NE's 414 queue positions
    on /map; the 541 deal-seeded rows on the deals page's companies tab;
  the analysis files (tests/test_ready_held_out_analysis.py, PLACES, carried over from wip/audit-analysis-2's test):
    MISO's 48 gallery charts and its network hub prices (MISO is paused, not licensed); the impact study's default
    download (56 days of NYISO New York City); the weekly results (NYISO's and SPP's regulation prices); the findings
    cards built on NYISO's and ISO-NE's prices;
  this file: the held deals table and its evidence file in git's current files (energy_deals 583 rows, its evidence
    652 rows on origin/main), the daily workflow no longer committing them, and the runner restoring them.

Measured on origin/main (ae43cdc96, 28 November 2026): 1,074 held values in the site's places, 1,952 in the analysis
files, 1,235 rows in git's two deals files: 4,261 in all. On this branch: 0.

Reads the repository's files and git's index only; no table, no request, no model call; the environment is never set."""
import csv
import importlib.util
import io
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEALS = ("warehouse/output/energy_deals.csv", "warehouse/output/energy_deals_evidence.csv")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def module(name):
    spec = importlib.util.spec_from_file_location(f"ready_{name}", os.path.join(ROOT, "tests", f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=60)


def deals_in_git(ref=None):
    """Rows of the held deals' two files in git's current files (the index), or at a ref when one is given."""
    n = 0
    for path in DEALS:
        if ref is None:
            listed = git("ls-files", "--", path)
            if listed.returncode != 0:
                raise unittest.SkipTest("not a git checkout")
            if not listed.stdout.strip():
                continue
            blob = git("show", f":{path}").stdout
        else:
            shown = git("show", f"{ref}:{path}")
            if shown.returncode != 0:
                continue
            blob = shown.stdout
        body = "\n".join(ln for ln in blob.splitlines() if not ln.startswith("#"))
        n += max(0, sum(1 for _ in csv.reader(io.StringIO(body))) - 1)
    return n


def every_place():
    places = {"git: the held deals table and its evidence file": deals_in_git}
    for name in ("test_ready_held_out_site", "test_ready_held_out_analysis"):
        places.update(module(name).PLACES)
    return places


class NoHeldValueLeft(unittest.TestCase):
    def test_zero_held_values_in_every_place(self):
        left = {name: fn() for name, fn in every_place().items()}
        self.assertEqual({k: v for k, v in left.items() if v}, {})
        self.assertGreaterEqual(len(left), 15)

    def test_the_deals_files_leave_git_and_the_workflow(self):
        self.assertEqual(deals_in_git(), 0)
        ignore = src(".gitignore")
        yml = src(".github", "workflows", "daily-prices.yml")
        for path in DEALS:
            self.assertNotIn("!" + path, ignore)
            self.assertNotIn(path, yml)
        self.assertIn("warehouse/output/*.csv", ignore)

    def test_the_runner_restores_the_deals_or_skips_their_steps(self):
        sh = src("warehouse", "run_daily.sh")
        self.assertIn("restore_tables.py energy_deals energy_deals_evidence --no-redivis", sh)
        guard = sh.index("if [ -e warehouse/output/energy_deals.csv ]")
        self.assertLess(guard, sh.index('model_step deals "$PYTHON" warehouse/deals/extract.py'))
        self.assertLess(sh.index("seed_from_deals.py"), sh.index("deal_counterparties skipped"))


if __name__ == "__main__":
    unittest.main()
