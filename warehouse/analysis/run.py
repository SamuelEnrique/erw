#!/usr/bin/env python3
"""Automated Analysis (platform tool 26): run every template, pick the chart of the week, write it out.

Energy Research Warehouse (ERW), session 23. Weekly, before the Energy Roundup (Sundays 23:00 UTC,
.github/workflows/roundup.yml):

    python warehouse/analysis/run.py                  # the ISO week that contains yesterday (UTC)
    python warehouse/analysis/run.py --week 2026-W39
    python warehouse/analysis/run.py --no-gallery     # skip the parameter grid
    python warehouse/analysis/run.py --no-model       # the note and caption from the template's own sentences

Steps:
  1. Run every template in warehouse/analysis/templates/ at its default parameters. A template whose inputs are
     not in the warehouse on this machine (NoData) is skipped and named, with the reason.
  2. Notability, a rule and not a model: each template's headline number is compared with its own history (the
     same number for every earlier period the tables hold, plus the values stored in docs/analysis/history.csv by
     earlier runs): robust z = |x - median(history)| / (1.4826 x MAD(history)), capped at 10; when the MAD is 0
     (a sparse history, mostly one value) the scale is 1.2533 x the mean absolute deviation instead. A template needs at
     least 8 earlier values, and its headline period must have ended within the last 45 days, to be eligible.
  3. The chart of the week is the eligible public template with the highest robust z (ties: template order). An
     internal template is never picked and never written under docs/.
  4. Its note (two sentences) and a social caption are drafted by the model from the template's own sentences
     ("facts") and checked with the chat's literal-number check (warehouse/chat/ask.py): every number must appear
     in the facts or the headline. One regeneration; if it still fails, the note is the template's first two
     fact sentences as written (and the caption the first), which hold only the template's numbers.
  5. Writes docs/analysis/YYYY-Www/: results.json (every public template's result, notability and ECharts option),
     chart_of_the_week.json, chart_email.png (1200 x 750), social_1200x627.png, social_1080x1080.png; copies the
     two social PNGs and caption.txt to docs/analysis/social/ for manual posting; appends every template's
     headline to docs/analysis/history.csv; writes docs/analysis/templates.json (methods and parameters).
     Internal results go to warehouse/output/analysis_internal/ (not in git).
  6. The gallery: every public template over its grid of parameter values, each an ECharts option with its
     frame and citations, in docs/analysis/gallery/<template>/<params>.json and gallery/index.json. The site's
     /analysis serves these files; they are recomputed here, from the warehouse, every week.
"""

import argparse
import datetime as dt
import itertools
import json
import os
import re
import shutil
import sys
import traceback

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "templates"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "news"))
import iso_prices as ip  # noqa: E402
import templates  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
from voice import VOICE_NOTE  # noqa: E402  session 25: docs/voice.md
from common import NoData, nodes  # noqa: E402

DOCS = os.path.join(ROOT, "docs", "analysis")
INTERNAL = os.path.join(ROOT, "warehouse", "output", "analysis_internal")
HISTORY = os.path.join(DOCS, "history.csv")
MIN_HISTORY, MAX_AGE_DAYS, Z_CAP = 8, 45, 10.0
EM = chr(0x2014)  # the em dash, which no file here may hold (CLAUDE.md, non-negotiable 2)


def week_label(week, now):
    if week:
        return week
    y, w, _ = (now - pd.Timedelta(days=1)).date().isocalendar()
    return f"{y}-W{w:02d}"


def period_end(period):
    """The last date of a headline period: 'YYYY-MM-DD to YYYY-MM-DD', 'YYYY-MM' or 'YYYY-MM-DD'."""
    last = str(period).split(" to ")[-1]
    if re.fullmatch(r"\d{4}-\d{2}", last):
        return (pd.Timestamp(last + "-01") + pd.offsets.MonthEnd(0)).date()
    return pd.Timestamp(last).date()


def notability(value, history):
    vals = [float(v) for v in history if v is not None and not pd.isna(v)]
    if value is None or len(vals) < MIN_HISTORY:
        return None, len(vals), None
    s = pd.Series(vals)
    med = float(s.median())
    mad = float((s - med).abs().median()) * 1.4826
    if mad == 0:  # a sparse history (mostly one value): the mean absolute deviation, scaled to a normal sd
        mad = float((s - med).abs().mean()) * 1.2533
    if mad == 0:
        z = 0.0 if float(value) == med else Z_CAP
    else:
        z = min(Z_CAP, abs(float(value) - med) / mad)
    rank = float((s < float(value)).mean() * 100)
    return round(z, 2), len(vals), round(rank, 1)


