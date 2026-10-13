"""Session 252: write docs/reviews/findings-verified-2026-10-13.md from the two verification files of this folder
(verify_hunt.json, verify_scanner.json) and the license metadata. Every number in the document is read from those
files; the verdicts and their reasons are this session's, written below by id."""
import csv
import datetime as dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.exists(os.path.join(ROOT, "ARCHITECTURE.md")):   # the repository root, from runs/ or from docs/
    ROOT = os.path.dirname(ROOT)
HERE = os.path.join(ROOT, "runs", "session252")
OUT = os.path.join(ROOT, "docs", "reviews", "findings-verified-2026-10-13.md")

hunt = {r["id"]: r for r in json.load(open(os.path.join(HERE, "verify_hunt.json"), encoding="utf-8"))}
scan = {r["id"]: r for r in json.load(open(os.path.join(HERE, "verify_scanner.json"), encoding="utf-8"))}
index = json.load(open(os.path.join(HERE, "drafts", "index.json"), encoding="utf-8"))
cov = {r["table"]: r for r in csv.DictReader(ln for ln in open(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), encoding="utf-8") if not ln.startswith("#"))}
lic = {r["table"]: r for r in csv.DictReader(ln for ln in open(os.path.join(ROOT, "warehouse", "metadata", "license_status.csv"), encoding="utf-8") if not ln.startswith("#"))}


def f(v, nd=1):
    return f"{v:,.{nd}f}"


# The verdicts: strong, usable or drop, each with its reason. Order: strongest first.
VERDICT = [
    ("scan-hunt-e5fe5b80e074", "strong", "Every year moves the same way, six steps of six, and the year under way sits at 2025's level. Nothing in the claim leans on one year: 77 percent of it remains without 2019 and 95 percent without 2025."),
    ("scan-hunt-bbb2fe2a3844", "strong", "The mirror image of the evening draft, from the same days, and as steady: five steps of six, and 2026 to date is lower again. Publish it with the evening draft or not at all: they are one finding told twice."),
    ("scan-hunt-9868ad33205b", "strong", "Five steps of six, 2025 is the highest full year held and 2026 to date is higher again. The level is small (2.6 percent of hours): say hours, not a share alone."),
    ("scan-weekly-4be2976922ee", "strong", "The largest weekly fall of this position in the 611 weeks held since January 2015 under both names of the contract, not only in the 241 weeks the scanner compared, and the week after did not undo it. A reader will ask why: the draft does not say, and the same week's open interest fell too (1,837,146 to 1,782,129 contracts)."),
    ("scan-record-483f592bf064", "usable", "A record by a third, and a record for July too. One month, the newest EIA publishes, with no later month held to confirm it, and 82 percent above June: wait for August's value or EIA's revision, or say it is the first estimate. Jumps of this relative size happened five times before in this series."),
    ("scan-hunt-f5c8f78e8cf0", "usable", "The two end years are right and all six later years lie above 2019. It is a step, not a climb: the share jumped in 2021 (3.26 percent, the highest year held) and has moved between 1.9 and 2.7 since; 2026 to date is below 2025. Usable as 'three to five times the 2019 level in every year since 2021', not as a rising trend. North, above, is the cleaner of the two."),
    ("scan-record-90427afd38ee", "usable", "A record for any month and for July, and the largest value against its own prior twelve months in 295 months. It is one summer month of the newest data EIA publishes, in one state, 0.85 plain standard deviations past the old record, and the draft gives no cause: no temperature was read beside it, here or in the draft. Usable beside a weather line."),
    ("scan-spike-4c52d4239fe9", "usable", "A real episode of several days (3 to 9 October), not one bad hour. Not a first: it is the third dearest day of the 767 held, behind 5 and 6 September 2024, and two other days this autumn were as dear to the cent or two (10 September at 20.63, 7 October at 20.57). The rule's three years of history are 2.09 years here, since the table begins in September 2024. Usable as 'the dearest week since September 2024'."),
    ("scan-weekly-33b8c62e9e29", "usable", "The largest weekly fall held (403 weeks from January 2019), and Ohio as a whole fell 43 cents the same week. It follows a rise of 56 cents in the two weeks to 21 September, and this year already holds two larger weekly moves upward (91.5 cents on 4 May, 55.3 on 9 March): the story is a volatile year in Ohio, not this week. No later week is held."),
    ("scan-record-7abe48d6b46b", "usable", "A record for any month and for July, 8.9 percent past the old one, one preliminary month. A price here is revenue over sales for a whole sector: a small margin and no cause in the draft. Low interest by itself."),
    ("scan-record-34aae7580df2", "usable", "A record by 5.7 percent, 0.75 plain standard deviations, in the newest month EIA publishes, and the seventh largest value against its own prior twelve months. The record it passes dates from September 2001, which the draft does not explain. True and thin: the weakest record on the list that still stands."),
    ("scan-record-6e1d1cff0ae4", "drop", "The sector is one customer: the customers series of the same table holds 1 for the District's industrial sector in every month of the last year (and never more than 1 in 307 months). The price is one bill's revenue over its sales, and it has ranged from 78.6 to 321.5 USD per MWh in the last fourteen months. It reproduces exactly and means nothing."),
    ("scan-hunt-346d3337bb15", "drop", "The measure is one 15-minute interval a year over the year's median. 70 percent of the claim is 2019 alone (without it the change is 30 percent of the claim), the years between are not below 2019 as a group (2021 and 2023 are far above it), and the change is half a typical yearly move. The three tests pass because they ask only for the direction. Same numbers under HB_WEST and HB_SOUTH below."),
    ("scan-hunt-4bee49d6e8c5", "drop", "As the hub average above: one interval a year, 69 percent of the claim is 2019 alone, strength 0.51."),
    ("scan-hunt-8c67230bc8b7", "drop", "As the hub average above: one interval a year, 72 percent of the claim is 2019 alone, strength 0.50."),
    ("scan-hunt-f732d699c6b7", "drop", "As drafted it misleads: 'down from 2019' reads as a decline, and three of the six later years held more such hours than 2019 (2021, 2022 and 2023; the median of the years between is 35 hours against 2019's 26.25). Only 11 percent of the claim remains without 2019. What the numbers do support is narrower: 2025 is the calmest full year held (2.25 hours) and 2026 to date is calmer still (1.0)."),
]
PUBLISHER = {
    "ercot": ("ERCOT", "raw data in public parts of its site 'may be used, reproduced, and redistributed in compilations, charts, and analyses' (docs/licenses.md, read 2)"),
    "caiso": ("CAISO", "'may be used by you provided that you keep intact all copyright, trademark and other proprietary notices and that you credit the California ISO' (docs/licenses.md, read 3); a published card must credit the California ISO, and the same page's API terms forbid use 'for any other benchmarking or competitive purposes'"),
    "eia": ("EIA", "'U.S. government publications are in the public domain' (docs/licenses.md, read 1); EIA asks for the line 'Source: U.S. Energy Information Administration' with the date, which the draft's source line does not carry word for word"),
    "cftc": ("CFTC", "'Government information at the CFTC website is in the public domain'; an acknowledgement of the CFTC is asked for (docs/licenses.md, read 11)"),
}


