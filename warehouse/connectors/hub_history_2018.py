#!/usr/bin/env python3
"""Hub prices from July 2018 to 5 July 2023, before iso_hub_prices_history begins, from each operator's own archive (session
7803, chain 401 part C, table 8). A new table, read by no page.

Energy Research Warehouse (ERW) connector. Writes warehouse/output/iso_hub_prices_history_2018.csv from a backfill that
warehouse/connectors/hub_history.py made into a folder of its own:

    python warehouse/connectors/hub_history.py backfill --iso spp --start 2018-07-01 --until 2023-07-06 --out-dir DIR
    python warehouse/connectors/hub_history_2018.py --from DIR          # under the data lock

The rows, columns, markets and rules are hub_history.py's (its completeness per operating day, its 15-minute means of
5-minute real-time prices), unchanged; this step names the table, says which operators it holds and why the others are
not in it, and registers the sources for it. Operators (docs/methods/hub_prices_history_2018.md):
  SPP      pulled: SPPNORTH_HUB, day-ahead hourly and real-time 15-minute means, from SPP's portal file browser
  CAISO    not in it: OASIS keeps about 39 months, so its own archive holds nothing before July 2023
  NYISO    not pulled: license needed under the hold of 21 October 2026 (docs/licenses.md)
  ISO-NE   not pulled: license needed under the same hold
  MISO     not pulled: paused since 4 October 2026 (warehouse/metadata/paused_sources.csv)
  PJM      not pulled (the chain)
"""

import argparse
import datetime as dt
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

NAME = "iso_hub_prices_history_2018"
SRC = "iso_hub_prices_history"
NOTE = ("Operators: SPP (SPPNORTH_HUB) only. Not in it: CAISO (OASIS keeps about 39 months: nothing before July 2023), "
        "NYISO and ISO-NE (license needed under the hold of 21 October 2026), MISO (paused since 4 October 2026), PJM (not "
        "pulled). Method: docs/methods/hub_prices_history_2018.md.")


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW hub prices July 2018 to July 2023 (session 7803)")
    ap.add_argument("--from", dest="src", required=True, help="the folder hub_history.py's backfill wrote")
    ap.add_argument("--out-dir")
    args = ap.parse_args(argv)
    if args.out_dir:
        ip.set_out_dir(args.out_dir)
    src = os.path.join(args.src, SRC + ".csv")
    head, body = [], None
    with open(src, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                head.append(line[2:].rstrip("\n"))
            else:
                body = line
                break
        rest = f.read()
    if body is None:
        raise SystemExit(f"{src}: no column row")
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    head[0] = ("Energy Research Warehouse (ERW): main-hub day-ahead and real-time prices from 2018-07-01 to 2023-07-05, before "
               "iso_hub_prices_history begins (session 7803, chain 401 part C, table 8), from hub_history.py's backfill; " + head[0])
    head.insert(1, NOTE)
    head.insert(2, f"Written: {run_id} (UTC) by warehouse/connectors/hub_history_2018.py from {os.path.relpath(src, ip.ROOT)}")
    path = os.path.join(ip.OUT_DIR, NAME + ".csv")
    ip._require_lock(path, f"writing {NAME}")
    with open(path + ".tmp", "w", encoding="utf-8", newline="") as f:
        for line in head:
            f.write("# " + line + "\n")
        f.write(body)
        f.write(rest)
    os.replace(path + ".tmp", path)
    srcs = [line.split(" ", 2)[1] for line in head if line.startswith("Source: ")]
    import csv  # each source's registry row as it stands, with this table added to its tables
    with open(os.path.join(ip.METADATA_DIR if os.path.exists(os.path.join(ip.METADATA_DIR, "sources.csv"))
                           else os.path.join(ip.ROOT, "warehouse", "metadata"), "sources.csv"), encoding="utf-8") as f:
        reg = {r["source"]: r for r in csv.DictReader(f)}
    for s in srcs:
        if s not in reg:
            raise SystemExit(f"source {s} is not in sources.csv")
        r = reg[s]
        ip.update_sources([dict(source=s, publisher=r["publisher"], report=r["report"], report_url=r["report_url"],
                                document_list=r["document_list"], license=r["license"], tables=[NAME])])
    rows = rest.count("\n") + (0 if rest.endswith("\n") or not rest else 1)
    print(f"{NAME}.csv: {rows} rows from {src}; sources {srcs}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
