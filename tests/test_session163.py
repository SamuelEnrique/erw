"""Session 163: "How long a large load waits", in the section "How soon" of /cost-of-power (in review).

Energy Research Warehouse (ERW). No request is made, no model is called and nothing is written outside a temporary
folder. The module reads the environment and never sets it.

    TheBuilder        warehouse/derived/how_soon.py on rows MADE UP FOR THE TEST: a median only on five or more, a small
                      group as its count and two bounds, one request as "too few to show"; lower bounds marked; an entity
                      on none of the page's grids left out and named; MISO never; a stated figure with no sentence; a
                      file that would hold a request's name or a request-level field is refused; a table that is missing
                      writes nothing.
    TheFile           where site/data/datacenter/how_soon.json is on the machine: aggregates only (no request-level
                      field, no megawatt, no sentence of a document), lower bounds marked, the counts add up, nothing
                      for MISO, every stated figure with its document's address.
    AgainstTheTables  where the two internal tables are on the machine (warehouse/output of this copy, or the directory
                      ERW_TABLES_DIR names): each aggregate equals the same figure worked again from the raw rows by
                      this file's own code; no request's name or queue position is in the file; every stated figure is
                      a row of the statements table.
    TheSentence       site/scripts/test-howsoon.mjs passes; on the real file every number of each grid's sentence is a
                      number of the file.
    ThePage           in review; the block stands in "How soon" between the section's table and "Rules in motion";
                      one site file and nothing else; nothing the section showed is dropped; no live page and no shared
                      component takes anything of it; no em dash; the Method note has its section.
On the built site: node site/scripts/check-how-soon.mjs <base>.

    python -m unittest tests.test_session163
"""

import csv
import io
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import how_soon as hs  # noqa: E402

NODE = shutil.which("node")
FILE = os.path.join(SITE, "data", "datacenter", "how_soon.json")
EM_DASH = chr(0x2014)
MINE = (
    ("warehouse", "derived", "how_soon.py"), ("site", "app", "cost-of-power", "LoadWaits.tsx"), ("site", "lib", "howsoon.ts"), ("site", "lib", "howsoondata.ts"),
    ("site", "scripts", "test-howsoon.mjs"), ("site", "scripts", "check-how-soon.mjs"), ("tests", "test_session163.py"), ("site", "app", "cost-of-power", "page.tsx"),
    ("docs", "methods", "datacenter_cost.md"),
)
REQUEST_KEYS = {"request_id", "request_id_as_printed", "request_name", "request_names_seen", "queue_position", "queue_date", "queue_date_printed", "mw", "mw_first", "mw_last",
                "size_class", "parties", "entity_ids", "event_id", "sentence", "megawatts", "status_in_last_copy", "start_earlier_date", "end_later_date"}
NOT_A_FIGURE = {"page", "date", "url", "first", "last", "retrieved", "built_at_utc"}   # a day, a page number or an address of a document


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def tables_dir():
    """The directory that holds the two internal tables, or None. Reads the environment, never sets it."""
    for d in (os.environ.get("ERW_TABLES_DIR"), os.path.join(ROOT, "warehouse", "output")):
        if d and all(os.path.exists(os.path.join(d, n + ".csv")) for n in (hs.WAITS, hs.STATEMENTS)):
            return d
    return None


def leaves(v, key=""):
    """Every (key, value) leaf of a JSON value, and every key on the way."""
    if isinstance(v, dict):
        for k, x in v.items():
            yield ("<key>", k)
            yield from leaves(x, k)
    elif isinstance(v, list):
        for x in v:
            yield from leaves(x, key)
    else:
        yield (key, v)


# ---- made-up rows: no entity, request, duration or document below is real ------------------------------------------
W_HEAD = ["Energy Research Warehouse (ERW): MADE UP FOR THE TEST",
          "Retrieved: 20310304T050607Z (UTC) by a test",
          "This run: New York ISO: 9 copies read (2030-01-02 to 2031-01-02), 14 requests seen, 10 followed; Made-up District: 3 copies read (2030-05-01 to 2030-09-01), 1 requests seen, 1 followed. "
          "ERCOT (made up): 29 status reports read (2030-05-06 to 2031-01-09), 0 name a request, no row.",
          "License: internal. MADE UP."]
S_HEAD = ["Energy Research Warehouse (ERW): MADE UP FOR THE TEST", "Retrieved: 20310304T050607Z (UTC) by a test", "License: internal. MADE UP."]


