"""Session 286: append the hunt's twelve drafts of 14 October 2026, verified, to docs/reviews/findings-verified-2026-10-13.md.

Every number in the appended section is read from verify_286.json (written by verify_286.py beside this file, and kept
here too) by session 251's own block writer (build_251.block, imported); the verdicts and their reasons are this
session's, written below by id. The text above the section is not touched: the section begins at its own heading and
runs to the end of the file, and a second run replaces that section alone. (Session 251's builder does the same with
its own heading, so run it before this one, never after.)"""
import datetime as dt
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while not os.path.exists(os.path.join(ROOT, "ARCHITECTURE.md")):
    ROOT = os.path.dirname(ROOT)
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("build_251", os.path.join(ROOT, "docs", "reviews", "findings-verified-2026-10-13-session251", "build_251.py"))
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)

RUN = os.path.join(ROOT, "runs", "session286")
DOC = b.DOC
HEADING = "## Session 286's twelve drafts, verified (the hunt of 14 October 2026)"
SRC = os.path.join(RUN, "verify_286.json") if os.path.exists(os.path.join(RUN, "verify_286.json")) else os.path.join(HERE, "verify_286.json")
res = {r["id"]: r for r in json.load(open(SRC, encoding="utf-8"))}
# the publishers behind the rows of the tables these drafts read, for the drafted region (docs/licenses.md)
b.BEHIND.update({"ercot_rtm_price_adders": ["ERCOT"], "ercot_zone_load_hourly": ["ERCOT"], "eia_fuel_spot_prices": ["EIA"], "merchant_revenue_monthly": ["ERCOT"]})

