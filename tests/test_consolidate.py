"""Session 29: consolidated tables (warehouse/consolidate.py). A family's members are built into one table with the
partition in a column, split back byte for byte with their own headers, and a member the run did not write is
carried from the consolidated table as it was."""
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import consolidate as C  # noqa: E402

COLS = "entity,variable,ts_utc,value,unit,freq,geo,market,node,source,source_url,retrieved_at,vintage"


def member(ba, n, retrieved="20260929T000000Z"):
    head = [f"# Energy Research Warehouse (ERW): EIA-930 {ba} demand",
            f"# Retrieved: {retrieved} (UTC) by warehouse/connectors/eia930.py",
            f"# Source: eia:electricity/rto/region-data EIA-930, https://api.eia.gov/{ba}",
            "#   document list: https://www.eia.gov/opendata/"]
    rows = [f"eia930:{ba.upper()},demand_mw,2026-09-0{i + 1}T00:00:00Z,{100 + i},MW,PT1H,US,,,"
            f"eia:electricity/rto/region-data,\"https://api.eia.gov/x?a=1,b=2\",2026-09-29T00:00:00Z," for i in range(n)]
    return "\n".join(head + [COLS] + rows) + "\n"


class ConsolidateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.out = os.path.join(self.tmp, "output")
        os.makedirs(self.out)
        self.map = os.path.join(self.tmp, "map.csv")
        with open(self.map, "w", encoding="utf-8") as f:
            f.write("old_table,new_table,partition,added_columns,session,migrated_on\n"
                    "eia930_aaa_demand,eia930_all_demand,ba=aaa,ba,29,2026-09-29\n"
                    "eia930_bbb_demand,eia930_all_demand,ba=bbb,ba,29,2026-09-29\n")
        self.patches = [mock.patch.object(C, "OUT", self.out), mock.patch.object(C, "MAP", self.map),
                        mock.patch.object(C, "STAGE", os.path.join(self.out, "members")),
                        mock.patch.object(C, "SPLIT_RECORD", os.path.join(self.out, "members", "_split.json"))]
        for p in self.patches:
            p.start()
        for ba, n in (("aaa", 3), ("bbb", 2)):
            with open(os.path.join(self.out, f"eia930_{ba}_demand.csv"), "w", encoding="utf-8", newline="") as f:
                f.write(member(ba, n))

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def read(self, name, sub=""):
        with open(os.path.join(self.out, sub, name + ".csv"), encoding="utf-8") as f:
            return f.read()

    def test_build_adds_the_partition_column_and_moves_the_members(self):
        fams = C.read_map()
        total, counts = C.build_family("eia930_all_demand", fams["eia930_all_demand"])
        self.assertEqual((total, counts), (5, {"eia930_aaa_demand": 3, "eia930_bbb_demand": 2}))
        text = self.read("eia930_all_demand")
        self.assertIn(COLS + ",ba\n", text)
        self.assertEqual(text.count(",aaa\n"), 3)
        self.assertIn("# Member eia930_bbb_demand: # ", text.replace("Member eia930_bbb_demand: Energy", "Member eia930_bbb_demand: # Energy"))
        self.assertFalse(os.path.exists(os.path.join(self.out, "eia930_aaa_demand.csv")))
        self.assertTrue(os.path.exists(os.path.join(self.out, "members", "eia930_aaa_demand.csv")))

    def test_split_gives_back_each_member_byte_for_byte(self):
        before = {ba: member(ba, n) for ba, n in (("aaa", 3), ("bbb", 2))}
        fams = C.read_map()
        C.build_family("eia930_all_demand", fams["eia930_all_demand"])
        C.split_family("eia930_all_demand", fams["eia930_all_demand"])
        for ba in ("aaa", "bbb"):
            self.assertEqual(self.read(f"eia930_{ba}_demand"), before[ba])

    def test_a_member_the_run_did_not_write_is_carried_from_the_table(self):
        fams = C.read_map()
        C.build_family("eia930_all_demand", fams["eia930_all_demand"])
        with open(os.path.join(self.out, "eia930_aaa_demand.csv"), "w", encoding="utf-8", newline="") as f:
            f.write(member("aaa", 4, retrieved="20260930T000000Z"))  # a new day for one member only
        total, counts = C.build_family("eia930_all_demand", fams["eia930_all_demand"])
        self.assertEqual(counts, {"eia930_aaa_demand": 4, "eia930_bbb_demand": 2})
        self.assertIn("Retrieved: 20260930T000000Z", self.read("eia930_all_demand"))

    def test_a_member_with_other_columns_is_refused(self):
        with open(os.path.join(self.out, "eia930_bbb_demand.csv"), "w", encoding="utf-8", newline="") as f:
            f.write(member("bbb", 2).replace(COLS, COLS.replace("vintage", "x_other")))
        with self.assertRaises(RuntimeError):
            C.build_family("eia930_all_demand", C.read_map()["eia930_all_demand"])
        self.assertTrue(os.path.exists(os.path.join(self.out, "eia930_aaa_demand.csv")))  # nothing moved


if __name__ == "__main__":
    unittest.main()
