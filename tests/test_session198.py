"""Session 198: the battery tool's data side. What is held to:

  the step       ercot_as_quantities (ERCOT's DAM Ancillary Service Plan, NP4-33-CD) is a daily step of
                 warehouse/scheduled.py whose input is the table itself, rebuilt from the archive when absent, so the
                 connector always merges into the table held and never writes a month in its place;
  the run        warehouse/run_data_machine.sh starts it once, as a soft step, after ERCOT's price steps and before
                 the page files; the validator and the coverage builder that follow gate that table's stores only and
                 are never piped; the runner's daily run does not start it;
  the connector  asks ERCOT's pause before any request; stops before the first download when a run would download
                 more than 60 files (a file saved by an earlier run is not a download); holds the ceiling of 400,000
                 rows against the table as it will stand after the merge; and gives a row the retrieval time of its
                 file, so a file read again from warehouse/raw does not restamp its rows;
  the note       docs/methods/battery_earns_algorithm.md, section 3.3, states what ERCOT's documents say of the
                 durations before 9 December 2022 and before 5 December 2025, each quotation with its address.

No request, no model call, no table of warehouse/output: every reader and writer the connector uses is replaced."""
import datetime as dt
import io
import json
import os
import re
import sys
import unittest
import zipfile
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import ercot_as_prices as eap  # noqa: E402
import ercot_as_quantities as q  # noqa: E402
import iso_prices as ip  # noqa: E402
import scheduled  # noqa: E402

