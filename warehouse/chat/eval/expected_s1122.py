"""Session 1122 (chain 075): the keys of the five price-board questions (questions_s1122.yaml), computed from the rows of
price_board_latest and price_board_spreads recorded from the live set (tests/fixtures/session1122/board_reads.json),
independently of the tools: for each measure, every public hub's newest row (ISO-NE's, NYISO's and MISO's rows are held
for a license and left out, as the site's reads leave them), ranked as the question asks. No model, no network.

    python warehouse/chat/eval/expected_s1122.py      writes expected_s1122.json and questions_s1122.yaml beside itself, and
                                                      site/data/board_questions.json (the questions alone, the board's
                                                      Ask examples, session 1145)

The keys are the board on the day the rows were recorded: asked on a later day, compute them again from the day's rows.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FIX = os.path.join(ROOT, "tests", "fixtures", "session1122", "board_reads.json")
HELD = ("isone:", "nyiso:", "miso:")
QUESTIONS = [
    ("k01", "da_latest_day_mean", "highest", "On the price board's newest day for each hub, which hub had the highest day-ahead daily mean, and what was it in USD per MWh?"),
    ("k02", "da_day_change_pct", "largest_move", "What moved most on the price board: which hub's day-ahead daily mean changed most, in percent, on its newest day against the day before, and by how much?"),
    ("k03", "spark_spread_7", "highest", "Where is the spark spread widest on the price board (each hub's newest day, at the board's stated heat rate), and what is it in USD per MWh?"),
    ("k04", "rt_latest_day_mean", "lowest", "Which hub on the price board had the lowest real-time daily mean on its newest day, and what was it in USD per MWh?"),
    ("k05", "da_minus_rt", "largest_move", "On the price board, which hub's day-ahead price ran furthest from real time (day-ahead minus real time, either sign) on its newest day, and by how much in USD per MWh?"),
]
TABLE = {"spark_spread_7": "price_board_spreads"}
WORDS = {"ercot:HB_HUBAVG": "ERCOT", "caiso:TH_SP15_GEN-APND": "SP15", "caiso:TH_NP15_GEN-APND": "NP15", "caiso:TH_ZP26_GEN-APND": "ZP26", "spp:SPPNORTH_HUB": "SPP"}


def newest(rows, measure):
    out = {}
    for r in rows:
        if r["variable"] != measure or r["entity"].startswith(HELD) or r["value"] is None:
            continue
        if r["entity"] not in out or r["ts_utc"] > out[r["entity"]]["ts_utc"]:
            out[r["entity"]] = r
    return out


def rank(by, order):
    key = {"highest": lambda r: -r["value"], "lowest": lambda r: r["value"], "largest_move": lambda r: -abs(r["value"])}[order]
    return sorted(by.values(), key=key)


def build():
    with open(FIX, encoding="utf-8") as f:
        fix = json.load(f)
    out = []
    for qid, measure, order, question in QUESTIONS:
        ranked = rank(newest(fix["rows"], measure), order)
        if len(ranked) < 3:
            raise SystemExit(f"{qid}: fewer than three public hubs hold {measure}")
        top = ranked[0]
        out.append({"id": qid, "measure": measure, "order": order, "question": question, "table": TABLE.get(measure, "price_board_latest"),
                    "entity": top["entity"], "value": top["value"], "at": top["ts_utc"], "ranking": [r["entity"] for r in ranked]})
    return {"_about": "Session 1122: the keys of questions_s1122.yaml, from tests/fixtures/session1122/board_reads.json by expected_s1122.py.",
            "recorded_at": fix["recorded_at"], "questions": out}


def yaml_of(doc):
    lines = ["# Energy Research Warehouse (ERW): five price-board questions for Ask, session 1122 (chain 075, 23 October 2026), answered",
             "# by the tool board_rank over the board's own derived tables. Keys from the rows recorded at " + doc["recorded_at"] + " by",
             "# expected_s1122.py (tests/fixtures/session1122/board_reads.json): each hub's newest value, the held grids left out.",
             f"today: '{doc['recorded_at'][:10]}'", "questions:"]
    for q in doc["questions"]:
        v = q["value"]
        lines += [f"- id: {q['id']}", "  grid: ERCOT", "  via: general", f"  question: {json.dumps(q['question'])}",
                  f"  expected: [{round(v, 4)}]", f"  tolerance: {0.01 if abs(v) < 1000 else 0.5}", f"  text: {json.dumps([WORDS.get(q['entity'], q['entity'].split(':')[1])])}",
                  f"  tables: {json.dumps([q['table']])}", "  refuse: false",
                  f"  note: {json.dumps(q['table'] + ', ' + q['measure'] + ', ' + q['order'] + ' of each public hub newest row: ' + q['entity'] + ' on ' + q['at'][:10])}"]
    return "\n".join(lines) + "\n"


def main():
    doc = build()
    with open(os.path.join(HERE, "expected_s1122.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    with open(os.path.join(HERE, "questions_s1122.yaml"), "w", encoding="utf-8", newline="\n") as f:
        f.write(yaml_of(doc))
    with open(os.path.join(ROOT, "site", "data", "board_questions.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"_about": "Session 1145: the five board questions of warehouse/chat/eval/questions_s1122.yaml, the board's Ask examples, written by expected_s1122.py.",
                   "questions": [{"id": q["id"], "question": q["question"]} for q in doc["questions"]]}, f, indent=1)
        f.write("\n")
    for q in doc["questions"]:
        print(q["id"], q["measure"], q["order"], q["entity"], q["value"], q["at"][:10])
    return 0


if __name__ == "__main__":
    sys.exit(main())
