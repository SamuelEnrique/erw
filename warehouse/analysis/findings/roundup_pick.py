"""The Sunday Roundup's chosen finding (session 170).

Energy Research Warehouse (ERW). "Use in Roundup" on /analysis writes a row of public.analysis_requests (kind roundup,
params {card_id, week}; migration 026). The Roundup (warehouse/news/roundup.py) asks here for its week's choice: the
latest such row for the week, read with the service role (SUPABASE_URL, SUPABASE_SERVICE_KEY, as warehouse/lock.py
reads them). The card itself comes from the chosen request's row when the worker wrote one there, else from the
committed card file site/data/findings/<card_id>.json. No choice, no credentials or no card: None, and the Roundup
falls back to the rule's chart of the week and says so.

    python warehouse/analysis/findings/roundup_pick.py 2026-W41      # print the choice, if any
"""

import json
import os
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CARD_DIR = os.path.join(ROOT, "site", "data", "findings")
RENDER_DIR = os.path.join(ROOT, "docs", "analysis", "findings")


def chosen_card_id(label, log=print):
    """The card_id chosen for the week `label` (YYYY-Www), or None."""
    sys.path.insert(0, os.path.join(ROOT, "warehouse"))
    try:
        import lock
        import requests
    except ImportError as exc:
        log(f"  roundup pick: cannot ask the queue ({exc})")
        return None
    url, key = lock.env("SUPABASE_URL"), lock.env("SUPABASE_SERVICE_KEY")
    if not url or not key:
        log("  roundup pick: no Supabase credentials here; the rule's chart stands")
        return None
    u = urllib.parse.urlparse(url)
    try:
        r = requests.get(f"{u.scheme}://{u.netloc}/rest/v1/analysis_requests",
                         params={"kind": "eq.roundup", "params->>week": f"eq.{label}", "order": "asked_at.desc", "limit": "1",
                                 "select": "id,params,asked_at"},
                         headers={"apikey": key, "Authorization": f"Bearer {key}"}, timeout=30)
        if r.status_code != 200:
            log(f"  roundup pick: HTTP {r.status_code} {r.text[:120]}; the rule's chart stands")
            return None
        rows = r.json()
    except Exception as exc:
        log(f"  roundup pick: {type(exc).__name__}: {str(exc)[:120]}; the rule's chart stands")
        return None
    if not rows:
        return None
    p = rows[0].get("params") or {}
    return p.get("card_id") if isinstance(p, dict) else None


def load_card(card_id):
    if not card_id or not all(ch.isalnum() or ch in "_.-" for ch in card_id):
        return None
    f = os.path.join(CARD_DIR, card_id + ".json")
    if not os.path.exists(f):
        return None
    with open(f, encoding="utf-8") as fh:
        return json.load(fh)


def lines(card, label):
    """The chosen finding as the Roundup's markdown: the card's words, as the engine wrote them, and its render when
    one is committed (docs/analysis/findings/<card_id>_1600x900.png)."""
    cid = card["card_id"]
    L = [f"**{card['title']}** (chosen for this Roundup)", "", f"*{card['subtitle']}*", ""]
    png = os.path.join(RENDER_DIR, f"{cid}_1600x900.png")
    if os.path.exists(png):
        L += [f"![{card['title']}](../analysis/findings/{cid}_1600x900.png)", ""]
    for c in card.get("callouts", []):
        L.append(f"- {c['label']}: {c['before']['text']} ({c['before']['period']}), {c['after']['text']} ({c['after']['period']})"
                 + (f" {c['unit']}" if c.get("unit") else ""))
    L += ["", card["why"], "", f"{card['source_line']} The card, its data, Python and Stata do-file are on [/analysis/card/{cid}](/analysis/card/{cid})."]
    return L


def chosen(label, log=print):
    """(card, lines) for the week, or None."""
    cid = chosen_card_id(label, log)
    if not cid:
        return None
    card = load_card(cid)
    if card is None:
        log(f"  roundup pick: {cid} was chosen but no card file is committed for it; the rule's chart stands")
        return None
    log(f"  roundup pick: {cid} chosen for {label}")
    return card, lines(card, label)


if __name__ == "__main__":
    got = chosen(sys.argv[1] if len(sys.argv) > 1 else "")
    print("\n".join(got[1]) if got else "no finding chosen")
