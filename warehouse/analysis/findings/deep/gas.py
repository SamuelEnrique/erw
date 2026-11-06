#!/usr/bin/env python3
"""The findings hunt over the whole warehouse (chain 164), family "gas": session 3008.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-06.md. Public sources:

    gas_balance_weekly                  the ERW's gas balance: the monthly US consumption, dry production, power burn and
                                        LNG exports (EIA), and each storage region's working gas by week against its
                                        five years (min, max)
    eia_gas_production_state_monthly    EIA's production by state (MMcf): marketed, gross withdrawals, shale, vented and
                                        flared; no US total, so the US is the sum of the states, "other states" and the
                                        federal offshore
    eia_gas_consumption_state_monthly   EIA's deliveries by state and sector (MMcf)
    eia_gas_trade_country_monthly       EIA's imports and exports by country (MMcf)

Most candidates are a ratio of two sums over a year's months: the numerator's rows over the denominator's, with the
year's count of the numerator's months as its observations (a year missing a month is not whole). RATIO below is that
one rule, and the reproduction scripts follow it line for line.

    python warehouse/analysis/findings/deep/gas.py --dry-run
    python warehouse/analysis/findings/deep/gas.py --load
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)
import builder  # noqa: E402
import findings_common as common  # noqa: E402
import generation  # noqa: E402
import hunt_measures as hm  # noqa: E402

FAMILY = "gas"
STATES = generation.STATES
MIN_GROSS_MMCF = 100000.0           # session 3008: flaring is hunted in states with at least 100 Bcf of gross withdrawals a year
SECTORS = ["consumption_residential", "consumption_commercial", "consumption_industrial", "consumption_electric_power"]
REGIONS = {"gas_storage:east": "the East storage region", "gas_storage:midwest": "the Midwest storage region", "gas_storage:mountain": "the Mountain storage region",
           "gas_storage:pacific": "the Pacific storage region", "gas_storage:salt": "the South Central salt storage region",
           "gas_storage:nonsalt": "the South Central non-salt storage region", "gas_storage:lower48": "the lower 48 states' storage"}


def ratio(d, num_re, num_vars, den_re, den_vars, scale=100.0):
    """{year: (sum of the numerator's rows * scale / sum of the denominator's rows, the numerator's months)}; d holds
    entity, variable, ts_utc and a numeric value. A year whose denominator is zero is left out."""
    d = d.assign(year=d["ts_utc"].str[:4].astype(int))
    num = d[d["entity"].str.contains(num_re, regex=True) & d["variable"].isin(num_vars)]
    den = d[d["entity"].str.contains(den_re, regex=True) & d["variable"].isin(den_vars)] if den_re else None
    out = {}
    for y, s in num.groupby("year"):
        n = s["ts_utc"].nunique()
        if den is None:
            out[int(y)] = (float(s["value"].sum() * scale), n)
            continue
        b = den.loc[den["year"] == y, "value"].sum()
        if b != 0:
            out[int(y)] = (float(s["value"].sum() * scale / b), n)
    return out


def _table(name, in_dir, variables):
    d = hm.series(name, in_dir, variables=variables)
    return d[["entity", "variable", "ts_utc", "value"]]


SPECS = {}


def spec(name, table, num_re, num_vars, den_re, den_vars, scale=100.0):
    SPECS[name] = (table, num_re, num_vars, den_re, den_vars, scale)


def _run(name, region, words, in_dir, **fmt):
    table, num_re, num_vars, den_re, den_vars, scale = SPECS[name]
    num_re, den_re = num_re.format(**fmt), (den_re.format(**fmt) if den_re else den_re)
    d = _table(table, in_dir, list(set(num_vars) | set(den_vars or [])))
    return [hm._row(region, words, y, v, n) for y, (v, n) in ratio(d, num_re, num_vars, den_re, den_vars, scale).items()]


spec("lng_share", "gas_balance_weekly", r"^gas_balance:US$", ["lng_exports"], r"^gas_balance:US$", ["dry_production"])
spec("power_share", "gas_balance_weekly", r"^gas_balance:US$", ["power_burn"], r"^gas_balance:US$", ["consumption"])
# session 3008: the table holds a US row (NUS) beside the states; it is the denominator, never summed with them
spec("state_production_share", "eia_gas_production_state_monthly", r"^eia_gas_production:S{st}:", ["marketed_production"], r"^eia_gas_production:NUS:", ["marketed_production"])
spec("flared_share", "eia_gas_production_state_monthly", r"^eia_gas_production:S{st}:", ["vented_flared"], r"^eia_gas_production:S{st}:", ["gross_withdrawals"])
spec("shale_share", "eia_gas_production_state_monthly", r"^eia_gas_production:NUS:", ["shale_withdrawals"], r"^eia_gas_production:NUS:", ["gross_withdrawals"])
spec("state_power_share", "eia_gas_consumption_state_monthly", r":S{st}$", ["consumption_electric_power"], r":S{st}$", SECTORS)
spec("mexico_exports", "eia_gas_trade_country_monthly", r"^eia_gas_trade:N9132MX2$", ["volume"], None, None, 1.0)


def lng_share(in_dir=None):
    """LNG exports as a percent of US dry gas production over the year."""
    return {"rows": _run("lng_share", "us_lng", "the United States", in_dir), "tables": {"us_lng": ["gas_balance_weekly"]}}


def power_share(in_dir=None):
    """Gas burned for power as a percent of US gas consumption over the year."""
    return {"rows": _run("power_share", "us_power_burn", "the United States", in_dir), "tables": {"us_power_burn": ["gas_balance_weekly"]}}


def _states(name, prefix, in_dir):
    rows, tables = [], {}
    for st in STATES:
        if st in ("US", "DC"):
            continue
        r = _run(name, f"{prefix}_{st}", STATES[st], in_dir, st=st)
        if r:
            rows += r
            tables[f"{prefix}_{st}"] = [SPECS[name][0]]
    return {"rows": rows, "tables": tables}


def state_production_share(in_dir=None):
    """A state's marketed gas production as a percent of EIA's US total."""
    return _states("state_production_share", "prod", in_dir)


def flared_share(in_dir=None):
    """A state's vented and flared gas as a percent of its gross withdrawals, for the states with at least 100 Bcf of
    gross withdrawals in their last whole year (a small producer's share swings on a few wells)."""
    got = _states("flared_share", "flare", in_dir)
    d = _table("eia_gas_production_state_monthly", in_dir, ["gross_withdrawals"])
    d = d.assign(year=d["ts_utc"].str[:4].astype(int), st=d["entity"].str.split(":").str[1].str[1:])
    last = d.groupby(["st", "year"]).agg(v=("value", "sum"), n=("ts_utc", "nunique")).reset_index()
    last = last[last["n"] == 12].sort_values("year").groupby("st").tail(1)
    big = {f"flare_{s}" for s, v in zip(last["st"], last["v"]) if v >= MIN_GROSS_MMCF}
    return {"rows": [r for r in got["rows"] if r["region"] in big], "tables": {k: v for k, v in got["tables"].items() if k in big}}


def state_power_share(in_dir=None):
    """Gas delivered to a state's power plants as a percent of its gas delivered to the four consuming sectors."""
    return _states("state_power_share", "burn", in_dir)


def shale_share(in_dir=None):
    """Shale gas as a percent of US gross withdrawals (EIA's US rows)."""
    return {"rows": _run("shale_share", "us_shale", "the United States", in_dir), "tables": {"us_shale": ["eia_gas_production_state_monthly"]}}


def mexico_exports(in_dir=None):
    """US pipeline exports of gas to Mexico over the year (MMcf)."""
    rows = [dict(r, value=r["value"] / 1000.0) for r in _run("mexico_exports", "us_mexico", "US pipeline exports to Mexico", in_dir)]
    return {"rows": rows, "tables": {"us_mexico": ["eia_gas_trade_country_monthly"]}}


def storage_outside(in_dir=None):
    """The percent of the year's weeks on which a region's working gas lay outside its five-year minimum to maximum."""
    d = hm.series("gas_balance_weekly", in_dir, variables=["working_gas_bcf", "five_year_min_bcf", "five_year_max_bcf"], entities=list(REGIONS))
    w = d.pivot_table(index=["entity", "ts_utc"], columns="variable", values="value").dropna().reset_index()
    w["out"] = (w["working_gas_bcf"] < w["five_year_min_bcf"]) | (w["working_gas_bcf"] > w["five_year_max_bcf"])
    w["year"] = w["ts_utc"].str[:4].astype(int)
    rows, tables = [], {}
    for ent, g in w.groupby("entity"):
        region = "stor_" + ent.split(":")[1]
        for y, s in g.groupby("year"):
            rows.append(hm._row(region, REGIONS[ent], y, float(100 * s["out"].mean()), len(s)))
        tables[region] = ["gas_balance_weekly"]
    return {"rows": rows, "tables": tables}


# ---------------------------------------------------------------------------------------------------------------------
# the reproduction scripts
# ---------------------------------------------------------------------------------------------------------------------
PY_RATIO = '''"""ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public table.

    python {{this file}} <{table}.csv>

{label}. A year's figure: the numerator's rows summed{over}, with the year's count of the numerator's months.
"""
import sys

import pandas as pd

with open(sys.argv[1], encoding="utf-8") as f:
    skip = 0
    for line in f:
        if not line.startswith("#"):
            break
        skip += 1
d = pd.read_csv(sys.argv[1], skiprows=skip, usecols=["entity", "variable", "ts_utc", "value"], dtype=str)
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"])
d["year"] = d["ts_utc"].str[:4].astype(int)
num = d[d["entity"].str.contains({num_re!r}, regex=True) & d["variable"].isin({num_vars!r})]
{den_line}
for y, s in num.groupby("year"):
{body}
'''


def reproduce_py(name, region):
    P = next(p for p in CANDIDATES if p["name"] == name)
    label = P["label"][0].upper() + P["label"][1:]
    if name == "storage_outside":
        ent = "gas_storage:" + region[len("stor_"):]
        return ('"""ERW findings hunt (chain 164): reproduce candidate storage_outside for ' + region + " from the ERW's public table.\n\n"
                "    python {this file} <gas_balance_weekly.csv>\n\n" + label + ", " + REGIONS[ent] + '.\n"""\nimport sys\n\nimport pandas as pd\n\n'
                'with open(sys.argv[1], encoding="utf-8") as f:\n    skip = 0\n    for line in f:\n        if not line.startswith("#"):\n            break\n        skip += 1\n'
                'd = pd.read_csv(sys.argv[1], skiprows=skip, usecols=["entity", "variable", "ts_utc", "value"], dtype=str)\n'
                f'd = d[(d["entity"] == {ent!r}) & d["variable"].isin(["working_gas_bcf", "five_year_min_bcf", "five_year_max_bcf"])].copy()\n'
                'd["value"] = pd.to_numeric(d["value"], errors="coerce")\n'
                'w = d.pivot_table(index="ts_utc", columns="variable", values="value").dropna()\n'
                'w["out"] = (w["working_gas_bcf"] < w["five_year_min_bcf"]) | (w["working_gas_bcf"] > w["five_year_max_bcf"])\n'
                'for y, s in w.groupby(w.index.str[:4].astype(int)):\n    print(y, round(float(100 * s["out"].mean()), 6), len(s))\n')
    table, num_re, num_vars, den_re, den_vars, scale = SPECS[name]
    st = region.rsplit("_", 1)[1] if name in ("state_production_share", "flared_share", "state_power_share") else ""
    num_re, den_re = num_re.format(st=st), (den_re.format(st=st) if den_re else None)
    if den_re:
        den_line = f'den = d[d["entity"].str.contains({den_re!r}, regex=True) & d["variable"].isin({den_vars!r})]'
        body = ('    b = den.loc[den["year"] == y, "value"].sum()\n    if b != 0:\n'
                f'        print(y, round(float(s["value"].sum() * {scale!r} / b), 6), s["ts_utc"].nunique())')
        over = " times " + repr(scale) + " over the denominator's rows summed"
    else:
        den_line = ""
        body = f'    print(y, round(float(s["value"].sum() * {scale!r} / 1000.0), 6), s["ts_utc"].nunique())'
        over = ", in Bcf (MMcf over 1,000)"
    return PY_RATIO.format(name=name, region=region, table=table, label=label, over=over, num_re=num_re, num_vars=num_vars, den_line=den_line, body=body)


def _stata_re(rx):
    """A Python regex of this module as Stata's regexm reads it (the same here: anchors, a literal colon)."""
    return rx


def reproduce_do(name, region):
    head = [f"* ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public table.",
            "* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.",
            "clear all"]
    if name == "storage_outside":
        ent = "gas_storage:" + region[len("stor_"):]
        lines = head + ['import delimited "gas_balance_weekly.csv", varnames(1) stringcols(_all) clear',
                        f'keep if entity == "{ent}" & (variable == "working_gas_bcf" | variable == "five_year_min_bcf" | variable == "five_year_max_bcf")',
                        "destring value, replace force", "keep ts_utc variable value", "reshape wide value, i(ts_utc) j(variable) string",
                        "drop if missing(valueworking_gas_bcf) | missing(valuefive_year_min_bcf) | missing(valuefive_year_max_bcf)",
                        "generate byte out = valueworking_gas_bcf < valuefive_year_min_bcf | valueworking_gas_bcf > valuefive_year_max_bcf",
                        "generate int year = real(substr(ts_utc, 1, 4))", "collapse (mean) measure = out (count) n = out, by(year)", "replace measure = 100 * measure"]
    else:
        table, num_re, num_vars, den_re, den_vars, scale = SPECS[name]
        st = region.rsplit("_", 1)[1] if name in ("state_production_share", "flared_share", "state_power_share") else ""
        num_re, den_re = num_re.format(st=st), (den_re.format(st=st) if den_re else None)
        nv = " | ".join(f'variable == "{v}"' for v in num_vars)
        lines = head + [f'import delimited "{table}.csv", varnames(1) stringcols(_all) clear', "destring value, replace force", "drop if missing(value)",
                        "generate int year = real(substr(ts_utc, 1, 4))", f'generate double num = value if regexm(entity, "{_stata_re(num_re)}") & ({nv})',
                        "egen byte num_month = tag(ts_utc) if !missing(num)"]
        if den_re:
            dv = " | ".join(f'variable == "{v}"' for v in den_vars)
            lines += [f'generate double den = value if regexm(entity, "{_stata_re(den_re)}") & ({dv})',
                      "collapse (sum) num (sum) den (sum) n = num_month, by(year)", "keep if n > 0 & den != 0", f"generate double measure = num * {scale!r} / den"]
        else:
            lines += ["collapse (sum) num (sum) n = num_month, by(year)", "keep if n > 0", f"generate double measure = num * {scale!r} / 1000"]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
LIMIT_EIA = "EIA's monthly figures as published, the latest months preliminary and EIA's estimates where a state does not report."
CANDIDATES = [
    C("lng_share", FAMILY, lng_share, "percent of dry production", 1, 11, 2.0, "LNG'S SHARE OF US GAS",
      "LNG exports as a percent of US dry gas production over the year", lambda w: "US LNG exports as a share of US dry gas production",
      LIMIT_EIA + " LNG exports are measured at the terminals, dry production at the wells' processing; the share is of what is produced, not of what is used.",
      reproduce("lng_share"), consequence=3),
    C("power_share", FAMILY, power_share, "percent of consumption", 1, 11, 2.0, "GAS FOR POWER",
      "gas burned for power as a percent of US gas consumption over the year", lambda w: "the gas burned for power as a share of US gas consumption",
      LIMIT_EIA, reproduce("power_share"), consequence=3),
    C("state_production_share", FAMILY, state_production_share, "percent of US marketed production", 1, 11, 1.0, "A STATE'S SHARE OF US GAS",
      "a state's marketed gas production as a percent of the US total", lambda w: f"{w}'s share of US marketed gas production",
      LIMIT_EIA + " The US total is EIA's own US row.",
      reproduce("state_production_share"), consequence=3),
    C("flared_share", FAMILY, flared_share, "percent of gross withdrawals", 2, 11, 0.5, "GAS VENTED AND FLARED",
      "a state's vented and flared gas as a percent of its gross withdrawals", lambda w: f"the share of {w}'s gross gas withdrawals vented or flared",
      LIMIT_EIA + " Venting and flaring are reported or estimated by the states, and EIA's series ends in 2024; states with less than 100 Bcf of gross withdrawals in their last whole year are not hunted.",
      reproduce("flared_share"), consequence=2),
    C("state_power_share", FAMILY, state_power_share, "percent of delivered gas", 1, 11, 2.0, "A STATE'S GAS FOR POWER",
      "gas delivered to a state's power plants as a percent of its gas delivered to the four consuming sectors",
      lambda w: f"the share of {w}'s delivered gas that went to power plants",
      LIMIT_EIA + " Deliveries to the four sectors, not counting the gas pipelines and fields use themselves.",
      reproduce("state_power_share"), consequence=2),
    C("shale_share", FAMILY, shale_share, "percent of gross withdrawals", 1, 11, 2.0, "SHALE'S SHARE OF US GAS",
      "shale gas as a percent of US gross withdrawals", lambda w: "shale gas's share of US gross gas withdrawals",
      LIMIT_EIA + " EIA's shale series ends in 2024.",
      reproduce("shale_share"), consequence=3),
    C("mexico_exports", FAMILY, mexico_exports, "Bcf", 0, 11, 50.0, "PIPELINE GAS TO MEXICO",
      "US pipeline exports of gas to Mexico over the year", lambda w: "US pipeline exports of natural gas to Mexico",
      LIMIT_EIA + " Volumes in Bcf (EIA's MMcf over 1,000); the latest months are EIA's estimates.",
      reproduce("mexico_exports"), consequence=3),
    C("storage_outside", FAMILY, storage_outside, "percent of weeks", 1, 45, 10.0, "STORAGE OUTSIDE ITS FIVE YEARS",
      "the percent of the year's weeks on which a region's working gas lay outside its five-year minimum to maximum",
      lambda w: f"the share of weeks on which {w} lay outside its five-year range",
      "EIA's weekly working gas against the ERW's five-year range of the same week (gas_balance_weekly); a week outside is outside by any margin.",
      reproduce("storage_outside"), consequence=2),
]
for _P in CANDIDATES:
    if _P["name"] in ("state_production_share", "state_power_share"):
        _P["rank"] = lambda c: abs(c["change"])


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt, family gas (chain 164)")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--only", default=None)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    cands = [P for P in CANDIDATES if not a.only or P["name"] == a.only]
    builder.run(FAMILY, cands, a.in_dir, dry_run=not a.load)
    return 0


if __name__ == "__main__":
    sys.exit(main())