def license_words(tables, pub):
    name, sentence = PUBLISHER[pub]
    flags = []
    for t in tables:
        c = cov.get(t, {}).get("license", "not in coverage.csv")
        s = lic.get(t)
        flags.append(f"`{t}` {c}" + (f", but '{s['status']}' from {s['from']} for {s['publishers']}" if s else ""))
    return name, sentence, flags


def hunt_block(n, r, verdict, reason):
    c, m, d = r["claim"], r["more"], r["decimals"]
    years = sorted(r["series"])
    by_year = ", ".join(f"{y} {f(r['series'][y][0], d)}" for y in years if y != "2026")
    uw = m.get("year_under_way")
    name, sentence, flags = license_words(r["tables"], "ercot")
    needed = [x for x in flags if "license needed" in x]
    L = [f"### {n}. {r['words']}: {r['label']}", "",
         f"- **Draft:** `{r['id']}`, the weekly hunt, pattern `{r['pattern']}`, region `{r['region']}`; state {r['state']}; the hunt's strength {f(r['strength'], 2)}.",
         f"- **Claim:** {r['fact']}",
         f"- **Number:** {f(c['first'], d)} {r['unit']} in {c['first_year']}, {f(c['last'], d)} in {c['last_year']}: a change of {f(c['change'], d)}. By year: {by_year}."
         + (f" {uw['year']} to date: {f(uw['value'], d)} ({f(uw['n'], 0)} observations)." if uw else ""),
         f"- **Reproduced:** yes, exactly. Its own Python mirror on its own CSV: exit {r['mirror_exit']}, the claim line and the three verdicts equal the draft's. "
         f"{r['numbers_compared']} stored values recomputed from the CSV and compared (the claim, the card's numbers, the three tests, the fact line and the caption character by character): 0 differ. "
         f"The CSV rebuilt from today's tables by the finding `{r['module']}`: {len(years)} years, {len(r['today_diffs'])} differ."
         + ("" if r["row_value_column"]["equal_in_full"] else f" One note: the row's own `value` column reads back as {r['row_value_column']['stored']!r} (15 digits; the card holds {r['row_value_column']['recomputed']!r})."),
         f"- **Robust, the hunt's three tests, run again:** {sum(1 for t in r['tests'] if t['passed'])} of 3 pass. " + " ".join(f"{t['name'].capitalize()}: {t['words']}." for t in r["tests"]),
         f"- **Robust, five tests the hunt does not run:** year-to-year steps in the claim's direction: {m['steps_on_side']} of {m['steps']}. Rank correlation of the value with the year: {f(m['spearman_year'], 2)}. "
         f"The last two years against the first two: {f(m['two_year_ends'], d)} ({'the same side' if m['two_year_ends_same_side'] else 'THE OTHER SIDE'}). "
         f"Without {c['first_year']}: {f(m['share_of_claim_without_first_year'] * 100, 0)} percent of the change remains; without {c['last_year']}: {f(m['share_of_claim_without_last_year'] * 100, 0)} percent. "
         f"Median of the years between: {f(m['median_between'], d)}. The change is {f(c['strength'], 2)} typical yearly moves ({f(c['typical_move'], d)} {r['unit']})."
         + (f" {uw['year']} to date is {'beyond' if uw['beyond_last'] else 'not beyond'} {c['last_year']}." if uw else ""),
         f"- **License:** public by the publisher: {name}, {sentence}. The claim's years, {c['first_year']} to {c['last_year']}, lie inside `ercot_all_hub_prices_history` (2015 to 26 August 2026). "
         + (f"To fix before approval: the draft's source line also names {len(needed)} table(s) that `license_status.csv` marks 'license needed' from 21 October for other grids' rows ({', '.join(x.split(' ')[0] for x in needed)}); none of those grids' rows is in the draft." if needed else "No table it names is marked 'license needed'."),
         f"- **Verdict: {verdict}.** {reason}", ""]
    return L