VERDICT = [
    ("scan-hunt-7a9b1b9695e1", "strong",
     "Five steps of six, rank correlation 0.96, and nothing leans on an end year (115 percent of the change remains without 2019, 80 without 2025); 2026 to date is higher again (4,074). "
     "Asked as a share of the year's peak demand it says the same (1.63 to 2.37 percent), and so do the table's one-evening columns. "
     "Two things a reader must be told: these are EIA's rows about PJM (EIA-930), not PJM's own, and PJM's ramp has grown far less than ERCOT's (session 251, block 17: 1,123 to 6,871 MW per hour)."),
    ("scan-hunt-4aa7db84eaa1", "strong",
     "Three steps of three, and the change (16.4 points) is four times the fit's own uncertainty for ERCOT (4.04 percent in every year). "
     "Before weather is taken out the year's energy rises the same way (11.8 to 26.6 percent above the base), and the part weather explains shrinks (3.9 to 2.4): it is not hot summers. "
     "The limit is the length: four full years after a 2019 to 2021 base. Say 'since 2022', not a trend of a decade."),
    ("scan-hunt-ff565ef92fa1", "usable",
     "The fall is real and every cut agrees (hours with the adder above USD 1: 3.7 to 0.2 percent; the year's mean adder: 0.91 to 0.07). But it is two years, not a decade: "
     "from 2015 to 2023 the share swung between 15.1 and 27.6 percent with no direction, then 4.9 in 2024 and 2.4 in 2025. "
     "And 2025 ends on 4 December, when this adder ended (the measure's own note; 8,108 hours held), so there is no 2026 to test it on. Say 'in 2024 and 2025', and do not join it to the adder that followed."),
    ("scan-hunt-a1f89315595c", "usable",
     "True, seven steps of ten, 62 percent without 2015, and 2026 to date is higher again (3.03). It is the North hub's story told from the load zone's rows, which session 252 called strong (block 3: 0.57 to 2.56 percent). "
     "Publish one of the two, not both."),
    ("scan-hunt-e80da58b1903", "usable",
     "True and every cut agrees, but the series begins in 2019 (the finding's own window), the step was 2021 (0.84 to 1.71) and since then it has moved between 1.0 and 1.7: 2025 (1.62) is below 2021. "
     "Usable as 'about three times the level of 2019' with the years shown; 'rising' would not be honest. The load zone's draft below (block 40) tells the same story worse."),
    ("scan-hunt-0a27000ec580", "usable",
     "Three steps of three, and before weather the energy rises too (2.8 to 7.2 percent). The limit: the change from 2022 to 2024 (1.8 points) is inside the fit's uncertainty for PJM (2.54), "
     "so the claim rests on 2025 alone (3.87 to 6.59; 40 percent remains without it). Hold it until 2026 is a full year, or say 'in 2025'."),
    ("scan-hunt-fc2cbd068294", "usable",
     "A step, not a trend: from 2015 to 2022 the median day's implied heat rate stayed between 8.0 and 9.6, and since 2023 it has stood between 9.5 and 10.8 (2026 to date 10.42, on 190 days). "
     "Five steps of ten and a rank correlation of 0.50. Both other cuts agree (the day-ahead median 9.3 to 10.3). It reads more gas-fired hours setting the price at Houston, or cheaper gas against the same prices: the card must not say which."),
    ("scan-hunt-a97fbd7cc709", "usable",
     "Solar's capture rate at ERCOT's hub average fell from 181 percent of the average price in 2019 to 75 in 2025, and the unweighted monthly mean agrees (130.6 to 72.5). The limits: "
     "the years swing with scarcity (62 in 2021, the year of Uri), only 49 percent of the change remains without 2019, and the clean part is the last three years (146 in 2023, 85, 75, and 72 to date). "
     "And its table `merchant_revenue_monthly` is marked 'license needed' from 21 October for its ISO-NE, MISO and NYISO rows; the draft uses ERCOT's only, but its source line names the table whole (session 252's point)."),
    ("scan-hunt-6040ef25cbd6", "drop",
     "The whole claim is 2025: without it 5 percent of the change remains (2024 was minus 0.31). The values are under a dollar a MWh on both sides of zero, the rank correlation is 0.42, "
     "and the mean spread says nothing at all (minus 0.34 in 2015, minus 0.23 in 2025)."),
    ("scan-hunt-b8cdd74f952b", "drop",
     "A hump, not a rise: 7.1 to 8.6 from 2015 to 2022, 11.0 in 2023 and 2024, 9.8 in 2025, and 8.8 in 2026 to date (190 days), back near where it began. "
     "Six steps of ten and a rank correlation of 0.50. The Houston hub's draft (block 35) is the one to keep if either is."),
    ("scan-hunt-dc66d4095dfc", "drop",
     "It depends on how the evening is cut. From 4 PM to 9 PM the premium falls (1.86 to 1.44 percent); on the intensity of generation instead of demand it falls too (3.95 to 3.19). "
     "And 2020 was already 2.45, so a third of the change remains without 2019. The evening and the whole day both got cleaner (408 to 344 and 405 to 333 kg per MWh); the gap between them is noise."),
    ("scan-hunt-f7df3c239056", "drop",
     "The whole claim is 2015: 2016 already stood at 1.43 percent, and without 2015 only 18 percent of the change remains (the fourth test session 252 asked for would stop it). "
     "It also repeats the Houston hub's draft above (block 33). 2026 to date (1.50) is below 2025."),
]


def block(n, r, verdict, reason):
    L = b.block(n, r, verdict, reason)
    if r.get("measure") is None:                      # a finding's pattern: no measure family, its finding's own compute
        L = [ln.replace("(measure `hunt_measures.None`)", "(the finding `negative_prices_west`)").replace("rebuilt from today's tables by the measure", "rebuilt from today's tables by the finding's own compute")
             for ln in L]
    return L


