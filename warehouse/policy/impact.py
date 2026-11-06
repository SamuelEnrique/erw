#!/usr/bin/env python3
"""The impact read of a policy action (session 3058, chain 166): one sentence that says what the action changes and
which table of the warehouse (and which page of the site) it bears on, with a figure only where the text states one.

Energy Research Warehouse (ERW), platform tool 12. Two parts, kept apart so that the model never chooses where an
action shows:

  bears_on(action)   the table, by written rules over the action's body, instrument, title and proceeding (TABLE_RULES,
                     every table one that coverage.csv holds), and the site page whose own list of tables names it
                     (site/lib/pages.ts), else the table's row of the data catalogue (/data#<table>). No model.
  Reader.read()      the model writes the clause of what changes, from the action's own text, with the words of the
                     text it rests on; the clause is kept only if those words stand in the text word for word, every
                     number in it stands in the text, it is one sentence with no em or en dash and no word of opinion
                     (UNSAID). The sentence is the clause and then "; it bears on <table> (<page>)", written by code.

    python warehouse/policy/impact.py --items tests/fixtures/policy/actions_3056.json --out runs/impact.json --max-usd 2

The method note's section 15 (docs/methods/policy_monitor.md) has the map in words. The reads of this session are
docs/reviews/policy-impact-2026-11-06.csv, for the owner's reading; nothing here writes a table of the warehouse.
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import policy_fields as pf  # noqa: E402  session 3233: its own name, beside the deals tracker's fields
import records as pr  # noqa: E402

# (table, a test over the action). The first rule that holds names the table. `t` is the title and the opening of the
# text, lower case; `b` the body; `keys` the proceeding ids (records.proceeding_ids).
TABLE_RULES = [
    ("epa_rfs_rins_monthly", lambda t, b, keys: "renewable fuel standard" in t or "small refinery" in t),
    # amendments and transfers of the licenses of plants that run (a transfer can name a combined license too)
    ("nrc_license_actions", lambda t, b, keys: b == "NRC" and re.search(r"biweekly notice|transfer of (?:control of )?(?:the )?(?:operating )?licen", t)),
    ("nrc_advanced_reactor_preapplicants", lambda t, b, keys: b == "NRC" and re.search(r"non-light[- ]water|advanced reactor|non-lwr", t)),
    ("nrc_new_reactor_applications", lambda t, b, keys: b == "NRC" and re.search(
        r"construction permit|early site permit|design certification|combined license|limited work authorization|\bsmr\b", t)),
    ("nrc_license_actions", lambda t, b, keys: b == "NRC"),
    ("doe_lng_export_applications", lambda t, b, keys: any(k.startswith("doe:") for k in keys) or (b == "DOE" and re.search(r"\blng\b|liquefied natural gas", t))),
    ("ornl_hydropower_pipeline", lambda t, b, keys: any(k.startswith("project:") for k in keys) and "preliminary permit" in t),
    ("ornl_hydropower_relicensing", lambda t, b, keys: any(k.startswith("project:") for k in keys) and re.search(
        r"license application|continued project operation|relicens|new (?:major |minor )?license", t)),
    ("ornl_eha_hydropower_plants", lambda t, b, keys: any(k.startswith("project:") for k in keys)),
    ("eia_gas_storage_capacity_monthly", lambda t, b, keys: re.search(r"storage field|gas storage|injection/withdrawal|storage well", t)),
    ("eia_lng_liquefaction_projects", lambda t, b, keys: b == "FERC" and re.search(r"\blng\b|liquefied natural gas|liquefaction", t[:250])),
    ("eia_gas_pipeline_projects", lambda t, b, keys: any(re.match(r"ferc:(CP|PF)", k) for k in keys) or re.search(
        r"natural gas (?:pipeline|project|act)|gas pipeline|\bpipeline\b.*\bgas\b|\bgas\b.*\bpipeline\b", t)),
    ("isone_interconnection_queue", lambda t, b, keys: re.search(r"iso new england|iso-ne", t) and re.search(r"interconnection|lgia|queue", t)),
    ("interconnection_queue_summary", lambda t, b, keys: re.search(r"interconnection (?:queue|request|agreement)|\blgia\b", t)),
    ("grid_network_links", lambda t, b, keys: re.search(r"reconductor|dynamic line rating|transmission (?:line|project|technolog)", t)),
    ("large_load_rules", lambda t, b, keys: re.search(r"large load|data cent(?:er|re)", t)),
    ("eia860m_retired_generators", lambda t, b, keys: b == "DOE" and re.search(r"emergency order|keep[a-z ]{0,40}(?:online|operating|available)", t)),
    ("epa_needs_units", lambda t, b, keys: b == "EPA" and re.search(
        r"electric generating|power plant|steam electric|coal combustion residuals|\begus?\b|power sector", t)),
    ("eia_coal_mine_production_annual", lambda t, b, keys: b == "OSMRE" or re.search(r"coal (?:mining|exploration|lease)|surface mining", t)),
    ("boem_renewable_leases", lambda t, b, keys: b == "BOEM" and re.search(r"wind|renewable", t)),
    ("boem_ogor_lease_production_monthly", lambda t, b, keys: b == "BOEM" or re.search(r"outer continental shelf", t)),
    ("blm_oil_gas_statistics_annual", lambda t, b, keys: b == "BLM" and re.search(r"oil and gas|oil, gas|mancos|petroleum", t)),
    ("grid_network_links", lambda t, b, keys: re.search(r"transmission line|transmission project|\bkv\b|kilovolt", t)),
    ("iso_all_capacity_prices", lambda t, b, keys: re.search(r"capacity market|capacity auction|reliability pricing model", t)),
    ("storage_capacity", lambda t, b, keys: re.search(r"battery|energy storage", t)),
    ("eia861_utility_reliability", lambda t, b, keys: re.search(r"reliability", t) and re.search(r"grant|fund", t)),
    ("eia860m_planned_generators", lambda t, b, keys: re.search(r"\bsolar\b|\bwind\b|geothermal", t)),
    ("policy_actions", lambda t, b, keys: True),
]


def pages_of_tables(path=None):
    """{table: page} from site/lib/pages.ts: each page's own `tables` list."""
    path = path or os.path.join(ROOT, "site", "lib", "pages.ts")
    out = {}
    try:
        src = open(path, encoding="utf-8").read()
    except OSError:
        return out
    for m in re.finditer(r'href:\s*"([^"]+)"[^\n]*?tables:\s*"([^"]+)"', src):
        for t in re.split(r"[,;]\s*", m.group(2)):
            t = re.sub(r"\s*\(.*?\)\s*", "", t).strip()
            if re.fullmatch(r"[a-z0-9_]+", t):
                out.setdefault(t, m.group(1))
    return out


