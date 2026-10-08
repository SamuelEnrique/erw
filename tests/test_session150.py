"""Session 150: the Thesis Builder's stage of data providers is provider-agnostic, and two providers stand beside PitchBook.

What is proven here, with no network, no model call, no database and no connector:

  - PitchBook is the first provider of one interface with NO change to the text of an erw-pitchbook-1 request: the
    code makes, byte for byte, the request the code of main made before this session (tests/fixtures/session150/
    pitchbook_request_main.json), and the reader of a pasted answer (site/lib/thesis/pitchbook.ts) is the file of main.
  - the store is not rewritten: migration 025 adds one table and two functions and alters nothing of migration 024;
    a record that names no provider reads as PitchBook's, in code. The pending request of run 20261006T193517Z-50a8be
    is touched by nothing.
  - the formats erw-harmonic-1 and erw-crunchbase-1 map only fields their providers' public documentation names: on a
    machine that holds the saved pages (runs/session150/docs, not in git) every mapped field is found in its page, the
    pages' hashes are the ones the code and the method note state, and each quoted terms sentence is in its page word
    for word. On a machine without them (GitHub's runner) those tests skip.
  - the walls: /thesis stays in review, nothing here calls a provider, a connector or a model, no address of a person
    is in any new file, and the only contact string the documentation pull sent is the owner's ruling.

The page's own behaviour is tested by site/scripts/test-thesis-providers.mjs (pure functions) and
site/scripts/check-thesis.mjs (the page against a stand-in). Every company and figure in a fixture is made up.
"""
import csv
import hashlib
import html
import importlib.util
import json
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIX = os.path.join(ROOT, "tests", "fixtures", "session150")
PENDING_RUN = "20261006T193517Z-50a8be"
CONTACT = "ERW research project, github.com/SamuelEnrique/erw"
EM = chr(0x2014)