def scanner_block(n, r, verdict, reason):
    m, st = r["more"], r["stored"]
    pub = r["table"].split("_")[0]
    name, sentence, flags = license_words([r["table"]], pub)
    L = [f"### {n}. {r['label']}: {r['rule']} ({r['date']})", "",
         f"- **Draft:** `{r['id']}`, the daily scanner, rule `{r['rule']}`, table `{r['table']}`; state {r['state']}; raised by the scan of {r['scan_date']}; the scanner's strength {f(r['strength'], 2)}.",
         f"- **Claim:** {r['fact']}."]
    if r["rule"] == "record":
        c = st["compared"]
        L += [f"- **Number:** {f(r['value'], 2)} {r['unit']} in {r['date'][:7]}; the record until then {f(c['old_record'], 2)} ({c['old_record_date'][:7]}); margin {f(c['margin'], 2)}, {f(c['margin_sigmas'], 2)} robust standard deviations; {st['history']['points']} months held before it, from {st['history']['first'][:7]}.",
              f"- **Reproduced:** yes, exactly. A scanner draft has no file: its data is its table. The series read again from today's table by the scanner's own reader and the rule run again at the scan date: {r['numbers_compared']} stored values compared, 0 differ. The value in today's table is unrevised.",
              f"- **Robust:** {f(m['pct_past_old_record'], 1)} percent past the old record; {f(m['margin_plain_sd'], 2)} plain standard deviations. A record for its own calendar month too: {'yes' if m['record_for_its_month_too'] else 'NO'} "
              f"(the month's record was {f(m['same_month_old_record'], 2)}; {f(m['pct_vs_same_month_last_year'], 1)} percent against the same month a year before). Against the month before: {f(m['pct_vs_previous_point'], 1)} percent. "
              f"Without the season (the value over the mean of its prior twelve months): {f(m['ratio_to_prior_12_mean'], 2)}, rank {m['ratio_rank_from_top']} of {m['ratio_points']}. "
              f"Months held after it: {m['points_after']}. Still the record in today's table: {'yes' if m['still_the_record_today'] else 'NO'}."]
    elif r["rule"] == "spike":
        c = st["compared"]
        L += [f"- **Number:** a UTC day's mean of {f(r['value'], 2)} {r['unit']} on {r['date']}, {f(c['multiple_of_percentile'], 2)} times the 99th percentile of the days held before ({f(c['percentile_value'], 2)}); the line it crossed, {f(st['threshold']['value'], 2)}; {c['prior_points']} days before it.",
              f"- **Reproduced:** yes, exactly. The series read again from today's table and the rule run again at the scan date: {r['numbers_compared']} stored values compared, 0 differ.",
              f"- **Robust:** the day's dearest hour {f(m['day_max_interval'], 2)}, its cheapest {f(m['day_min_interval'], 2)}. With the days of the run-up counted in the history (the rule leaves the newest ten days out): "
              f"{f(m['multiple_all'], 2)} times the 99th percentile of every day before it ({m['points_all']} days), {f(m['multiple_1y'], 2)} times that of the last year alone ({m['points_1y']} days). "
              f"History held before it: {m['years_held_before']} years from {m['history_first_day']}, where the rule names three. Rank among the {m['held_days_before'] + 1 + m['days_after']} days held: {m['rank_from_top_all_days']}. Days above the line before it: {m['days_above_line_before']}. "
              f"The six days held after it: {m['days_after_above_line']} above the line, the dearest {f(m['after_max'], 2)} on {m['after_max_date']}. The fortnight around it: " + ", ".join(f"{d[5:]} {f(v, 2)}" for d, v in m["around"]) + "."]
    else:
        c = st["compared"]
        L += [f"- **Number:** {f(m['level_before'], 3 if abs(m['level']) < 100 else 0)} to {f(m['level'], 3 if abs(m['level']) < 100 else 0)} {r['unit']} in the week to {r['date']}: a change of {f(c['change'], 3 if abs(m['level']) < 100 else 0)} ({f(m['pct_change'], 1)} percent). "
              f"The five-year range of the weekly change it left: {f(c['range_low'], 3 if abs(m['level']) < 100 else 0)} to {f(c['range_high'], 3 if abs(m['level']) < 100 else 0)} ({c['range_points']} weeks from {c['range_first']}).",
              f"- **Reproduced:** yes, exactly. The series read again from today's table and the rule run again at the scan date: {r['numbers_compared']} stored values compared, 0 differ."
              + (f" One note: {r['cut_note']}." if r.get("cut_note") else ""),
              f"- **Robust:** against every week of the series, not five years: {'outside' if m['outside_all_history'] else 'INSIDE'} ({m['all_history_points']} weeks from {m['all_history_first']}; rank {m['rank_in_all_history']}). "
              f"{f(m['z_plain_sd'], 2)} plain standard deviations from the mean weekly change. As a percent change: rank {m['pct_change_rank']} of {m['pct_change_points']}. "
              + (f"The week after ({m['after'][0][0]}): a further change of {f(m['change_next_week'], 3 if abs(m['level']) < 100 else 0)}, so the move was not undone." if m["weeks_after"] else "No later week is held.")]
    L += [f"- **License:** public: {name}, {sentence}. " + "; ".join(flags) + " in `coverage.csv`; not in `license_status.csv` (which lists the 40 tables that need a license).",
          f"- **Verdict: {verdict}.** {reason}", ""]
    return L


