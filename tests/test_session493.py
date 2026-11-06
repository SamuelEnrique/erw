"""Session 493: BOEM's renewable energy leases and grants. The page's one table with its seven columns; BOEM's status
kept, mapped to the standard's vocabulary only where a word fits (Active); an unknown status or a repeated lease number
stops the run."""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import boem_leases as bl  # noqa: E402


def page(*rows):
    head = "".join(f"<th>{c}</th>" for c in bl.COLUMNS)
    body = "".join("<tr>" + "".join(f"<td>{v}</td>" for v in r) + "</tr>" for r in rows)
    return f"<html><body><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></body></html>"


ACTIVE = ["OCS-A 0486", "Revolution Wind", "Commercial Lease", "Wind", "2013", "Revolution Wind, LLC", "Active"]
EXPIRED = ["OCS-A 0472", "Deepwater Wind", "Interim Policy Lease*", "Wind", "2009", "Deepwater Wind, LLC", "Expired"]


class Leases(unittest.TestCase):
    def test_two_leases(self):
        t = bl.leases(page(ACTIVE, EXPIRED), "u", "r")
        by = {r["entity_id"]: r for _, r in t.iterrows()}
        self.assertEqual(sorted(by), ["boem:ocs-a_0472", "boem:ocs-a_0486"])
        self.assertEqual((by["boem:ocs-a_0486"]["status"], by["boem:ocs-a_0486"]["boem_status"]), ("active", "Active"))
        self.assertEqual((by["boem:ocs-a_0472"]["status"], by["boem:ocs-a_0472"]["boem_status"]), ("", "Expired"))
        self.assertEqual((by["boem:ocs-a_0472"]["entity_type"], by["boem:ocs-a_0472"]["effective_year"]), ("project", "2009"))

    def test_an_unknown_status_stops_the_run(self):
        with self.assertRaisesRegex(RuntimeError, "not in the map"):
            bl.leases(page(ACTIVE[:-1] + ["Suspended"]), "u", "r")

    def test_a_repeated_lease_stops_the_run(self):
        with self.assertRaisesRegex(RuntimeError, "given twice"):
            bl.leases(page(ACTIVE, ACTIVE), "u", "r")

    def test_a_changed_table_stops_the_run(self):
        html = page(ACTIVE).replace("<th>Status</th>", "<th>Lease Status</th>")
        with self.assertRaisesRegex(RuntimeError, "tables with the columns"):
            bl.leases(html, "u", "r")


if __name__ == "__main__":
    unittest.main()
