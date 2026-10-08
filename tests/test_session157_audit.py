"""Session 157: the audit of 50 more policy actions against their source documents (100 with session 154's).

The second sample is drawn by seed 157 from the rows not in session 154's sample. Its record is in git under
warehouse/policy/eval/ (audit_s157_sample.csv, _manifest.csv, _findings.csv, _errors.csv, _error_table.md, and
_error_table_100.md for both samples), with the place of each of the 100 as codes in audit_states_truth.csv.

Every test here asserts on the contents of files in the repository: no request is made, no model is called, and the
tests that need the table itself (warehouse/output, not in git) skip cleanly on a machine without it. The four real
documents under tests/fixtures/session157/audit/ are the Register's own files as the audits saved them (MANIFEST.csv
there gives each one's address, hash and retrieval time).

What is tested:
1. the seed reproduces the sample, and the sample holds no row of session 154's;
2. the error table's counts equal the findings file's, for the 50 and for the 100;
3. the truth file says the same as the findings (class and codes agree, 100 rows);
4. a printed text held in the connector's store is copied, not requested, and counts toward no ceiling;
5. the title the Register's record cuts short is found whole in the printed document;
6. the fetch of the second sample stayed under its ceiling and reached every source.
"""

import csv
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIX = os.path.join(ROOT, "tests", "fixtures", "session157", "audit")
EVAL = os.path.join(ROOT, "warehouse", "policy", "eval")
AUDIT = os.path.join(ROOT, "warehouse", "policy", "audit")
CONNECTORS = os.path.join(ROOT, "warehouse", "connectors")
# The table is not in git. On the machine that holds it, it is in the main copy; a path in ERW_OUT_DIR wins.
TABLE_DIRS = [os.environ.get("ERW_OUT_DIR", ""), os.path.join(ROOT, "warehouse", "output"),
              "C:/Users/lossa/Documents/erw/warehouse/output"]
BAD = ["wrong", "missing", "not_in_source", "unsupported", "contradicted"]
_ADDED = []


def setUpModule():
    for p in (AUDIT, CONNECTORS):
        if p not in sys.path:
            sys.path.insert(0, p)
            _ADDED.append(p)


def tearDownModule():
    for p in _ADDED:
        if p in sys.path:
            sys.path.remove(p)
    del _ADDED[:]


def rows(name):
    with open(os.path.join(EVAL, name), encoding="utf-8") as f:
        return list(csv.DictReader(ln for ln in f if not ln.startswith("#")))


def table_dir():
    for d in TABLE_DIRS:
        if d and os.path.exists(os.path.join(d, "policy_actions.csv")):
            return d
    return None


class Sample(unittest.TestCase):
    def test_fifty_rows_none_of_session_154s(self):
        new, old = rows("audit_s157_sample.csv"), rows("audit_s154_sample.csv")
        ids = [r["event_id"] for r in new]
        self.assertEqual((len(ids), len(set(ids))), (50, 50))
        self.assertEqual([r["draw"] for r in new], [str(n) for n in range(1, 51)])
        self.assertEqual(set(ids) & {r["event_id"] for r in old}, set())
        self.assertEqual(len(set(ids) | {r["event_id"] for r in old}), 100)

    def test_the_file_states_its_seed_and_frame(self):
        with open(os.path.join(EVAL, "audit_s157_sample.csv"), encoding="utf-8") as f:
            head = [ln for ln in f if ln.startswith("#")]
        self.assertIn("random.Random(157).sample(", head[0])
        self.assertIn("not in audit_s154_sample.csv", head[0])
        self.assertIn("before any source was fetched", head[1])

    def test_the_draw_leaves_out_what_it_is_told_to(self):
        import audit_sample as sample
        ids = [f"federalregister:2026-{n:05d}" for n in range(1, 400)]
        first = sample.draw(ids)
        second = sample.draw(ids, 157, 50, first)
        self.assertEqual(second, sample.draw(list(reversed(ids)), 157, 50, first))
        self.assertEqual(set(first) & set(second), set())
        self.assertEqual((len(second), len(set(second))), (50, 50))
        self.assertEqual(first, sample.draw(ids, sample.SEED, sample.N))   # session 154's draw is as it was

    def test_the_seed_reproduces_the_sample_on_the_table_held(self):
        d = table_dir()
        if not d:
            self.skipTest("policy_actions.csv is not on this machine")
        import audit_sample as sample
        path = os.path.join(d, "policy_actions.csv")
        with open(os.path.join(EVAL, "audit_s157_sample.csv"), encoding="utf-8") as f:
            head = f.readline()
        with open(path, "rb") as f:
            if hashlib.sha256(f.read()).hexdigest() not in head:
                self.skipTest("the table on this machine is not the one the sample was drawn from (its hash differs)")
        acts = sample.read_events(path)
        gone = sample.sample_ids(os.path.join(EVAL, "audit_s154_sample.csv"))
        self.assertEqual(sample.draw(acts["event_id"], 157, 50, gone), [r["event_id"] for r in rows("audit_s157_sample.csv")])
        self.assertEqual(sample.draw(acts["event_id"]), gone)