def wait_row(entity, rid, interval, label, least="", most="", name=None):
    return {"entity": entity, "entity_group": entity, "request_id": rid, "request_id_as_printed": rid, "request_name": name or f"Made-up Load Number {rid}",
            "request_names_seen": name or f"Made-up Load Number {rid}", "mw": "77.0", "size_class": "20 to under 100 MW", "interval": interval, "stage_as_worded": "",
            "days_at_least": str(least), "days_at_most": str(most), "label": label, "source": "madeup:queue", "first_copy_date": "2030-01-02", "last_copy_date": "2031-01-02",
            "retrieved_at": "2031-03-04T05:06:07Z"}


def stmt_row(group, figure, status, basis="expected", **more):
    r = {"row_kind": "wait", "entity_group": group, "entity": group, "quantity_as_written": figure, "status": status, "wait_basis": basis, "wait_counted": "yes",
         "wait_figure_holder": "yes", "source_flag": "", "load_scope": "large loads (or every load at transmission voltage: the notes say which)",
         "source_url": "https://example.invalid/made-up.pdf", "document_title": "Made-up bulletin", "document_type": "operator report", "event_date": "2030-11-07",
         "event_date_basis": "document", "page": "3", "sentence": "A made-up sentence that says the median was long.", "wait_or_lead_time_as_worded": "made up"}
    r.update(more)
    return r


def made_up_waits():
    op, rows = "New York ISO", []
    sis, svc = "system impact study, pending or in progress to approved", "request to energized"
    for i, (a, b) in enumerate([(10, 40), (20, 50), (30, 90), (44, 61), (100, 300)]):          # five measured: a median
        rows.append(wait_row(op, f"A{i}", sis, "measured", a, b))
    for i, a in enumerate([7, 300, 12]):                                                        # three still waiting
        rows.append(wait_row(op, f"B{i}", sis, "lower bound", a))
    for i, (a, b) in enumerate([(1000, 1100), (1200, 1300), (900, 1250)]):                      # three measured: bounds only
        rows.append(wait_row(op, f"A{i}", svc, "measured", a, b))
    rows.append(wait_row(op, "B0", svc, "lower bound", 555))                                    # one still waiting: too few
    rows.append(wait_row(op, "C0", svc, "two copies only", 57))
    rows.append(wait_row(op, "C1", svc, "upper bound", "", 4000))
    rows.append(wait_row(op, "A0", "request to construction", "measured", 500, 600))            # one measured: too few
    rows.append(wait_row(op, "A0", "in stage", "measured", 5, 6))                               # an interval the block does not show
    rows.append(wait_row("Made-up District", "3", "request to energized", "lower bound", 2000))  # on none of the page's grids
    return rows


