"""Session 896: EIA-860's environmental schedules (boilers, cooling systems, emissions controls) and the multifuel
schedule; Decision 54, the entity type equipment.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia860_environment.py on sheets built here in EIA's form
(figures made up for the test, not EIA's): a boiler's design joined with its standards and its associations listed, the
environmental schedules' own status codes (CO, PL, SC, OZ) and codes in lower case, an empty code left empty, a code not
in the map stopping the run, a control's key carrying its ids; the multifuel schedule registered in eia860_schedules.py;
the entity type in the validator; the sector rules and the holds. No network.

    python -m unittest tests.test_session896 -v
"""

import io
import os
import sys
import unittest
import zipfile

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
sys.path.append(os.path.join(ROOT, "warehouse", "validate"))
import eia860_environment as E  # noqa: E402
import eia860_schedules as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402
import erw_validate as V  # noqa: E402

N = float("nan")
BASE = ["Utility ID", "Utility Name", "Plant Code", "Plant Name"]


def book(sheets):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf) as w:
        for name, rows in sheets.items():
            pd.DataFrame([["title"] + [N] * (len(rows[0]) - 1)] + rows).to_excel(w, sheet_name=name, header=False, index=False)
    return buf.getvalue()


def zf(boiler_status="OP", control_status="co"):
    assoc = {n: [BASE + ["Boiler ID", h, "Steam Plant Type"], [1, "U", 3, "Barry", "1", v, 1]]
             for n, h, v in [("Boiler Generator", "Generator ID", "G1"), ("Boiler Cooling", "Cooling ID", "C1"),
                             ("Boiler Particulate Matter", "Particulate Matter Control ID", "P1"), ("Boiler SO2", "SO2 Control ID", "S1"),
                             ("Boiler NOx", "NOx Control ID", "N1"), ("Boiler Mercury", "Mercury Control ID", "M1"),
                             ("Boiler Stack Flue", "Stack / Flue ID", "1-3")]}
    assoc["Boiler Generator"].append([1, "U", 3, "Barry", "1", "G2", 1])
    assoc["Emissions Control Equipment"] = [
        BASE + ["Equipment Type", "Particulate Matter Control ID", "SO2 Control ID", "NOx Control ID", "Mercury Control ID", "Status",
                "Inservice Month", "Inservice Year", "Retirement Month", "Retirement Year", "Total Cost (Thousand Dollars)"],
        [1, "U", 3, "Barry", "SR", N, N, "N1", N, control_status, 5, 2027, N, N, 900]]
    equip = {
        "Boiler Info & Design Parameters": [BASE + ["State", "Boiler ID", "Boiler Status", "Inservice Month", "Inservice Year",
                                                    "Retirement Month", "Retirement Year", "Firing Type 1"],
                                            [1, "U", 3, "Barry", "AL", "1", boiler_status, 2, 1954, N, N, "TF"]],
        "Emission Standards & Strategies": [BASE + ["State", "Boiler ID", "Boiler Status", "Regulation Sulfur"],
                                            [1, "U", 3, "Barry", "AL", "1", boiler_status, "FD"]],
        "Cooling": [BASE + ["State", "Cooling ID", "Cooling Status", "Inservice Month", "Inservice Year", "Cooling Water Source"],
                    [1, "U", 3, "Barry", "AL", "C1", "SC", 2, 1954, "Mobile River"]],
    }
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("6_1_EnviroAssoc_Y2025.xlsx", book(assoc))
        z.writestr("6_2_EnviroEquip_Y2025.xlsx", book(equip))
    return zipfile.ZipFile(io.BytesIO(buf.getvalue()))


class Environment(unittest.TestCase):
    def test_boiler_joined_and_listed(self):
        t, _ = E.build(zf(), "u", "r")
        b = t["boilers"].set_index("entity_id").loc["eia860_boiler:3:1"]
        self.assertEqual((b.entity_type, b.status, b.status_date, b.geo), ("equipment", "operating", "1954-02-01", "US-AL"))
        self.assertEqual((b.x_generator_ids, b.x_so2_control_ids, b.x_stack_flue_ids, b.x_regulation_sulfur), ("G1;G2", "S1", "1-3", "FD"))

    def test_status_codes(self):
        t, _ = E.build(zf(boiler_status="op", control_status="co"), "u", "r")
        self.assertEqual(t["boilers"].status.iloc[0], "operating")
        self.assertEqual(t["boilers"].x_eia_status.iloc[0], "op")
        self.assertEqual(t["cooling"].status.iloc[0], "operating")                        # SC, cold standby
        c = t["controls"].set_index("entity_id").loc["eia860_control:3:SR:nox_N1"]
        self.assertEqual((c.status, c.status_date, c.x_total_cost_thousand_dollars), ("under_construction", "", "900"))
        self.assertEqual(E.build(zf(control_status=""), "u", "r")[0]["controls"].status.iloc[0], "")
        with self.assertRaises(RuntimeError):
            E.build(zf(boiler_status="ZZ"), "u", "r")


class Registered(unittest.TestCase):
    def test_multifuel_unit_type_sectors_and_holds(self):
        self.assertEqual(S.TABLES["3_5_Multifuel"]["name"], "eia860_multifuel_generators")
        self.assertIn("equipment", V.ENTITY_TYPES)
        for name in ("eia860_boilers", "eia860_cooling_systems", "eia860_emission_controls", "eia860_multifuel_generators"):
            self.assertEqual(B.sector_of(name), "power")
            self.assertIn(name, R.STORAGE_HELD)
            with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
                self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
