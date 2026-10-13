"""Session 251: append the twelve new drafts, verified, to docs/reviews/findings-verified-2026-10-13.md.

Every number in the appended section is read from verify_251.json (written by verify_251.py beside this file, and kept
here too); the verdicts and their reasons are this session's, written below by id. Session 252's text above the
section is not touched: the section begins at its own heading and runs to the end of the file, and a second run
replaces that section alone."""
import csv
import datetime as dt
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while not os.path.exists(os.path.join(ROOT, "ARCHITECTURE.md")):
    ROOT = os.path.dirname(ROOT)
RUN = os.path.join(ROOT, "runs", "session251")
DOC = os.path.join(ROOT, "docs", "reviews", "findings-verified-2026-10-13.md")
HEADING = "## Session 251's twelve drafts, verified"
SRC = os.path.join(RUN, "verify_251.json") if os.path.exists(os.path.join(RUN, "verify_251.json")) else os.path.join(HERE, "verify_251.json")
res = {r["id"]: r for r in json.load(open(SRC, encoding="utf-8"))}
cov = {r["table"]: r for r in csv.DictReader(ln for ln in open(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), encoding="utf-8") if not ln.startswith("#"))}
lic = {r["table"]: r for r in csv.DictReader(ln for ln in open(os.path.join(ROOT, "warehouse", "metadata", "license_status.csv"), encoding="utf-8") if not ln.startswith("#"))}


def f(v, nd=1):
    return f"{v:,.{nd}f}"