def load(name, *parts):
    """A module by its path, under a name of its own ("run" and "build" are names other folders use too)."""
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, *parts))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def lf_sha(*parts):
    with open(os.path.join(ROOT, *parts), "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def fixture(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as f:
        return json.load(f)


def docs_dir():
    """The saved documentation pages of the session's pull: under this copy's runs/, or the main copy's beside it."""
    for d in (os.path.join(ROOT, "runs", "session150", "docs"), os.path.abspath(os.path.join(ROOT, "..", "erw", "runs", "session150", "docs"))):
        if os.path.isfile(os.path.join(d, "fetch_log.csv")):
            return d
    return None


def specs():
    """The mapped fields as site/lib/thesis/providers.ts lists them: {group: [(field, kind, doc)]}."""
    code = src("site", "lib", "thesis", "providers.ts")
    out = {}
    for m in re.finditer(r"export const ((?:HARMONIC|CRUNCHBASE)_[A-Z_]+): readonly Spec\[\] = \[(.*?)\];", code, re.S):
        out[m.group(1)] = re.findall(r'\["([^"]+)", "([a-z]+)", "([A-Z0-9]+)"\]', m.group(2))
    return out


def doc_refs():
    """The pages the formats rest on, as the code states them: {id: (url, retrieved, sha256)}."""
    code = src("site", "lib", "thesis", "providers.ts")
    return {m.group(1): (m.group(2), m.group(3), m.group(4))
            for m in re.finditer(r'(\w+): \{ id: "\w+", title: "[^"]*", url: "([^"]+)", retrieved: "([^"]+)", sha256: "([0-9a-f]{64})" \}', code)}


class Registry(unittest.TestCase):
    def setUp(self):
        self.pv = load("erw_thesis_providers", "warehouse", "thesis", "providers.py")

    def test_three_providers_pitchbook_first_and_the_default(self):
        pv = self.pv
        self.assertEqual([(p.id, p.label, p.format) for p in pv.PROVIDERS],
                         [("pitchbook", "PitchBook", "erw-pitchbook-1"), ("harmonic", "Harmonic", "erw-harmonic-1"), ("crunchbase", "Crunchbase", "erw-crunchbase-1")])
        self.assertIs(pv.DEFAULT, pv.PITCHBOOK)
        code = src("site", "lib", "thesis", "providers.ts")
        for p in pv.PROVIDERS:
            self.assertIn(f'"{p.format}"', code if p.id != "pitchbook" else src("site", "lib", "thesis", "pitchbook.ts"), p.id)
            self.assertIn(p.terms.split("public warehouse.")[1].strip(), code.replace("${OWN(\"%s\")} " % p.label, ""), p.id)

    def test_each_terms_line_says_whose_copy_the_data_is(self):
        for p in self.pv.PROVIDERS:
            self.assertTrue(p.terms.startswith(f"{p.label} figures here are your own licensed copy: brought by you from your own account, shown to you, and not "
                                               "published, redistributed or kept in the public warehouse."), p.id)
            self.assertNotIn(EM, p.terms)
        self.assertIn("was not read", self.pv.PITCHBOOK.terms)                  # its terms page refused a plain request
        self.assertIn('Terms of Service (read 8 October 2026): "', self.pv.HARMONIC.terms)
        self.assertIn('License Agreement (read 8 October 2026): "', self.pv.CRUNCHBASE.terms)

    def test_a_record_that_names_no_provider_is_pitchbooks(self):
        pv = self.pv
        req = fixture("pitchbook_request_main.json")["request"]
        self.assertNotIn("provider", req)
        self.assertIs(pv.provider_of(req), pv.PITCHBOOK)
        for old in ({}, None, {"companies": []}, {"format": "something-else"}, "text"):
            self.assertIs(pv.provider_of(old), pv.PITCHBOOK, old)
        self.assertIs(pv.provider_of({"format": "erw-harmonic-1"}), pv.HARMONIC)
        self.assertIs(pv.provider_of({"provider": "crunchbase", "format": "erw-pitchbook-1"}), pv.CRUNCHBASE)

    def test_a_stamp_is_the_provider_the_format_the_time_and_the_hash_of_the_pasted_text(self):
        s = self.pv.stamp("harmonic", "pasted text", "2026-10-08T00:00:00Z")
        self.assertEqual(s, {"provider": "harmonic", "format": "erw-harmonic-1", "pasted_at": "2026-10-08T00:00:00Z",
                             "pasted_sha256": hashlib.sha256(b"pasted text").hexdigest()})

    def test_the_module_calls_nothing(self):
        code = src("warehouse", "thesis", "providers.py")
        for w in ("import os", "urllib", "requests", "http", "anthropic", "subprocess", "socket", "environ", "API_KEY"):
            self.assertNotIn(w, code.split('"""', 2)[2], w)


class PitchBookUnchanged(unittest.TestCase):
    """Part 1 of the brief: no change to the text of an erw-pitchbook-1 request, none to how an answer is read."""

    @classmethod
    def setUpClass(cls):
        cls.R = load("erw_thesis_run", "warehouse", "thesis", "run.py")
        cls.fx = fixture("pitchbook_request_main.json")

    def make(self):
        i = self.fx["inputs"]
        orgs = self.R.select([dict(o) for o in i["orgs"]], "", "", 5, {"S1"})
        return self.R.pitchbook_request(i["run_id"], i["niche"], i["geography"], orgs, i["trends"], i["key"])

    def test_the_fixture_was_made_by_the_code_of_main_before_this_session(self):
        self.assertEqual(self.fx["made_from_commit"], "7ae13c1e2df1e4355a09616ee57430bc95bccc17")
        self.assertIs(self.fx["run_py_changed_when_made"], False)
        self.assertTrue(self.fx["_note"].startswith("FIXTURE, made up for a test."))
        self.assertEqual(hashlib.sha256(self.fx["request"]["paste_text"].encode("utf-8")).hexdigest(), self.fx["paste_text_sha256"])

    def test_the_request_text_is_the_same_byte_for_byte(self):
        q = self.make()
        self.assertEqual(q["paste_text"].encode("utf-8"), self.fx["request"]["paste_text"].encode("utf-8"))
        self.assertEqual(hashlib.sha256(q["paste_text"].encode("utf-8")).hexdigest(), self.fx["paste_text_sha256"])

    def test_the_request_record_is_the_same_and_gains_no_key(self):
        q = self.make()
        self.assertEqual(q, self.fx["request"])
        self.assertEqual(json.dumps(q, sort_keys=True), json.dumps(self.fx["request"], sort_keys=True))
        self.assertEqual(set(q), {"format", "run_id", "companies", "discover", "paste_text"})      # no provider field: read as PitchBook's in code
        self.assertEqual(q["format"], "erw-pitchbook-1")
        self.assertEqual(self.R.FORMAT, "erw-pitchbook-1")
        self.assertIs(load("erw_thesis_providers", "warehouse", "thesis", "providers.py"), self.R.pv)

    def test_the_formats_own_example_is_what_the_pending_run_waits_for(self):
        # run 20261006T193517Z-50a8be holds a request of this format, written by this code. Its own text carries its
        # one-time key and is not read by any test: the format's own example block stands in for it.
        block = self.make()["paste_text"].split("```json")[1].split("```")[0]
        ex = json.loads(block)
        self.assertEqual(ex["format"], "erw-pitchbook-1")
        self.assertEqual(set(ex), {"format", "run_id", "key", "pulled_on", "companies", "additional_companies"})
        self.assertEqual(set(ex["companies"][0]), {"name", "found", "pitchbook_name", "hq", "founded_year", "description", "employees", "financing_status",
                                                   "last_round", "total_raised_usd_m", "investors", "lead_investors", "founders"})
        # every key of the example is a key the reader of main accepts (the reader's own list, read from its source)
        reader = src("site", "lib", "thesis", "pitchbook.ts")
        keys = re.search(r"const COMPANY_KEYS = \[(.*?)\] as const;", reader).group(1)
        for k in ex["companies"][0]:
            self.assertIn(f'"{k}"', keys, k)

    def test_the_reader_of_a_pasted_answer_is_the_file_of_main(self):
        self.assertEqual(lf_sha("site", "lib", "thesis", "pitchbook.ts"), fixture("pitchbook_read_main.json")["pitchbook_ts_sha256_lf"])
        self.assertEqual(lf_sha("site", "lib", "thesis", "pitchbook.ts"), "662e6ce0db34043c7eb89b328c35c2a85ee3fb5e06a744e822ba16ecede9e442")

    def test_the_pitchbook_route_and_function_are_still_the_ones_that_store_it(self):
        route = src("site", "app", "api", "thesis", "pitchbook", "route.ts")
        self.assertIn("validatePitchbook(sub.payload, sub.run_id)", route)
        self.assertIn("acceptPitchbook(sub.run_id, sub.key, checked.payload)", route)
        self.assertNotIn("providers", route)                              # the old route knows nothing of the new ones
        panel = src("site", "components", "thesis", "PitchbookPanel.tsx")
        self.assertIn('send("/api/thesis/pitchbook", { run_id: runId, key, payload })', panel)
        server = src("site", "lib", "thesis", "server.ts")
        self.assertIn('rpc<{ ok: boolean; reason?: string; companies?: number }>("thesis_pitchbook_accept", { p_run_id: runId, p_key: key, p_payload: payload }', server)

    def test_session_135s_answers_are_kept_with_what_main_made_of_them(self):
        fx = fixture("pitchbook_read_main.json")
        self.assertTrue(fx["_note"].startswith("FIXTURE, made up for a test."))
        self.assertEqual(len(fx["cases"]), 3)
        for c in fx["cases"]:
            self.assertEqual(hashlib.sha256(c["read"].encode("utf-8")).hexdigest(), c["read_sha256"], c["name"])
            read = json.loads(c["read"])
            self.assertEqual(list(read), ["format", "run_id", "pulled_on", "label", "received_note", "companies", "additional_companies"])
            self.assertEqual(read["label"], "PitchBook")


class Store(unittest.TestCase):
    """Part 6: the run's row and its pending request stay exactly as they are."""

    def setUp(self):
        self.sql = src("warehouse", "supabase", "migrations", "025_thesis_providers.sql")
        self.code = "\n".join(line for line in self.sql.splitlines() if not line.lstrip().startswith("--"))

    def test_the_migration_alters_nothing_of_the_runs_table(self):
        low = self.code.lower()
        for words in ("alter table public.thesis_runs", "update public.thesis_runs", "delete from public.thesis_runs", "insert into public.thesis_runs",
                      "drop ", "truncate", "for update", "pitchbook_key", "pitchbook_request"):
            self.assertNotIn(words, low, words)
        for fn in ("thesis_submit", "thesis_list", "thesis_get", "thesis_pitchbook_accept", "thesis_token_ok"):
            self.assertNotIn(f"function public.{fn}(", self.code, fn)      # none of migration 024's functions is replaced
        self.assertEqual(re.findall(r"create or replace function public\.(\w+)\(", self.code), ["thesis_provider_accept", "thesis_provider_results"])
        self.assertEqual(re.findall(r"create table if not exists public\.(\w+)", self.code), ["thesis_provider_results"])

    def test_the_new_table_is_internal_and_both_functions_ask_for_the_token(self):
        self.assertIn("alter table public.thesis_provider_results enable row level security;", self.code)
        self.assertIn("revoke all on public.thesis_provider_results from public, anon, authenticated;", self.code)
        self.assertNotIn("create policy", self.code.lower())
        for fn in ("thesis_provider_accept", "thesis_provider_results"):
            body = self.code.split(f"function public.{fn}(")[1].split("$$;")[0]
            self.assertIn("thesis_token_ok(p_token)", body, fn)
        accept = self.code.split("function public.thesis_provider_accept(")[1].split("$$;")[0]
        self.assertIn("on conflict (run_id, provider) do nothing", accept)        # one answer a provider and run, never merged
        self.assertIn("r.pitchbook is null or p_payload is not null", accept)      # for PitchBook only the stamp: its answer stays on the run's row
        self.assertIn("pasted_sha256", self.code)
        self.assertNotIn("thesis_provider_results", src("warehouse", "supabase", "live_set.yaml"))
        self.assertNotIn("thesis_provider_results", src("warehouse", "redivis", "config.yaml"))

    def test_migration_024_still_holds_the_one_time_key_as_it_did(self):
        sql = src("warehouse", "supabase", "migrations", "024_thesis.sql")
        accept = sql.split("function public.thesis_pitchbook_accept(")[1].split("$$;")[0]
        self.assertIn("pitchbook_key = null", accept)
        self.assertIn("r.pitchbook_key <> p_key", accept)
        self.assertNotIn("provider", sql)

    def test_the_pending_run_is_named_only_in_words_never_in_code_that_runs(self):
        for base in (("warehouse", "thesis"), ("warehouse", "supabase"), ("site", "lib"), ("site", "app"), ("site", "components"), ("site", "scripts"), (".github", "workflows")):
            for folder, _, names in os.walk(os.path.join(ROOT, *base)):
                if "node_modules" in folder or "__pycache__" in folder:
                    continue
                for name in names:
                    if not name.endswith((".py", ".ts", ".tsx", ".mjs", ".sql", ".yml", ".sh")):
                        continue
                    with open(os.path.join(folder, name), encoding="utf-8", errors="replace") as f:
                        for n, line in enumerate(f, 1):
                            if PENDING_RUN in line:
                                s = line.lstrip()
                                where = f"{os.path.relpath(os.path.join(folder, name), ROOT)}:{n}"
                                self.assertTrue(s.startswith(("--", "//", "#", "*")) or name == "providers.py", where)     # providers.py: its docstring
        code = src("warehouse", "thesis", "providers.py").split('"""', 2)[2]
        self.assertNotIn(PENDING_RUN, code)

    def test_the_site_reads_an_old_record_as_pitchbooks_and_writes_nothing_back(self):
        code = src("site", "lib", "thesis", "providers.ts")
        self.assertIn('return "pitchbook";', code.split("export function providerOf(")[1].split("\n}\n")[0])
        page = src("site", "app", "thesis", "page.tsx")
        self.assertIn("getProviderResults(run.run_id)", page)
        self.assertNotIn("acceptProvider", page)                                    # the page only reads
        server = src("site", "lib", "thesis", "server.ts")
        self.assertEqual(server.count('rpc<Run | null>("thesis_get"'), 1)           # the run is read by the function of migration 024, as before


class Documentation(unittest.TestCase):
    """Parts 2, 3 and 7: only what the providers' own public documentation states, each page saved with its hash."""

    @classmethod
    def setUpClass(cls):
        cls.dir = docs_dir()
        cls.specs = specs()
        cls.refs = doc_refs()

    def page(self, name):
        """A saved page as text: tags out, entities read, white space single."""
        for ext in (".html", ".txt", ".json"):
            p = os.path.join(self.dir, name + ext)
            if os.path.isfile(p):
                with open(p, "rb") as f:
                    raw = f.read().decode("utf-8", "replace")
                raw = re.sub(r"<wbr\s*/?>", "", raw)          # a hint of where a long field name may break, inside the name
                if ext == ".html":
                    raw = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", raw)
                    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
                return re.sub(r"\s+", " ", html.unescape(raw))
        self.fail(f"no saved page {name}")

    def log(self):
        with open(os.path.join(self.dir, "fetch_log.csv"), newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def test_the_code_lists_113_mapped_fields_each_with_its_page(self):
        self.assertEqual({k: len(v) for k, v in self.specs.items()},
                         {"HARMONIC_COMPANY": 31, "HARMONIC_ROUND": 9, "HARMONIC_ROUND_INVESTOR": 4, "HARMONIC_PERSON": 7, "HARMONIC_EXPERIENCE": 6, "HARMONIC_INVESTOR": 10,
                          "CRUNCHBASE_ORGANIZATION": 29, "CRUNCHBASE_ROUND": 10, "CRUNCHBASE_PERSON": 7})
        self.assertEqual(sorted(self.refs), ["C1", "C2", "C3", "CT", "H1", "H2", "HT"])
        for group, fields in self.specs.items():
            for field, _, doc in fields:
                self.assertIn(doc, self.refs, (group, field))
                self.assertTrue(doc.startswith("H" if group.startswith("HARMONIC") else "C"), (group, field, doc))

    def test_the_method_note_lists_every_mapped_field_every_page_and_every_terms_sentence(self):
        note = src("docs", "methods", "thesis_builder.md")
        for group, fields in self.specs.items():
            for field, _, _ in fields:
                self.assertIn(f"`{field}`", note, (group, field))
        for doc, (url, retrieved, sha) in self.refs.items():
            self.assertIn(url, note, doc)
            self.assertIn(sha, note, doc)
            self.assertIn(retrieved, note, doc)
        for words in ("erw-harmonic-1", "erw-crunchbase-1", "erw-pitchbook-1", "not_mapped", "025_thesis_providers.sql", "HTTP 403", "was not read",
                      "provide, sell, transfer, sublicense, lend, distribute, or otherwise allow others to access or use the Services or the data obtained through the Services;",
                      "Except as otherwise expressly set forth herein, Licensee may not license, sublicense, sell, offer to sell, distribute or otherwise provide any Crunchbase data to any third parties.",
                      "Not verified against the connector"):
            self.assertIn(words, note, words)
        self.assertNotIn(EM, note)

    def test_the_saved_pages_have_the_hashes_the_code_states(self):
        if not self.dir:
            self.skipTest("the saved documentation pages are not on this machine (runs/session150/docs is not in git)")
        rows = {r["url"]: r for r in self.log()}
        for doc, (url, retrieved, sha) in self.refs.items():
            self.assertIn(url, rows, doc)
            r = rows[url]
            self.assertEqual((r["status"], r["sha256"], r["retrieved_utc"]), ("200", sha, retrieved), doc)
            with open(os.path.join(self.dir, r["saved_as"]), "rb") as f:
                self.assertEqual(hashlib.sha256(f.read()).hexdigest(), sha, doc)

    def test_every_mapped_field_is_named_by_its_providers_own_page(self):
        if not self.dir:
            self.skipTest("the saved documentation pages are not on this machine (runs/session150/docs is not in git)")
        h2 = self.page("harmonic_data_fields")
        prefix = {"HARMONIC_ROUND_INVESTOR": ("investors.", "investors[]."), "HARMONIC_EXPERIENCE": ("experience.",)}
        for group in ("HARMONIC_COMPANY", "HARMONIC_ROUND", "HARMONIC_ROUND_INVESTOR", "HARMONIC_PERSON", "HARMONIC_EXPERIENCE", "HARMONIC_INVESTOR"):
            for field, _, doc in self.specs[group]:
                self.assertEqual(doc, "H2")
                ways = [p + field for p in prefix.get(group, ("",))]
                self.assertTrue(any(re.search(r"(?<![\w.])" + re.escape(w) + r"(?![\w.])", h2) for w in ways), (group, field))
        c1, c2, c3 = self.page("crunchbase_tool_reference"), self.page("crunchbase_data_dictionary"), self.page("crunchbase_reference_getorganization_advanced")
        spec = json.loads(c3.split("```json", 1)[1].rsplit("```", 1)[0])["components"]["schemas"]
        schema = {"CRUNCHBASE_ORGANIZATION": "Organization", "CRUNCHBASE_ROUND": "FundingRound", "CRUNCHBASE_PERSON": "Person"}
        for group, name in schema.items():
            for field, kind, doc in self.specs[group]:
                if doc == "C1":
                    self.assertEqual(field, "url")
                    self.assertIn("Each entity in the results carries a `url` field linking to its Crunchbase profile.", c1)
                elif doc == "C2":
                    self.assertRegex(c2, r"(?<![\w.])" + re.escape(field) + r"(?![\w.])", (group, field))
                    self.assertIn(field, spec[name]["properties"], (group, field))
                else:
                    self.assertIn(field, spec[name]["properties"], (group, field))
                    ref = json.dumps(spec[name]["properties"][field])
                    want = {"money": "schemas/Money", "cbdate": "schemas/DateWithPrecision", "ident": "schemas/EntityIdentifier", "idents": "Identifier", "link": "schemas/Link"}.get(kind)
                    if want:
                        self.assertIn(want, ref, (group, field, kind))
        # the shapes of Crunchbase's objects, as the reader checks them
        self.assertEqual(sorted(spec["Money"]["properties"]), ["currency", "value", "value_usd"])
        self.assertEqual(sorted(spec["DateWithPrecision"]["properties"]), ["precision", "value"])
        self.assertEqual(spec["DateWithPrecision"]["properties"]["precision"]["enum"], ["none", "year", "month", "day"])
        self.assertEqual(sorted(spec["Link"]["properties"]), ["label", "value"])
        self.assertEqual(sorted(set(spec["EntityIdentifier"]["properties"]) | set(spec["LocationIdentifier"]["properties"])), ["entity_def_id", "image_id", "location_type", "permalink", "uuid", "value"])
        self.assertIn("c_00011_00050 - 11-50", spec["Organization"]["properties"]["num_employees_enum"]["description"])
        self.assertIn("founders", json.dumps(spec["OrganizationEntity"]))
        self.assertIn("raised_funding_rounds", json.dumps(spec["OrganizationEntity"]))

    def test_what_the_requests_say_of_the_connectors_is_in_their_guides(self):
        if not self.dir:
            self.skipTest("the saved documentation pages are not on this machine (runs/session150/docs is not in git)")
        h1 = self.page("harmonic_mcp_getting_started")
        for words in ("Enrichment tools", "Search tools", "Lookup tools", "Saved search tools", "Get results from your saved searches across companies, people, and investors",
                      "Deal data is available as an add-on", "Most tools in the Harmonic MCP server are read-only"):
            self.assertIn(words, h1, words)
        c1 = self.page("crunchbase_tool_reference")
        for words in ("cb_expert_resolve_entity", "cb_entity_get", "cb_search_query", "cb_expert_build_search", "never guessed or fabricated", "cb_list_create"):
            self.assertIn(words, c1, words)

    def test_each_quoted_terms_sentence_is_in_its_saved_page_word_for_word(self):
        if not self.dir:
            self.skipTest("the saved documentation pages are not on this machine (runs/session150/docs is not in git)")
        pv = load("erw_thesis_providers", "warehouse", "thesis", "providers.py")
        pages = {"harmonic": self.page("harmonic_legal_terms"), "crunchbase": self.page("crunchbase_license_agreement")}
        for p in (pv.HARMONIC, pv.CRUNCHBASE):
            quote = re.search(r'\(read 8 October 2026\): "(.*)"$', p.terms).group(1)
            for part in quote.split(" [...] "):
                self.assertIn(part, pages[p.id], (p.id, part))
        rows = {r["name"]: r for r in self.log()}
        self.assertEqual(rows["pitchbook_terms_of_use"]["status"], "403")          # refused a plain request: recorded and left
        self.assertEqual(sum(1 for r in self.log() if "pitchbook.com" in r["url"]), 1)

    def test_the_pull_stayed_under_its_ceiling_and_sent_only_the_contact_string(self):
        if not self.dir:
            self.skipTest("the saved documentation pages are not on this machine (runs/session150/docs is not in git)")
        rows = self.log()
        self.assertLessEqual(len(rows), 60)
        self.assertLessEqual(sum(int(r["bytes"] or 0) for r in rows), 40_000_000)
        for r in rows:
            host = re.match(r"https://([^/]+)/", r["url"]).group(1)
            self.assertTrue(host.endswith(("harmonic.ai", "crunchbase.com", "pitchbook.com")), host)
            self.assertNotIn("mcp.", host)                                          # a documentation page, never a connector
            self.assertNotIn("api.", host)
            self.assertNotIn("@", r["url"])
        with open(os.path.join(self.dir, "..", "fetch_doc.py"), encoding="utf-8") as f:
            code = f.read()
        self.assertIn(f'UA = "{CONTACT}"', code)
        self.assertEqual(re.findall(r"headers=\{([^}]*)\}", code), ['"User-Agent": UA, "Accept": "text/html,application/json,text/plain,*/*"'])


class Walls(unittest.TestCase):
    NEW = [("site", "lib", "thesis", "providers.ts"), ("site", "components", "thesis", "ProviderBlock.tsx"), ("site", "app", "api", "thesis", "provider", "route.ts"),
           ("site", "scripts", "test-thesis-providers.mjs"), ("site", "scripts", "thesis-providers-fixtures.mjs"), ("warehouse", "thesis", "providers.py"),
           ("warehouse", "supabase", "migrations", "025_thesis_providers.sql"), ("tests", "test_session150.py"),
           ("tests", "fixtures", "session150", "pitchbook_request_main.json"), ("tests", "fixtures", "session150", "pitchbook_read_main.json")]
    CHANGED = [("site", "components", "thesis", "PitchbookPanel.tsx"), ("site", "components", "thesis", "Report.tsx"), ("site", "app", "thesis", "page.tsx"),
               ("site", "lib", "thesis", "server.ts"), ("site", "lib", "thesis", "types.ts"), ("site", "scripts", "thesis-stub.mjs"), ("site", "scripts", "check-thesis.mjs"),
               ("warehouse", "thesis", "run.py"), ("docs", "methods", "thesis_builder.md"), ("docs", "methods", "thesis.md")]

    def test_no_em_dash_in_any_file_of_the_session(self):
        for parts in self.NEW + self.CHANGED:
            self.assertNotIn(EM, src(*parts), parts)

    def test_no_address_of_a_person_in_any_new_file(self):
        mail = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}")
        for parts in self.NEW + self.CHANGED:
            self.assertEqual(mail.findall(src(*parts)), [], parts)

    def test_nothing_calls_a_provider_a_connector_or_a_model(self):
        for parts in (("site", "lib", "thesis", "providers.ts"), ("site", "components", "thesis", "ProviderBlock.tsx"), ("site", "app", "api", "thesis", "provider", "route.ts"),
                      ("warehouse", "thesis", "providers.py"), ("site", "components", "thesis", "PitchbookPanel.tsx")):
            text = src(*parts)
            for w in ("anthropic", "messages.create", "mcp.api.harmonic.ai", "mcp.crunchbase.com", "api.crunchbase.com", "api.harmonic.ai", "api.pitchbook.com",
                      "PITCHBOOK_API_KEY", "HARMONIC_API_KEY", "CRUNCHBASE_API_KEY", "apikey", "Bearer "):
                self.assertNotIn(w, text, (parts[-1], w))
        # the only requests the page's own code makes go to the site's two routes
        panel = src("site", "components", "thesis", "PitchbookPanel.tsx")
        self.assertEqual(sorted(set(re.findall(r'send\("([^"]+)"', panel))), ["/api/thesis/pitchbook", "/api/thesis/provider"])
        self.assertEqual(len(re.findall(r"\bfetch\(", panel)), 1)
        self.assertNotIn("fetch(", src("site", "lib", "thesis", "providers.ts"))
        self.assertNotIn("fetch(", src("site", "components", "thesis", "ProviderBlock.tsx"))

    def test_the_page_stays_in_review_and_the_new_route_answers_only_the_internal_view(self):
        self.assertRegex(src("site", "lib", "release.ts"), r'"/thesis": "review"')
        route = src("site", "app", "api", "thesis", "provider", "route.ts")
        self.assertIn("if (!(await internalOk(req.cookies.get(COOKIE)?.value))) return hidden();", route)
        self.assertLess(route.index("internalOk(req.cookies"), route.index("req.text()"))      # before anything of the request is read
        self.assertIn("headers: NO_STORE", route)
        self.assertIn('createHash("sha256").update(body.pasted, "utf8")', route)               # the hash is of the pasted text, as pasted

    def test_the_page_offers_the_three_and_refuses_another_providers_format_in_plain_words(self):
        panel = src("site", "components", "thesis", "PitchbookPanel.tsx")
        self.assertIn('useState<ProviderId>("pitchbook")', panel)                               # PitchBook first, as today's default
        self.assertIn("PROVIDER_IDS.map((id) =>", panel)
        self.assertIn("formatFault(chosen, value.format)", panel)
        self.assertIn("provider.requestText({ run_id: runId, niche, request })", panel)
        code = src("site", "lib", "thesis", "providers.ts")
        self.assertIn("requestText: (run) => str(run.request?.paste_text),", code)             # PitchBook's text is the saved one, never made again
        self.assertIn("Choose ${other.label} above, or paste ${p.label}'s answer.", code)

    def test_what_the_panel_showed_before_is_still_there(self):
        panel = src("site", "components", "thesis", "PitchbookPanel.tsx")
        for words in ("PitchBook received", "Pulled on", "companies found", "more found by PitchBook", ": PB_PENDING}", "Asked for {asked.length}", 'data-thesis-asked="1"',
                      "Paste this into a Claude chat that has a", 'data-thesis-copy="1"', 'data-thesis-paste="1"', "Paste Claude&apos;s answer here", 'data-thesis-submit="1"',
                      'data-thesis-answer="1"', 'data-thesis-said="1"', "This run holds no key to submit under.", "The text could not be copied: select it in the box and copy it by hand."):
            self.assertIn(words, panel, words)
        report = src("site", "components", "thesis", "Report.tsx")
        for words in ('data-pb-tag="1"', "Found by PitchBook", "not in PitchBook&apos;s answer", "not found in PitchBook", "no PitchBook figure", "not asked", 'kind="pitchbook_pending"'):
            self.assertIn(words.replace("&apos;", "'"), report, words)

    def test_the_fixtures_say_they_are_made_up(self):
        text = src("site", "scripts", "thesis-providers-fixtures.mjs")
        self.assertIn("THE ANSWERS BELOW ARE A FIXTURE.", text)
        self.assertIn("is made up for", text)
        self.assertIn("no connector was ever called", text)
        for name in re.findall(r'name: "([^"]+)"', text) + re.findall(r'full_name: "([^"]+)"', text) + re.findall(r'investor_name: "([^"]+)"', text):
            self.assertRegex(name, r"Fixture|Example|Sample", name)                            # every name says it is an example

    def test_the_session_25_connectors_are_still_not_wired(self):
        code = src("warehouse", "thesis", "connectors", "__init__.py")
        self.assertIn("raise NotWired", code)
        for name in ("harmonic.py", "crunchbase.py", "pitchbook.py"):
            self.assertNotIn("def fetch_companies", src("warehouse", "thesis", "connectors", name), name)


if __name__ == "__main__":
    unittest.main()
