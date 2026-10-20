#!/usr/bin/env python3
"""Session 316: the publisher's own figure beside a scanner record draft (the Research pack's ruling 4b, 19 October 2026).

Energy Research Warehouse (ERW). A draft the scanner raised as a record of EIA's newest month (rule "record" on a table
of warehouse/connectors/eia_series.py) carries, before it can be approved, the figure EIA's own data service holds for
that series and that month: read from EIA's API (api.eia.gov/v2, the publisher's own page for a series), the address
recorded without the key, with the time of the read, EIA's own unit and the value in the ERW's unit by the connector's
conversion. /internal/findings shows it beside ours (site/app/internal/findings/page.tsx), and the approval route
(site/app/internal/findings/state/route.ts) refuses "approved" while the figure is missing. A figure is never made up:
a read that fails leaves the draft without one, and this script exits 1 (session 336: 75, warehouse/health.py's skip,
when every read that failed is EIA not answering: HTTP 5xx, a timeout or a refused connection).

The read is a request to a publisher, so it is the data machine's (run after the daily scan; a code machine makes no
pull), and EIA is asked once per draft and month: a draft that carries a figure for its month is not asked again.

    python warehouse/analysis/findings/publisher_figure.py [--dry-run] [--only <draft id>] [--out <json>]

--dry-run prints what would be asked and asked nothing. Needs EIA_API_KEY, SUPABASE_URL and SUPABASE_SERVICE_KEY (.env
or the environment). The pure parts (request_of, figure_of, compare) take no key and are what tests/test_session316.py
runs.
"""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))

API = "https://api.eia.gov/v2/"
PUBLISHER = "EIA"
UTC = dt.timezone.utc
# the ERW tables EIA's API answers for, with the facet names their entities carry after "eia:<measure>:" (eia_series.py
# series_of): the electricity routes by state and sector or location and energy source; the others by EIA series id
FACETS = {
    "eia_retail_electricity_prices": ("electricity/retail-sales", "price", ("stateid", "sectorid")),
    "eia_retail_sales_monthly": ("electricity/retail-sales", None, ("stateid", "sectorid")),   # the data column is the measure: sales or customers
    "eia_state_generation_monthly": ("electricity/electric-power-operational-data", "generation", ("location", "fueltypeid")),
}
SKIP = 75   # warehouse/health.py's skip: EIA did not answer (session 336)
MEASURE_COLUMNS = {"retail_sales": "sales"}   # the entity's measure to EIA's data column, where they differ
SERIES_TABLES = {"eia_product_spot_prices", "eia_retail_fuel_prices", "eia_petroleum_trade_weekly", "eia_petroleum_stocks_weekly",
                 "eia_lng_exports_monthly", "eia_crude_first_purchase_prices", "eia_crude_imports_by_country", "eia_padd_crude_pipeline_flows",
                 "eia_sector_energy_consumption_monthly", "eia_fuel_spot_prices", "eia_regional_retail_fuel_prices", "eia_crude_stream_prices",
                 "eia_power_plant_fuel_costs"}
# EIA's unit words to the ERW's, and the factor the connectors apply (eia_series.py UNITS and SCALE)
UNITS = {"$/GAL": ("USD/gal", 1.0), "MBBL/D": ("kbbl/d", 1.0), "MBBL": ("kbbl", 1.0), "MMCF": ("MMcf", 1.0), "$/MCF": ("USD/Mcf", 1.0),
         "$/BBL": ("USD/bbl", 1.0), "cents per kilowatt-hour": ("USD/MWh", 10.0), "thousand megawatthours": ("MWh", 1000.0),
         "million kilowatt hours": ("MWh", 1000.0), "number of customers": ("count", 1.0), "Trillion Btu": ("TBtu", 1.0),
         "dollars per million Btu": ("USD/MMBtu", 1.0)}


def is_eia_record(draft):
    """Whether a draft is a scanner record on a table EIA's API answers for (rule record, table eia_*)."""
    return draft.get("rule") == "record" and str(draft.get("table_name", "")) in set(FACETS) | SERIES_TABLES


def period_of(flag_date, freq="monthly"):
    """EIA's period for the flagged date: the month (YYYY-MM) of a monthly series, the day otherwise."""
    d = str(flag_date)[:10]
    return d[:7] if freq == "monthly" else d


def request_of(table, series, flag_date, freq="monthly"):
    """The EIA request for one series and period: (route, the query without the key, the data column). The entity
    "eia:retail_price:DC:IND" names the facets after its measure; a series-id table names EIA's series id last."""
    ent = str(series.get("entity", ""))
    parts = ent.split(":")
    if len(parts) < 3 or parts[0] != "eia":
        raise ValueError(f"{table}: the entity {ent!r} is not an EIA series")
    period = period_of(flag_date, freq)
    q = [("frequency", freq), ("start", period), ("end", period), ("length", "5")]
    if table in FACETS:
        route, data, names = FACETS[table]
        values = parts[2:]
        if len(values) != len(names):
            raise ValueError(f"{table}: the entity {ent!r} does not carry {len(names)} facets")
        # session 336: the entity's measure is the ERW's variable; EIA's column for retail_sales is "sales" (eia_series.py),
        # and the measure as written was answered HTTP 400 on 20 October
        data = data or MEASURE_COLUMNS.get(parts[1], parts[1])
        q.insert(0, ("data[0]", data))
        q += [(f"facets[{n}][]", v) for n, v in zip(names, values)]
        if table == "eia_state_generation_monthly":
            q.append(("facets[sectorid][]", "99"))
        return route, q, data
    if table in SERIES_TABLES:
        route = _route_of(table)
        q.insert(0, ("data[0]", "value"))
        q.append(("facets[series][]", parts[-1]))
        return route, q, "value"
    raise ValueError(f"{table}: not a table EIA's API answers for")


