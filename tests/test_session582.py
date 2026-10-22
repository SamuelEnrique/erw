"""Session 582: the five tools' replications, run as a reader runs them (the chain of 22 October 2026).

Energy Research Warehouse (ERW). Roadmap item 2 asks of each of the five tools "a replication a reader can run". On
22 October 2026 session 582 ran each in a new virtual environment outside the repository, from a folder holding only the
files the page links, and set its figures beside the page's (docs/reviews/replications-2026-10-22.md). One differed: the
datacenter tool's carbon file was a copy of 14 October, and the live set had moved since. The file was rewritten and the
data machine's run now rewrites it every day.

What is held here: each of the four mirrors that claim the standard library only runs with no site-packages (python -I
-S) from a temporary folder holding only its own files, exits 0 and prints the lines the review compares; the datacenter
mirror reads the carbon file beside it; the carbon file's header counts its own rows; the data machine's run rewrites
the carbon file after the hourly CSV and commits it; Research's mirror rebuilds the tenth card /research shows
(peak_hour_moved), every figure equal to its JSON; the review has a row for each of the five tools. Nothing here sets
the environment, reads a table, makes a request or calls a model.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PUBLIC = os.path.join(ROOT, "site", "public")
REVIEW = os.path.join(ROOT, "docs", "reviews", "replications-2026-10-22.md")

# tool: (folder, mirror, its data files, the arguments, the lines the review compares with the page)
MIRRORS = {
    "battery": ("battery", "erw_2026_battery_replication.py", ["erw_2026_battery_dispatch.csv"], [],
                ["last twelve months, total, USD for 100 MW: ", "last twelve months, all streams, USD per kW: ",
                 "debt coverage, last twelve months, times: ", "scenario A, NPV at the hurdle rate, USD per kW: ",
                 "scenario A, breakeven toll, USD per kW-month: ", "a bad month: "]),
    "generator": ("seller", "erw_2026_generator_replication.py", ["erw_2026_generator_hourly.csv"], ["erw_2026_generator_hourly.csv"],
                  ["revenue, last twelve months, USD per kW: ", "price received, weighted by generation, USD per MWh: ",
                   "debt coverage, last twelve months, times: ", "NPV at the hurdle rate, USD million for 100 MW: ",
                   "breakeven PPA price, the whole of the energy for the PPA term, USD per MWh: ", "worst month 1: "]),
    "datacenter": ("datacenter", "erw_2026_datacenter_replication.py", ["erw_2026_datacenter_hourly.csv", "erw_2026_datacenter_carbon.csv"], [],
                   ["market energy, a flat load, last twelve months, USD per MWh: ", "power per GPU-hour, USD: ",
                    "a bad month, nearest rank 4: ", "tonnes of CO2 a year for 100 MW: ",
                    "hours of the hourly window the price and the intensity are both held: ",
                    "a flat load's own hours over them, kg CO2 per MWh (the grid's mean): "]),
    "grid": ("grid", "erw_2026_grid_replication.py", ["erw_2026_grid_replication.csv"], ["erw_2026_grid_replication.csv"],
             ["hour_shown = ", "pairs_reporting = ", "net_import_ERCO = ", "gravity_d_NYIS = "]),
}


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def run_alone(folder, mirror, files, args):
    """The mirror run as a reader runs it: its own folder holds only it and its data files, no site-packages."""
    with tempfile.TemporaryDirectory() as tmp:
        for name in [mirror] + files:
            shutil.copy(os.path.join(PUBLIC, folder, name), os.path.join(tmp, name))
        return subprocess.run([sys.executable, "-I", "-S", mirror, *args], cwd=tmp, capture_output=True, text=True,
                              encoding="utf-8", timeout=600)


class TheMirrorsRunAlone(unittest.TestCase):
    def test_each_runs_with_the_standard_library_alone_and_prints_the_compared_lines(self):
        for tool, (folder, mirror, files, args, lines) in MIRRORS.items():
            with self.subTest(tool=tool):
                done = run_alone(folder, mirror, files, args)
                self.assertEqual(done.returncode, 0, done.stderr[-2000:])
                out = done.stdout.splitlines()
                for start in lines:
                    self.assertTrue(any(line.startswith(start) for line in out), f"{tool}: no line starts {start!r}")

    def test_the_mirrors_import_only_the_standard_library(self):
        for tool, (folder, mirror, _, _, _) in MIRRORS.items():
            text = src("site", "public", folder, mirror)
            names = {m.group(1).split(".")[0] for m in re.finditer(r"^(?:import|from) ([\w.]+)", text, re.M)}
            self.assertLessEqual(names, set(sys.stdlib_module_names), f"{tool}: {sorted(names - set(sys.stdlib_module_names))}")

    def test_without_the_carbon_file_the_datacenter_mirror_still_runs(self):
        folder, mirror, files, args, _ = MIRRORS["datacenter"]
        done = run_alone(folder, mirror, files[:1], args)
        self.assertEqual(done.returncode, 0, done.stderr[-2000:])
        self.assertIn("market energy, a flat load, last twelve months, USD per MWh: ", done.stdout)
        self.assertNotIn("tonnes of CO2 a year for 100 MW: ", done.stdout)


class ResearchsTenthCard(unittest.TestCase):
    def test_the_mirror_rebuilds_peak_hour_moved_and_equals_its_json(self):
        try:
            import numpy  # noqa: F401  (the mirror's one package beyond the standard library)
        except ImportError:
            self.skipTest("numpy is not here")
        findings = os.path.join(PUBLIC, "findings")
        with tempfile.TemporaryDirectory() as tmp:
            for name in os.listdir(findings):
                if name.endswith(".csv") or name == "erw_2026_research_replication.py":
                    shutil.copy(os.path.join(findings, name), tmp)
            done = subprocess.run([sys.executable, "-I", "erw_2026_research_replication.py", tmp, "--json", os.path.join(ROOT, "site", "data", "findings")],
                                  cwd=tmp, capture_output=True, text=True, encoding="utf-8", timeout=600)
        self.assertEqual(done.returncode, 0, done.stdout[-2000:] + done.stderr[-2000:])
        self.assertIn("== peak_hour_moved (erw_2026_peak_hour_solar.csv)", done.stdout)
        ours = [line for line in done.stdout.splitlines() if line.startswith("same  peak_hour_moved.")]
        with open(os.path.join(ROOT, "site", "data", "findings", "peak_hour_moved.json"), encoding="utf-8") as f:
            numbers = json.load(f)["numbers"]
        self.assertEqual(len(ours), len(numbers))
        for key in ("ercot_first_median_hour", "ercot_last_median_hour", "ercot_first_evening_pct", "ercot_last_evening_pct",
                    "ercot_first_solar_mw", "ercot_last_solar_mw"):   # the six callouts /research shows
            self.assertTrue(any(line.startswith(f"same  peak_hour_moved.{key} = ") for line in ours), key)
        self.assertNotIn("DIFFERENT", done.stdout)


class TheCarbonFile(unittest.TestCase):
    def test_its_header_counts_its_own_rows(self):
        lines = src("site", "public", "datacenter", "erw_2026_datacenter_carbon.csv").splitlines()
        self.assertEqual(lines[7], "kind,ts_utc,kg_co2_per_mwh")
        rows = [line.split(",") for line in lines[8:] if line]
        months = [r for r in rows if r[0] == "month"]
        hours = [r for r in rows if r[0] == "hour"]
        self.assertEqual(len(months) + len(hours), len(rows))
        m = re.search(r"kind month, one per month held of carbon_intensity_monthly \((\d+) rows, (\d{4}-\d\d) to (\d{4}-\d\d)\); "
                      r"kind hour, one per hour of carbon_intensity_hourly the live set holds \((\d+) rows, (\S+) to (\S+) UTC", lines[2])
        self.assertIsNotNone(m, lines[2])
        self.assertEqual(int(m.group(1)), len(months))
        self.assertEqual((m.group(2), m.group(3)), (months[0][1][:7], months[-1][1][:7]))
        self.assertEqual(int(m.group(4)), len(hours))
        self.assertEqual((m.group(5), m.group(6)), (hours[0][1][:13], hours[-1][1][:13]))
        self.assertIn("read with the public key at ", lines[4])

    def test_the_data_machines_run_rewrites_it_after_the_hourly_csv_and_commits_it(self):
        text = src("warehouse", "run_data_machine.sh")
        step = 'soft_step dm_datacenter_carbon "$PYTHON" site/scripts/write-datacenter-carbon.py'
        self.assertIn(step, text)
        self.assertGreater(text.index(step), text.index('soft_step dm_datacenter_export "$PYTHON" warehouse/derived/datacenter_hourly_export.py'))
        self.assertLess(text.index(step), text.index("# ---- 4. the commit"))
        paths = text.split("PAGE_PATHS=(", 1)[1].split(")", 1)[0].split()
        self.assertIn("site/public/datacenter/erw_2026_datacenter_carbon.csv", paths)
        # the writer reads with the public key only, and writes nothing when a read fails
        writer = src("site", "scripts", "write-datacenter-carbon.py")
        self.assertIn('key = env("SUPABASE_ANON_KEY")', writer)
        self.assertNotIn("SERVICE", writer)
        self.assertLess(writer.index("r.raise_for_status()"), writer.index('with open(a.out, "w"'))

    def test_the_method_note_says_it_goes_stale(self):
        note = src("docs", "methods", "datacenter_pays_algorithm.md")
        self.assertIn("**The carbon file goes stale too** (session 582).", note)
        self.assertIn("`dm_datacenter_carbon`", note)


class TheReview(unittest.TestCase):
    def test_a_row_for_each_tool_with_its_command_and_exit(self):
        text = src("docs", "reviews", "replications-2026-10-22.md")
        for tool in ("What a battery earns", "What a generator earns", "What a datacenter pays", "The Grid tool", "Research"):
            row = [line for line in text.splitlines() if line.startswith(f"| {tool} |")]
            self.assertTrue(row, tool)
            self.assertRegex(row[0], r"exit 0")
        self.assertIn("python -m venv", text)

    def test_no_em_dash_in_what_this_session_wrote(self):
        for parts in (("docs", "reviews", "replications-2026-10-22.md"), ("tests", "test_session582.py"),
                      ("warehouse", "run_data_machine.sh"), ("docs", "methods", "datacenter_pays_algorithm.md"),
                      ("archive", "sessions", "SESSION_582_REPORT.md")):
            if os.path.exists(os.path.join(ROOT, *parts)):
                self.assertEqual(src(*parts).count(chr(0x2014)), 0, parts)


if __name__ == "__main__":
    unittest.main()
