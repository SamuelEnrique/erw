"""Session 10217: one rule changed at a time, and the claims of the monitor view of /policy set against its files.
Reads the page's own files only (site/data/policy/monitor.json, site/data/siting/large_load_rules.json,
site/data/policy/state_rules.json, paused.json); prints counts, ids and dates, no row of a held table whole.
    python runs/c10217/measures.py <worktree root> <today> <out.json>
"""
import collections
import datetime as dt
import json
import os
import re
import sys

root, today, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
m = json.load(open(os.path.join(root, "site", "data", "policy", "monitor.json"), encoding="utf-8"))
ll = json.load(open(os.path.join(root, "site", "data", "siting", "large_load_rules.json"), encoding="utf-8"))
sr = json.load(open(os.path.join(root, "site", "data", "policy", "state_rules.json"), encoding="utf-8"))
rows = m["rows"]
D = dt.date.fromisoformat
res = {}


def say(k, v):
    res[k] = v
    print(f"{k}: {v}")


opened = [r for r in rows if r.get("significance") is not None and r["significance"] >= 5]
say("base|opened", len(opened))

# 1. the week: eight calendar days against seven
last = max(r["date"] for r in rows)
to = D(last) if last < today else D(today)
for days_back, name in ((7, "page (to minus 7, both ends: 8 days)"), (6, "seven days (to minus 6)")):
    frm = (to - dt.timedelta(days=days_back)).isoformat()
    w = [r for r in opened if frm <= r["date"] <= to.isoformat()]
    say(f"week|{days_back}", {"rule": name, "from": frm, "to": to.isoformat(), "n": len(w), "dates": dict(collections.Counter(r["date"] for r in w))})
# the same over the last 30 page days (every day the file ran to, as the page would have drawn it on each)
extra = []
for k in range(30):
    t = D(today) - dt.timedelta(days=k)
    lt = max((r["date"] for r in rows if r["date"] <= t.isoformat()), default="")
    tt = D(lt) if lt and lt < t.isoformat() else t
    n8 = sum(1 for r in opened if (tt - dt.timedelta(days=7)).isoformat() <= r["date"] <= tt.isoformat())
    n7 = sum(1 for r in opened if (tt - dt.timedelta(days=6)).isoformat() <= r["date"] <= tt.isoformat())
    extra.append(n8 - n7)
say("week|extra_over_30_days", {"mean_extra": round(sum(extra) / len(extra), 2), "max_extra": max(extra), "days_with_extra": sum(1 for x in extra if x)})

# 2. records with no score: hidden by the opening floor, whatever they are
uns = [r for r in rows if r.get("significance") is None]
say("unscored|n", len(uns))
say("unscored|by_body", dict(collections.Counter(r["body"] for r in uns).most_common()))
say("unscored|by_month", dict(sorted(collections.Counter(r["date"][:7] for r in uns).items())))
say("unscored|with_steps_ahead", sum(1 for r in uns if any(today <= s["date"] <= (D(today) + dt.timedelta(days=30)).isoformat() for s in r.get("steps", []))))
ll_words = re.compile(r"large load|large-load|data cent|datacent", re.I)
say("unscored|large_load_titles", sum(1 for r in uns if ll_words.search(r["title"])))
say("all|large_load_titles", sum(1 for r in rows if ll_words.search(r["title"])))
say("opened|large_load_titles", sum(1 for r in opened if ll_words.search(r["title"])))
say("rule|unscored_shown_at_opening", {"shown": len(opened) + len(uns), "from": len(opened)})

# 3. status as of the newest document against as of the page's day
def eff_steps(r):
    return sorted(s["date"] for s in r.get("steps", []) if s["kind"] == "effective")
