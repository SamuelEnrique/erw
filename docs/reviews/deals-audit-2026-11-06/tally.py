"""Session 2231: the fault classes of the sample, counted, with up to three examples each (the readers' notes)."""
import pandas as pd
SP = "docs/reviews/deals-audit-2026-11-06/"
d = pd.read_csv(SP + "sample_deals.csv", dtype=str).fillna("")
f = pd.read_csv(SP + "sample_facilities.csv", dtype=str).fillna("")
print("deals graded", len(d), "facilities graded", len(f))
D = [("not a deal", d.not_a_deal == "1"),
     ("party wrong", d.party == "wrong"), ("party incomplete", d.party == "incomplete"),
     ("party unnamed (a description, not a name)", d.party == "unnamed"),
     ("kind wrong or vocabulary gap", (d.kind_ok == "0") & (d.not_a_deal != "1")),
     ("MW missed", d.mw == "missed"), ("MW wrong", d.mw.isin(["wrong", "invented"])),
     ("MWh missed or wrong", d.mwh.isin(["missed", "wrong", "invented"])),
     ("USD missed", d.usd == "missed"), ("USD wrong (another sum, a valuation, a currency)", d.usd.isin(["wrong", "invented"])),
     ("price missed", d.price == "missed"), ("price wrong (not an energy price)", d.price.isin(["wrong", "invented"])),
     ("term missed or wrong", d.term.isin(["missed", "wrong", "invented"])),
     ("status missed", d.status == "missed"), ("status wrong or unsupported", d.status.isin(["wrong", "unsupported"])),
     ("AI-power tag wrong", d.ai_power == "wrong"),
     ("place missed", d.place == "missed"), ("place wrong", d.place == "wrong"),
     ("confidence too high", d.confidence_fit == "too_high"), ("confidence too low", d.confidence_fit == "too_low")]
F = [("not a facility", f.not_a_facility == "1"),
     ("operator missed", f.operator == "missed"), ("operator wrong", f.operator == "wrong"),
     ("site missed or wrong", f.site.isin(["missed", "wrong"])), ("state missed or wrong", f.state.isin(["missed", "wrong"])),
     ("MW missed or wrong", f.mw.isin(["missed", "wrong", "invented"])),
     ("MW basis unstated (IT or total)", f.mw_basis == "unstated"),
     ("status missed", f.status == "missed"), ("status wrong", f.status.isin(["wrong", "unsupported"])),
     ("power source missed or wrong", f.power_source.isin(["missed", "wrong"])),
     ("utility missed or wrong", f.utility.isin(["missed", "wrong"])),
     ("timeline missed", f.timeline == "missed"),
     ("confidence too high", f.confidence_fit == "too_high"), ("confidence too low", f.confidence_fit == "too_low")]
for title, df, classes, n in [("deals", d, D, len(d)), ("facilities", f, F, len(f))]:
    print(f"\n## {title}")
    for i, (name, m) in enumerate(classes, 1):
        rows = df[m]
        ex = "; ".join(f"{r.n}: {r.note}" for r in rows.head(3).itertuples())
        print(f"{i}|{name}|{m.sum()}|{100*m.sum()/n:.0f}|{ex}")