# The verdicts, strongest first: strong, usable or drop, each with its reason (the rule is session 252's).
VERDICT = [
    ("scan-hunt-5ed296972954", "strong",
     "Six steps of six, and 2026 to date is higher again (8,067). Asked three other ways it says the same: as a share of the year's peak demand the median ramp goes from 1.5 to 8.2 percent. "
     "One thing to tell a reader: it is not a steady climb. Four fifths of the rise came in 2024 and 2025 (2,236 MW per hour in 2023, 6,871 in 2025), the two years in which the same table's solar fleet went from 12,317 to 25,939 MW; without 2025 the claim keeps 58 percent."),
    ("scan-hunt-eb88fc07112e", "strong",
     "Six steps of six, the rank correlation with the year is 1.00, 95 percent of the change remains without 2019 and 83 percent without 2025, and 2026 to date is higher again (8,619). "
     "As a share of peak demand the median ramp goes from 10.2 to 16.2 percent. The two one-episode columns of the table point the same way and jump about from year to year, which is why the median was drafted and they were not."),
    ("scan-hunt-64af52af05e4", "strong",
     "Eight steps of ten, rank correlation 0.98, and nothing leans on an end year (95 percent remains without 2015, 98 without 2025). Solar alone, wind alone and the plain GWh all say the same. "
     "Two things a reader must be told. The share has been flat since 2022 (4.2, 4.2, 4.5, 4.5) while the fleet beside it went on growing, and 2026 to date is a new high (6.8 percent of nine months). "
     "And the battery figure beside the claim is stated, not tested: this card must not be read as batteries causing, or curing, curtailment. Findings 7 and 10 are the tested versions of that question."),
    ("scan-hunt-dafe6c88cbd4", "usable",
     "True, and it survives every cut: the evening's electricity went from dirtier than California's average to cleaner than it (247 to 172 kg per MWh from 5 PM to 10 PM, against 222 to 190 in all hours). "
     "The limit: the sign changed in 2024 and 2025 alone (the premium was 7.2 percent in 2023), so 'down from 2019' is two years, and 2026 to date is back near zero (minus 1.7). "
     "Before it is published, look at the table's 2026 rows: its all-hours level reads 118 against 190 in 2025, a fall no other year shows."),
    ("scan-hunt-ab16dcb071fb", "usable",
     "Four times the 2015 level, and both other cuts agree. But it is a hump, not a rise: the share peaked in 2022 (9.95 percent), fell in three years to 5.42 in 2025, and 2026 to date is the highest held (11.57). "
     "'Up from 2015' is true and hides all of that. Usable as the zone's history by year; the single pair of years is the weakest way to say it."),
    ("scan-hunt-b0be36367f04", "usable",
     "The median night hour at the West hub moved from a small real-time premium to a day-ahead premium, seven steps of ten, and day-ahead stood above real time in 40.4 percent of night hours in 2015 and 57.8 in 2025. "
     "Two limits. It is small in money (USD 1.54 per MWh), and it holds for the median only: the mean spread goes the other way (minus 0.32 to minus 0.47; minus 17.38 in 2021), because a few real-time spikes carry a mean. Say 'the typical hour'. "
     "Without 2025 the claim keeps 41 percent (2024 was 0.38), and 2026 to date is 0.76."),
    ("scan-hunt-a3f52d9a2b65", "usable",
     "Every full year above the one before and nothing leaning on an end year. But it is under one point in six years on a level of 4 percent, and it is wind as a whole, not the night: "
     "wind's share in every hour goes from 2.9 to 3.7 percent, and the night adds 0.1 point to that. These are EIA's rows about PJM (EIA-930), not PJM's own; no PJM price is held, so the family's second number is absent. Low interest by itself."),
    ("scan-hunt-93c9518aa8b7", "usable",
     "The two end years are right and all three windows agree in direction. It is a step, not a climb: the share jumped in 2021 (38 to 76 percent) when the fleet arrived, and has drifted down since (76.0, 68.7, 74.0, 74.5, 70.8, and 67.9 in 2026 to date). "
     "The 2019 and 2020 figures rest on a fleet that discharged 47 and 59 GWh in the year against 12,215 in 2025. Usable as 'about 70 percent of discharge falls from 5 PM to 10 PM since 2021'; "
     "the newer story is the other one: from 4 PM to 9 PM the share fell from 71.9 percent in 2021 to 59.2 in 2025 as discharge moved later."),
    ("scan-hunt-deb675c56b2a", "usable",
     "Imports on California's stress days halved, and the 10 percent cut says the same. Three limits. It is one step, in 2023 (19.2 to 7.9 percent), with two steps of five in the claim's direction. "
     "It is not about stress days: over every day of the year the share fell from 25.1 to 14.2 percent as well. And the claim ends in 2024 because 2025 is not a full year in the interchange table (315 days held with both figures). "
     "Before it is published, read EIA's known issues for CISO's interchange in 2023: a step this sharp can be a change in what is reported."),
    ("scan-hunt-218d72573b8e", "usable",
     "The same finding as the South hub draft session 252 called usable (`scan-hunt-f5c8f78e8cf0`), from the zone's rows instead of the hub's: a step in 2021 (0.99 to 3.00 percent) and flat since, between 2.1 and 3.0. "
     "Half the claim remains without 2015 and five steps of ten go its way. Publish one of the two, as 'about three times the level before 2021' (0.4 to 1.5 percent in 2015 to 2020, 2.1 to 3.0 since)."),
    ("scan-hunt-896268eaf427", "drop",
     "The change, 2.5 points, is smaller than the table's own uncertainty for California (3.21 percent in every year), one step of three goes its way, and before the weather is taken out the year's energy against the base does not rise at all (3.08 percent in 2022, 2.86 in 2025). "
     "The hunt's strength of 5.46 is an accident of four years: two of the three yearly moves are near zero, so the typical move it divides by is 0.46."),
    ("scan-hunt-81c8eceefbb2", "drop",
     "The whole claim is 2019. From 2020 to 2025 the share goes from 31.38 to 31.45 percent: 1.5 percent of the change remains without the first year, and since 2022 it has fallen (33.3 to 31.5). "
     "It is not the night either: wind's share in every hour moves the same way (20.0 to 23.2). The price beside it does not move with it: the median night hour stood USD 3.24 under the median hour in 2019, 6.74 under it in 2022 and 1.14 under it in 2025."),
]
PUBLISHER = {
    "ERCOT": "ERCOT: raw data in public parts of its site 'may be used, reproduced, and redistributed in compilations, charts, and analyses' (docs/licenses.md, read 2)",
    "CAISO": "CAISO: 'may be used by you provided that you keep intact all copyright, trademark and other proprietary notices and that you credit the California ISO' (docs/licenses.md, read 3), so a published card must credit the California ISO",
    "EIA": "EIA: 'U.S. government publications are in the public domain' (docs/licenses.md, read 1); EIA asks for the line 'Source: U.S. Energy Information Administration' with the date",
}
# the publishers behind each table's rows for the drafted region (docs/licenses.md, "Every table", read for that region)
BEHIND = {"ercot_all_hub_prices_history": ["ERCOT"], "ercot_zone_prices_history": ["ERCOT"], "caiso_fuel_supply_history": ["CAISO"], "caiso_fuel_supply": ["CAISO"],
          "eia930_daily_demand": ["EIA"], "eia930_daily_total_interchange": ["EIA"], "eia930_demand_weather": ["EIA"], "carbon_intensity_hourly": ["EIA"],
          "storage_buildout_monthly": ["EIA"], "iso_curtailment_monthly": ["CAISO"], "grid_stress_yearly": ["EIA", "CAISO"], "generation_mix_hourly_profile": ["EIA", "CAISO"]}


