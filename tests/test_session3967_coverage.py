"""Session 3967 (chain 278): a derived table kept internal over public inputs, named.

The daily re-run of 14 November 2026 stopped at coverage: "datacenter_tracker_rollups: license internal, but its inputs
make it public". The rollups aggregate datacenter_projects (tier public, its rows held on the site as "license needed");
session 3775 registered them internal for that reason, and session 3888's Derived from line made the license rule ask
for public. build_coverage.py now names the table in INTERNAL_OVER_PUBLIC; any other table still takes its inputs'
license, both ways. No network, no lock.
"""
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (("warehouse", "connectors"), ("warehouse", "metadata")):   # metadata first: validate/ holds a shim of the name
    sys.path.insert(0, os.path.join(ROOT, *p))
import build_coverage as bc  # noqa: E402
assert os.path.basename(os.path.dirname(bc.__file__)) == "metadata", bc.__file__


def rows(name, license_):
    return [dict(table="datacenter_projects", license="public", _derived_from=None),
            dict(table=name, license=license_, _derived_from=["datacenter_projects"])]


class TheException(unittest.TestCase):
    def test_only_the_rollups_are_named(self):
        self.assertEqual(set(bc.INTERNAL_OVER_PUBLIC), {"datacenter_tracker_rollups"})

    def test_the_rollups_pass_internal(self):
        out = bc.apply_derived(rows("datacenter_tracker_rollups", "internal"))
        self.assertEqual([(r["table"], r["license"], r["derived"]) for r in out],
                         [("datacenter_projects", "public", "no"), ("datacenter_tracker_rollups", "internal", "yes")])

    def test_the_rollups_may_still_be_public(self):
        out = bc.apply_derived(rows("datacenter_tracker_rollups", "public"))
        self.assertEqual(out[1]["license"], "public")

    def test_any_other_table_internal_over_public_still_fails(self):
        with self.assertRaises(ValueError) as e:
            bc.apply_derived(rows("another_rollup", "internal"))
        self.assertIn("but its inputs make it public", str(e.exception))

    def test_the_rollups_public_over_an_internal_input_still_fails(self):
        r = [dict(table="datacenter_projects", license="internal", _derived_from=None),
             dict(table="datacenter_tracker_rollups", license="public", _derived_from=["datacenter_projects"])]
        with self.assertRaises(ValueError):
            bc.apply_derived(r)

    def test_the_builder_still_names_its_input_and_says_internal(self):
        src = open(os.path.join(ROOT, "warehouse", "derived", "datacenter_tracker_rollups.py"), encoding="utf-8").read()
        self.assertIn('"Derived from: datacenter_projects"', src)
        self.assertRegex(src, r'license="internal", tables=\[NAME\]')


if __name__ == "__main__":
    unittest.main()