class TheBuilder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        stmts = [stmt_row("New York ISO", "nine months", "System Impact Study (SIS)"),
                 stmt_row("Oncor Electric Delivery", "603 days", "made-up interconnections", "measured", sentence="The made-up average was 603 days."),
                 stmt_row("Oncor Electric Delivery", "544 days", "made-up interconnections", "measured", sentence="The made-up median was 544 days."),
                 stmt_row("ERCOT", "13 weeks", "Batch Zero study, step 1: made up"),
                 stmt_row("ERCOT", "41 weeks", "a third party's copy", source_flag="a third party's copy: made up"),
                 stmt_row("ERCOT", "42 weeks", "an address with a person in it", source_url="https://example.invalid/someone@example.invalid/x.pdf"),
                 stmt_row("ERCOT", "43 weeks", "a rate, not a wait", wait_counted="no: a rate, an interval or a difference, not a duration"),
                 stmt_row("Made-up Utility Elsewhere", "44 weeks", "another entity")]
        cls.waits, cls.stmts = made_up_waits(), stmts
        cls.file, cls.left = hs.build(W_HEAD, cls.waits, S_HEAD, stmts)
        cls.ny = cls.file["grids"]["nyiso"]
        cls.stage = {s["interval"]: s for s in cls.ny["stages"]}

    def test_a_median_on_five_or_more_as_its_two_bounds(self):
        m = self.stage["system impact study, pending or in progress to approved"]["measured"]
        self.assertEqual((m["n"], m["form"], m["median_at_least"], m["median_at_most"], m["least"], m["most"]), (5, "median", 30, 61, 10, 300))
        self.assertNotIn(45.5, m.values())                                  # never a midpoint of the two bounds
        self.assertEqual(hs.median([1, 2, 3, 4]), 2.5)                      # a half day is kept, not rounded
        self.assertIsInstance(hs.median([1, 3]), int)

    def test_a_small_group_is_its_count_and_two_bounds(self):
        m = self.stage["request to energized"]["measured"]
        self.assertEqual(m, {"n": 3, "form": "bounds", "least": 900, "most": 1300})

    def test_one_request_is_too_few_to_show(self):
        m = self.stage["request to construction"]["measured"]
        self.assertEqual(m, {"n": 1, "form": "too few", "words": "too few to show"})
        w = self.stage["request to energized"]["waiting"]
        self.assertEqual(w, {"n": 1, "lower_bound": True, "form": "too few", "words": "too few to show"})

    def test_lower_bounds_are_marked_and_never_mixed_with_the_measured(self):
        s = self.stage["system impact study, pending or in progress to approved"]
        self.assertEqual(s["waiting"], {"n": 3, "lower_bound": True, "form": "range", "least": 7, "most": 300})
        self.assertEqual(s["measured"]["least"], 10)                        # the 7 of a request still waiting is not in the measured range
        for st in self.ny["stages"]:
            self.assertIs(st["waiting"]["lower_bound"], True)
            self.assertIs(st["two_copies_only"]["lower_bound"], True)
            self.assertEqual(st["requests"], st["measured"]["n"] + st["waiting"]["n"] + st["two_copies_only"]["n"] + st["ended_before_first_copy"]["n"])

    def test_the_copies_and_the_requests_followed(self):
        c = self.ny["copies"]
        self.assertEqual((c["n"], c["first"], c["last"], c["requests_seen"], c["requests_followed"]), (9, "2030-01-02", "2031-01-02", 14, 10))

    def test_the_header_and_the_rows_must_agree(self):
        head = [h.replace("10 followed", "11 followed") for h in W_HEAD]
        with self.assertRaises(SystemExit):
            hs.build(head, self.waits, S_HEAD, self.stmts)

    def test_an_entity_on_none_of_the_pages_grids_is_left_out_and_named(self):
        self.assertEqual([e["entity"] for e in self.left["entities"]], ["Made-up District"])
        self.assertNotIn("Made-up District", json.dumps(self.file))        # named in the printed summary only
        self.assertEqual(self.file["left_out"]["entities"], 1)
        self.assertTrue(any("LEFT OUT, entity: Made-up District (1 rows)" in ln for ln in hs.summary(self.file, self.left)))
        self.assertEqual(self.left["intervals"], {"in stage": 1})

    def test_new_entities_do_not_break_it(self):
        more = self.waits + [wait_row("Bonneville Power Administration", "L0999", "request to energized", "measured", 1, 2),
                             wait_row("Alberta Electric System Operator", "P2468", "a new interval", "lower bound", 3)]
        file, left = hs.build(W_HEAD, more, S_HEAD, self.stmts)
        self.assertEqual(file["grids"], self.file["grids"])
        for name in ("Bonneville", "Alberta", "L0999", "P2468"):
            self.assertNotIn(name, json.dumps(file))
        self.assertEqual(sorted(e["entity"] for e in left["entities"]), ["Alberta Electric System Operator", "Bonneville Power Administration", "Made-up District"])

    def test_miso_is_never_in_the_file(self):
        self.assertNotIn("Midcontinent", " ".join(hs.ENTITY_GRID))
        self.assertNotIn("miso", hs.ENTITY_GRID.values())
        self.assertNotIn("miso", hs.STATED_GROUPS)
        self.assertEqual(self.file["paused"], ["miso"])
        self.assertNotIn("miso", self.file["grids"])

    def test_texas_is_not_measured_here_with_the_headers_counts(self):
        tx = self.file["grids"]["ercot"]
        self.assertEqual(tx["state"], "not measured here")
        self.assertEqual((tx["reports"]["n"], tx["reports"]["requests_named"], tx["reports"]["first"], tx["reports"]["last"]), (29, 0, "2030-05-06", "2031-01-09"))
        self.assertEqual(tx["stages"], [])
        none, _ = hs.build([h for h in W_HEAD if not h.startswith("This run:")], self.waits, S_HEAD, self.stmts)
        self.assertIsNone(none["grids"]["ercot"]["reports"]["n"])           # a count the header does not give is not made up

    def test_stated_figures_as_written_with_no_sentence(self):
        tx = self.file["grids"]["ercot"]["stated"]
        self.assertEqual([(s["stated_by"], s["figure"], s["basis"], s["statistic"]) for s in tx],
                         [("Oncor Electric Delivery", "603 days", "measured", "average"), ("Oncor Electric Delivery", "544 days", "measured", "median"), ("ERCOT", "13 weeks", "expected", "")])
        self.assertIn("not their sum", tx[2]["note"])
        beside = self.stage["system impact study, pending or in progress to approved"]["stated"]
        self.assertEqual([(s["figure"], s["mark"]) for s in beside], [("nine months", "")])
        self.assertIn("Not the same start", beside[0]["note"])
        text = json.dumps(self.file)
        for never in ("made-up sentence", "The made-up average", "41 weeks", "42 weeks", "43 weeks", "44 weeks", "someone@"):
            self.assertNotIn(never, text)

    def test_the_steps_are_never_added(self):
        t = src("warehouse", "derived", "how_soon.py")
        self.assertNotRegex(t, r"sum\([^)]*weeks|58 weeks")

    def test_a_file_that_would_hold_a_request_is_refused(self):
        hs.check(self.file, self.waits)
        bad = json.loads(json.dumps(self.file))
        bad["grids"]["nyiso"]["stages"][0]["label"] = "Made-up Load Number A0"
        with self.assertRaises(SystemExit):
            hs.check(bad, self.waits)
        for key in ("request_id", "mw", "queue_position", "sentence", "mw_last"):
            worse = json.loads(json.dumps(self.file))
            worse["grids"]["nyiso"][key] = "x"
            with self.assertRaises(SystemExit):
                hs.check(worse, self.waits)

    def test_no_request_level_value_of_the_made_up_rows_is_in_the_file(self):
        text = json.dumps(self.file)
        for r in self.waits:
            self.assertNotIn(r["request_name"], text)
        self.assertNotRegex(text, r"\b77\.0\b|20 to under 100 MW")
        for k, v in leaves(self.file):
            if k == "<key>":
                self.assertNotIn(v, REQUEST_KEYS)

    def test_a_missing_table_writes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = hs.main(["--in-dir", d, "--out-dir", os.path.join(d, "out")])
            self.assertEqual(code, 1)
            self.assertIn("FAILED", err.getvalue())
            self.assertFalse(os.path.exists(os.path.join(d, "out", "how_soon.json")))

    def test_a_trial_writes_under_its_own_folder_and_a_second_run_changes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            for name, head, rows in ((hs.WAITS, W_HEAD, self.waits), (hs.STATEMENTS, S_HEAD, self.stmts)):
                with open(os.path.join(d, name + ".csv"), "w", encoding="utf-8", newline="") as f:
                    for h in head:
                        f.write(f"# {h}\n")
                    w = csv.DictWriter(f, fieldnames=list(rows[0]))
                    w.writeheader()
                    w.writerows(rows)
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(hs.main(["--in-dir", d, "--out-dir", os.path.join(d, "out")]), 0)
            at = os.path.join(d, "out", "how_soon.json")
            with open(at, encoding="utf-8") as f:
                first = f.read()
            self.assertEqual({k: v for k, v in json.loads(first).items() if k != "built_at_utc"}, {k: v for k, v in self.file.items() if k != "built_at_utc"})
            with redirect_stdout(out):
                self.assertEqual(hs.main(["--in-dir", d, "--out-dir", os.path.join(d, "out")]), 0)
            with open(at, encoding="utf-8") as f:
                self.assertEqual(f.read(), first)
            self.assertIn("unchanged", out.getvalue())


