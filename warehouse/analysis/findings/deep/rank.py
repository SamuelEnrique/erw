#!/usr/bin/env python3
"""The findings hunt's drafts ranked (chain 164, session 3020): docs/reviews/findings-ranked-2026-11-06.md.

Energy Research Warehouse (ERW). The rubric is the plan's (docs/reviews/findings-hunt-plan-2026-11-06.md, "The ranking
rubric"): consequence, novelty and strength, each 1 to 3, ranked by the sum, ties by strength. Consequence is the
candidate's (set by its author from its scale); strength is 3 at two typical yearly moves or more, else 2 (every draft
passed all five tests); novelty is 3 unless the ERW already shows the measure (NOVELTY below, each with its reason).
Nothing is approved: the file is a reading order.

    python warehouse/analysis/findings/deep/rank.py            # reads the drafts over SUPABASE_DB_URL, writes the file
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
OUT = os.path.join(ROOT, "docs", "reviews", "findings-ranked-2026-11-06.md")
sys.path.insert(0, os.path.join(ROOT, "warehouse"))

# candidate: (novelty, the reason it is not 3)
NOVELTY = {
    "daily_spread": (2, "the battery page (/cost-of-power/battery) shows ERCOT's daily spreads"),
    "spread_4h": (2, "the battery page shows the four-hour spread a battery could take"),
    "wide_spread_days": (2, "the battery page shows ERCOT's daily spreads"),
    "top_days_share": (2, "the battery page shows the spread's days"),
    "midday_discount": (2, "the ERCOT peak premium explorer shows the midday against the peak"),
    "evening_premium": (2, "the ERCOT peak premium explorer shows the peak against the day"),
    "midday_minus_night": (2, "the ERCOT peak premium explorer shows the hours of the day"),
    "cheapest_hour": (2, "the weekly hunt's peak-hour patterns ask the dearest hour, not the cheapest"),
    "solar_midday_share": (2, "the ERW's generation mix profile and shoulder-hours pages show the hours"),
    "gas_evening_share": (2, "the ERW's shoulder-hours page shows the evening"),
    "battery_fleet_mw": (1, "the /storage page shows the battery fleet by grid"),
    "fleet_hours": (1, "the /storage page shows the fleet's duration"),
}


def score(card):
    h, n = card["hunt"], card["numbers"]
    cons = int(h.get("consequence") or 2)
    nov, why = NOVELTY.get(h["pattern"], (3, ""))
    strength = 3 if float(n["strength"]) >= 2.0 else 2
    return cons, nov, strength, why


def main(append=None):
    import lock
    import psycopg
    with psycopg.connect(lock.env("SUPABASE_DB_URL")) as c:
        rows = c.execute("select id, card from public.scanner_drafts where id like 'scan-deep-%' and state = 'draft'").fetchall()
    ranked = []
    for did, card in rows:
        cons, nov, st, why = score(card)
        ranked.append((cons + nov + st, float(card["numbers"]["strength"]), did, card, cons, nov, st, why))
    ranked.sort(key=lambda r: (-r[0], -r[1], r[2]))
    by_family = {}
    for r in ranked:
        by_family[r[3]["hunt"]["family"]] = by_family.get(r[3]["hunt"]["family"], 0) + 1
    lines = ["# The findings hunt's drafts, ranked (6 November 2026)", "",
             f"Written by session 3020 (chain 164) with `warehouse/analysis/findings/deep/rank.py` from the {len(ranked)} drafts this chain put on the review list "
             "(`public.scanner_drafts`, module `deep.*`, every one still a draft). Nothing here is approved; it is an order to read them in. Each draft is at "
             "`/internal/findings` with its chart, its tests, its CSV, its Python and Stata scripts, and in `docs/findings/<family>/`.", "",
             "## The rubric and its reasoning", "",
             "- **Consequence (1 to 3):** the candidate's scale, set when it was written: 3 a price shape, a spread worth more than a dollar a MWh over a year, a peak or a fleet in GW, a national share; 2 a region, a technology or a sub-market; 1 a curiosity.",
             "- **Novelty (1 to 3):** 3 unless the ERW already shows the measure. 2 where a page or a weekly hunt pattern shows it for another place or cut (the battery page's spreads, the peak premium explorer's hours, the mix profile); 1 where a page shows it outright (/storage's fleet). The reason is written beside each such draft below.",
             "- **Strength (2 or 3):** every draft passed the hunt's five tests; 3 when its change is at least two typical yearly moves, else 2.",
             "- **Order:** the sum, highest first; ties by the strength in typical moves.", "",
             "## The drafts by family", "", "| Family | Drafts |", "|---|---:|"]
    lines += [f"| {f} | {k} |" for f, k in sorted(by_family.items())] + [f"| all | {len(ranked)} |", "", "## The twenty to read first", ""]
    for i, (tot, s, did, card, cons, nov, st, why) in enumerate(ranked[:20], 1):
        lines.append(f"{i}. **{card['hunt']['family']}**, score {tot} (consequence {cons}, novelty {nov}, strength {st}; {s:.1f} typical moves). {card['subtitle']} `{did}`"
                     + (f" Novelty {nov}: {why}." if why else ""))
    lines += ["", "## Every draft", "", "| Rank | Score | C | N | S | Moves | Family | Candidate | Region | Draft |", "|---:|---:|---:|---:|---:|---:|---|---|---|---|"]
    for i, (tot, s, did, card, cons, nov, st, why) in enumerate(ranked, 1):
        lines.append(f"| {i} | {tot} | {cons} | {nov} | {st} | {s:.1f} | {card['hunt']['family']} | {card['hunt']['pattern']} | {card['hunt']['region']} | `{did}` |")
    if append:
        # session 3184 (chain 166): a later ranking is a dated section added to the file; the earlier ones are kept
        first = lines.index("## The drafts by family")
        lines = ["", f"## {append}", "", f"Every draft still a draft on the review list, {len(ranked)} in all, ranked by the same rubric (above)."] + [
            ("#" + ln if ln.startswith("## ") else ln) for ln in lines[first:]]
    text = "\n".join(lines) + "\n"
    if chr(0x2014) in text or chr(0x2013) in text:
        raise SystemExit("a dash the repository forbids")
    with open(OUT, "a" if append else "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(f"{len(ranked)} drafts ranked; {OUT}{' (appended)' if append else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "--append" else None))