fin = [r for r in rows if r["status"] == "final"]
fin_now = [r for r in fin if any(d <= today for d in eff_steps(r))]
fin_later = [r for r in fin if eff_steps(r) and all(d > today for d in eff_steps(r))]
fin_none = [r for r in fin if not eff_steps(r)]
say("status|final", {"all": len(fin), "effective_date_passed_by_today": len(fin_now), "effective_date_ahead": len(fin_later), "no_effective_date": len(fin_none)})
ofin = [r for r in opened if r["status"] == "final"]
say("status|final_opened", {"all": len(ofin), "effective_date_passed_by_today": sum(1 for r in ofin if any(d <= today for d in eff_steps(r)))})
eff = [r for r in rows if r["status"] == "effective"]
say("status|effective", {"all": len(eff), "opened": sum(1 for r in opened if r["status"] == "effective")})
prop = [r for r in rows if r["status"] in ("proposed", "open")]
closed = [r for r in prop if any(s["kind"] == "comments_due" for s in r.get("steps", [])) and all(s["date"] < today for s in r.get("steps", []) if s["kind"] == "comments_due")]
say("status|proposed_or_open_comments_closed", {"proposed_or_open": len(prop), "every_comment_date_passed": len(closed),
                                                "opened": sum(1 for r in closed if r in opened)})
# a status of the newest document, when an older document of the record is a final rule
hist_final = [r for r in rows if r["status"] not in ("final", "effective") and any(" rule final " in f" {h} " or " rule effective " in f" {h} " for h in r.get("history", []))]
say("status|newest_not_final_but_history_holds_a_final_rule", len(hist_final))

# 4. the next step as the page shows it
def nxt(r):
    st = sorted(r.get("steps", []), key=lambda s: (s["date"], s["kind"], s["event_id"]))
    if st:
        a = [s for s in st if s["date"] >= today]
        return ("ahead", a[0]) if a else ("passed", st[-1])
    if r.get("next"):
        return ("passed" if r["next"]["date"] < today else "ahead", None)
    return ("none", None)
say("next|opened", dict(collections.Counter(nxt(r)[0] for r in opened)))
passed_effective = sum(1 for r in opened if nxt(r)[0] == "passed" and nxt(r)[1] and nxt(r)[1]["kind"] == "effective")
say("next|opened_passed_is_effective", passed_effective)

# 5. "changes in the last 90 days": every change of the file, counted against the 90 days to the page's day
since90 = (D(today) - dt.timedelta(days=90)).isoformat()
ch = ll["changes"]
out90 = [c for c in ch if c["date"] < since90]
say("changes|public", len(ch))
say("changes|dates", {"first": min(c["date"] for c in ch), "last": max(c["date"] for c in ch), "since90": since90})
say("changes|before_90_days_to_today", {"n": len(out90), "states": dict(collections.Counter(s for c in out90 for s in set(re.findall(r"\b[A-Z]{2}\b", c["state"] or ""))))})
say("changes|date_kind", dict(collections.Counter(c["date_kind"] for c in ch)))
say("changes|held", len(ll["held_changes"]))
say("changes|retrieved", ll["retrieved"]["utility_large_load_rule_changes"])
say("changes|multi_state_rows", sum(1 for c in ch if len(set(re.findall(r"\b[A-Z]{2}\b", c["state"] or ""))) > 1))

# 6. the laws' status words against their dates and the page's day
laws = ll["laws"]
iso_day = re.compile(r"^\d{4}-\d{2}-\d{2}$")
en_passed = [l for l in laws if l["status"] == "enacted" and iso_day.match(l["effective"] or "") and l["effective"] <= today]
ie_ahead = [l for l in laws if l["status"] == "in effect" and iso_day.match(l["effective"] or "") and l["effective"] > today]
say("laws|enacted_effective_passed_by_today", [(l["state"], l["bill"], l["effective"]) for l in en_passed])
say("laws|in_effect_effective_ahead", [(l["state"], l["bill"], l["effective"]) for l in ie_ahead])
say("laws|effective_words", dict(collections.Counter("date" if iso_day.match(l["effective"] or "") else (l["effective"] or "blank")[:40] for l in laws)))
say("laws|read_dates", dict(collections.Counter(l["read"][:10] for l in laws)))
say("laws|date_kind", dict(collections.Counter(l["date_kind"] for l in laws)))
say("laws|threshold_not_published", sum(1 for l in laws if not l["threshold"] or l["threshold"] == "not published"))
# a requirement with no cite, a threshold with no cite
req = [(l["id"], p) for l in laws for p in (l["requirements"] or "").split(" || ") if p.strip()]
say("laws|requirements", len(req))
say("laws|requirements_without_cite", sum(1 for _, p in req if not re.search(r"\[[^\]]+\]\s*$", p.strip())))
say("laws|threshold_without_cite", sum(1 for l in laws if l["threshold"] and l["threshold"] != "not published" and not (l["threshold_cite"] or "").strip()))

