"""Energy Research Warehouse (ERW), session 7508 (chain 304): EIA's hourly demand, read from the eight EIA-930 workbooks
the warehouse saved, into one small CSV an area (the input of from_hourly.py).

    python replication/demand_growth/extract_hours.py <folder of the workbooks> <out folder>

The workbooks are EIA's own files (https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx, and
Region_US48.xlsx), as the emissions connector saved them under warehouse/raw/eia930_emissions/<run>/. No request is
made here. From the sheet "Published Hourly Data" it keeps two columns: "UTC time" (the hour's end, as EIA writes it)
and the demand docs/methods/demand_growth.md names: "Adjusted demand" for a balancing authority, "Demand" for the
Lower 48, whose workbook has no adjusted column. A blank stays a blank. Nothing is computed.

The out folder is not committed (75 to 100 MB of workbooks give 8 files of about 2 MB; EIA's data is public domain,
and the folder is rebuilt by this command).
"""
import csv
import glob
import os
import sys

from openpyxl import load_workbook

AREAS = ["ERCO", "CISO", "PJM", "MISO", "SWPP", "NYIS", "ISNE", "US48"]


def workbook_of(folder, area):
    name = "Region_US48" if area == "US48" else area
    files = [f for f in glob.glob(os.path.join(folder, f"*_{name}.xlsx")) if os.path.getsize(f) > 0]
    if not files:
        raise SystemExit(f"no workbook of {area} in {folder}")
    return sorted(files)[-1]


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    folder, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    for area in AREAS:
        f = workbook_of(folder, area)
        ws = load_workbook(f, read_only=True, data_only=True)["Published Hourly Data"]
        rows = ws.iter_rows(values_only=True)
        head = list(next(rows))
        t = head.index("UTC time")
        column = "Demand" if area == "US48" else "Adjusted demand"
        d = head.index(column)
        n = blank = 0
        with open(os.path.join(out, f"{area}.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            fh.write(f"# {os.path.basename(f)}, sheet Published Hourly Data, column {column}; utc_end is EIA's UTC time (the hour's end)\n")
            w.writerow(["utc_end", "demand_mw"])
            for r in rows:
                if r[t] is None:
                    continue
                v = r[d]
                if v is None or v == "":
                    blank += 1
                    v = ""
                w.writerow([r[t].strftime("%Y-%m-%dT%H:%M:%SZ"), v])
                n += 1
        print(f"{area}: {n} hours, {blank} blank, column {column}, from {os.path.basename(f)}", flush=True)


if __name__ == "__main__":
    main()