PAGES = pages_of_tables()


def bears_on(row, text=""):
    """(table, page) the action bears on."""
    t = f"{row.get('title', '')} {(text or row.get('first_paragraph', '') or row.get('abstract', ''))[:1500]}".lower()
    t = re.sub(r"\s+", " ", t)
    b = row.get("body") or pf.body(row.get("agency", ""), None, row.get("docket", ""), row.get("title", ""))
    keys = pr.proceeding_ids(row.get("docket", ""), b)
    for table, test in TABLE_RULES:
        if test(t, b, keys):
            return table, PAGES.get(table, f"/data#{table}")   # the catalogue's row of the table when no page lists it
    return "policy_actions", "/policy"


SYSTEM = """You write the clause of an impact read of a US government energy action, from the action's own text only.

The clause says what the action changes: who must, may or may no longer do what, and from or by which date, in plain words. It is one sentence of at most 40 words, written so that a reader who knows the energy industry learns what is different after this document than before it.

Rules:
- Use only what the text states. A date, a number, a capacity, a sum of money or a place goes in only if the text states it; never estimate, never round a number differently from the text.
- No opinion and no forecast: no adjective of size or importance (significant, major, critical, key, huge, massive, unprecedented, landmark), no verb that asserts nothing (signals, underscores, highlights, reflects, demonstrates), no word that judges (boost, threat, win, setback, burden, relief).
- No em dash and no en dash. No second sentence. Do not name the warehouse, a table or a website.
- If the document only gives notice of a meeting or of a filing received, say that, and what the next step is if the text states one.
- quote: the words of the text the clause rests on, copied exactly, at most 300 characters."""

SCHEMA = {"type": "object", "properties": {"clause": {"type": "string"}, "quote": {"type": "string"}},
          "required": ["clause", "quote"], "additionalProperties": False}

# Terms of art are not opinions: "no significant impact" (a FONSI), "significant adverse comments" (a direct final
# rule's condition), a "major license" or "major modification" (FERC's and EPA's own classes)
UNSAID = re.compile(r"(?<!\bno )\b(significant(?:ly)?(?! adverse)|major(?! (?:license|modification|source|project))|critical|key|huge|massive|unprecedented|landmark|signals?|underscores?|"
                    r"highlights?|reflects?|demonstrates?|boosts?|threats?|wins?|setbacks?|burdens?|relief)\b", re.I)