def stored_history(template, params):
    if not os.path.exists(HISTORY):
        return {}
    h = pd.read_csv(HISTORY, dtype=str, keep_default_na=False)
    h = h[(h["template"] == template) & (h["params"] == json.dumps(params, sort_keys=True))]
    return {r["period"]: float(r["value"]) for r in h.to_dict("records") if r["value"] != ""}


# ---------------------------------------------------------------------------------------------
# the note and the caption: drafted by the model, kept only under the literal-number check
# ---------------------------------------------------------------------------------------------

NOTE_SYSTEM = """You write the note under the ERW's chart of the week and a social caption for it. The ERW is the Energy
Research Warehouse, the live, citable record of the US energy system.
- note: exactly two plain sentences saying what the chart shows and why it stands out this week. Use only the numbers
  written in the facts and the headline, exactly as written; compute nothing new, round nothing.
- caption: one or two sentences for a social post, at most 240 characters, the same rule for numbers, no hashtags,
  no emoji, no hype, no advice.
- No em dashes. Return JSON with the fields note and caption.""" + VOICE_NOTE
NOTE_SCHEMA = {"type": "object", "properties": {"note": {"type": "string"}, "caption": {"type": "string"}},
               "required": ["note", "caption"], "additionalProperties": False}


def draft_note(res, z, log, use_model=True):
    import ask as chat_ask
    h = res["headline"]
    head = f"Headline: {h['label']}, {h['period']}: {h['value']} {h['unit']}. Its robust z against its own history: {z}."
    pool = res["facts"] + [head]
    fallback = (" ".join(res["facts"][:2]), res["facts"][0][:240], "the template's own sentences")
    if not use_model:
        return fallback
    try:
        import anthropic
        from score import PRICES, pick_model
        client = anthropic.Anthropic(api_key=ip.load_key("ANTHROPIC_API_KEY", log))
        model = pick_model(client, log)
        msgs = [{"role": "user", "content": f"Chart: {res['title']}. {res['subtitle']}.\n\nFacts:\n" +
                 "\n".join(f"- {f}" for f in res["facts"]) + f"\n- {head}"}]
        cost = 0.0
        for attempt in (1, 2):
            resp = client.messages.create(model=model, max_tokens=800, system=NOTE_SYSTEM, messages=msgs,
                                          output_config={"effort": "low", "format": {"type": "json_schema",
                                                                                     "schema": NOTE_SCHEMA}})
            if model in PRICES:
                cost += (resp.usage.input_tokens * PRICES[model][0] + resp.usage.output_tokens * PRICES[model][1]) / 1e6
            out = json.loads(next(b.text for b in resp.content if b.type == "text"))
            note, cap = out["note"].replace(EM, ",").strip(), out["caption"].replace(EM, ",").strip()
            bad = chat_ask.unverified(note + " " + cap, pool)
            sentences = len(re.findall(r"[.!?](\s|$)", note))
            if not bad and sentences == 2 and len(cap) <= 240:
                log(f"  note and caption: attempt {attempt} passed the literal check; cost USD {cost:.4f}")
                return note, cap, f"model {model}, literal-number check passed (attempt {attempt}), USD {cost:.4f}"
            log(f"  note attempt {attempt}: numbers not in the facts {bad}; sentences {sentences}; caption {len(cap)} chars")
            msgs += [{"role": "assistant", "content": json.dumps(out)},
                     {"role": "user", "content": f"These numbers are not in the facts as written: {bad}. The note must be "
                      "exactly two sentences and the caption at most 240 characters. Rewrite both."}]
        log(f"  note: the model's drafts failed twice; the template's own sentences are used (cost USD {cost:.4f})")
    except Exception as exc:
        log(f"  note: model unavailable ({ip.redact(repr(exc))[:200]}); the template's own sentences are used")
    return fallback


# ---------------------------------------------------------------------------------------------
# output
# ---------------------------------------------------------------------------------------------

def public_record(res, z, n_hist, rank):
    return {"template": res["template"], "params": res["params"], "title": res["title"], "subtitle": res["subtitle"],
            "headline": {k: v for k, v in res["headline"].items() if k != "history"},
            "history_n": n_hist, "notability_z": z, "percentile": rank, "source_line": res["source_line"],
            "tables": res["tables"], "citations": res["citations"], "facts": res["facts"],
            "option": res["_option"], "frame": json.loads(res["frame"].to_json(orient="records", date_format="iso"))}


def param_grid(mod):
    """Every combination of a template's parameter choices; a hub's choices are the nodes of the ISO's tables."""
    names = list(mod.PARAMS)
    if "hub" in names and "iso" in names:
        out = []
        others = [n for n in names if n not in ("iso", "hub")]
        for iso in mod.PARAMS["iso"]["choices"]:
            hubs = sorted(set(hub_choices(mod, iso)))
            for hub in hubs:
                for combo in itertools.product(*[mod.PARAMS[n]["choices"] for n in others]):
                    out.append(dict(iso=iso, hub=hub, **dict(zip(others, combo))))
        return out
    return [dict(zip(names, combo)) for combo in itertools.product(*[mod.PARAMS[n]["choices"] for n in names])]