def _route_of(table):
    import eia_series
    cfg = eia_series.TABLES.get(table)
    if cfg and cfg.get("parts"):
        return cfg["parts"][0]["route"]
    raise ValueError(f"{table}: no route in eia_series.TABLES")


def figure_of(rows, data, period):
    """The figure EIA answered for the period: (value in EIA's unit, EIA's unit words), or None when no row holds it."""
    for r in rows:
        if str(r.get("period", "")) == period and r.get(data) not in (None, ""):
            unit = next((str(v) for k, v in r.items() if k.endswith("-units") or k == "units"), "")
            return float(r[data]), unit
    return None


def convert(value, eia_unit):
    """EIA's value in the ERW's unit, by the connectors' factor; the unit words as EIA wrote them when unknown."""
    unit, factor = UNITS.get(eia_unit, (eia_unit, 1.0))
    return value * factor, unit


def compare(ours, theirs, rel=1e-6):
    """Whether the ERW's value and the publisher's agree to a relative tolerance (after the conversion)."""
    if ours is None or theirs is None:
        return False
    return abs(float(ours) - float(theirs)) <= rel * max(1.0, abs(float(theirs)))


def read(draft, key, get, log=print):
    """One draft's publisher figure, read from EIA: the record for card.publisher, or raises."""
    flag = draft["flag"] if isinstance(draft.get("flag"), dict) else json.loads(draft.get("flag") or "{}")
    freq = "monthly" if "monthly" in str(flag.get("statistic", "")) or str(flag.get("series", {}).get("freq", "")) == "P1M" else "daily"
    route, q, data = request_of(draft["table_name"], flag.get("series") or {}, draft["flag_date"], freq)
    url = API + route + "/data/?" + urllib.parse.urlencode(q)
    r = get(API + route + "/data/", params=[("api_key", key)] + q, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"EIA {route} HTTP {r.status_code}")
    rows = r.json().get("response", {}).get("data", [])
    period = period_of(draft["flag_date"], freq)
    got = figure_of(rows, data, period)
    if got is None:
        raise RuntimeError(f"EIA {route}: no row for {period}")
    raw, eia_unit = got
    value, unit = convert(raw, eia_unit)
    ours = flag.get("value")
    out = {"source": PUBLISHER, "period": period, "value": value, "unit": unit, "eia_value": raw, "eia_unit": eia_unit, "url": url,
           "read_at": dt.datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"), "ours": ours, "same": compare(ours, value)}
    log(f"  {draft['id']}: EIA {period} {raw} {eia_unit} = {value} {unit}; ours {ours}; {'same' if out['same'] else 'DIFFERS'}")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", default=None, help="one draft id")
    ap.add_argument("--out", default=None, help="write the figures read to this JSON file too")
    args = ap.parse_args(argv)
    import requests
    import lock
    url, skey = lock.env("SUPABASE_URL"), lock.env("SUPABASE_SERVICE_KEY")
    ekey = lock.env("EIA_API_KEY")
    if not url or not skey:
        print("needs SUPABASE_URL and SUPABASE_SERVICE_KEY", file=sys.stderr)
        return 2
    u = urllib.parse.urlparse(url)
    base = f"{u.scheme}://{u.netloc}/rest/v1/scanner_drafts"
    h = {"apikey": skey, "Authorization": f"Bearer {skey}", "Content-Type": "application/json"}
    r = requests.get(base, params={"select": "id,rule,table_name,flag_date,flag,card,state", "state": "in.(draft,full_card_asked)", "rule": "eq.record", "limit": "500"}, headers=h, timeout=30)
    r.raise_for_status()
    drafts = [d for d in r.json() if is_eia_record(d) and (not args.only or d["id"] == args.only)]
    todo = [d for d in drafts if not (d.get("card") or {}).get("publisher", {}).get("period") == period_of(d["flag_date"])]
    print(f"{len(drafts)} open record draft(s) on EIA tables; {len(todo)} without the publisher's figure for their month")
    if args.dry_run:
        for d in todo:
            flag = d["flag"] if isinstance(d["flag"], dict) else json.loads(d["flag"])
            route, q, data = request_of(d["table_name"], flag.get("series") or {}, d["flag_date"])
            print(f"  would ask {API}{route}/data/?{urllib.parse.urlencode(q)}")
        return 0
    if not ekey:
        print("needs EIA_API_KEY", file=sys.stderr)
        return 2
    failed, done, unanswered = [], [], 0
    for d in todo:
        try:
            pub = read(d, ekey, requests.get)
        except Exception as exc:
            failed.append((d["id"], str(exc)[:200]))
            print(f"  {d['id']}: not read: {str(exc)[:200]}")
            # session 336: EIA's gateway answered 504 twice on 20 October; a publisher that does not answer is a skip
            # (session 321's rule for a pull), a request EIA refuses (4xx) or a month it lacks is a failure
            unanswered += isinstance(exc, (requests.ConnectionError, requests.Timeout)) or " HTTP 5" in str(exc)
            continue
        card = dict(d["card"]); card["publisher"] = pub
        w = requests.patch(base, params={"id": f"eq.{d['id']}"}, headers={**h, "Prefer": "return=minimal"}, json={"card": card}, timeout=30)
        w.raise_for_status()
        done.append({"id": d["id"], **pub})
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as f:
            json.dump({"read_at": dt.datetime.now(UTC).isoformat(), "done": done, "failed": failed}, f, indent=1)
    print(f"{len(done)} figure(s) recorded, {len(failed)} not read")
    if failed and unanswered == len(failed):
        print(f"dm_publisher_figure SKIPPED: EIA did not answer for {len(failed)} draft(s); asked again on the next run")
        return SKIP
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