def norm(s):
    s = (s or "").replace("``", '"').replace("''", '"').replace("“", '"').replace("”", '"').replace("’", "'")
    s = re.sub(r"\[\[Page \d+\]\]", " ", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def numbers(s):
    return [re.sub(r"[,]", "", n).rstrip(".") for n in re.findall(r"\d[\d,]*(?:\.\d+)?", s or "")]


def check(clause, quote, text):
    """The reasons a clause is not kept ([] when it is)."""
    why = []
    nt = norm(text)
    if not quote or norm(quote) not in nt:
        why.append("its quotation is not in the text word for word")
    have = set(numbers(nt))
    left = [n for n in numbers(clause) if n not in have]
    if left:
        why.append(f"numbers not in the text: {left}")
    if re.search(f"[{chr(0x2014)}{chr(0x2013)}]", clause or ""):
        why.append("an em or en dash")
    if UNSAID.search(clause or ""):
        why.append(f"a word of opinion: {UNSAID.search(clause).group(0)}")
    body = (clause or "").strip().rstrip(".")
    ends = [m for m in re.finditer(r"[.!?]\s+(?=[A-Z])", body)
            if not pf.ABBREV.search(body[max(0, m.start() - 8):m.start()])]   # "5:00 p.m. Eastern", "Inc. ", "R.M. "
    if ends or not body:
        why.append("not one sentence")
    if len(body.split()) > 45:
        why.append("over 45 words")
    return why


def sentence(clause, table, page):
    return f"{clause.strip().rstrip('.;')}; it bears on {table} ({page})."


class Reader:
    def __init__(self, log=print):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "news"))
        import llm
        from score import PRICES, pick_model
        self.llm = llm
        self.client = llm.client("policy_impact", log)
        self.model = pick_model(self.client, log)
        self.price = PRICES.get(self.model)
        self.spent = 0.0

    def read(self, row, text):
        msg = (f"Action: {row.get('body') or row.get('agency')} {row.get('instrument') or row.get('action_type')}, "
               f"{row.get('event_date', '')[:10]}: {row.get('title', '')}\n\nText:\n{text[:9000]}")
        resp = self.client.messages.create(
            model=self.model, max_tokens=1000, messages=[{"role": "user", "content": msg}],
            system=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}],
            output_config={"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}})
        cost = self.llm.usd(self.model, self.llm.usage_numbers(resp.usage)) or 0
        self.spent += cost
        if resp.stop_reason != "end_turn":
            raise RuntimeError(f"stop_reason {resp.stop_reason}")
        return json.loads(next(b.text for b in resp.content if b.type == "text")), cost


def read_items(path):
    """[(row, text)] of a fixture file of session 3056's form."""
    base = os.path.dirname(os.path.abspath(path))
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    out = []
    for it in doc["items"]:
        with open(os.path.join(base, it["text_file"]), encoding="utf-8") as f:
            text = f.read()
        row = dict(it["row"])
        row.update(pf.derive(row, text, it.get("record") or None))
        out.append((row, text))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW policy impact reads (session 3058)")
    ap.add_argument("--items", required=True, help="a file of session 3056's fixture form: rows, texts")
    ap.add_argument("--out", required=True, help="the reads, as JSON (never a table of the warehouse)")
    ap.add_argument("--max-usd", type=float, default=2.0, help="stop before the spend would pass this")
    ap.add_argument("--limit", type=int, default=60)
    args = ap.parse_args(argv)
    items = read_items(args.items)[:args.limit]
    reader, out = Reader(), []
    for row, text in items:
        table, page = bears_on(row, text)
        rec = {"event_id": row["event_id"], "table": table, "page": page, "model": reader.model}
        if reader.spent + 0.05 > args.max_usd:
            rec.update(kept=False, why="not read: the cap")
            out.append(rec)
            continue
        try:
            got, cost = reader.read(row, text)
        except Exception as exc:
            rec.update(kept=False, why=f"call failed: {type(exc).__name__}: {str(exc)[:160]}", usd=0)
            out.append(rec)
            continue
        why = check(got.get("clause", ""), got.get("quote", ""), text)
        rec.update(clause=got.get("clause", ""), quote=got.get("quote", ""), usd=round(cost, 5), kept=not why,
                   why="; ".join(why), impact=sentence(got.get("clause", ""), table, page) if not why else "")
        out.append(rec)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"model": reader.model, "usd": round(reader.spent, 4), "reads": out}, f, ensure_ascii=False, indent=1)
    kept = sum(1 for r in out if r.get("kept"))
    print(f"policy impact: {len(out)} actions, {kept} kept, USD {reader.spent:.4f} ({reader.model})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
