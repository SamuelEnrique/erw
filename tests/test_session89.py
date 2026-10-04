"""Session 89: the findings brief (docs/briefs/findings_2026-10-04.md). No finding without a row behind it.

Energy Research Warehouse (ERW). Every check key in the brief is read here and compared with the table it names:
a `series|<table>|<entity>|<variable>|<time>` key with that row's value, and a `bs|<battery>|<statistic>` key with the
battery page's own statistic, recomputed by site/lib/batterystack.ts from the rows of battery_stack_monthly. A key
whose table is not on the machine is skipped and counted; the form of the brief is tested everywhere.

    python -m unittest tests.test_session89 -v
"""

import json
import os
import re
import shutil
import subprocess
import sys
import unittest
from decimal import ROUND_HALF_UP, Decimal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))

BRIEF = os.path.join(ROOT, "docs", "briefs", "findings_2026-10-04.md")
OUT = os.path.join(ROOT, "warehouse", "output")
KEY = re.compile(r"`((?:series|bs)\|[^`]+)` = (-?[0-9][0-9.]*)")


def brief():
    with open(BRIEF, encoding="utf-8") as f:
        return f.read()


def findings(text):
    """The ten findings: (number, title, body)."""
    parts = re.split(r"^### (\d+)\. (.+)$", text, flags=re.M)
    out = []
    for i in range(1, len(parts), 3):
        body = parts[i + 2].split("\n## ")[0]
        out.append((int(parts[i]), parts[i + 1].strip(), body))
    return out


def decimals(stated):
    return len(stated.split(".")[1]) if "." in stated else 0


def half_up(value, d):
    """value to d decimals, a half rounded up, as a reader rounds and as the site prints (18,204.5 MW reads 18,205)."""
    q = Decimal(1).scaleb(-d)
    return float(Decimal(repr(value)).quantize(q, rounding=ROUND_HALF_UP))


class Form(unittest.TestCase):
    def setUp(self):
        self.text = brief()
        self.f = findings(self.text)

    def test_ten_findings_each_with_its_number_table_key_and_one_caveat(self):
        self.assertEqual([n for n, _, _ in self.f], list(range(1, 11)))
        for n, title, body in self.f:
            self.assertEqual(body.count("- **Number:**"), 1, n)
            self.assertEqual(body.count("- **Table:**"), 1, n)
            self.assertEqual(body.count("- **Check keys:**"), 1, n)
            self.assertEqual(body.count("- **Caveat:**"), 1, n)                # one caveat, not a list of them
            self.assertGreaterEqual(len(KEY.findall(body)), 1, n)              # no finding without a row behind it
            self.assertTrue(title.endswith("."), n)
            self.assertEqual(len(re.findall(r"[.!?](?:\s|$)", title)), 1, (n, title))   # one sentence
            table = re.search(r"- \*\*Table:\*\* `([a-z0-9_]+)`", body).group(1)
            for key, _ in KEY.findall(body.split("- **Caveat:**")[0]):
                self.assertIn(table, key.split("|")[1] if key.startswith("series|") else "battery_stack_monthly", (n, key))

    def test_the_six_subjects_are_all_there(self):
        heads = re.findall(r"^## (.+)$", self.text, flags=re.M)
        self.assertEqual(heads[:6], ["Storage", "Duration", "The evening shoulder", "Battery revenue", "California's imports", "The December 2025 data break"])

    def test_no_em_dash(self):
        self.assertNotIn(chr(0x2014), self.text)
        with open(__file__, encoding="utf-8") as f:
            self.assertNotIn(chr(0x2014), f.read())

    def test_every_figure_in_a_number_line_is_one_of_its_keys(self):
        # each figure stated in a finding's Number line is the rounding of a value its keys give
        for n, _, body in self.f:
            line = re.search(r"- \*\*Number:\*\* (.+)", body).group(1)
            values = [float(v) for _, v in KEY.findall(body)]
            for fig in re.findall(r"(?<![A-Za-z0-9])\d[\d,]*\.?\d*", line):
                s = fig.rstrip(".").replace(",", "")
                if re.fullmatch(r"20\d\d", s):                               # a year
                    continue
                d = decimals(s)
                self.assertTrue(any(half_up(v, d) == float(s) for v in values), (n, fig, values))


class Rows(unittest.TestCase):
    """Every key against its table, where the machine holds the table."""

    @classmethod
    def setUpClass(cls):
        cls.keys = KEY.findall(brief())
        cls.tables = {}

    def table(self, name):
        if name not in self.tables:
            path = os.path.join(OUT, name + ".csv")
            if not os.path.exists(path):
                self.tables[name] = None
            else:
                import storage_buildout as sb
                t = sb.read(path)
                self.tables[name] = {(e, v, ts): float(x) for e, v, ts, x in zip(t["entity"], t["variable"], t["ts_utc"], t["value"])}
        return self.tables[name]

    def test_each_series_key_is_a_row_with_that_value(self):
        checked = skipped = 0
        for key, stated in self.keys:
            if not key.startswith("series|"):
                continue
            _, name, entity, variable, ts = key.split("|")
            t = self.table(name)
            if t is None:
                skipped += 1
                continue
            self.assertIn((entity, variable, ts), t, key)
            self.assertEqual(half_up(t[(entity, variable, ts)], decimals(stated)), float(stated), key)
            checked += 1
        self.assertGreaterEqual(checked + skipped, 25)
        if not checked:
            self.skipTest("none of the brief's tables is on this machine")

    def test_each_battery_key_is_the_pages_statistic(self):
        node = shutil.which("node")
        path = os.path.join(OUT, "battery_stack_monthly.csv")
        if not node or not os.path.exists(path):
            self.skipTest("node or battery_stack_monthly.csv is not on this machine")
        import storage_buildout as sb
        t = sb.read(path)
        bs = [(k, v) for k, v in self.keys if k.startswith("bs|")]
        self.assertGreaterEqual(len(bs), 6)
        rows = [dict(entity=e, variable=v, ts_utc=ts, value=float(x)) for e, v, ts, x in zip(t["entity"], t["variable"], t["ts_utc"], t["value"])]
        dump = os.path.join(ROOT, "runs", "session89_rows_for_test.json")
        os.makedirs(os.path.dirname(dump), exist_ok=True)
        with open(dump, "w", encoding="utf-8") as f:
            json.dump(dict(rows=rows, keys=[k for k, _ in bs]), f)
        js = """
import fs from 'node:fs';
import * as B from './lib/batterystack.ts';
const d = JSON.parse(fs.readFileSync(process.argv[1], 'utf-8'));
const out = {};
for (const key of d.keys) {
  const [, inputs, stat] = key.split('|');
  const x = B.parseKey(inputs);
  if (B.inputsKey(x) !== inputs) throw new Error('not a battery the page shows: ' + inputs);
  const entity = B.gridOf(x.grid).entity;
  const rows = d.rows.filter((r) => r.entity === entity && r.variable.startsWith(`${x.strat}_${x.dur}h_`));
  out[key] = B.stat(rows, [], x, stat);
}
console.log(JSON.stringify(out));
"""
        r = subprocess.run([node, "--input-type=module", "-e", js, dump], cwd=SITE, capture_output=True, text=True, timeout=180)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        got = json.loads(r.stdout.strip().splitlines()[-1])
        for key, stated in bs:
            self.assertIsNotNone(got[key], key)
            self.assertEqual(half_up(got[key], decimals(stated)), float(stated), key)


if __name__ == "__main__":
    unittest.main()
