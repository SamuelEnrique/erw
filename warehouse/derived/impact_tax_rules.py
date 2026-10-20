#!/usr/bin/env python3
"""The tax rules the economic impact tool reads (session 346): the table impact_tax_rules.

Energy Research Warehouse (ERW). Two kinds of rule, one row each, every row with its citation:

1. The severance rules the /severance page holds (site/data/severance_rules.json, sessions 40 and 41: Texas, Louisiana
   and New Mexico), in a table shape: each base rate, fee, reduced rate or exemption, and Louisiana's two oil rates,
   with the passage of the page that states it and, where the page held one, the statute's section and words. Nothing
   is read again and no rate is changed: the file is the record, as it was read on 30 September 2026.
2. The property-tax treatment of a generating project in the same three states. No public statute on it is held in
   the repository (searched on 20 October 2026: docs/, site/data/, warehouse/metadata/, archive/sessions/), and this
   session made no request. Each treatment the chain prompt names (Texas Tax Code chapters 312 and 313, Louisiana's
   Industrial Tax Exemption Program, New Mexico's Industrial Revenue Bonds) and each state's general property tax on
   a plant is therefore a row whose status is "no_rule_held": a statement that the ERW holds no rule, never a guess.

    python warehouse/derived/impact_tax_rules.py      # writes warehouse/output/impact_tax_rules.csv (the data lock)

Shape: events (docs/datastandard.md). event_id erw_tax:<state>:<rule>; event_date the effective date the citation
gives where it gives one as a date, else the day the rule was read (x_date_kind says which); event_type
severance_tax, severance_fee, severance_option or property_tax_rule; status held or no_rule_held.
"""

import datetime as dt
import json
import os
import re
import sys

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

NAME = "impact_tax_rules"
RULES = os.path.join(ROOT, "site", "data", "severance_rules.json")
READ_ON = "2026-09-30"          # sessions 40 and 41 read the pages as text on this day (the file's own note)
CHECKED_ON = "2026-10-20"       # the day this session searched the repository for a property-tax statute
METHOD_URL = "https://erw-flame.vercel.app/data/methods/economic_impact"
# a citation's publisher -> the namespace of its rows' source
NAMESPACE = {"Texas Comptroller of Public Accounts": "tx_cpa", "Texas Legislature": "tx_legislature",
             "Louisiana State Legislature": "la_legislature", "Louisiana Department of Revenue": "la_ldr",
             "New Mexico Taxation and Revenue Department": "nm_trd"}
STATE_NAME = {"TX": "Texas", "LA": "Louisiana", "NM": "New Mexico"}
# the property-tax treatments of a generating project the chain prompt names, by state; none is held
PROPERTY = {
    "TX": [("tx_property_general", "Texas property (ad valorem) tax on a generating project"),
           ("tx_chapter_312", "Texas Tax Code chapter 312: tax abatement agreements"),
           ("tx_chapter_313", "Texas Tax Code chapter 313: limitation on appraised value")],
    "LA": [("la_property_general", "Louisiana property (ad valorem) tax on a generating project"),
           ("la_itep", "Louisiana Industrial Tax Exemption Program (ITEP)")],
    "NM": [("nm_property_general", "New Mexico property tax on a generating project"),
           ("nm_irb", "New Mexico Industrial Revenue Bonds (IRB): the property-tax exemption of a project they finance")],
}
COLS = ip.EVENTS_COLS if hasattr(ip, "EVENTS_COLS") else [
    "event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source",
    "source_url"]
X_COLS = ["x_state", "x_tax", "x_product", "x_rule", "x_rule_name", "x_kind", "x_basis", "x_rate", "x_per_unit",
          "x_unit", "x_effective_text", "x_date_kind", "x_who", "x_what", "x_how_long", "x_quote", "x_quote2",
          "x_code_section", "x_code_quote", "x_code_url", "x_detail", "x_applies_to", "x_note"]
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def text(v):
    if v is None:
        return ""
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False, sort_keys=True)
    return str(v)


