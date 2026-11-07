#!/usr/bin/env python3
"""ERW, Research (/research, Automated Analysis): the page's keyed figures, written to page_figures.json and
page_figures.csv (session 3701, chain 208).

The figures /research prints are the callouts of the findings library's cards (each a Num whose check key is
finding|<card>|callout|<i>|before or after|<grid>, components/analysis/FindingCard.tsx) and, under "This week's chart",
the finding of the newest Roundup's chart (its value, the period before, the change and its score, in the sentence the
page prints). site/scripts/check-values.mjs reads the callouts from the cards' own files (site/data/findings/<card>.json),
so this script reads them there too; a callout whose words name a grid held under its publisher's terms on the day
(site/lib/license.ts licenseHeldGrids, read from site/data/license_status.json) is printed "license needed" on the page,
and is so here. The weekly chart is the newest Roundup's (docs/roundup/<week>.md, its section "Chart of the Week"): a
finding's card when the section shows one, else the rule's pick, docs/analysis/<week>/chart_of_the_week.json (served at
/analysis-files/<week>/).

    python replication/analysis/figures_of_the_page.py [--day YYYY-MM-DD] [--check]

FIELDS names, for every callout, the figure of the card's "numbers" it prints; the script refuses (exit 1) when a
callout's text is not that figure at the text's own decimals, so a card recomputed with other figures is caught here
first. --check compares the files with what would be written and writes nothing (exit 1 when they differ). Standard
library only. Method: docs/methods/automated_analysis.md, "Replication".
"""

import argparse
import csv
import datetime as dt
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CARDS_DIR = os.path.join(ROOT, "site", "data", "findings")
LICENSE = os.path.join(ROOT, "site", "data", "license_status.json")
FINDINGS_TS = os.path.join(ROOT, "site", "lib", "findings.ts")
ROUNDUP = os.path.join(ROOT, "docs", "roundup")
ANALYSIS = os.path.join(ROOT, "docs", "analysis")
OUT_JSON = os.path.join(HERE, "page_figures.json")
OUT_CSV = os.path.join(HERE, "page_figures.csv")

# components/analysis/FindingCard.tsx GRID_WORD, in its order; site/lib/license.ts GRID_PREFIX
GRID_WORD = [("ERCOT", "ercot"), ("CAISO", "caiso"), ("PJM", "pjm"), ("MISO", "miso"), ("SPP", "spp"), ("NYISO", "nyiso"), ("ISO-NE", "isone")]
GRID_PREFIX = {"ISO-NE": "isone", "MISO": "miso", "NYISO": "nyiso", "PJM": "pjm", "SPP": "spp", "CAISO": "caiso", "ERCOT": "ercot"}

# (card, callout, side) -> the figures of the card's "numbers" its text prints, in the order of the numbers in the text.
# {period} is the callout side's own period, {label_year} the year its label names.
FIELDS = {
    "batteries_lunch_grids": [["ercot_multiple_first"], ["ercot_multiple_last"], ["nyiso_multiple_first"], ["nyiso_multiple_last"],
                              ["ercot_fleet_last_mw"], ["nyiso_fleet_last_mw"]],
    "batteries_curtailment": [["curtailed_low_charging_days"], ["curtailed_high_charging_days"], ["charging_coef"], ["charging_solar_month_coef"],
                              ["charging_solar_month_se"], ["charging_solar_month_r2"]],
    "batteries_curtailment_hourly": [["y{label_year}_pred_charging_mw"], ["y{label_year}_obs_charging_mw"], ["corr_curtailed_charging"], ["charging_r2"],
                                     ["y{period}_sat_curt_hours"], ["y{period}_sat_curt_hours"]],
    "gas_sets_price": [["ercot_first"], ["ercot_last"], ["isone_first"], ["isone_last"], ["ercot_last_hr6p5"], ["ercot_last_hr8"]],
    "impact_study": [["series_pre"], ["series_post"], ["control_pre"], ["control_post"], ["did"], ["reg_did_se"]],
    "negative_prices_west": [["ercot_west_first"], ["ercot_west_last"], ["ercot_houston_first"], ["ercot_houston_last"],
                             ["ercot_west_first_share"], ["ercot_west_last_share"]],
    "peak_hour_grids": [["ercot_first_evening_pct"], ["ercot_last_evening_pct"], ["nyiso_first_evening_pct"], ["nyiso_last_evening_pct"],
                        ["ercot_last_solar_mw"], ["nyiso_last_solar_mw"]],
    "queue_divorce": [["withdrawn_pct", "requested_gw"], ["operational_pct"], ["worst_withdrawn_pct"], ["best_withdrawn_pct"],
                      ["cdc_divorce_rate", "cdc_marriage_rate"], ["cdc_ratio_pct"]],
    "who_rescues_whom": [["n_to_export"], ["n_to_import"], ["grid_baseline_abs"], ["grid_event_abs"], ["big_exp_baseline_abs"], ["big_exp_event_abs"]],
    "siting_battery_swing": [["narrowest"], ["widest"], ["median"], ["nodes"], ["widest_p10"], ["widest_p90"]],
    "siting_flexible": [["saved_least"], ["saved_most"], ["lost_fewest"], ["lost_most"], ["hub_flat"], ["hub_flex"]],
    "siting_gigawatt": [["least_allin"], ["most_allin"], ["least_year_usd"], ["most_year_usd"], ["connect_least"], ["connect_most"]],
}
# figures a card prints that its download does not hold: the replication says so and computes nothing
NOT_IN_DOWNLOAD = {
    ("siting_gigawatt", "connect_least"): "the months to connect are read from interconnection_durations by the All grids tab, not written to siting_gigawatt.csv",
    ("siting_gigawatt", "connect_most"): "the months to connect are read from interconnection_durations by the All grids tab, not written to siting_gigawatt.csv",
}
NUMBER = re.compile(r"-?\d[\d,]*(?:\.\d+)?")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def superseded():
    """site/lib/findings.ts SUPERSEDED: the single-grid cards a five-grid card replaces on the page."""
    with open(FINDINGS_TS, encoding="utf-8") as f:
        m = re.search(r"export const SUPERSEDED[^=]*=\s*\{([^}]*)\}", f.read())
    return dict(re.findall(r"(\w+)\s*:\s*\"(\w+)\"", m.group(1))) if m else {}


