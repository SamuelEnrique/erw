"""Session 138: Texas delivery charges (warehouse/connectors/texas_delivery_charges.py).

The rule that keeps a figure (its line found literally on the page, its digits in that line), the spend check that
refuses a model call before it is sent, and the table's rows: each has a sentence, an address and a page.
"""

import csv
import importlib.util
import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (os.path.join(ROOT, "warehouse", "connectors"), os.path.join(ROOT, "warehouse")):
    if p not in sys.path:
        sys.path.insert(0, p)

spec = importlib.util.spec_from_file_location(
    "texas_delivery_charges", os.path.join(ROOT, "warehouse", "connectors", "texas_delivery_charges.py"))
tdc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tdc)

# A real passage: Oncor Electric Delivery Company LLC, Tariff for Retail Delivery Service, page 80 (6.1.1.1.7
# Transmission Service, effective June 1, 2026), as pdfplumber extracted it on 2026-10-07 from
# https://www.oncor.com/content/dam/oncorwww/documents/about-us/regulatory/tariff-and-rate-schedules/Tariff%20for%20Retail%20Delivery%20Service.pdf.coredownload.pdf
PASSAGE = """6.1.1 Delivery System Charges Sheet: 1.7
Applicable: Entire Certified Service Area Page 1 of 2
Effective Date: June 1, 2026 Revision: Twelve
6.1.1.1.7 Transmission Service
MONTHLY RATE
I. Base Rate Charges:
Customer Charge $ 258.80 per Retail Customer
Metering Charge $ 321.63 per Retail Customer
Distribution System Charge $ 0.331004 per Distribution System billing
kW
II. Nuclear Decommissioning Charge: See Rider NDC
"""


def fig(line, value):
    return {"page": 80, "rate_class": "Transmission Service", "schedule": "6.1.1.1.7 Transmission Service",
            "charge_name": "Customer Charge", "value": value, "unit": "per Retail Customer",
            "effective_date": "June 1, 2026", "line": line}


def test_a_sentence_on_the_page_is_kept():
    assert tdc.verify(fig("Customer Charge $ 258.80 per Retail Customer", "$ 258.80"), PASSAGE) == (True, "")
    # whitespace normalized: a line that breaks on the page is still the page's own text
    assert tdc.verify(fig("Distribution System Charge $ 0.331004 per Distribution System billing kW", "$ 0.331004"),
                      PASSAGE) == (True, "")
    assert tdc.verify(fig("Customer  Charge $ 258.80\nper Retail Customer", "$258.80"), PASSAGE)[0]


def test_a_sentence_altered_by_one_digit_is_rejected():
    ok, why = tdc.verify(fig("Customer Charge $ 258.90 per Retail Customer", "$ 258.90"), PASSAGE)
    assert (ok, why) == (False, "line not found on the page")
    ok, why = tdc.verify(fig("Distribution System Charge $ 0.331005 per Distribution System billing kW", "$ 0.331005"),
                         PASSAGE)
    assert not ok


def test_a_value_that_is_not_in_its_sentence_is_rejected():
    ok, why = tdc.verify(fig("Customer Charge $ 258.80 per Retail Customer", "$ 258.90"), PASSAGE)
    assert (ok, why) == (False, "value not in its line")
    # digits inside a longer number are not the number
    assert not tdc.verify(fig("Customer Charge $ 258.80 per Retail Customer", "58.80"), PASSAGE)[0]
    assert not tdc.verify(fig("Distribution System Charge $ 0.331004 per Distribution System billing", "0.33100"), PASSAGE)[0]
    assert not tdc.verify(fig("", "$ 258.80"), PASSAGE)[0]                       # no number without its sentence
    assert not tdc.verify(fig("Customer Charge per Retail Customer", ""), PASSAGE)[0]


def test_nothing_is_rounded_or_converted():
    assert tdc.decimal_of("$ 0.331004") == "0.331004"
    assert tdc.decimal_of("$1,288.84") == "1288.84"
    assert tdc.decimal_of("($0.000649)") == "-0.000649"
    assert tdc.decimal_of("$0.00") == "0.00"
    assert tdc.iso_date("Effective Date: June 1, 2026") == "2026-06-01"
    assert tdc.iso_date("09/17/25") == "2025-09-17"
    assert tdc.iso_date("upon approval") is None