# 7. each step's date in its own words; each figure's value in its own words
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
def date_forms(d):
    y, mo, da = d.split("-")
    full = MONTHS[int(mo) - 1]
    forms = [f"{full} {int(da)}, {y}", f"{full[:3]}. {int(da)}, {y}", f"{full[:3]} {int(da)}, {y}", f"Sept. {int(da)}, {y}" if mo == "09" else None, d]
    return [f for f in forms if f]
steps = [(r["id"], s) for r in rows for s in r.get("steps", [])]
miss = [(rid, s["kind"], s["date"]) for rid, s in steps if not any(f in re.sub(r"\s+", " ", s["words"]) for f in date_forms(s["date"]))]
say("steps|n", len(steps))
say("steps|date_not_in_words", {"n": len(miss), "first": miss[:6]})
say("steps|from_register_record", sum(1 for _, s in steps if s["words"].startswith("the Federal Register's record")))
def num_forms(v, unit):
    out = set()
    if unit == "USD":
        for scale, w in ((1e9, "billion"), (1e6, "million"), (1e3, "thousand")):
            x = v / scale
            if x >= 1 and abs(x - round(x, 3)) < 1e-9:
                s = f"{x:,.3f}".rstrip("0").rstrip(".")
                out.add(f"{s} {w}")
                out.add(f"{s} {w.capitalize()}")
        out.add(f"{v:,.2f}".rstrip("0").rstrip("."))
        out.add(f"{int(v):,}" if v == int(v) else str(v))
    else:
        out.add(f"{v:,.3f}".rstrip("0").rstrip(".") if v != int(v) else f"{int(v):,}")
        out.add(str(int(v)) if v == int(v) else str(v))
    return out
figs = [r for r in rows if r.get("figure")]
fmiss = [(r["id"], r["figure"]["value"], r["figure"]["unit"]) for r in figs if not any(f in r["figure"]["words"] for f in num_forms(r["figure"]["value"], r["figure"]["unit"]))]
say("figures|n", len(figs))
say("figures|value_not_in_words", {"n": len(fmiss), "first": fmiss[:8]})
say("figures|units", dict(collections.Counter(r["figure"]["unit"] for r in figs)))

# 8. machine words reaching a cell
STAT = {"proposed", "final", "effective", "stayed", "vacated", "withdrawn", "filed", "open", "scheduled", "issued", "announced"}
INSTR = {"rule", "proposed_rule", "order", "guidance", "approval", "lease_sale", "award", "application", "complaint", "environmental_review", "meeting", "decision", "notice", "announcement"}
KINDS = {"effective", "expires", "comments_due", "intervention_due", "review_due", "decision_due", "meeting", "filing_due", "review_petition_due"}
SECT = {"policy", "nuclear", "renewables", "gas", "generation", "oil", "other", "lng", "storage", "transmission", "transport", "grid_conditions", "power_prices", "geopolitics", "interconnection", "capital", "company", "deal"}
say("keys|status_unmapped", sorted({r["status"] for r in rows} - STAT))
say("keys|instrument_unmapped", sorted({r["instrument"] for r in rows} - INSTR))
say("keys|kind_unmapped", sorted({s["kind"] for r in rows for s in r.get("steps", [])} - KINDS))
say("keys|sector_unmapped", sorted({r["sector"] for r in rows if r.get("sector")} - SECT))
hist_status = {h.split(" ")[2] for r in rows for h in r.get("history", []) if len(h.split(" ")) > 3}
say("keys|history_status_unmapped", sorted(hist_status - STAT))
doc_prefixes = collections.Counter(d.split(":")[0] for r in rows for h in r.get("history", []) for d in (h.split(" ")[3] if len(h.split(" ")) > 3 else "").split(","))
say("keys|history_document_prefixes", dict(doc_prefixes))
say("keys|impact_models", dict(collections.Counter(r["impact"]["model"] for r in rows if r.get("impact"))))
say("keys|bears_on_tables_opened", len({r["bears_on"]["table"] for r in opened}))