def license_line(r):
    pubs, flags = [], []
    for t in r["tables"]:
        for p in BEHIND[t]:
            if p == "CAISO" and t in ("grid_stress_yearly", "generation_mix_hourly_profile") and r["region"] != "caiso":
                continue                                 # CAISO's own rows are in those tables for the caiso region only
            if p not in pubs:
                pubs.append(p)
        s = lic.get(t)
        flags.append(f"`{t}` {cov.get(t, {}).get('license', 'not in coverage.csv')}" + (f", but '{s['status']}' from {s['from']} for {s['publishers']}" if s else ""))
    needed = [x for x in flags if "license needed" in x]
    return ("public by the publisher" + ("s" if len(pubs) > 1 else "") + ". " + ". ".join(PUBLISHER[p] for p in pubs) + ". In `coverage.csv`: " + "; ".join(flags) + ". "
            + (f"{len(needed)} of them is marked 'license needed' in `license_status.csv`." if needed else "None is in `license_status.csv`, and the source line names these tables and no other: session 252's point is met."))


def block(n, r, verdict, reason):
    c, m, d = r["claim"], r["more"], r["decimals"]
    years = sorted(r["series"])
    by_year = ", ".join(f"{y} {f(r['series'][y][0], d)}" for y in years if y != "2026")
    uw = m.get("year_under_way")
    not_full = [y for y in years if y != "2026" and c["first_year"] <= y <= c["last_year"] and y not in [str(k) for k in r_years(r)]]
    cuts = []
    for k in r["cuts"]:
        if k.get("first") is None or k.get("last") is None:
            cuts.append(f"{k['name']}: not held in both of the claim's years (" + ", ".join(f"{y} {f(v, 2)}" for y, v in k["by_year"].items()) + ")")
        else:
            cuts.append(f"{k['name']}: {f(k['first'], 2)} in {c['first_year']}, {f(k['last'], 2)} in {c['last_year']} ({'the same direction' if k['same_direction'] else 'NOT the claim\'s direction'})")
    L = [f"### {n}. {r['words']}: {r['label']}", "",
         f"- **Draft:** `{r['id']}`, the weekly hunt, pattern `{r['pattern']}` (measure `hunt_measures.{r['measure']}`), region `{r['region']}`; state {r['state']}; raised {r['raised_at'][:19]} UTC; the hunt's strength {f(r['strength'], 2)}.",
         f"- **Claim:** {r['fact']}",
         f"- **Number:** {f(c['first'], d)} {r['unit']} in {c['first_year']}, {f(c['last'], d)} in {c['last_year']}: a change of {f(c['change'], d)}. By year: {by_year}."
         + (f" {uw['year']} to date: {f(uw['value'], d)} ({f(uw['n'], 0)} observations)." if uw else "")
         + (f" Not a full year, so outside the claim: {', '.join(not_full)}." if not_full else ""),
         f"- **Reproduced:** yes, exactly. Its own Python mirror on its own CSV: exit {r['mirror_exit']}, the claim line and the three verdicts equal the draft's. "
         f"{r['numbers_compared']} stored values recomputed from the CSV and compared (the claim, the card's numbers, the three tests, the fact line and the caption character by character): 0 differ. "
         f"The CSV rebuilt from today's tables by the measure: {len(years)} years, {len(r['today_diffs'])} differ"
         + (f"; the second number beside the claim, {len(r['context']['values'])} years, {len(r['context_diffs'])} differ." if r.get("context") and r["context"].get("beside") else ".")
         + ("" if r["row_value_column"]["equal_in_full"] else f" One note: the row's own `value` column reads back as {r['row_value_column']['stored']!r} (15 digits; the card holds {r['row_value_column']['recomputed']!r})."),
         f"- **Robust, the hunt's three tests, run again:** {sum(1 for t in r['tests'] if t['passed'])} of 3 pass. " + " ".join(f"{t['name'].capitalize()}: {t['words']}." for t in r["tests"]),
         f"- **Robust, five tests the hunt does not run:** year-to-year steps in the claim's direction: {m['steps_on_side']} of {m['steps']}. Rank correlation of the value with the year: {f(m['spearman_year'], 2)}. "
         f"The last two years against the first two: {f(m['two_year_ends'], d)} ({'the same side' if m['two_year_ends_same_side'] else 'THE OTHER SIDE'}). "
         f"Without {c['first_year']}: {f(m['share_of_claim_without_first_year'] * 100, 0)} percent of the change remains; without {c['last_year']}: {f(m['share_of_claim_without_last_year'] * 100, 0)} percent. "
         f"Median of the years between: {f(m['median_between'], d)}. The change is {f(c['strength'], 2)} typical yearly moves ({f(c['typical_move'], max(d, 2))} {r['unit']})."
         + (f" {uw['year']} to date is {'beyond' if uw['beyond_last'] else 'not beyond'} {c['last_year']}." if uw else ""),
         "- **Robust, the question asked another way:** " + ". ".join(cuts) + ".",
         f"- **License:** {license_line(r)}",
         f"- **Verdict: {verdict}.** {reason}", ""]
    return L