def held_grids(day):
    """site/lib/license.ts licenseHeldGrids on the day."""
    out = set()
    for row in load(LICENSE)["tables"].values():
        if row.get("status") == "license needed" and day >= row.get("from", "9999"):
            out.update(GRID_PREFIX[p] for p in row.get("publishers", []) if p in GRID_PREFIX)
    return sorted(out)


def grid_of_words(s):
    for word, grid in GRID_WORD:
        if re.search(rf"\b{re.escape(word)}\b", s, re.I):
            return grid
    return "-"


def decimals(text):
    m = re.search(r"\.(\d+)", text)
    return len(m.group(1)) if m else 0


def numbers_in(text):
    """The numbers of a callout's text with their decimals: "75% of 3,509 GW" gives [(75.0, 0), (3509.0, 0)]."""
    return [(float(t.replace(",", "")), decimals(t)) for t in NUMBER.findall(text)]


def card_figures(day, held):
    out, sup = [], superseded()
    for card in FIELDS:
        if card in sup:
            continue
        c = load(os.path.join(CARDS_DIR, card + ".json"))
        nums = c["numbers"]
        for i, co in enumerate(c["callouts"]):
            for j, side in enumerate(("before", "after")):
                words = f"{co[side]['period']} {co['label']}"
                grid = grid_of_words(words)
                text = co[side]["text"]
                label_year = (re.search(r"\b(19|20)\d\d\b", co["label"]) or [""])[0]
                fields = [f.format(period=co[side]["period"], label_year=label_year) for f in FIELDS[card][2 * i + j]]
                shown = numbers_in(text)
                if len(shown) < len(fields):
                    raise SystemExit(f"{card} callout {i} {side}: {text!r} holds {len(shown)} numbers, FIELDS names {len(fields)}")
                for k, field in enumerate(fields):
                    value, dec = shown[k]
                    if field not in nums:
                        raise SystemExit(f"{card} callout {i} {side}: {field} is not a figure of the card's numbers")
                    got = nums[field]
                    if got is None or round(abs(float(got)), dec) != value:
                        raise SystemExit(f"{card} callout {i} {side}: {text!r} is not {field} = {got} at {dec} decimals")
                    is_held = grid in held
                    out.append({
                        "card": card, "callout": i, "side": side, "part": k,
                        "key": f"finding|{card}|callout|{i}|{side}|{grid}",
                        "name": f"{co['label']}, {co[side]['period']}" + (f" (number {k + 1} of the text)" if len(fields) > 1 else ""),
                        "page_text": "license needed" if is_held else text,
                        "page": None if is_held else value,
                        "decimals": dec,
                        "tolerance": 0.5 * 10 ** -dec,
                        "field": field,
                        "download": c["downloads"]["csv"],
                        "held": is_held,
                        "not_in_download": NOT_IN_DOWNLOAD.get((card, field), ""),
                    })
    return out