def severance_rows(d):
    src = d["sources"]
    out = []
    for st, s in d["states"].items():
        for product, p in s["products"].items():
            for kind, items in (("base", p.get("base", [])), ("fee", p.get("fees", [])), ("option", p.get("options", []))):
                for r in items:
                    cite = src[r["cite"]]
                    eff = text(r.get("effective"))
                    code = r.get("code") or {}
                    code_url = src[code["cite"]]["url"] if code.get("cite") in src else ""
                    detail = {k: r[k] for k in ("tiers", "bounds", "param", "certified", "districts", "input", "min_per_unit",
                                                "exempt_below_price", "pct", "group", "cite2") if k in r}
                    out.append(dict(
                        event_id=f"erw_tax:{st.lower()}:{r['id']}", event_date=eff if DATE.match(eff) else READ_ON,
                        event_type={"base": "severance_tax", "fee": "severance_fee", "option": "severance_option"}[kind],
                        parties=cite["publisher"], entity_ids="", mw="", price="", currency="", status="held",
                        source=f"{NAMESPACE[cite['publisher']]}:{r['cite']}", source_url=cite["url"],
                        x_state=st, x_tax="severance", x_product=product, x_rule=r["id"], x_rule_name=r["name"],
                        x_kind=text(r.get("kind", kind)), x_basis=text(r.get("basis")), x_rate=text(r.get("rate")),
                        x_per_unit=text(r.get("per_unit")), x_unit=p.get("unit", "") if (r.get("per_unit") is not None or r.get("basis") == "per_unit") else "",
                        x_effective_text=eff,
                        x_date_kind=("the effective date the citation gives" if DATE.match(eff)
                                     else f"the day the rule was read ({READ_ON}); the citation's own words are in x_effective_text"),
                        x_who=text(r.get("who")), x_what=text(r.get("what")), x_how_long=text(r.get("how_long")),
                        x_quote=text(r.get("quote")), x_quote2=text(r.get("quote2")),
                        x_code_section=text(code.get("section")), x_code_quote=text(code.get("quote")), x_code_url=code_url,
                        x_detail=text(detail) if detail else "",
                        x_applies_to="oil and gas production; none of the economic impact tool's technologies produces oil or gas",
                        x_note=f"As site/data/severance_rules.json holds it (version {d['version']})"))
            for v in p.get("variants", []):
                base = p["base"][0]
                cite = src[base["cite"]]
                out.append(dict(
                    event_id=f"erw_tax:{st.lower()}:{v['id']}", event_date=READ_ON, event_type="severance_tax",
                    parties=cite["publisher"], entity_ids="", mw="", price="", currency="", status="held",
                    source=f"{NAMESPACE[cite['publisher']]}:{base['cite']}", source_url=cite["url"],
                    x_state=st, x_tax="severance", x_product=product, x_rule=v["id"], x_rule_name=v["label"],
                    x_kind="variant", x_basis=text(base.get("basis")), x_rate=text(v.get("rate")), x_per_unit="", x_unit="",
                    x_effective_text="", x_date_kind=f"the day the rule was read ({READ_ON})", x_who="", x_what="",
                    x_how_long="", x_quote=text(base.get("quote")), x_quote2="", x_code_section="", x_code_quote="",
                    x_code_url="", x_detail="",
                    x_applies_to="oil and gas production; none of the economic impact tool's technologies produces oil or gas",
                    x_note=f"One of the base rate's variants, as site/data/severance_rules.json holds it (version {d['version']})"))
    return out