class ErrorTable(unittest.TestCase):
    def counts(self, findings):
        out = {}
        for r in findings:
            key = (r["group"], r["field"])
            n, bad = out.get(key, (0, 0))
            out[key] = (n + 1, bad + (r["cls"] in BAD))
        return out

    def table(self, name):
        """{field label: (rows checked, the 'errors of rows checked' cell)} of a stored error table."""
        out = {}
        with open(os.path.join(EVAL, name), encoding="utf-8") as f:
            for ln in f:
                cells = [c.strip() for c in ln.strip().strip("|").split("|")]
                if ln.startswith("|") and len(cells) == 13 and cells[1].isdigit():
                    out[cells[0]] = (int(cells[1]), cells[11])
        return out

    def check(self, findings, table_name, n_rows):
        import audit_table as table
        want = self.counts(findings)
        got = self.table(table_name)
        self.assertEqual(len(got), len(table.EXTRACTED) + len(table.MODEL) + len(table.READ))
        for (group, field), (n, bad) in want.items():
            label = field + (" (read)" if group == "read" else "")
            self.assertEqual(got[label][0], n, label)
            self.assertTrue(got[label][1].startswith(f"{bad} of {n} ("), (label, got[label][1], bad, n))
        for field in table.EXTRACTED + table.MODEL:
            self.assertEqual(got[field][0], n_rows, field)

    def test_the_fifty(self):
        f = rows("audit_s157_findings.csv")
        self.assertEqual(len({r["event_id"] for r in f}), 50)
        self.check(f, "audit_s157_error_table.md", 50)

    def test_the_hundred(self):
        f = rows("audit_s154_findings.csv") + rows("audit_s157_findings.csv")
        self.assertEqual(len({r["event_id"] for r in f}), 100)
        self.check(f, "audit_s157_error_table_100.md", 100)

    def test_the_errors_file_is_the_findings_errors(self):
        f = [r for r in rows("audit_s157_findings.csv") if r["cls"] in BAD]
        e = rows("audit_s157_errors.csv")
        self.assertEqual([(r["event_id"], r["field"], r["cls"]) for r in e], [(r["event_id"], r["field"], r["cls"]) for r in f])
        self.assertGreater(len(e), 0)
        for r in e:   # every error names the source's words
            self.assertTrue(r["source_words"].strip(), (r["event_id"], r["field"]))

    def test_the_table_function_gives_the_stored_lines(self):
        import pandas as pd
        import audit_table as table
        df = pd.DataFrame(rows("audit_s157_findings.csv"))
        with open(os.path.join(EVAL, "audit_s157_error_table.md"), encoding="utf-8") as f:
            self.assertEqual(table.error_table(df), f.read().rstrip("\n").split("\n"))

    def test_every_class_is_a_known_one(self):
        import audit_table as table
        known = set(table.GOOD) | set(table.BAD) | set(table.NEUTRAL)
        self.assertEqual({r["cls"] for r in rows("audit_s157_findings.csv")} - known, set())


