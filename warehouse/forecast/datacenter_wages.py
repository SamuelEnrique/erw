"""Wages per job by state for /impact's datacenter (chain 740): Census County Business Patterns, 2023.

Operations: NAICS 518210 (computing infrastructure providers, data processing, web hosting, and related services),
from the warehouse table census_cbp_hosting_annual (public). Construction: NAICS 2362 (nonresidential building
construction) and 238 (specialty trade contractors), all legal forms, from the Bureau's 2023 state file read by
chain 740 (request 129 of runs/c740/probe/probe.csv on lab-desktop) until window A holds them (data request 7 of
docs/state/data_requests_forecast.md). Payroll per job = annual payroll / employment in the pay period including
12 March. A figure the Bureau withholds (D) or leaves empty is not written: that state's line is blank.

Usage (one run, untrusted file read as data):
  python -I warehouse/forecast/datacenter_wages.py CBP23ST_ZIP STATE_TXT CBP_HOSTING_CSV
"""
import csv, io, json, os, sys, zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(ROOT, "site", "data", "forecast", "datacenter_wages.json")
YEAR = 2023
CODES = {"2362//": "nonresidential_building", "238///": "specialty_trades"}


def main(zip_path, state_txt, hosting_csv):
    fips = {}
    for row in csv.DictReader(open(state_txt, encoding="utf-8"), delimiter="|"):
        fips[row["STATE"]] = row["STUSAB"].lower()

    construction = {}
    z = zipfile.ZipFile(zip_path)
    with z.open("cbp23st.txt") as f:
        for row in csv.DictReader(io.TextIOWrapper(f, encoding="latin-1")):
            if row["lfo"] != "-" or row["naics"] not in CODES:
                continue
            st = fips.get(row["fipstate"])
            if not st:
                continue
            emp, ap = row["emp"].strip(), row["ap"].strip()
            if not emp or not ap or int(emp) == 0:
                continue
            construction.setdefault(st, {})[CODES[row["naics"]]] = {
                "employment": int(emp), "annual_payroll_usd": int(ap) * 1000,
                "emp_noise": row["emp_nf"], "ap_noise": row["ap_nf"]}

    hosting = {}
    with open(hosting_csv, encoding="utf-8") as f:
        rows = csv.DictReader(io.StringIO("".join(ln for ln in f if not ln.startswith("#"))))
        for r in rows:
            if not r["ts_utc"].startswith(str(YEAR)):
                continue
            st = r["entity"].split(":")[1]
            hosting.setdefault(st, {})[r["variable"]] = (float(r["value"]), r["x_emp_noise"], r["x_ap_noise"])

    states = {}
    for st in sorted(set(fips.values())):
        rec = {}
        h = hosting.get(st, {})
        if "employment" in h and "annual_payroll" in h and h["employment"][0] > 0:
            rec["operations"] = {"naics": "518210", "employment": int(h["employment"][0]),
                                 "annual_payroll_usd": int(h["annual_payroll"][0]),
                                 "per_job_usd": round(h["annual_payroll"][0] / h["employment"][0], 2),
                                 "emp_noise": h["employment"][1], "ap_noise": h["annual_payroll"][2]}
        c = construction.get(st, {})
        if len(c) == 2:
            emp = sum(v["employment"] for v in c.values())
            ap = sum(v["annual_payroll_usd"] for v in c.values())
            rec["construction"] = {"naics": "2362 and 238", "employment": emp, "annual_payroll_usd": ap,
                                   "per_job_usd": round(ap / emp, 2), "parts": c}
        if rec:
            states[st] = rec

    out = {
        "about": "Payroll per job by state, 2023, for a datacenter's earnings in /impact: operations from NAICS 518210, construction from NAICS 2362 and 238 together. In 2023 dollars; the tool puts them in 2025 dollars by deflator.json. NAICS 518210 is wider than datacenters (JLARC, Data Centers in Virginia 2024, Appendix D: only 15 percent of Virginia's 518210 employment was datacenter employment in 2016), a proxy said on the page. The Bureau infuses noise into employment and payroll (the noise flags kept).",
        "source": "U.S. Census Bureau, County Business Patterns 2023, state file cbp23st.zip (construction) and the warehouse table census_cbp_hosting_annual (518210), with the Bureau's state codes (state.txt)",
        "source_url": "https://www2.census.gov/programs-surveys/cbp/datasets/2023/cbp23st.zip",
        "read": "2026-11-26, chain 740 session 10801 (runs/c740/probe/probe.csv requests 129 and 130 on lab-desktop)",
        "license": "may be public (the Census Bureau, license_verdicts.csv; its name is not to imply endorsement). Cite the U.S. Census Bureau, County Business Patterns.",
        "year": YEAR,
        "written_by": "warehouse/forecast/datacenter_wages.py",
        "states": states,
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print("wrote", os.path.relpath(OUT, ROOT), len(states), "states;",
          sum(1 for s in states.values() if "operations" in s), "with operations,",
          sum(1 for s in states.values() if "construction" in s), "with construction")


if __name__ == "__main__":
    main(*sys.argv[1:4])
