"""Session 46: policy_reads keeps a provenance header after a restore (daily run 13's failure), and the lease page
turns link prefetch off.

Energy Research Warehouse (ERW). No network, no model.
1. warehouse/policy/reads.py rebuilds the header of a policy_reads file that came back from the Redivis draft with the
   one-line placeholder, from its rows (read_at, model_id), leaving every row as it was; a file with an ERW header is
   left alone. Run on a copy in a temporary directory.
2. warehouse/redivis/upload.py --restore writes a table's header lines from erw_headers and never carries a
   placeholder line forward (checked in the source: the restore needs Redivis).
3. The lease page and the shared links: prefetch off on /severance/lease (components/SiteLink.tsx).

    python -m unittest tests.test_session46 -v
"""

import os
import re
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "policy"))
REAL = os.path.join(ROOT, "warehouse", "output", "policy_reads.csv")
PLACEHOLDER = ("# Restored from the Redivis draft of energy_research_warehouse by warehouse/redivis/upload.py --restore; "
               "the connector rewrites this header when it merges\n")


def data_lines(path):
    with open(path, encoding="utf-8") as f:
        return [ln for ln in f if not ln.startswith("#")]


class RestoredHeader(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(REAL):
            self.skipTest("warehouse/output/policy_reads.csv is not on this machine")
        import iso_prices as ip
        # session 59: all five paths, as test_session30 does (set_out_dir(OUT_DIR) put RAW_DIR under warehouse/output, so
        # later tests that read warehouse/raw found nothing)
        self.ip, self.saved = ip, (ip.OUT_DIR, ip.LOG_DIR, ip.METADATA_DIR, ip.STATUS_DIR, ip.RAW_DIR)
        self.tmp = tempfile.mkdtemp()
        ip.set_out_dir(self.tmp)
        import reads
        self.reads = reads
        self.path = os.path.join(self.tmp, "policy_reads.csv")

    def tearDown(self):
        ip = self.ip
        ip.OUT_DIR, ip.LOG_DIR, ip.METADATA_DIR, ip.STATUS_DIR, ip.RAW_DIR = self.saved
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_a_placeholder_header_is_rebuilt_from_the_rows(self):
        with open(self.path, "w", encoding="utf-8", newline="") as f:
            f.write(PLACEHOLDER)
            f.writelines(data_lines(REAL))
        self.assertTrue(self.reads.rebuild_restored_header(lambda m: None))
        with open(self.path, encoding="utf-8") as f:
            head = [ln for ln in f if ln.startswith("#")]
        self.assertTrue(head[0].startswith("# Energy Research Warehouse (ERW):"))
        self.assertTrue(any(ln.startswith("# Run log: ") for ln in head))
        self.assertTrue(any("Header rebuilt from the rows" in ln for ln in head))
        self.assertFalse(any("Restored from the Redivis draft" in ln for ln in head))
        self.assertEqual(data_lines(self.path), data_lines(REAL))
        self.assertFalse(self.reads.rebuild_restored_header(lambda m: None))  # done once, then left alone

    def test_an_erw_header_is_left_alone(self):
        shutil.copyfile(REAL, self.path)
        before = open(self.path, encoding="utf-8").read()
        self.assertFalse(self.reads.rebuild_restored_header(lambda m: None))
        self.assertEqual(open(self.path, encoding="utf-8").read(), before)


class Sources(unittest.TestCase):
    def test_the_restore_keeps_header_lines_and_drops_placeholders(self):
        src = open(os.path.join(ROOT, "warehouse", "redivis", "upload.py"), encoding="utf-8").read()
        self.assertIn("ds.table(HEADERS_TABLE).to_pandas_dataframe", src)
        self.assertIn('if not x.startswith("Restored from the Redivis draft")', src)
        self.assertIn('f.write(f"# {line}\\n")', src)

    def test_reads_rebuilds_on_a_day_with_nothing_new(self):
        src = open(os.path.join(ROOT, "warehouse", "policy", "reads.py"), encoding="utf-8").read()
        self.assertIn("        else:\n            rebuild_restored_header(log)", src)

    def test_no_prefetch_on_the_lease_page(self):
        site = open(os.path.join(ROOT, "site", "components", "SiteLink.tsx"), encoding="utf-8").read()
        self.assertIn('NO_PREFETCH = ["/severance/lease"]', site)
        page = open(os.path.join(ROOT, "site", "app", "severance", "lease", "page.tsx"), encoding="utf-8").read()
        tags = re.findall(r"<Link\s[^>]*>", page)
        self.assertTrue(tags and all("prefetch={false}" in t for t in tags), tags)


if __name__ == "__main__":
    unittest.main()