EM = chr(0x2014)
STEP = 'soft_step dm_ercot_as_quantities "$PYTHON" warehouse/scheduled.py ercot_as_quantities'
FILES = ["tests/test_session198.py", "warehouse/scheduled.py", "warehouse/run_data_machine.sh", "warehouse/connectors/ercot_as_quantities.py",
         "docs/methods/battery_earns_algorithm.md", "archive/sessions/SESSION_198_REPORT.md"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def plan_zip(first_day, days=2):
    """One NP4-33-CD file: the plan for `days` delivery days from first_day, every service and hour."""
    lines = ["DeliveryDate,HourEnding,AncillaryType,Quantity,DSTFlag"]
    for k in range(days):
        day = (first_day + dt.timedelta(days=k)).strftime("%m/%d/%Y")
        lines += [f"{day},{h:02d}:00,{s},{100 + h},N" for s in eap.SERVICES for h in range(1, 25)]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("x.ASPLANNP433.csv", "\n".join(lines) + "\n")
    return buf.getvalue()


class Site:
    """ERCOT's reports site, as the connector meets it through ip.fetch_raw and ip.raw_cached: n files, published on
    n consecutive days from 1 April 2026 (no clock change in the window), `saved` of them already in warehouse/raw."""
    SAVED_AT = "2026-04-02T10:00:00Z"
    NOW = "2026-07-01T12:00:00Z"

    def __init__(self, n, saved=0):
        self.first = dt.date(2026, 4, 1)
        self.docs = [{"DocID": str(1000 + i), "FriendlyName": f"plan_{i}_csv",
                      "PublishDate": f"{self.first + dt.timedelta(days=i)}T05:00:12-05:00"} for i in range(n)]
        self.saved = {eap.DOWNLOAD.format(d["DocID"]) for d in self.docs[:saved]}
        self.asked, self.written = [], []

    def body(self, url):
        i = int(url.rsplit("=", 1)[1]) - 1000
        return plan_zip(self.first + dt.timedelta(days=i + 1))

    def raw_cached(self, connector, url):
        return (self.body(url), {"retrieved_at": self.SAVED_AT, "cached": True}) if url in self.saved else None

    def fetch_raw(self, connector, url, log, **kw):
        if url == eap.DOC_LIST.format(q.REPORT):
            self.asked.append("list")
            listed = [{"Document": d} for d in self.docs]
            return json.dumps({"ListDocsByRptTypeRes": {"DocumentList": listed}}).encode(), {"retrieved_at": self.NOW}
        hit = self.raw_cached(connector, url)
        if hit:
            return hit
        self.asked.append(url)
        return self.body(url), {"retrieved_at": self.NOW, "cached": False}

    def run(self, held=frozenset(), paused=None):
        log = mock.MagicMock()
        with mock.patch.object(ip, "paused", return_value=paused), mock.patch.object(ip, "Log", return_value=log), \
                mock.patch.object(ip, "RAW", mock.MagicMock()), mock.patch.object(ip, "fetch_raw", self.fetch_raw), \
                mock.patch.object(ip, "raw_cached", self.raw_cached), mock.patch.object(ip, "update_sources"), \
                mock.patch.object(ip, "write_status") as status, mock.patch.object(q.os, "makedirs"), \
                mock.patch.object(q, "held_keys", return_value=set(held)), \
                mock.patch.object(ip, "write_csv", side_effect=lambda s, *a, **k: self.written.append(s)), \
                mock.patch.object(ip, "pause_line", return_value="PAUSED"), mock.patch.object(eap, "PAUSE", 0), \
                mock.patch("builtins.print"), mock.patch.object(sys, "stderr", io.StringIO()):
            rc = q.main([])
        self.results = status.call_args[0][2] if status.call_args else None
        return rc


class TheStep(unittest.TestCase):
    def test_the_scheduler_names_it_and_its_input_is_the_table_itself(self):
        job = scheduled.JOBS["ercot_as_quantities"]
        self.assertEqual(job["cadence"], "daily")
        self.assertEqual(job["cmd"], ["warehouse/connectors/ercot_as_quantities.py"])
        # the connector merges the day into the table held: without the table it would write a month as the whole
        self.assertEqual(job["tables"], ["ercot_as_quantities"])
        self.assertEqual(job["restore"], ["ercot_as_quantities"])
        self.assertTrue(os.path.exists(os.path.join(ROOT, job["cmd"][0])))

    def test_without_the_table_and_without_the_archive_nothing_is_requested(self):
        ran = []
        with mock.patch.object(scheduled, "missing", return_value=(["ercot_as_quantities"], [], [])), mock.patch("builtins.print"):
            rc = scheduled.step("ercot_as_quantities", run=lambda *a, **k: ran.append(a), restore=lambda t: False)
        self.assertEqual(ran, [])
        self.assertEqual(rc, int(os.environ.get("ERW_SKIP_EXIT") or 0))

    def test_the_data_machine_starts_it_once_after_the_price_steps_and_before_the_pages(self):
        text = src("warehouse", "run_data_machine.sh").split("set -uo pipefail", 1)[1]   # the commands, past the header's words
        self.assertEqual(text.count(STEP), 1)
        zones = text.index('soft_step dm_ercot_zone_prices "$PYTHON" warehouse/connectors/ercot_zone_prices.py --refresh')
        self.assertGreater(text.index(STEP), zones)
        self.assertGreater(text.index(STEP), text.index("soft_step dm_zone_redivis"))        # after the load zones' own stores
        self.assertLess(text.index(STEP), text.index('soft_step dm_datacenter_page "$PYTHON" warehouse/derived/datacenter_page.py'))
        self.assertLess(text.index(STEP), text.index("# ---- 4. the commit"))

    def test_it_is_never_fatal_and_no_gate_of_it_is_piped(self):
        text = src("warehouse", "run_data_machine.sh").split("set -uo pipefail", 1)[1]
        block = text.split("# ---- 2b.", 1)[1].split("# ---- 3. the page files", 1)[0]
        self.assertNotIn("--strict", block)
        self.assertNotRegex(block, r"(?m)^\s*exit\b")
        gates = [ln for ln in block.splitlines() if ln.lstrip().startswith(('"$PYTHON" warehouse/validate/erw_validate.py',
                                                                            '"$PYTHON" warehouse/metadata/build_coverage.py'))]
        self.assertEqual(len(gates), 2)
        for ln in gates:
            self.assertNotIn("|", ln)
        # its stores: the validator before coverage, coverage before the archive and the draft, each of those a soft step
        order = [block.index(x) for x in ("erw_validate.py", "build_coverage.py", "soft_step dm_as_quantities_archive", "soft_step dm_as_quantities_redivis")]
        self.assertEqual(order, sorted(order))
        self.assertIn('--tables "^${AS_Q}\\$"', block)
        self.assertIn("0 new, ", block)                       # a day with no new delivery day leaves the stores alone

    def test_the_load_zone_block_is_as_it_was(self):
        text = src("warehouse", "run_data_machine.sh")
        for line in ('soft_step dm_zone_archive "$PYTHON" warehouse/archive/archive.py write --tables "^${ZONES}\\$"',
                     'soft_step dm_zone_redivis "$PYTHON" warehouse/redivis/upload.py --tables "$ZONES"', "soft_step dm_sync"):
            self.assertEqual(text.count(line), 1, line)

    def test_the_runner_does_not_start_it(self):
        # the runner restores only its rolling tables: this one is extended where it is held, and uploaded from there
        for name in ("run_daily.sh", "run_monthly.sh"):
            for ln in src("warehouse", name).splitlines():
                if not ln.lstrip().startswith("#"):
                    self.assertNotIn("ercot_as_quantities", ln, name)


class TheConnector(unittest.TestCase):
    def test_the_ceilings_are_the_approved_ones(self):
        self.assertEqual(q.MAX_FILES, 60)
        self.assertEqual(q.CEILING, 400_000)

    def test_a_paused_ercot_is_not_asked(self):
        site = Site(3)
        with self.assertRaises(SystemExit):
            site.run(paused={"scope": "ercot"})
        self.assertEqual(site.asked, [])
        body = src("warehouse", "connectors", "ercot_as_quantities.py").split("def main(", 1)[1]
        self.assertLess(body.index('ip.paused("ercot")'), body.index("ip.fetch_raw("))

    def test_a_run_downloads_what_is_listed_and_takes_the_next_day_from_each_file(self):
        site = Site(3)
        self.assertEqual(site.run(), 0)
        self.assertEqual(len(site.asked), 4)                  # the list and three files
        s = site.written[0]
        self.assertEqual(len(s), 3 * 5 * 24)                  # each file gives the day after its publication, and no other
        self.assertEqual(sorted(s["ts_utc"].str[:10].unique())[0], "2026-04-02")
        self.assertEqual(set(s["retrieved_at"]), {Site.NOW})
        self.assertFalse(s.duplicated(["entity", "variable", "ts_utc"]).any())

    def test_more_than_sixty_downloads_stop_before_the_first(self):
        site = Site(61)
        self.assertEqual(site.run(), 1)
        self.assertEqual(site.asked, ["list"])                # the list was read; no file was requested
        self.assertEqual(site.written, [])
        self.assertEqual(site.results[0]["status"], "failed")
        self.assertIn("61 files to download exceed the approved 60", site.results[0]["detail"])

    def test_a_saved_file_is_not_a_download_and_keeps_its_retrieval_time(self):
        site = Site(61, saved=59)                             # 61 listed, 2 to download: under the ceiling
        self.assertEqual(site.run(), 0)
        self.assertEqual(len(site.asked), 3)                  # the list and the two files not saved
        s = site.written[0]
        at = s.groupby(s["ts_utc"].str[:10])["retrieved_at"].agg(lambda x: sorted(set(x)))
        self.assertEqual(at["2026-04-02"], [Site.SAVED_AT])   # read again from warehouse/raw: the day it was downloaded
        self.assertEqual(at[sorted(at.index)[-2]], [Site.NOW])

    def test_the_row_ceiling_is_held_against_the_merged_table(self):
        held = {("ercot:X", f"k{i}") for i in range(q.CEILING - 100)}
        site = Site(1)
        self.assertEqual(site.run(held=held), 1)              # 120 new rows on 399,900 held
        self.assertEqual(site.written, [])
        self.assertIn("would exceed the approved ceiling", site.results[0]["detail"])
        again = Site(1)
        self.assertEqual(again.run(held={("ercot:X", f"k{i}") for i in range(q.CEILING - 120)}), 0)

    def test_a_row_already_held_counts_once(self):
        site = Site(1)
        site.run()
        s = site.written[0]
        held = set(zip(s["entity"], s["ts_utc"])) | {("ercot:X", f"k{i}") for i in range(q.CEILING - 120)}
        self.assertEqual(Site(1).run(held=held), 0)           # the same 120 rows again: nothing is added to the count


class TheNote(unittest.TestCase):
    """docs/methods/battery_earns_algorithm.md, section 3.3.1: what ERCOT's documents state, quoted with their addresses.
    The model is not changed by it: the hours and their labels in warehouse/derived/battery_stack.py are as they were."""
    DOCS = ("https://www.ercot.com/files/docs/2022/05/17/1096NPRR-28%20PUCT%20Report%20051222.docx",
            "https://www.ercot.com/files/docs/2024/04/12/1186NPRR-36%20PUCT%20Report%20041124.docx",
            "https://www.ercot.com/files/docs/2025/08/04/1282NPRR-20-PUCT-Report-073125.docx")

    @classmethod
    def setUpClass(cls):
        note = src("docs", "methods", "battery_earns_algorithm.md")
        cls.note = note
        cls.part = note[note.index("#### 3.3.1 What ERCOT's own documents state"):note.index("**The cap this puts on a product.**")]

    def test_three_documents_each_with_its_address_and_page(self):
        self.assertEqual(len(re.findall(r"https://www\.ercot\.com/files/docs/[^`\s]+", self.part)), 3)   # the approved pull: at most three
        for url in self.DOCS:
            self.assertIn(url, self.part)
        for page in ("page 9 of 20", "pages 75 and 76 of 93", "pages 35 to 39 of 40"):
            self.assertIn(page, self.part)

    def test_the_quotations(self):
        for words in ('"Running at a specified output level for at least one hour"',
                      "multiplied by the remaining time in the Operating Hour, in hours",
                      "multiplied by 0.25 hours", '"at least 30 minutes"',
                      '"changing the duration requirement for Regulation Service and RRS from 15 minutes to 30 minutes"'):
            self.assertIn(words, self.part)
        self.assertIn("**Not stated in any of the three documents.**", self.part)     # 2018 to 26 June 2024: the label stays
        self.assertIn("The model and the page are unchanged by this section", self.part)

    def test_the_table_of_durations_says_which_hour_is_stated_and_which_assumed(self):
        table = self.note[self.note.index("### 3.3 The products"):self.note.index("#### 3.3.1")]
        self.assertIn("to 26 June 2024: assumed, no document read states it", table)
        self.assertIn("27 June 2024 to 4 December 2025: NPRR 1186", table)
        self.assertIn('before: the Protocols as NPRR 1096 found them, "at least one hour"', table)
        self.assertIn("| ECRS, bought from 10 June 2023 | up | 2 hours; 1 hour from 5 December 2025 | NPRR 1096; NPRR 1282 |", table)

    def test_the_model_is_as_it_was(self):
        model = src("warehouse", "derived", "battery_stack.py")
        self.assertEqual(model.count('("2018-01-01", 1.0, ONE_HOUR)'), 4)              # Regulation Up and Down, Responsive Reserve, Non-Spin
        self.assertEqual(model.count('("2025-12-05", 0.5, NPRR1282)'), 3)
        self.assertIn('("2022-12-09", 4.0, NPRR1096)', model)
        self.assertIn('hours=[("2023-06-10", 2.0, NPRR1096), ("2025-12-05", 1.0, NPRR1282)]', model)
        self.assertNotIn("1186", model)
        self.assertNotIn(EM, self.note)


class TheFiles(unittest.TestCase):
    def test_no_em_dash(self):
        for f in FILES:
            self.assertNotIn(EM, src(*f.split("/")), f)

    def test_the_shell_script_keeps_unix_line_ends(self):
        with open(os.path.join(ROOT, "warehouse", "run_data_machine.sh"), "rb") as f:
            self.assertNotIn(b"\r\n", f.read())


if __name__ == "__main__":
    unittest.main()