# 9. one proceeding as two records: the same body and title, or a shared proceeding id
def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()
by_title = collections.defaultdict(list)
for r in rows:
    by_title[(r["body"], norm(r["title"]))].append(r)
dups = {k: v for k, v in by_title.items() if len(v) > 1}
say("dup|same_body_title_records", {"groups": len(dups), "records": sum(len(v) for v in dups.values())})
close = []
for k, v in dups.items():
    ds = sorted(D(r["date"]) for r in v)
    gaps = [(b - a).days for a, b in zip(ds, ds[1:])]
    close.append(min(gaps))
say("dup|same_body_title_min_gap_days", dict(sorted(collections.Counter("<=45" if g <= 45 else ">45" for g in close).items())))
say("dup|same_body_title_opened", sum(1 for v in dups.values() if sum(1 for r in v if r in opened) > 1))
pid = collections.defaultdict(list)
for r in rows:
    for p in (r.get("docket") or "").split(";"):
        if p:
            pid[p].append(r["id"])
shared = {p: ids for p, ids in pid.items() if len(set(ids)) > 1}
say("dup|proceeding_id_in_two_records", {"ids": len(shared), "first": list(shared.items())[:5]})
# the same docket written two ways (a RIN-split key and its bare key)
say("dup|rin_split_records", sum(1 for r in rows if re.search(r"\.\d{4}-[A-Z]{2}\d{2}$", r["id"])))

# 10. the rows of the publisher whose terms hold the table (the PUCT's page: PUCT and the Texas Governor)
pu = [r for r in rows if r["body"] in ("PUCT", "Texas Governor")]
say("held_publisher|records", {"all": len(pu), "opened": sum(1 for r in opened if r["body"] in ("PUCT", "Texas Governor")),
                                "with_figure": sum(1 for r in pu if r.get("figure")), "opened_with_figure": sum(1 for r in opened if r in pu and r.get("figure"))})
say("records|bodies_state_level", dict(collections.Counter(r["body"] for r in rows if r["body"] in ("PUCT", "CPUC", "Texas Governor"))))

# 11. the paused publishers
say("paused|miso_grid_records", {"all": sum(1 for r in rows if "miso" in r.get("grids", [])), "opened": sum(1 for r in opened if "miso" in r.get("grids", []))})
say("paused|va_state_records", {"all": sum(1 for r in rows if "VA" in r.get("states", [])), "opened": sum(1 for r in opened if "VA" in r.get("states", []))})
sources = collections.Counter(re.sub(r"^https?://(www\.)?", "", u).split("/")[0] for r in rows for u in r.get("sources", []))
say("paused|source_hosts", dict(sources.most_common(12)))
say("paused|misoenergy_or_scc_source", sum(v for k, v in sources.items() if "misoenergy" in k or "scc.virginia" in k))
va = [s for s in sr["rows"] if s.get("regulator_key") == "vascc"]
say("paused|vascc_docket_rows", {"n": len(va), "newest": max((s["date"] for s in va), default=""), "in_30_days": sum(1 for s in va if s["date"] >= (D(today) - dt.timedelta(days=30)).isoformat())})
say("statefile|built", sr["built_at_utc"])
say("statefile|by_regulator", dict(collections.Counter(s.get("regulator_key") for s in sr["rows"]).most_common()))

# 12. the marks of documents out of scope, and the governor
say("scope|marked", {"all": sum(1 for r in rows if r.get("scope")), "opened": sum(1 for r in opened if r.get("scope"))})

# 13. the large-load orders of FERC and the grid operators read from utility_large_load_rule_changes (session 7009)
say("changes_docs|in_monitor", sum(1 for r in rows for h in r.get("history", []) if "llchange:" in h))
say("monitor|fields_from", m["fields_from"])
say("monitor|built", m["built"])
say("monitor|documents", m["documents"])

# 14. as-of dates the page holds
say("asof|monitor_built", m["built"])
say("asof|monitor_last_document", last)
say("asof|large_load_file_built", ll["built"])
say("asof|large_load_retrieved", ll["retrieved"])
say("asof|state_rules_built", sr["built_at_utc"])

json.dump(res, open(out_path, "w", encoding="utf-8"), indent=1, default=str)
