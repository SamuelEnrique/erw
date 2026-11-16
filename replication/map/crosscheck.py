#!/usr/bin/env python3
"""ERW, the project map (/map): the cross-check of its headline figures against EIA's own published table
(session 7601, chain 305).

The map counts generating units and sums their nameplate megawatts from EIA's monthly inventory (Form EIA-860M). EIA
publishes its own totals of the same inventory in the Electric Power Monthly, Table 6.1 ("Electric Generating Summer
Capacity Changes"): net summer capacity in service at the end of a month, by technology, for utility-scale facilities.
That table is one month behind the inventory the map holds, and it is net summer capacity, not nameplate. So three
columns stand side by side for each technology: the map's nameplate megawatts (operating units), the same units' net
summer megawatts from the same workbook, and EIA's table. No figure is adjusted to match.

    python replication/map/crosscheck.py --fetch    # read EIA's table again into crosscheck_epm.csv (one request)
    python replication/map/crosscheck.py            # the table, from rows/units.csv and crosscheck_epm.csv
    python replication/map/crosscheck.py --write    # also writes crosscheck.csv

EIA's robots file allows /electricity/ (read 16 November 2026). Standard library only.
"""
import csv
import datetime
import html
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
EPM_URL = "https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=table_6_01"
EPM_FILE = os.path.join(HERE, "crosscheck_epm.csv")
AGENT = "erw-replication (python)"
# the technologies of the inventory that EIA's table names with the same words (its subtotals are left out)
SAME = ["Onshore Wind Turbine", "Offshore Wind Turbine", "Solar Photovoltaic", "Solar Thermal without Energy Storage", "Solar Thermal with Energy Storage",
        "Conventional Hydroelectric", "Wood/Wood Waste Biomass", "Landfill Gas", "Municipal Solid Waste", "Other Waste Biomass", "Geothermal",
        "Natural Gas Fired Combined Cycle", "Natural Gas Fired Combustion Turbine", "Natural Gas Steam Turbine", "Natural Gas Internal Combustion Engine",
        "Natural Gas with Compressed Air Storage", "Other Natural Gas", "Conventional Steam Coal", "Coal Integrated Gasification Combined Cycle", "Petroleum Coke",
        "Petroleum Liquids", "Other Gases", "Hydroelectric Pumped Storage", "Flywheels", "Batteries", "Nuclear", "All Other"]
EPM_NAME = {"Onshore Wind Turbine": "Onshore Wind (Summer Capacity)", "Offshore Wind Turbine": "Offshore Wind (Summer Capacity)"}


def fetch():
    req = urllib.request.Request(EPM_URL, headers={"User-Agent": AGENT})
    with urllib.request.urlopen(req, timeout=120) as r:
        t = r.read().decode("utf-8", errors="replace")
    month = re.search(r"Table 6\.1\. Electric Generating Summer Capacity Changes \(MW\), ([A-Za-z]+ \d{4}) to ([A-Za-z]+ \d{4})", t)
    if not month:
        raise RuntimeError("the page does not hold Table 6.1's title")
    rows = []
    for tr in re.findall(r"<tr[^>]*>([\s\S]*?)</tr>", t):
        cells = [html.unescape(re.sub(r"<[^>]+>", "", c)).replace("\xa0", " ").strip() for c in re.findall(r"<t[dh][^>]*>([\s\S]*?)</t[dh]>", tr)]
        if len(cells) >= 6 and cells[1] == "Utility Scale Facilities":
            rows.append([cells[0].lstrip(". ").strip(), cells[2], cells[3], cells[4], cells[5]])
    if len(rows) < 30:
        raise RuntimeError(f"Table 6.1 has {len(rows)} rows of utility-scale facilities: not the table expected")
    read = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(EPM_FILE, "w", encoding="utf-8", newline="") as f:
        f.write(f"# U.S. Energy Information Administration, Electric Power Monthly, Table 6.1, Electric Generating Summer Capacity Changes (MW), {month.group(1)} to {month.group(2)}: "
                f"utility-scale facilities, each cell as the page prints it (public domain). Source: {EPM_URL}. Retrieved {read}.\n")
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["technology", "in_service_end_of_prior_month_mw", "additions_mw", "reductions_mw", "in_service_end_of_month_mw", "month"])
        for r in rows:
            w.writerow(r + [month.group(2)])
    return len(rows), month.group(2)


def number(t):
    try:
        return float(str(t).replace(",", ""))
    except ValueError:
        return None


def main(argv):
    if "--fetch" in argv:
        n, month = fetch()
        print(f"Table 6.1 read: {n} rows, in service at the end of {month}")
    with open(EPM_FILE, encoding="utf-8", newline="") as f:
        head = f.readline().strip()
        epm = {}
        for r in csv.DictReader(f):
            epm.setdefault(r["technology"], r)             # the table prints "All Other" twice: the first is its row of all other sources
    month = next(iter(epm.values()))["month"]
    with open(os.path.join(HERE, "rows", "units.csv"), encoding="utf-8", newline="") as f:
        units = [r for r in csv.DictReader(ln for ln in f if not ln.startswith("#")) if r["kind"] == "operating"]
    out = []
    for tech in SAME:
        rs = [r for r in units if r["technology"] == tech]
        states = [r for r in rs if r["sheet"] == "Operating"]                  # the 50 states and the District of Columbia; Puerto Rico is its own sheet
        nameplate = sum(number(r["nameplate_mw"]) or 0 for r in rs)
        summer = sum(number(r["net_summer_mw"]) or 0 for r in states)
        e = number(epm[EPM_NAME.get(tech, tech)]["in_service_end_of_month_mw"])
        out.append([tech, len(rs), round(nameplate, 1), round(summer, 1), e, round(summer - e, 1), round(100 * (summer - e) / e, 2) if e else ""])
    total_e = sum(r[4] for r in out)
    total = ["Every technology above", sum(r[1] for r in out), round(sum(r[2] for r in out), 1), round(sum(r[3] for r in out), 1), round(total_e, 1),
             round(sum(r[3] for r in out) - total_e, 1), round(100 * (sum(r[3] for r in out) - total_e) / total_e, 2)]
    cols = ["technology", "operating_units_on_the_map", "nameplate_mw_on_the_map", "net_summer_mw_same_units_50_states_and_dc", f"eia_table_6_1_in_service_end_of_{month.replace(' ', '_').lower()}_mw",
            "net_summer_less_eia_mw", "percent"]
    for r in [cols] + out + [total]:
        print(" | ".join(str(x) for x in r))
    print(head)
    if "--write" in argv:
        with open(os.path.join(HERE, "crosscheck.csv"), "w", encoding="utf-8", newline="") as f:
            f.write(f"# ERW replication of /map: the map's operating units by EIA technology beside EIA's Electric Power Monthly, Table 6.1 (in service at the end of {month}). "
                    "The map holds the inventory of the month after; nameplate is the map's measure, net summer capacity EIA's table's. Method: docs/methods/map.md, section 12.\n")
            w = csv.writer(f, lineterminator="\n")
            w.writerow(cols)
            w.writerows(out + [total])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