def test_the_spend_check_arithmetic():
    price = {"input": 2.00, "output": 10.00}
    # 60,000 characters at 2 characters a token: 30,000 input tokens (USD 0.06); 16,000 output tokens (USD 0.16)
    est = tdc.worst_case_usd(60000, 16000, price)
    assert abs(est - 0.22) < 1e-9
    assert tdc.fits(0.0, est, 2.70)
    assert tdc.fits(2.48, est, 2.70)
    assert not tdc.fits(2.49, est, 2.70)
    assert not tdc.fits(2.70, est, 2.70)


def test_a_call_that_would_not_fit_is_refused_before_it_is_sent(monkeypatch, tmp_path):
    import llm
    sent = []

    def no_client(*a, **k):
        sent.append(1)
        raise AssertionError("a model client was built although the call does not fit under the cap")

    monkeypatch.setenv("ERW_SESSION", "138")
    monkeypatch.setenv("ERW_SPEND_CAP_USD", "2.70")
    monkeypatch.setattr(llm, "session_total", lambda name=None: 2.60)   # USD 2.60 already in the ledger
    monkeypatch.setattr(llm, "client", no_client)
    monkeypatch.setattr(tdc, "ANSWERS", str(tmp_path / "answers"))
    monkeypatch.setattr(tdc, "select_pages", lambda doc_id: [(80, PASSAGE)])
    lines = []
    assert tdc.read(["oncor_tariff"], lines.append, "test") == 1
    assert sent == []
    assert any("REFUSED before the call" in x for x in lines)
    assert not os.path.exists(tmp_path / "answers" / "oncor_tariff_test.json")


def test_no_call_without_a_cap(monkeypatch, tmp_path):
    import llm
    monkeypatch.delenv("ERW_SPEND_CAP_USD", raising=False)
    monkeypatch.setattr(llm, "client", lambda *a, **k: (_ for _ in ()).throw(AssertionError("called")))
    monkeypatch.setattr(tdc, "ANSWERS", str(tmp_path / "answers"))
    lines = []
    assert tdc.read(["oncor_tariff"], lines.append, "test") == 1
    assert any("REFUSED" in x for x in lines)


def table_rows():
    path = os.path.join(ROOT, "warehouse", "output", "texas_delivery_charges.csv")
    if not os.path.exists(path):
        pytest.skip("warehouse/output/texas_delivery_charges.csv is not on this machine (the outputs are not in git)")
    with open(path, encoding="utf-8", newline="") as f:
        lines = f.readlines()
    n = 0
    while lines[n].startswith("#"):   # the provenance header is skipped by count, never by the comment character
        n += 1
    return list(csv.DictReader(lines[n:]))


def test_every_row_has_a_sentence_an_address_and_a_page():
    rows = table_rows()
    assert rows
    for r in rows:
        assert r["sentence"].strip(), r["event_id"]
        assert r["source_url"].startswith("https://"), r["event_id"]
        assert r["page"].isdigit() and int(r["page"]) >= 1, r["event_id"]
        assert r["amount"] != "" and r["value_as_written"].strip(), r["event_id"]
        assert tdc.number_in(r["value_as_written"], r["sentence"]), r["event_id"]
        assert r["mw"] == "" and r["price"] == "", r["event_id"]   # delivery charges are never written as market prices


def test_every_row_is_on_its_page_where_the_pages_are_held():
    rows = table_rows()
    doc_of = {v: k for k, v in tdc.SOURCE_OF.items()}
    checked = 0
    for r in rows:
        doc_id = doc_of[r["source"]]
        p = tdc.page_path(doc_id, int(r["page"]))
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            assert tdc.norm(r["sentence"]) in tdc.norm(f.read()), r["event_id"]
        checked += 1
    if not checked:
        pytest.skip("the extracted pages (warehouse/raw/texas_delivery/pages) are not on this machine")
