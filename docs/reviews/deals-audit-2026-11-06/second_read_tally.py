"""Session 2249: each fault class's count before (the stored rows, session 2231) and after (the new extraction on the same
stories), on the same 106 deals and 60 facilities."""
import pandas as pd
SP = "docs/reviews/deals-audit-2026-11-06/"
A = "docs/reviews/deals-audit-2026-11-06/"
b = pd.read_csv(A + "sample_deals.csv", dtype=str).fillna("")
a = pd.read_csv(SP + "second_read_deals.csv", dtype=str).fillna("")
fb = pd.read_csv(A + "sample_facilities.csv", dtype=str).fillna("")
fa = pd.read_csv(SP + "second_read_facilities.csv", dtype=str).fillna("")
present = a["row"] == "present"
D = [
    ("Not a deal, and a row kept", b.not_a_deal == "1", (a.not_a_deal == "1") & present),
    ("A stated deal with no row", pd.Series(False, index=b.index), (a.not_a_deal != "1") & ~present),
    ("Place missed", b.place == "missed", a.place == "missed"),
    ("Status missed", b.status == "missed", a.status == "missed"),
    ("Status wrong or unsupported", b.status.isin(["wrong", "unsupported"]), a.status.isin(["wrong", "unsupported"])),
    ("Kind wrong or no word for it", (b.kind_ok == "0") & (b.not_a_deal != "1"), (a.kind_ok == "0") & present & (a.not_a_deal != "1")),
    ("A party a description", b.party == "unnamed", a.party == "unnamed"),
    ("A party wrong", b.party == "wrong", a.party == "wrong"),
    ("A party missed or incomplete", b.party == "incomplete", a.party.isin(["incomplete"])),
    ("AI-power tag wrong", b.ai_power == "wrong", a.ai_power == "wrong"),
    ("MW missed", b.mw == "missed", a.mw == "missed"),
    ("A figure wrong or invented", b[["mw", "mwh", "usd", "price", "term"]].isin(["wrong", "invented"]).any(axis=1),
     a[["mw", "mwh", "usd", "price", "term"]].isin(["wrong", "invented"]).any(axis=1)),
    ("USD missed", b.usd == "missed", a.usd == "missed"),
    ("Term missed", b.term == "missed", a.term == "missed"),
    ("Confidence too low", b.confidence_fit == "too_low", a.confidence_fit == "too_low"),
    ("Confidence too high", b.confidence_fit == "too_high", a.confidence_fit == "too_high"),
]
fpres = fa["row"] == "present"
F = [
    ("Not a facility, and a row kept", fb.not_a_facility == "1", (fa.not_a_facility == "1") & fpres),
    ("A stated facility with no row", pd.Series(False, index=fb.index), (fa.not_a_facility != "1") & ~fpres),
    ("Two places in one row", pd.Series(False, index=fb.index), fa.two_places == "1"),
    ("MW basis unstated or wrong", fb.mw_basis == "unstated", fa.mw_basis == "wrong"),
    ("Status missed", fb.status == "missed", fa.status == "missed"),
    ("Status wrong", fb.status.isin(["wrong", "unsupported"]), fa.status.isin(["wrong", "unsupported"])),
    ("State missed or wrong", fb.state.isin(["missed", "wrong"]), fa.state.isin(["missed", "wrong"])),
    ("Operator missed or wrong", fb.operator.isin(["missed", "wrong"]), fa.operator.isin(["missed", "wrong"]) & fpres),
    ("Site missed", fb.site.isin(["missed", "wrong"]), fa.site.isin(["missed", "wrong"])),
    ("Power source missed or wrong", fb.power_source.isin(["missed", "wrong"]), fa.power.isin(["missed", "wrong"])),
    ("Timeline missed or wrong", fb.timeline.isin(["missed"]), fa.timeline.isin(["missed", "wrong"])),
    ("Confidence too low", fb.confidence_fit == "too_low", fa.confidence_fit == "too_low"),
]
def ex(df, m):
    return "; ".join(f"{r.n}: {r.note}" for r in df[m].head(2).itertuples())
for title, rows in (("deals (106)", D), ("facilities (60)", F)):
    print(f"\n{title}")
    for name, mb, ma in rows:
        print(f"|{name}|{int(mb.sum())}|{int(ma.sum())}|{ex(a if title.startswith('deals') else fa, ma)[:260]}|")