@unittest.skipUnless(os.path.exists(FILE), "site/data/datacenter/how_soon.json is not on this machine")
class TheFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = src("site", "data", "datacenter", "how_soon.json")
        cls.file = json.loads(cls.text)

    def test_aggregates_only(self):
        for k, v in leaves(self.file):
            if k == "<key>":
                self.assertNotIn(v.lower(), REQUEST_KEYS, v)
                self.assertNotIn("mw", re.split(r"[^a-z]+", v.lower()), v)
            elif isinstance(v, str):
                self.assertNotRegex(v, r"(?i)\bMW\b|megawatt", f"{k}: a megawatt figure or word")
        self.assertNotIn(EM_DASH, self.text)
        self.assertNotRegex(self.text, r"(?i)made[- ]up|example\.invalid|lorem ipsum")
        self.assertEqual(self.file["rule"], {"min_for_median": 5, "min_for_bounds": 2, "too_few": "too few to show"})
        for name in (hs.WAITS, hs.STATEMENTS):
            self.assertEqual(self.file["tables"][name]["license"], "internal")

    def test_the_shape_of_every_figure(self):
        for grid, g in self.file["grids"].items():
            self.assertIn(g["state"], ("measured", "not measured here", "not measured yet"), grid)
            self.assertEqual(g["state"] == "measured", bool(g["stages"]), grid)
            for st in g["stages"]:
                m, w = st["measured"], st["waiting"]
                self.assertIs(w["lower_bound"], True, st["interval"])
                self.assertIs(st["two_copies_only"]["lower_bound"], True)
                self.assertEqual(st["requests"], m["n"] + w["n"] + st["two_copies_only"]["n"] + st["ended_before_first_copy"]["n"], st["interval"])
                want = "median" if m["n"] >= 5 else "bounds" if m["n"] >= 2 else "too few" if m["n"] == 1 else "none"
                self.assertEqual(m["form"], want, st["interval"])
                self.assertEqual(set(m) - {"n", "form"}, {"median": {"median_at_least", "median_at_most", "least", "most"}, "bounds": {"least", "most"}, "too few": {"words"}, "none": set()}[want])
                if want == "median":
                    self.assertLessEqual(m["median_at_least"], m["median_at_most"])
                    self.assertLessEqual(m["least"], m["median_at_least"])
                    self.assertLessEqual(m["median_at_most"], m["most"])
                self.assertEqual(set(w) - {"n", "lower_bound", "form"}, {"range": {"least", "most"}, "too few": {"words"}, "none": set()}[w["form"]])
                self.assertEqual(set(st["two_copies_only"]), {"n", "lower_bound"})          # counts only
                self.assertEqual(set(st["ended_before_first_copy"]), {"n"})

    def test_nothing_for_miso(self):
        self.assertNotIn("miso", self.file["grids"])
        self.assertIn("miso", self.file["paused"])
        self.assertNotRegex(self.text, r"(?i)misoenergy|Midcontinent")

    def test_every_stated_figure_has_its_stater_and_its_document(self):
        n = 0
        for grid, g in self.file["grids"].items():
            for s in g["stated"] + [x for st in g["stages"] for x in st["stated"]]:
                n += 1
                for key in ("stated_by", "figure", "basis", "covers", "document", "date", "url"):
                    self.assertTrue(s[key].strip(), f"{grid}: {key}")
                self.assertTrue(s["url"].startswith("https://"))
                self.assertNotRegex(s["url"], r"@|%40")
                self.assertIn(s["basis"], ("measured", "expected", "general statement"))
                self.assertRegex(s["date"], r"^\d{4}-\d\d-\d\d$")
        self.assertGreater(n, 0)

    def test_new_york_and_texas(self):
        g = self.file["grids"]
        self.assertEqual((g["nyiso"]["state"], g["nyiso"]["place"]), ("measured", "New York"))
        self.assertEqual((g["ercot"]["state"], g["ercot"]["place"]), ("not measured here", "Texas"))
        self.assertTrue(any(s["basis"] == "measured" and s["stated_by"] != "ERCOT" for s in g["ercot"]["stated"]))