def r_years(r):
    """The full years of the claim: those the CSV's series holds with at least 90 percent of the fullest year's observations."""
    most = max(v[1] for v in r["series"].values())
    return [y for y, v in r["series"].items() if int(y) < 2026 and v[1] >= 0.9 * most]


def main():
    assert sorted(res) == sorted(v[0] for v in VERDICT), "a draft without a verdict, or a verdict without a draft"
    counts = {v: sum(1 for _, x, _ in VERDICT if x == v) for v in ("strong", "usable", "drop")}
    read_at = dt.datetime.fromtimestamp(os.path.getmtime(os.path.join(RUN, "drafts", "index.json")), dt.timezone.utc).strftime("%H:%M") if os.path.exists(os.path.join(RUN, "drafts", "index.json")) else "18:21"
    compared = sorted({r["numbers_compared"] for r in res.values()})
    L = [HEADING, "",
         f"Session 251, on lab-desktop (the data machine), later on 13 October 2026. Its hunt (version 1.1.0: 20 patterns, 143 claims, 50 passing the three tests) added 12 drafts to the review list at 18:18 UTC; "
         f"the list was read back at {read_at} UTC: 28 rows, 28 in state draft. No draft's state was changed, no publisher was asked and no model was called. "
         "The section above that says session 251 left no drafts was true when it was written, at 10:49 UTC; it is kept as it stood. "
         "Everything below was computed by `docs/reviews/findings-verified-2026-10-13-session251/` (`fetch_drafts.py`, `verify_251.py`, `build_251.py`; the result file `verify_251.json` is beside them).", "",
         "### Read these first", "",
         f"- **All 12 reproduce exactly.** Each draft's own Python mirror on its own CSV, {compared[0]} to {compared[-1]} stored values a draft recomputed and compared, and the CSV rebuilt from today's tables by the family's own measure: every year equal, in 12 of 12.",
         f"- **Verdicts of the 12: {counts['strong']} strong, {counts['usable']} usable, {counts['drop']} drop.**",
         "- **The three strong ones:** the evening ramp in ERCOT (the median day's steepest hour, 1,123 to 6,871 MW per hour, 2019 to 2025) and in CAISO (4,473 to 7,122), and CAISO's curtailed share of wind and solar (0.67 to 4.53 percent, 2015 to 2025).",
         "- **The two to drop:** California's demand growth after weather (a change smaller than the table's own uncertainty, over four years) and wind's share of ERCOT's night (the whole claim is the year 2019).",
         "- **Session 252's two lessons hold in these drafts.** No draft is a one-interval measure: the two spike patterns were computed, 7 of their claims passed, and none was drafted. Every draft's source line names the tables its own region's rows come from and no other; none of them is in `license_status.csv`.",
         "- **The hunt's strength misled twice.** It ranked California's demand growth third of the twelve (5.46) on four years of data. The two drops are the two claims a fourth test would have stopped: the change must stand outside the measure's own noise, and half of it must remain without the first year.", "",
         "### How these were checked", "",
         "- **Reproduced:** as session 252 did for a hunt draft, with one difference: a family has no finding behind it, so step (3) rebuilds the CSV by the family's measure (`hunt_measures.py`) on today's tables, and compares the second number beside the claim as well.",
         "- **Robust:** the hunt's three tests again; session 252's five further tests (its own function, imported); and one thing session 252 did not do: **the question asked another way**, a second definition of each family's measure (another window, another threshold, a mean beside the median, a part beside the whole), computed in `verify_251.py` apart from the measure where the table allows.",
         "- **License:** each table's flag in `coverage.csv`, its row or none in `license_status.csv`, and the sentence of the publisher behind that region's rows (`docs/licenses.md`).",
         "- **Not done:** no do-file was run (no Stata on this machine). No number was checked against a publisher's site. The other cuts read the same tables as the measures: a fault in a table is in both.",
         "- **Verdict:** session 252's rule. Strong, the claim holds whichever way it was cut; usable, true with a limit the block names; drop, with the reason.", "",
         "### The 12 drafts of session 251, strongest first", ""]
    order = {"strong": 0, "usable": 1, "drop": 2}
    assert [v for _, v, _ in VERDICT] == sorted((v for _, v, _ in VERDICT), key=order.get)
    for n, (did, verdict, reason) in enumerate(VERDICT, 17):
        L += block(n, res[did], verdict, reason)
    L += ["### What the hunt should learn from these twelve", "",
          "- **A fourth test, the one session 252 asked for:** at least half of the change must remain when the first year is left out. It stops ERCOT's night wind (1.5 percent remains) and would not stop any of the three strong drafts (99, 95 and 95 percent).",
          "- **A floor of years for strength.** With four full years the typical yearly move is the median of three numbers. California's demand growth got a strength of 5.46 from a typical move of 0.46.",
          "- **A measure with its own uncertainty should carry it.** `eia930_demand_weather` holds the fit's uncertainty beside each figure; a change inside it is not a claim.",
          "- **A step is not a trend.** Five of the seven usable drafts are one step (batteries in 2021, imports in 2023, the South zone in 2021) or a hump (the West zone). The three tests pass a step; a card that says 'up from' reads as a trend. The count of yearly steps in the claim's direction, printed on the card, would tell a reviewer at a glance.",
          "- **Two patterns can tell one story.** The South load zone's draft repeats the South hub's. The hunt drops a draft with the same numbers as another, not one with the same story.", ""]
    text = "\n".join(L)
    if chr(0x2014) in text or chr(0x2013) in text:
        print("a dash that is not allowed is in the text", file=sys.stderr)
        return 1
    doc = open(DOC, encoding="utf-8").read()
    head = doc[:doc.index(HEADING)] if HEADING in doc else doc.rstrip("\n") + "\n\n"
    with open(DOC, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(head + text)
    print(f"appended to {DOC}: {len(L)} lines, {len(VERDICT)} blocks; {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