def property_rows():
    out = []
    for st, rules in PROPERTY.items():
        for rid, name in rules:
            out.append(dict(
                event_id=f"erw_tax:{st.lower()}:{rid}", event_date=CHECKED_ON, event_type="property_tax_rule",
                parties="", entity_ids="", mw="", price="", currency="", status="no_rule_held",
                source="erw:impact_tax_rules", source_url=METHOD_URL,
                x_state=st, x_tax="property", x_product="generating_project", x_rule=rid, x_rule_name=name,
                x_kind="no_rule_held", x_basis="", x_rate="", x_per_unit="", x_unit="", x_effective_text="",
                x_date_kind=f"the day the ERW recorded that it holds no rule ({CHECKED_ON})", x_who="", x_what="",
                x_how_long="", x_quote="", x_quote2="", x_code_section="", x_code_quote="", x_code_url="", x_detail="",
                x_applies_to="every technology of the economic impact tool",
                x_note=(f"No rule held. No public statute on this treatment in {STATE_NAME[st]} is held in the ERW "
                        f"(docs/, site/data/, warehouse/metadata/ and archive/sessions/ searched on {CHECKED_ON}), and session "
                        "346 made no request. No rate, abatement or figure is stated; docs/methods/economic_impact.md, section 2.")))
    return out


def main():
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    results = []
    try:
        d = json.load(open(RULES, encoding="utf-8"))
        rows = severance_rows(d) + property_rows()
        df = pd.DataFrame(rows)
        if df.event_id.duplicated().any():
            raise RuntimeError(f"an event_id is given twice: {df.event_id[df.event_id.duplicated()].tolist()[:3]}")
        cols = COLS + X_COLS
        cites = sorted({(r["source"], r["parties"] or "the ERW", r["source_url"]) for r in rows})
        header = [
            "Energy Research Warehouse (ERW): the tax rules of the economic impact tool, one row per rule, each with its citation (session 346)",
            "Shape: events (docs/datastandard.md v0). event_id erw_tax:<state>:<rule>; event_date the effective date the citation gives, "
            "else the day the rule was read or checked (x_date_kind); status held, or no_rule_held where the ERW holds no statute",
            f"Read from: site/data/severance_rules.json version {d['version']} (sessions 40 and 41: every rate cites a page whose text states it, "
            f"read as text on {READ_ON}); no page was read again and no request was made",
            f"Property tax: no statute held for TX, LA or NM (searched {CHECKED_ON}); "
            + "; ".join(f"{STATE_NAME[s]}: " + ", ".join(n for _, n in r) for s, r in PROPERTY.items()) + ": each a no_rule_held row",
            "Sources: " + "; ".join(f"{s} ({p}) {u}" for s, p, u in cites),
            "License: public. State statutes and the agencies' own pages, as the /severance page cites them; their publishers' "
            "terms are not read (docs/licenses.md lists the table as not settled until they are)",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/{NAME}.py",
            f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
        ]
        ip.write_snapshot(df[cols], NAME, header, log, cols)
        regs = {}
        for s, p, u in cites:
            if s == "erw:impact_tax_rules":
                regs[s] = dict(source=s, publisher="Energy Research Warehouse (ERW)",
                               report="The ERW's record that it holds no property-tax rule (session 346)", report_url=METHOD_URL,
                               document_list=METHOD_URL, license="public", tables=[NAME])
            else:
                cid = s.split(":", 1)[1]
                regs[s] = dict(source=s, publisher=p, report=d["sources"][cid]["title"], report_url=u, document_list=u,
                               license="public", tables=[NAME])
        ip.update_sources(list(regs.values()))
        print(f"{NAME}: {len(df)} rows ({(df.status == 'held').sum()} held, {(df.status == 'no_rule_held').sum()} no rule held)")
        log(f"wrote {len(df)} rows")
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(df)} rows"))
    except Exception as exc:
        log(f"FAILED, no output file written: {type(exc).__name__}: {exc}")
        print(f"{NAME} FAILED, no output file written: {type(exc).__name__}: {exc}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=str(exc)[:300]))
    ip.write_status(NAME, run_id, results)
    log.close()
    return 1 if any(r["status"] == "failed" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