@unittest.skipUnless(os.path.exists(FILE) and tables_dir(), "the two internal tables are not on this machine (ERW_TABLES_DIR names their directory)")
class AgainstTheTables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        d = tables_dir()
        cls.w_head, cls.waits = hs.read_table(os.path.join(d, hs.WAITS + ".csv"))
        cls.s_head, cls.stmts = hs.read_table(os.path.join(d, hs.STATEMENTS + ".csv"))
        with open(FILE, encoding="utf-8") as f:
            cls.file = json.load(f)

    def test_the_file_is_what_the_builder_gives_from_the_tables_today(self):
        # what the page shows: the grids, the rule and the summary's stages. Not the stamps and not the tables' row counts:
        # a table read again, or rows of an entity on none of the page's grids appended (session 165), changes no figure
        def shown(f):
            def drop(v):
                if isinstance(v, dict):
                    return {k: drop(x) for k, x in v.items() if k != "retrieved"}
                return [drop(x) for x in v] if isinstance(v, list) else v
            return drop({k: f[k] for k in ("grids", "rule", "paused", "summary", "unit")})
        fresh, _ = hs.build(self.w_head, self.waits, self.s_head, self.stmts)
        self.assertEqual(shown(fresh), shown(self.file), "a figure of the tables has changed since the file was built: run warehouse/derived/how_soon.py again")

    def test_each_aggregate_worked_again_from_the_raw_rows(self):
        days = lambda t: float(t)                                           # noqa: E731
        checked = 0
        for grid, g in self.file["grids"].items():
            if g["state"] != "measured":
                continue
            mine = [r for r in self.waits if r["entity"] == g["entity"]]
            self.assertEqual(g["copies"]["requests_followed"], len({r["request_id"] for r in mine}))
            for st in g["stages"]:
                rows = [r for r in mine if r["interval"] == st["interval"]]
                self.assertEqual(st["requests"], len(rows), st["interval"])
                self.assertEqual(len(rows), len({r["request_id"] for r in rows}), st["interval"])
                meas = [(days(r["days_at_least"]), days(r["days_at_most"])) for r in rows if r["label"] == "measured"]
                low = [days(r["days_at_least"]) for r in rows if r["label"] == "lower bound"]
                m, w = st["measured"], st["waiting"]
                self.assertEqual(m["n"], len(meas), st["interval"])
                self.assertEqual(w["n"], len(low), st["interval"])
                self.assertEqual(st["two_copies_only"]["n"], sum(1 for r in rows if r["label"] == "two copies only"))
                self.assertEqual(st["ended_before_first_copy"]["n"], sum(1 for r in rows if r["label"] == "upper bound"))
                self.assertEqual(len(rows), len(meas) + len(low) + st["two_copies_only"]["n"] + st["ended_before_first_copy"]["n"], "the counts add up to the rows")
                if len(meas) >= 5:
                    self.assertEqual(m["median_at_least"], statistics.median(a for a, _ in meas), st["interval"])
                    self.assertEqual(m["median_at_most"], statistics.median(b for _, b in meas), st["interval"])
                if len(meas) >= 2:
                    self.assertEqual((m["least"], m["most"]), (min(a for a, _ in meas), max(b for _, b in meas)), st["interval"])
                if len(meas) < 2:
                    self.assertFalse({"least", "most", "median_at_least", "median_at_most"} & set(m), st["interval"])
                if len(low) >= 2:
                    self.assertEqual((w["least"], w["most"]), (min(low), max(low)), st["interval"])
                else:
                    self.assertFalse({"least", "most"} & set(w), st["interval"])
                checked += 1
        self.assertGreater(checked, 0)

    def test_no_request_name_or_queue_position_is_in_the_file(self):
        names, positions = set(), set()
        for r in self.waits:                                                # every entity of the table, shown or not
            for n in [r["request_name"]] + re.split(r"[;|]", r["request_names_seen"]):
                if len(n.strip()) >= 4:
                    names.add(n.strip().lower())
            positions |= {r["request_id"].strip().lower(), r["request_id_as_printed"].strip().lower()}
        positions.discard("")
        self.assertGreater(len(names), 10)
        marked = {p for p in positions if len(p) >= 4 or re.search(r"[a-z]", p)}
        for k, v in leaves(self.file):
            if k == "<key>":
                self.assertNotIn(v.lower(), positions, "a key that is a queue position")
                continue
            if not isinstance(v, str):
                continue                                                    # a number of the file is an aggregate: the test above works each again
            low = v.lower()
            for n in names:
                self.assertNotIn(n, low, f"{k}: a request's name")
            if k in NOT_A_FIGURE:
                continue
            self.assertNotIn(low.strip(), positions, f"{k}: a value that is a queue position")
            hit = marked & set(re.findall(r"[a-z0-9]+", low))
            self.assertFalse(hit, f"{k}: holds {sorted(hit)}, which a queue position also reads. If it is a number in a document's title, it is no request: say so here.")

    def test_no_number_of_a_measured_stage_is_one_requests_megawatts_field(self):
        # megawatts are in no key and no words of the file (TheFile); here: the file holds no size class of the table
        text = json.dumps(self.file)
        for size in {r["size_class"] for r in self.waits if r["size_class"]}:
            self.assertNotIn(size, text)

    def test_every_stated_figure_is_a_row_of_the_statements_table(self):
        for grid, g in self.file["grids"].items():
            groups = hs.STATED_GROUPS.get(grid, [])
            got = g["stated"] + [x for st in g["stages"] for x in st["stated"]]
            want = [r for r in self.stmts if r["row_kind"] == "wait" and r["entity_group"] in groups and r["wait_counted"] == "yes" and r["wait_figure_holder"] == "yes" and not r["source_flag"]]
            self.assertEqual(len(got), len(want), grid)
            for s in got:
                rows = [r for r in want if (r["entity_group"], r["quantity_as_written"].strip(), r["status"].strip(), r["source_url"], r["event_date"], r["wait_basis"]) ==
                        (s["stated_by"], s["figure"], s["covers"], s["url"], s["date"], s["basis"])]
                self.assertEqual(len(rows), 1, f"{grid}: {s['figure']}")
                self.assertIn(s["figure"], rows[0]["sentence"])             # the figure stands in the document's own sentence
                self.assertNotIn(rows[0]["sentence"], json.dumps(s, ensure_ascii=False))
                if s["statistic"]:
                    self.assertRegex(rows[0]["sentence"].lower(), r"\b%s\b" % s["statistic"])

    def test_the_raw_tables_stay_internal(self):
        for head in (self.w_head, self.s_head):
            self.assertTrue(hs.header_value(head, "License:").startswith("internal"))