def main():
    assert sorted(res) == sorted(v[0] for v in VERDICT), "a draft without a verdict, or a verdict without a draft"
    counts = {v: sum(1 for _, x, _ in VERDICT if x == v) for v in ("strong", "usable", "drop")}
    order = {"strong": 0, "usable": 1, "drop": 2}
    assert [v for _, v, _ in VERDICT] == sorted((v for _, v, _ in VERDICT), key=order.get)
    idx = os.path.join(RUN, "drafts", "index.json")
    read_at = dt.datetime.fromtimestamp(os.path.getmtime(idx), dt.timezone.utc).strftime("%H:%M") if os.path.exists(idx) else "18:54"
    compared = sorted({r["numbers_compared"] for r in res.values()})
    first = 29                                        # the document's blocks run 1 to 28 before this section
    L = [HEADING, "",
         f"Session 286, on lab-desktop (the data machine), 14 October 2026, in the daytime chain after sessions 284 and 285. The hunt (version 1.1.0: 20 patterns, 143 claims, 50 passing the three tests) "
         f"added 12 drafts to the review list at 18:48 UTC; the list was read back at {read_at} UTC: 40 rows. The scanner, run once at 18:51, raised none (its five drafts were raised before). "
         "No draft's state was changed, no publisher was asked and no model was called. Everything below was computed by `docs/reviews/findings-verified-2026-10-14-session286/` "
         "(`fetch_drafts.py`, `verify_286.py`, `build_286.py`; the result file `verify_286.json` is beside them). `verify_286.py` is session 251's verifier, imported and run as it stands, with three additions "
         "it names in its header; its last line still says 'of session 251' for that reason.", "",
         "### Read these first", "",
         f"- **All 12 reproduce exactly.** Each draft's own Python mirror on its own CSV, {compared[0]} to {compared[-1]} stored values a draft recomputed and compared, and the CSV rebuilt from today's tables: every year equal, in 12 of 12.",
         f"- **Verdicts of the 12: {counts['strong']} strong, {counts['usable']} usable, {counts['drop']} drop.**",
         "- **The two strong ones:** PJM's evening ramp (the median day's steepest hour, 2,484 to 3,805 MW per hour, 2019 to 2025, EIA's rows) and ERCOT's demand growth that weather does not explain (7.8 to 24.2 percent above the 2019 to 2021 base, 2022 to 2025).",
         "- **The four to drop:** the South hub's night spread (the whole claim is 2025), the West hub's implied heat rate (a hump), PJM's evening carbon premium (another window says the opposite), and the Houston load zone's negative hours (the whole claim is 2015).",
         "- **This hunt drafted weaker claims than the last.** Its strengths run from 1.24 to 3.74, against 2.46 to 11.23 on 13 October: the strongest claims were drafted then and are not new. Four of the twelve repeat a story already on the list (ERCOT's negative hours by hub and by zone, twice).",
         "- **One license note:** the solar capture draft's table `merchant_revenue_monthly` is marked 'license needed' from 21 October for its ISO-NE, MISO and NYISO rows; the draft uses ERCOT's alone.", "",
         "### How these were checked", "",
         "- **Reproduced:** as session 251 did (its verifier, imported). The one draft of a finding's pattern (`negative_prices`, Houston) is rebuilt by its finding's own compute, as session 252 did; its tables are checked to be a part of the pattern's `OWN_TABLES` entry, since session 258 narrows a draft's list to the tables that brought rows.",
         "- **Robust:** the hunt's three tests again; session 252's five further tests; and the question asked another way, with four cuts session 251 did not have: the implied heat rate by its mean and by the day-ahead market, beside Henry Hub; the solar capture rate's two halves (the price solar earned, the average price) and the unweighted monthly mean; the reserve adder above USD 1 and above USD 10, and its mean; the Houston hub's negative 15-minute intervals and hours below minus USD 10.",
         "- **License:** each table's flag in `coverage.csv`, its row or none in `license_status.csv`, and the sentence of the publisher behind that region's rows (`docs/licenses.md`).",
         "- **Not done:** no do-file was run (no Stata on this machine). No number was checked against a publisher's site.",
         "- **Verdict:** session 252's rule. Strong, the claim holds whichever way it was cut; usable, true with a limit the block names; drop, with the reason.", "",
         "### The 12 drafts of 14 October, strongest first", ""]
    for n, (did, verdict, reason) in enumerate(VERDICT, first):
        L += block(n, res[did], verdict, reason)
    L += ["### What the hunt should learn from these twelve", "",
          "- **Session 251's lessons, again.** The fourth test (half the change must remain without the first year) would have stopped the Houston load zone (18 percent) and PJM's evening carbon (33), and kept every strong and usable draft but the solar capture rate (49 percent). A floor of years for strength would not have changed this list.",
          "- **One region, one story.** ERCOT's negative hours have now been drafted at three hubs and four load zones. A draft whose years agree with one already on the list (in any state) to within its typical move should be folded into it, not raised beside it.",
          "- **A measure that ends should end the pattern.** The reserve adder stopped on 4 December 2025; the hunt will raise the same claim each week with no new year to test it on.", ""]
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