class Truth(unittest.TestCase):
    def test_a_hundred_rows_and_the_classes_fit_the_codes(self):
        t = rows("audit_states_truth.csv")
        self.assertEqual([(r["sample"], r["draw"]) for r in t],
                         [(s, str(n)) for s in ("154", "157") for n in range(1, 51)])
        for r in t:
            held = ";".join(sorted(x for x in r["row_states"].split(";") if x))
            true = r["true_states"]
            self.assertEqual(true, ";".join(sorted(x for x in true.split(";") if x)))
            fits = {"correct": held == true and true != "", "source_silent": true == "" and held == "",
                    "missing": held == "" and true != "", "wrong": held != "" and true != "" and held != true,
                    "not_in_source": held != "" and true == ""}
            self.assertTrue(fits[r["cls"]], (r["sample"], r["draw"], r["cls"], held, true))

    def test_it_says_what_the_findings_say(self):
        t = {(r["sample"], r["event_id"]): r for r in rows("audit_states_truth.csv")}
        for label, name in (("154", "audit_s154_findings.csv"), ("157", "audit_s157_findings.csv")):
            st = [r for r in rows(name) if r["field"] == "states"]
            self.assertEqual(len(st), 50)
            for r in st:
                self.assertEqual((t[(label, r["event_id"])]["cls"], t[(label, r["event_id"])]["row_states"]),
                                 (r["cls"], r["row_value"]))

    def test_the_codes_are_the_findings_modules(self):
        import audit_findings as f4
        import audit_findings_s157 as f7
        t = rows("audit_states_truth.csv")
        for label, truth, states in (("154", f7.TRUE_STATES_154, f4.STATES), ("157", f7.TRUE_STATES, f7.STATES)):
            self.assertEqual(sorted(truth), list(range(1, 51)))
            self.assertEqual(sorted(states), list(range(1, 51)))
            for r in (x for x in t if x["sample"] == label):
                n = int(r["draw"])
                self.assertEqual(r["true_states"], ";".join(sorted(x for x in truth[n].split(";") if x)))
                self.assertEqual(r["cls"], states[n][0])

    def test_the_one_cut_title_of_the_hundred(self):
        cut = [r for r in rows("audit_states_truth.csv") if r["title_cut"] == "yes"]
        self.assertEqual([r["event_id"] for r in cut], ["federalregister:2026-17632"])
        self.assertTrue(cut[0]["full_title"].startswith("Gulf South Pipeline Company, LLC; Notice of Intent To Prepare"))
        self.assertTrue(cut[0]["full_title"].endswith("Schedule for Environmental Review"))


class Tools(unittest.TestCase):
    def parsed(self, number):
        import audit_check as check
        with open(os.path.join(FIX, f"fr_{number}.api.json"), encoding="utf-8") as f:
            api = json.load(f)
        with open(os.path.join(FIX, f"fr_{number}.text.txt"), encoding="utf-8", errors="replace") as f:
            text = check.fr_text(f.read())
        names = [x.get("raw_name") or "" for x in api.get("agencies") or []] + [x.get("name") or "" for x in api.get("agencies") or []]
        return api, check.fr_parse(text, names)

    def test_the_whole_title_is_read_from_the_print(self):
        import audit_truth as truth
        api, p = self.parsed("2026-17632")
        self.assertEqual(api["title"], "Gulf South Pipeline Company, LLC;")   # the record stops at the semicolon
        whole = truth.printed_title(p["body"], p["title"])
        self.assertEqual(whole, "Gulf South Pipeline Company, LLC; Notice of Intent To Prepare an Environmental Impact "
                                "Statement for the Proposed Texas Gateway Project, Request for Comments on "
                                "Environmental Issues, and Schedule for Environmental Review")
        self.assertTrue(truth.title_cut(api["title"], whole))

    def test_a_whole_title_is_left_as_it_is(self):
        import audit_truth as truth
        for number in ("2026-17394", "2026-20107", "2026-07325"):
            api, p = self.parsed(number)
            whole = truth.printed_title(p["body"], p["title"])
            self.assertEqual(whole, p["title"])
            self.assertFalse(truth.title_cut(api["title"], whole), number)

    def test_the_place_is_in_the_first_paragraph_and_not_in_the_applicants_name(self):
        # the three faults of the second sample that a state in a company's name makes: the documents' own words
        want = {"2026-17394": ("FFP Missouri 5, LLC", "Emsworth Locks and Dam on the Ohio River in Allegheny County, Pennsylvania"),
                "2026-20107": ("Ohio Power and Light, LLC", "on the Ohio River in Mason County, West Virginia"),
                "2026-07325": ("Texas Eastern Transmission, LP", "located in federal waters in the Gulf of America near Louisiana")}
        import audit_check as check
        truth = {r["fr_document_number"]: r for r in rows("audit_states_truth.csv")}
        for number, (name, place) in want.items():
            api, p = self.parsed(number)
            self.assertIn(name, p["title"])
            self.assertIn(place, check.ws(p["body"][:3000]))
            self.assertEqual(truth[number]["cls"], "wrong")
        self.assertEqual([truth[n]["true_states"] for n in want], ["PA", "WV", "LA"])
        self.assertEqual([truth[n]["row_states"] for n in want], ["MO", "OH", "TX"])

    def test_a_text_held_in_the_store_is_copied_and_not_requested(self):
        import audit_fetch as fetch
        tmp = tempfile.mkdtemp(prefix="erw_s157_audit_")
        try:
            store_dir = os.path.join(tmp, "store")
            os.makedirs(store_dir)
            held = os.path.join(store_dir, "2026-17394.txt")
            shutil.copyfile(os.path.join(FIX, "fr_2026-17394.text.txt"), held)
            st = fetch.Store(os.path.join(tmp, "audit"))
            row = st.take_held("federalregister:2026-17394", "text",
                               "https://www.federalregister.gov/documents/full_text/text/2026/08/26/2026-17394.txt", held, "txt")
            self.assertEqual(row["status"], fetch.HELD)
            self.assertEqual((st.requests, st.bytes), (0, 0))   # neither ceiling counts it
            self.assertIsNotNone(st.have("federalregister:2026-17394", "text"))
            with open(held, "rb") as f:   # the copy's hash is the held file's, whatever its line ends on this machine
                self.assertEqual(row["sha256"], hashlib.sha256(f.read()).hexdigest())
            self.assertTrue(os.path.exists(os.path.join(tmp, "audit", row["file"])))
            again = fetch.Store(os.path.join(tmp, "audit"))   # the manifest is read back
            self.assertEqual((len(again.rows), again.requests), (1, 0))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_the_fetch_sends_no_persons_address(self):
        import audit_fetch as fetch
        self.assertNotIn("@", fetch.UA["User-Agent"])
        self.assertLessEqual(fetch.MAX_REQUESTS, 200)
        for host in ("misoenergy.org", "dataminer", "api.pjm.com"):
            self.assertIn(host, fetch.FORBIDDEN)


