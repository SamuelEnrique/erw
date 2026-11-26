"""Audit of the project map, finding 6 (session 10216, docs/reviews/map-model-audit-2026-11-26.md): a test only, not
for landing. Outside Alaska, seven units of the page's copy (19 November 2026) stand over 200 miles from the internal
point of the county EIA names for them: AmericoldCA - Plainville, CT (2 MW, Hartford County, drawn in California,
2,600 miles off), Big Creek Solar LLC (400 MW planned, Lee County, Arkansas, drawn in California, 1,537 miles),
Hardwood Hammock (74.5 MW planned, Walton County, Florida, drawn in central Florida, 349 miles), Rangeley (3 MW,
Franklin County, Maine, drawn at sea south of Massachusetts, 276 miles), Athens Solar I (Hybrid) (two units of 250 MW
planned, Placer County, California, drawn on the central coast, 232 miles) and Mullin Creek #1 Generating Station
(489.7 MW planned, Nodaway County, Missouri, drawn in Kansas, 230 miles): 1,469.2 MW, five planned (1,464.2 MW).
Either EIA's point or EIA's county is wrong; the map draws the point. For Samuel's ruling, default "left as it is";
the other choice draws such a unit at its county's point, marked, and moves no count or sum.

The Census Bureau's county gazetteers are read from ERW_GAZETTEER_DIR, or from the newest folder of
warehouse/raw/census_gazetteer/; the test is skipped where neither is held."""
import glob
import json
import math
import os
import re
import unicodedata
import unittest
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def gazetteer_dir():
    d = os.environ.get("ERW_GAZETTEER_DIR", "")
    if d and glob.glob(os.path.join(d, "*Gaz_counties*.zip")):
        return d
    found = sorted(glob.glob(os.path.join(ROOT, "warehouse", "raw", "census_gazetteer", "*", "*Gaz_counties*.zip")))
    return os.path.dirname(found[-1]) if found else ""


def key(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower().replace("&", " and ")
    s = re.sub(r"\bsaint\b", "st", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return re.sub(r" (county|parish|borough|census area|city and borough|municipality)$", "", s).replace(" ", "")


def miles(la1, lo1, la2, lo2):
    a = math.sin(math.radians(la2 - la1) / 2) ** 2 + math.cos(math.radians(la1)) * math.cos(math.radians(la2)) * math.sin(math.radians(lo2 - lo1) / 2) ** 2
    return 2 * 3958.8 * math.asin(min(1, math.sqrt(a)))


class FourPointsFarFromTheirCounty(unittest.TestCase):
    def test_four_units_outside_alaska_over_200_miles_from_their_county(self):
        d = gazetteer_dir()
        if not d:
            self.skipTest("the Census Bureau's county gazetteer is not held here")
        points = {}
        for z in sorted(glob.glob(os.path.join(d, "*Gaz_counties*.zip")), key=lambda p: "2020" in p):
            with zipfile.ZipFile(z) as zf:
                for member in zf.namelist():
                    raw = zf.read(member)
                    text = raw.decode("utf-8-sig") if raw[:3] == b"\xef\xbb\xbf" or b"\xc3" in raw[:200000] else raw.decode("latin-1")
                    rows = text.splitlines()
                    sep = "|" if "|" in rows[0] else "\t"
                    head = [h.strip() for h in rows[0].split(sep)]
                    if "USPS" not in head:
                        continue
                    for ln in rows[1:]:
                        v = dict(zip(head, [x.strip() for x in ln.split(sep)]))
                        points.setdefault((v["USPS"], key(v["NAME"])), (float(v["INTPTLAT"]), float(v["INTPTLONG"])))
        with open(os.path.join(ROOT, "site", "data", "map.json"), encoding="utf-8") as fh:
            f = json.load(fh)
        far = {}
        for i in range(f["kinds"][2]["start"]):
            st = f["states"][f["s"][i]]
            if st == "AK" or f["la"][i] is None or f["c"][i] < 0:
                continue
            hit = points.get((st, key(f["counties"][f["c"][i]])))
            if hit and miles(f["la"][i], f["lo"][i], *hit) > 200:
                far[f["id"][i]] = (f["names"][f["n"][i]], f["mw"][i], f["k"][i])
        self.assertEqual(sorted(far), ["64670:KOV4A", "67982:ATHS1", "67982:ATHSB", "68296:MC1", "68833:1", "70519:19735", "70557:G003"])
        self.assertAlmostEqual(sum(v[1] for v in far.values()), 1469.2, places=1)
        self.assertAlmostEqual(sum(v[1] for v in far.values() if v[2] == 1), 1464.2, places=1)


if __name__ == "__main__":
    unittest.main()