def week_figures():
    """The newest Roundup's chart: a card (its callouts are in the library above) or the rule's pick, whose finding
    sentence prints four figures."""
    weeks = sorted((f[:-3] for f in os.listdir(ROUNDUP) if re.fullmatch(r"\d{4}-W\d\d\.md", f)), reverse=True)
    for week in weeks:
        with open(os.path.join(ROUNDUP, week + ".md"), encoding="utf-8") as f:
            md = f.read()
        at = re.search(r"^## .*Chart of the Week\s*$", md, re.I | re.M)
        if not at:
            continue
        section = md[at.end():]
        section = section[:section.find("\n## ")] if "\n## " in section else section
        card = re.search(r"\.\./analysis/findings/([a-z0-9_.-]+)_1600x900\.png", section, re.I)
        if card:
            return week, card.group(1), []
        c = load(os.path.join(ANALYSIS, week, "chart_of_the_week.json"))
        ch, h = c["change"], c["headline"]
        key = f"not keyed: the finding sentence of the chart of {week} (chart_of_the_week.json, finding)"
        rows = [("the headline value", h["value"], "value"), ("the period before", ch["previous_value"], "previous"),
                ("the change from the period before", ch["delta"], "delta"),
                ("the score: percent of the earlier changes that were smaller", ch["score"], "score")]
        out = [{"card": "chart_of_the_week", "callout": 0, "side": "", "part": k, "key": key,
                "name": f"{c['headline']['label']}, {h['period']}: {name}" + (f", {h['unit']}" if k < 3 else ""),
                "page_text": f"{v:g}", "page": float(v), "decimals": decimals(f"{v:g}"), "tolerance": 0.5 * 10 ** -decimals(f"{v:g}"),
                "field": field, "download": f"/analysis-files/{week}/chart_of_the_week.json", "held": False, "not_in_download": "",
                "earlier_changes": ch["earlier_changes"]} for k, (name, v, field) in enumerate(rows)]
        return week, "", out
    return None, "", []


def build(day):
    held = held_grids(day)
    week, chosen, weekly = week_figures()
    figures = card_figures(day, held) + weekly
    doc = {
        "_about": ("Research (/research): the figures the page prints, each with its check key (a callout's Num key; the weekly "
                   "chart's finding sentence has none), the text the page shows, the number in it, its decimals and the tolerance "
                   "to which the replication must meet it (half of the last shown digit), the figure of the card's numbers it is, "
                   "and the download it is rebuilt from. Written by figures_of_the_page.py from the cards' own files "
                   "(site/data/findings/<card>.json, which site/scripts/check-values.mjs holds the page to) and the newest "
                   "Roundup's chart. A figure the page prints as \"license needed\" has no number here."),
        "written_for_day": day,
        "held_grids": held,
        "superseded_cards": superseded(),
        "cards_computed_at": {card: load(os.path.join(CARDS_DIR, card + ".json")).get("computed_at", "") for card in FIELDS if card not in superseded()},
        "week": week,
        "week_card": chosen,
        "not_replicated": ("today's chart (the Digest's chart of the day, docs/digest/charts/, drawn from the scanner's table "
                           "rows, which no download of /research holds); the five \"also moved\" sentences under the weekly chart "
                           "(their series are not in the week's file)"),
        "figures": figures,
    }
    cols = ["card", "callout", "side", "part", "key", "name", "page_text", "page", "decimals", "tolerance", "field", "download", "held", "not_in_download"]
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(cols)
    for f in figures:
        w.writerow(["" if f[c] is None else (int(f[c]) if c == "held" else f[c]) for c in cols])
    return json.dumps(doc, indent=1, ensure_ascii=False) + "\n", buf.getvalue()


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--day", default=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d"))
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    js, cs = build(a.day)
    if a.check:
        same = True
        for p, t in ((OUT_JSON, js), (OUT_CSV, cs)):
            if not os.path.exists(p):
                same = False
                continue
            with open(p, encoding="utf-8") as f:
                same = same and f.read() == t
        print("page_figures.json and page_figures.csv are current" if same else "page_figures.json or page_figures.csv differs from the cards' files: write them again")
        return 0 if same else 1
    for p, t in ((OUT_JSON, js), (OUT_CSV, cs)):
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(t)
    n = json.loads(js)["figures"]
    print(f"{len(n)} figures written ({sum(1 for f in n if f['held'])} license needed, {sum(1 for f in n if f['not_in_download'])} not in a download)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
