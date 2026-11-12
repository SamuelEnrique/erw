"""Session 3764 (chain 211): the All grids tab reads the filed large-load schedules and the operators' connection rules.

warehouse/derived/siting_page.py writes tariffs.json (each utility's schedules by EIA id, every figure with its page and
printed words, the filing, the status; "held" the EIA ids of schedules held for a license under ruling 4) and
conn_rules.json (by grid, each step a document states). Held here on fixtures: no request, no warehouse table.
"""
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import siting_page  # noqa: E402

TARIFFS = """# Energy Research Warehouse (ERW): fixture
# License: public (row-level holds): ... Held for a license and not written here (their only source asks written permission): Ohio Power Company (AEP Ohio), Schedule DCT, Data Center Tariff (EIA 14006).
entity,variable,ts_utc,value,unit,freq,geo,market,node,source,source_url,retrieved_at,vintage,x_eia_id,x_utility,x_sector,x_state,x_grid,x_schedule,x_tariff_sheet,x_voltage,x_commission,x_docket,x_document,x_page,x_printed,x_min_bill,x_collateral,x_exit_fee,x_ramp,x_term,x_status,x_license,x_notes
filed:19876:gs4,demand_charge_transmission,2026-01-01T00:00:00Z,2.31,USD/kW-month,,US-VA,,Schedule GS-4,filed:large_load_tariffs,https://example.org/gs4.pdf,2026-11-12T11:14:11Z,,19876,Dominion,large,VA,PJM,Schedule GS-4,GS-4,,Virginia SCC,PUR-2025-00058,GS-4 filed,3,"Transmission Service Voltage @ $2.310 per kW",,,,,,adopted,public,
filed:19876:gs4,min_bill_pct,2026-01-01T00:00:00Z,85,pct,,US-VA,,Schedule GS-4,filed:large_load_tariffs,https://example.org/gs4.pdf,2026-11-12T11:14:11Z,,19876,Dominion,large,VA,PJM,Schedule GS-4,GS-4,,Virginia SCC,PUR-2025-00058,GS-4 filed,6,"Eighty-five percent of the Customer's contracted demand",,,,,,adopted,public,
"""

RULES = """# Energy Research Warehouse (ERW): fixture
event_id,event_date,event_type,parties,entity_ids,mw,price,currency,status,source,source_url,x_body,x_grid,x_utility,x_eia_id,x_state,x_document,x_document_date,x_section,x_page,x_step,x_duration,x_duration_unit,x_date_kind,x_printed,x_retrieved_at
rule:pjm:eit:c,2026-01-16,connection_rule,PJM,,,,,stated,filed:large_load_connection_rules,https://example.org/pjm.pdf,PJM,PJM,,,PA,PJM Board letter,2026-01-16,"Appendix C",12,the EIT runs,10,months,document date,"Time Frame: 10 months from application",2026-11-12T11:21:29Z
"""


def written(text, name):
    d = tempfile.mkdtemp()
    p = os.path.join(d, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


class TheFiles(unittest.TestCase):
    def test_tariffs_carry_the_filing_and_the_held_ids(self):
        t = siting_page.tariffs_file(written(TARIFFS, "utility_large_load_tariffs.csv"))
        self.assertEqual(t["held"], ["14006"])
        gs4 = t["utilities"]["19876"][0]
        self.assertEqual((gs4["schedule"], gs4["status"], gs4["url"], gs4["effective"]), ("Schedule GS-4", "adopted", "https://example.org/gs4.pdf", "2026-01-01"))
        self.assertEqual([(x["variable"], x["page"]) for x in gs4["figures"]], [("demand_charge_transmission", "3"), ("min_bill_pct", "6")])
        self.assertEqual(gs4["figures"][0]["printed"], "Transmission Service Voltage @ $2.310 per kW")
        self.assertIsNone(gs4["demand"])     # session 730's field: the schedule prints no single demand_charge
        json.dumps(t)

    def test_rules_by_grid(self):
        r = siting_page.conn_rules_file(written(RULES, "large_load_connection_rules.csv"))
        step = r["grids"]["pjm"][0]
        self.assertEqual((step["duration"], step["unit"], step["page"]), ("10", "months", "12"))


class TheTab(unittest.TestCase):
    def test_the_view_shows_the_filed_steps_beside_the_load_line(self):
        v = open(os.path.join(ROOT, "site", "app", "cost-of-power", "AllGridsView.tsx"), encoding="utf-8").read()
        self.assertIn('{c.filed ? <>, <Tp tip={c.filed}>filed steps</Tp></> : null}', v)

    def test_the_files_are_built(self):
        for name in ("tariffs.json", "conn_rules.json"):
            with open(os.path.join(ROOT, "site", "data", "siting", name), encoding="utf-8") as f:
                d = json.load(f)
            self.assertIn("table", d)


if __name__ == "__main__":
    unittest.main()
