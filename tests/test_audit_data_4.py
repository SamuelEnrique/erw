"""Audit of the data pages, finding 5 (session 10233, docs/reviews/data-model-audit-2026-11-26.md): the data standard,
drawn on /data/standard and in /data's data dictionary, says its validator "enforces what this page states" and that
"Only the `series` shape has a connector and a validator today". The validator (warehouse/validate/erw_validate.py)
checks all three shapes, and does not check three rules the page states: which fields a provenance header names (it
warns only when there is no comment line), the x_ prefix of an extra column (a warning for series, nothing for entities
and events), and that an entity's namespace is the file's source part. The deferred list names entity_type and status
as unenforced, though Decision 20 enforces both for entities; "65 tables" stands for the cap's distance; 14 of the
validator's units are named only in the Decisions.

1. The validator as it is: an events and an entities table with unprefixed columns pass clean, a series file whose
   header names no address passes clean, a series whose namespace is not its file's source part passes, and the
   entities' vocabularies are enforced. Passes on main.
2. The fix on this branch, words only: the standard says what the validator checks and the three things it does not,
   where each rule is; the deferred list and the cap's line are brought up to date; the Units list names the Decisions
   that added units without a line. No figure moves. Fails on main."""
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "validate"))
import erw_validate  # noqa: E402


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


def report(name, text):
    d = tempfile.mkdtemp()
    p = os.path.join(d, name)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    return erw_validate.validate(p)


class TheValidatorChecksLessThanTheStandardStates(unittest.TestCase):
    def test_the_validator_as_it_is(self):
        ev = report("audit_events.csv", "# Source: a test\n"
                    "event_id,event_date,event_type,parties,entity_ids,mw,price,currency,status,source,source_url,title\n"
                    "t:1,2026-01-01,filing,,,,,,,t:1,https://example.org/,a title\n")
        self.assertEqual(ev["errors"] + ev["warnings"], [])
        en = report("audit_things.csv", "# Source: a test\n"
                    "entity_id,entity_type,name,geo,lat,lon,capacity_mw,status,status_date,operator,source,note\n"
                    "t:1,plant,A,,,,,operating,,,t:1,a note\n")
        self.assertEqual(en["errors"] + en["warnings"], [])
        se = report("audit_all_things.csv", "# no address and no retrieval time here\n"
                    "entity,variable,ts_utc,value,unit,source\nzzz:1,load,2026-01-01T00:00:00Z,1,MW,t:1\n")
        self.assertEqual(se["errors"] + se["warnings"], [])
        self.assertIn("company_link", erw_validate.ENTITY_TYPES)
        self.assertIn("withdrawn", erw_validate.ENTITY_STATUS)
        std = src("docs", "datastandard.md")
        for u in ("dwt", "ratio", "TBtu", "MMBtu/MWh", "m3"):
            self.assertIn(u, erw_validate.UNITS)

    def test_the_standard_says_so(self):
        std = flat(src("docs", "datastandard.md"))
        for gone in ("Only the `series` shape has a connector and a validator today.", "enforces the `series` rules below.",
                     "A controlled vocabulary for `variable`, `entity_type`, `event_type` and `status`", "puts the cap far away: 65 tables."):
            self.assertNotIn(gone, std)
        for s in ("`events` (session 6, Decision 15) and `entities` (session 8, Decision 20) have had connectors and validator checks since",
                  "checks the rules of the three shapes below, with three exceptions this page states where they arise",
                  "The validator warns when a file has no comment line at all; it does not check which of these the lines name.",
                  "The validator warns of an unprefixed column in a `series` table and does not check `entities` or `events` tables",
                  "The validator checks the form `namespace:native_id` only (a warning, for `series`); a derived or consolidated table keeps its inputs' namespaces",
                  "(`entity_type` and the `status` of an entity have been enforced since Decision 20)",
                  "left 65 tables then; `coverage.csv` lists the tables now",
                  "Some Decisions added units without a line in this list: `dwt` (Decision 22)"):
            self.assertIn(s, std)


if __name__ == "__main__":
    unittest.main()