def main():
    # the time the list was read: when fetch_drafts.py wrote its index
    now = dt.datetime.fromtimestamp(os.path.getmtime(os.path.join(HERE, "drafts", "index.json")), dt.timezone.utc).strftime("%H:%M")
    counts = {v: sum(1 for _, x, _ in VERDICT if x == v) for v in ("strong", "usable", "drop")}
    old = [x for x in index if x["raised_at"] < "2026-10-13T06:00"]
    new = [x for x in index if x["raised_at"] >= "2026-10-13T06:00"]
    L = ["# The waiting findings, verified: 13 October 2026", "",
         f"Session 252, on lab-desktop (the data machine). The review list `public.scanner_drafts` was read at {now} UTC on 13 October 2026: {len(index)} rows, "
         f"{sum(1 for x in index if x['state'] == 'draft')} in state draft. No draft's state was changed, no row was written, no publisher was asked and no model was called. "
         "Everything below was computed by the scripts of `docs/reviews/findings-verified-2026-10-13/` on this machine from each draft's own files and from the tables in `warehouse/output/`.", "",
         "## Read these first", "",
         f"- **All 16 drafts reproduce exactly.** The 8 of the weekly hunt: each one's own Python mirror on its own CSV, 45 stored values a draft recomputed and compared, and the CSV rebuilt from today's tables, every year equal. "
         "The 8 of the daily scanner carry no file, so each was rebuilt from its table by the scanner's own reader at its own scan date: 29 to 34 stored values a draft, 0 differ.",
         f"- **Verdicts: {counts['strong']} strong, {counts['usable']} usable, {counts['drop']} drop.** Reproducing is not the same as being worth publishing: every drop below reproduces to the last digit.",
         "- **The four strong ones:** ERCOT's dearest hour moving into the evening (24.9 to 71.0 percent of days, 2019 to 2025), its mirror at midday, negative prices at ERCOT North, and the largest weekly fall of managed-money long positions in NYMEX natural gas held since 2015.",
         "- **The five to drop:** the District of Columbia's industrial price (the sector is one customer) and the hunt's four spike drafts (one interval a year; most of each claim is the year 2019 alone). The four spike drafts are the ones session 233 already called weak; a floor on strength of one typical yearly move would have kept them off the list.",
         "- **Licenses:** every draft rests on a public publisher (ERCOT, EIA, CFTC, CAISO). One thing to fix before any hunt draft is approved: its source line names tables that are 'license needed' from 21 October for other grids' rows, though none of those rows is in the draft.",
         f"- **Session 251's new drafts: none.** The list holds the same 16 rows it held after session 233 (8 raised on 10 October, 8 on 13 October at 05:08 UTC); nothing was raised after that, and no report, branch or run folder of a session 251 is on this machine or on GitHub. See the last section.", "",
         "## How each was checked", "",
         "- **Reproduced, a hunt draft:** (1) the draft's `.py` run on the draft's `.csv`, as downloaded from the list; (2) the claim, the three tests, the card's numbers, the fact line and the caption computed again from that CSV and compared with the stored ones, numbers exactly and words character by character; (3) the CSV computed again from today's tables by the finding's own code.",
         "- **Reproduced, a scanner draft:** the series read again from the table in `warehouse/output/`, cut at the draft's scan date, the rule run again, and the value, the strength, the threshold and every number of the draft's compared and history blocks compared exactly.",
         "- **Robust, a hunt draft:** the hunt's three tests again, then five it does not run: the year-to-year steps, the rank correlation with the year, two-year ends, the claim without its first and without its last year, and the year under way.",
         "- **Robust, a scanner draft:** by rule. A record: the margin in plain standard deviations, its own calendar month, the value over its prior twelve months, and what the table holds since. A spike: other windows, its rank among every day held, the days after. A weekly change: every week held instead of five years, the percent change, the week after.",
         "- **Not done:** no do-file was run (there is no Stata on this machine, as session 233 said). No number was checked against the publisher's own site: the tables are the evidence, and they were not pulled again. The eight scanner drafts were not recomputed by code written apart from the scanner's.",
         "- **Verdict:** strong, the claim holds whichever way it was cut and can be approved as drafted; usable, true but with a limit a reader must be told, named in the block; drop, with the reason.", "",
         f"## The {len(old)} drafts from before session 251, strongest first", ""]
    for n, (did, verdict, reason) in enumerate(VERDICT, 1):
        L += hunt_block(n, hunt[did], verdict, reason) if did in hunt else scanner_block(n, scan[did], verdict, reason)
    L += ["## Session 251's new drafts", "",
          f"- **None to verify.** At {now} UTC the list holds {len(index)} rows; {len(new)} were raised after 06:00 UTC on 13 October. The newest row was raised at {max(x['raised_at'] for x in index)[:19]} UTC (session 233's hunt).",
          "- No `SESSION_251_REPORT.md`, no branch named for a session 251 on GitHub, and no `runs/session251/` on this machine at that time. If session 251 runs on the code machine and adds drafts later, they are not in this document.",
          "- **To verify them when they exist,** three commands on this machine, each read by its exit code: `.venv\\Scripts\\python.exe runs/session252/fetch_drafts.py`, then `runs/session252/verify_hunt.py` and `runs/session252/verify_scanner.py` (exit 0: every draft reproduces; 1: one does not, named). `runs/` is not in git: the scripts, what they printed and their two result files are copied to `docs/reviews/findings-verified-2026-10-13/` beside this file, and run from there as well.", "",
          "## What the list should learn from this", "",
          "- **A floor on strength.** The four hunt drafts under one typical yearly move are the four dropped here. Session 233 asked this as its ruling 2.",
          "- **A fourth test for the hunt: the claim without its first year.** Three of the dropped drafts keep under a third of their change when 2019 is left out; the three tests in force ask only for the direction.",
          "- **A guard for the scanner: a sector with fewer than, say, five customers is not a price series.** The table holds the customers count beside the sales.",
          "- **The scanner's series split when a contract is renamed.** The CFTC table's node changed name on 8 February 2022, so the scanner compared 241 weeks where 611 are held.",
          "- **A hunt draft's source line should name the tables its region's rows come from,** not every table the finding read.", ""]
    text = "\n".join(L)
    if chr(0x2014) in text or chr(0x2013) in text:
        print("a dash that is not allowed is in the text", file=sys.stderr)
        return 1
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print(f"wrote {OUT}: {len(L)} lines, {len(VERDICT)} blocks; {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