class Fetch(unittest.TestCase):
    def test_every_source_was_reached_under_the_ceiling(self):
        man = rows("audit_s157_manifest.csv")
        asked = [m for m in man if m["status"] != "held"]
        self.assertLessEqual(len(asked), 200)
        self.assertLess(sum(int(m["bytes"] or 0) for m in asked), 200 * 1024 * 1024)
        sample = rows("audit_s157_sample.csv")
        got = {(m["key"], m["kind"]) for m in man if m["status"] in ("200", "held")}
        for s in sample:
            kinds = ("api", "text") if s["event_id"].startswith("federalregister:") else ("page",)
            for k in kinds:
                self.assertIn((s["event_id"], k), got)
        for m in man:   # no address with a person's e-mail in it, no paused or licensed host
            self.assertNotIn("@", m["url"])
            self.assertNotIn("%40", m["url"])
            self.assertNotIn("misoenergy.org", m["url"])
            self.assertNotIn("pjm.com", m["url"])

    def test_the_fixtures_are_the_files_the_audits_saved(self):
        with open(os.path.join(FIX, "MANIFEST.csv"), encoding="utf-8") as f:
            listed = list(csv.DictReader(f))
        self.assertEqual(len(listed), 8)
        for m in listed:
            with open(os.path.join(FIX, m["fixture"]), "rb") as f:
                data = f.read()
            # the Register's files hold no carriage return; a Windows checkout may add one to each line end
            data = data.replace(b"\r\n", b"\n")
            self.assertEqual(hashlib.sha256(data).hexdigest(), m["sha256_of_the_response"], m["fixture"])
            self.assertEqual(len(data), int(m["bytes"]), m["fixture"])


class Files(unittest.TestCase):
    def test_no_em_dash_and_the_audit_prefix(self):
        names = sorted(n for n in os.listdir(AUDIT) if n.endswith(".py"))
        self.assertEqual([n for n in names if not n.startswith("audit_")], [])
        paths = [os.path.join(AUDIT, n) for n in names] + [os.path.abspath(__file__)]
        paths += [os.path.join(FIX, n) for n in os.listdir(FIX)]
        paths += [os.path.join(EVAL, n) for n in os.listdir(EVAL) if n.startswith("audit_s157_") or n == "audit_states_truth.csv"]
        for p in paths:
            with open(p, encoding="utf-8", errors="replace") as f:
                self.assertNotIn(chr(0x2014), f.read(), p)


if __name__ == "__main__":
    unittest.main()