def hub_choices(mod, iso):
    from common import DA, RT
    if mod.NAME == "implied_heat_rate":
        return nodes(f"{iso}_trader_daily")
    if mod.NAME == "da_rt_spread_by_hour":
        return sorted(set(nodes(DA[iso])) & set(nodes(RT[iso][0])))
    return nodes(RT[iso][0])


def key(params):
    return re.sub(r"[^A-Za-z0-9_.=-]+", "_", "&".join(f"{k}={params[k]}" for k in sorted(params)))


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"), default=str)


def gallery(mods, log):
    index = []
    gdir = os.path.join(DOCS, "gallery")
    for mod in mods:
        if not mod.PUBLIC:
            continue
        combos, ok = {}, 0
        for params in param_grid(mod):
            k = key(params)
            try:
                res = mod.compute(history=False, **params)
                write_json(os.path.join(gdir, mod.NAME, f"{k}.json"), {
                    "template": mod.NAME, "params": params, "title": res["title"], "subtitle": res["subtitle"],
                    "source_line": res["source_line"], "citations": res["citations"], "facts": res["facts"],
                    "option": mod.render(res, "site"), "computed_at": ip.utc_iso(pd.Timestamp.now(tz="UTC"))})
                combos[k] = {"params": params, "file": f"{mod.NAME}/{k}.json"}
                ok += 1
            except NoData as exc:
                combos[k] = {"params": params, "file": None, "reason": str(exc)[:200]}
            except Exception as exc:
                combos[k] = {"params": params, "file": None, "reason": f"failed: {ip.redact(repr(exc))[:200]}"}
                log(f"  gallery {mod.NAME} {k}: FAILED {ip.redact(repr(exc))[:200]}")
        log(f"  gallery {mod.NAME}: {ok} of {len(combos)} parameter combinations computed")
        default = {k: (v["default"] if not isinstance(v["default"], dict) else v["default"][mod.PARAMS["iso"]["default"]])
                   for k, v in mod.PARAMS.items()}
        index.append({"template": mod.NAME, "title": mod.TITLE, "combos": combos, "default": key(default)})
    write_json(os.path.join(gdir, "index.json"), {"computed_at": ip.utc_iso(pd.Timestamp.now(tz="UTC")), "templates": index})
    return index


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW Automated Analysis")
    ap.add_argument("--week", help="ISO week YYYY-Www (default: the week that contains yesterday, UTC)")
    ap.add_argument("--no-gallery", action="store_true")
    ap.add_argument("--no-model", action="store_true")
    ap.add_argument("--gallery-only", action="store_true", help="recompute only the gallery (and templates.json)")
    args = ap.parse_args(argv)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"analysis_{run_id}.log"))
    status = dict(table="analysis", market="weekly", status="ok", detail="")
    try:
        now = pd.Timestamp.now(tz="UTC")
        label = week_label(args.week, now)
        out = os.path.join(DOCS, label)
        mods = templates.load_all()
        if args.gallery_only:
            write_json(os.path.join(DOCS, "templates.json"), {"templates": [
                {"template": m.NAME, "title": m.TITLE, "public": m.PUBLIC, "method": " ".join(m.METHOD.split()),
                 "params": m.PARAMS, "tables": m.TABLES} for m in mods]})
            idx = gallery(mods, log)
            n_gal = sum(1 for t in idx for c in t["combos"].values() if c["file"])
            status["detail"] = f"gallery only: {n_gal} charts"
            log(status["detail"])
            print(f"analysis: {status['detail']}")
            ip.write_status("analysis", run_id, [status])
            log.close()
            return 0
        results, skipped, hist_rows = [], [], []
        for mod in mods:
            try:
                res = mod.compute()
            except NoData as exc:
                skipped.append({"template": mod.NAME, "reason": str(exc)[:300]})
                log(f"{mod.NAME}: skipped ({exc})")
                continue
            except Exception as exc:
                skipped.append({"template": mod.NAME, "reason": f"failed: {ip.redact(repr(exc))[:300]}"})
                log(f"{mod.NAME}: FAILED\n{ip.redact(traceback.format_exc())}")
                continue
            h = res["headline"]
            past = dict(h["history"])
            for period, v in stored_history(mod.NAME, res["params"]).items():
                if period != h["period"]:
                    past.setdefault(period, v)
            z, n_hist, rank = notability(h["value"], list(past.values()))
            age = (now.date() - period_end(h["period"])).days
            eligible = mod.PUBLIC and z is not None and age <= MAX_AGE_DAYS
            res["_option"] = mod.render(res, "site")
            res["_mod"] = mod
            results.append((res, z, n_hist, rank, eligible))
            hist_rows.append({"week": label, "template": mod.NAME, "params": json.dumps(res["params"], sort_keys=True),
                              "period": h["period"], "value": h["value"], "unit": h["unit"], "history_n": n_hist,
                              "notability_z": "" if z is None else z, "public": mod.PUBLIC})
            log(f"{mod.NAME}: {h['label']} {h['period']} = {h['value']} {h['unit']}; history {n_hist}; z {z}; "
                f"percentile {rank}; age {age} days; eligible {eligible}")
        pool = [r for r in results if r[4]]
        if not pool:
            raise RuntimeError(f"no eligible public template (skipped: {skipped})")
        best = max(pool, key=lambda r: (r[1], -templates.ORDER.index(r[0]["template"])))
        res, z, n_hist, rank, _ = best
        mod = res["_mod"]
        log(f"chart of the week: {mod.NAME} (z {z}, percentile {rank}, history {n_hist})")
        note, caption, how = draft_note(res, z, log, use_model=not args.no_model)
        os.makedirs(out, exist_ok=True)
        files = {"email": "chart_email.png", "social_wide": "social_1200x627.png", "social_square": "social_1080x1080.png"}
        for size, f in files.items():
            mod.render(res, size, os.path.join(out, f))
        cow = {"week": label, "template": mod.NAME, "title": res["title"], "subtitle": res["subtitle"], "note": note,
               "caption": caption, "note_by": how, "source_line": res["source_line"], "citations": res["citations"],
               "tables": res["tables"], "params": res["params"], "headline": {k: v for k, v in res["headline"].items()
                                                                               if k != "history"},
               "notability_z": z, "percentile": rank, "history_n": n_hist, "files": files, "option": res["_option"],
               "chart": res["chart"],
               "rule": f"highest robust z of the headline against its own history among eligible public templates "
                       f"(at least {MIN_HISTORY} earlier values, headline period ended within {MAX_AGE_DAYS} days)",
               "computed_at": ip.utc_iso(now)}
        write_json(os.path.join(out, "chart_of_the_week.json"), cow)
        write_json(os.path.join(out, "results.json"), {
            "week": label, "computed_at": ip.utc_iso(now), "picked": mod.NAME,
            "results": [public_record(r[0], r[1], r[2], r[3]) for r in results if r[0]["_mod"].PUBLIC],
            "skipped": [s for s in skipped if next(m for m in mods if m.NAME == s["template"]).PUBLIC]})
        # internal templates: kept on this machine only
        for r in results:
            if not r[0]["_mod"].PUBLIC:
                write_json(os.path.join(INTERNAL, label, f"{r[0]['template']}.json"), public_record(*r[:4]))
        social = os.path.join(DOCS, "social")
        os.makedirs(social, exist_ok=True)
        for size in ("social_wide", "social_square"):
            shutil.copyfile(os.path.join(out, files[size]), os.path.join(social, f"{label}_{mod.NAME}_{files[size]}"))
        with open(os.path.join(social, f"{label}_{mod.NAME}_caption.txt"), "w", encoding="utf-8", newline="\n") as f:
            f.write(caption + "\n\n" + res["source_line"] + "\n")
        hist = pd.DataFrame(hist_rows)
        hist["picked"] = hist["template"] == mod.NAME
        if os.path.exists(HISTORY):
            old = pd.read_csv(HISTORY, dtype=str, keep_default_na=False)
            old = old[old["week"] != label]
            hist = pd.concat([old, hist.astype(str)], ignore_index=True)
        hist.to_csv(HISTORY, index=False, lineterminator="\n")
        write_json(os.path.join(DOCS, "templates.json"), {"templates": [
            {"template": m.NAME, "title": m.TITLE, "public": m.PUBLIC, "method": " ".join(m.METHOD.split()),
             "params": m.PARAMS, "tables": m.TABLES} for m in mods]})
        n_gal = 0
        if not args.no_gallery:
            idx = gallery(mods, log)
            n_gal = sum(1 for t in idx for c in t["combos"].values() if c["file"])
        status["detail"] = (f"{label}: {len(results)} templates run, {len(skipped)} skipped; chart of the week "
                            f"{mod.NAME} (z {z}); note by {how.split(',')[0]}; gallery {n_gal} charts")
        log(status["detail"])
        print(f"analysis: {status['detail']}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"analysis FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        status.update(status="failed", detail=tb.strip().splitlines()[-1][:300])
    ip.write_status("analysis", run_id, [status])
    log.close()
    return 0 if status["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