@unittest.skipUnless(NODE, "node is not installed")
class TheSentence(unittest.TestCase):
    def test_the_node_tests_pass(self):
        r = subprocess.run([NODE, "scripts/test-howsoon.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])
        self.assertRegex(r.stdout, r"all \d+ passed")
        self.assertNotIn("FAIL", r.stdout)

    def test_its_figures_are_marked_made_up(self):
        t = src("site", "scripts", "test-howsoon.mjs")
        self.assertIn("THE FIGURES BELOW ARE MADE UP FOR THIS TEST", t)
        self.assertIn("example.invalid", t)

    @unittest.skipUnless(os.path.exists(FILE), "site/data/datacenter/how_soon.json is not on this machine")
    def test_every_number_of_the_sentence_is_a_number_of_the_file(self):
        code = ("import fs from 'node:fs'; import * as H from './lib/howsoon.ts';"
                "const f = H.fileOf(JSON.parse(fs.readFileSync('data/datacenter/how_soon.json', 'utf8')));"
                "console.log(JSON.stringify(Object.fromEntries(H.WAIT_GRIDS.map((g) => [g, H.sentenceOf(f, g, g.toUpperCase())]))));")
        r = subprocess.run([NODE, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        got = json.loads(r.stdout.strip().splitlines()[-1])
        with open(FILE, encoding="utf-8") as f:
            file = json.load(f)
        numbers = lambda s: [float(x.replace(",", "")) for x in re.findall(r"\d[\d,]*(?:\.\d+)?", s)]   # noqa: E731
        for grid, sentence in got.items():
            held = set()
            for _, v in leaves(file["grids"].get(grid, {})):
                if isinstance(v, bool):
                    continue
                if isinstance(v, (int, float)):
                    held.add(float(v))
                elif isinstance(v, str):
                    held |= set(numbers(v))
            for x in numbers(sentence):
                self.assertIn(x, held, f"{grid}: {x} in the sentence is not a number of the file: {sentence}")
            self.assertTrue(sentence.endswith(".") and ". " not in sentence, f"{grid}: one sentence")
        ny, tx = got["nyiso"], got["ercot"]
        self.assertTrue(ny.startswith("New York: "))
        self.assertIn("(a lower bound)", ny)
        self.assertRegex(ny, r"\d+ requests followed .* took a median of at least [\d,.]+ and at most [\d,.]+ days, where New York ISO itself states ")
        self.assertTrue(tx.startswith("Texas: no wait is measured here"))
        self.assertIn("measured by the entities themselves", tx)
        self.assertEqual(got["caiso"], "CAISO: not measured yet.")
        self.assertEqual(got["miso"], "MISO: paused while terms are reviewed.")


class ThePage(unittest.TestCase):
    def test_in_review(self):
        self.assertRegex(src("site", "lib", "release.ts"), r'"/cost-of-power": "review"')

    def test_the_block_stands_between_the_sections_table_and_the_rules(self):
        page = src("site", "app", "cost-of-power", "page.tsx")
        start = page.index('<ToolSection title="How soon" id="soon">')
        section = page[start:page.index("</ToolSection>", start)]
        self.assertEqual(page.count("<LoadWaits "), 1)
        self.assertLess(section.index("<ToolTable "), section.index("<LoadWaits "))
        self.assertLess(section.index("<LoadWaits "), section.index("<RulesInMotion "))        # the rules block sits beneath
        for key in ("q", "wait", "done", "ll", "line", "waitload"):                               # nothing the section showed is dropped
            self.assertIn('{ key: "%s", cells:' % key, section)
        for said in ("Generation waiting to connect", "From request to operation, the median", "Large load approved to energize", "Large load in line, by region", "How long a new large load waits"):
            self.assertIn(said, section)

    def test_one_site_file_of_aggregates_and_nothing_else(self):
        comp, data, lib = src("site", "app", "cost-of-power", "LoadWaits.tsx"), src("site", "lib", "howsoondata.ts"), src("site", "lib", "howsoon.ts")
        self.assertEqual(re.findall(r'"([a-z_]+\.json)"', data), ["how_soon.json"])
        self.assertIn('path.join(process.cwd(), "data", "datacenter", "how_soon.json")', data)
        self.assertNotRegex(lib, r"(?m)^\s*import\s", "lib/howsoon.ts imports nothing: Node runs it as it is")
        for name, t in (("LoadWaits.tsx", comp), ("howsoondata.ts", data), ("howsoon.ts", lib)):
            self.assertNotRegex(t, r"supabase|fetch\(|anthropic|/api/|\.csv", name)       # no table read, no request, no model
            self.assertNotIn('"use client"', t, name)
        self.assertIn('"/cost-of-power": ["./data/datacenter/*.json"]', src("site", "next.config.ts"))

    def test_the_words_of_the_face(self):
        lib = src("site", "lib", "howsoon.ts")
        words = json.loads(src("site", "data", "datacenter", "index.json"))["blank"]["miso"]["words"]
        self.assertIn('export const PAUSED_WORDS = "%s";' % words, lib)
        self.assertIn('export const NOT_YET = "not measured yet";', lib)
        self.assertIn('export const NOT_HERE = "not measured here";', lib)
        self.assertIn('export const LOWER = "lower bound";', lib)
        comp = src("site", "app", "cost-of-power", "LoadWaits.tsx")
        self.assertIn("{LOWER}", comp)                                       # the mark stands on the face beside every lower bound
        self.assertNotRegex(comp, r"s\.sentence|\.sentence\b")              # no sentence of a document is shown

    def test_no_live_page_and_no_shared_component_takes_anything_of_it(self):
        took = re.compile(r"LoadWaits|@/lib/howsoon|lib/howsoondata|how_soon")
        for parts in (("site", "app", "cost-of-power", "battery"), ("site", "app", "cost-of-power", "seller"), ("site", "app", "network"), ("site", "app", "storage"), ("site", "components", "tool")):
            for folder, _, names in os.walk(os.path.join(ROOT, *parts)):
                for n in names:
                    if n.endswith((".ts", ".tsx")):
                        with open(os.path.join(folder, n), encoding="utf-8") as fh:
                            self.assertIsNone(took.search(fh.read()), n)
        for parts in (("site", "app", "cost-of-power", "Tabs.tsx"), ("site", "app", "cost-of-power", "charts.tsx"), ("site", "lib", "pages.ts"), ("site", "lib", "supabase.ts"), ("site", "lib", "batterystack.ts")):
            self.assertIsNone(took.search(src(*parts)), parts[-1])

    def test_no_em_dash(self):
        for parts in MINE:
            self.assertNotIn(EM_DASH, src(*parts), parts[-1])

    def test_the_method_note_has_its_section(self):
        note = src("docs", "methods", "datacenter_cost.md")
        self.assertIn("### How long a large load waits (session 163)", note)
        for said in ("lower bound", "never a midpoint", "too few to show", "warehouse/derived/how_soon.py", "not measured here", "not measured yet", "Why Texas has none", "What is not shown"):
            self.assertIn(said, note)

    def test_the_check_names_it(self):
        check = src("site", "scripts", "check-how-soon.mjs")
        for said in ("data-waits", "not measured yet", "lower bound", "large_load_waits", "data-rules"):
            self.assertIn(said, check)


if __name__ == "__main__":
    unittest.main()
