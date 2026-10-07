"""Session 149: the owner's rulings applied, and the data loose ends.

  1. No tracked code carries an e-mail address inside a User-Agent, a From header or a contact default. The only
     contact string the ERW sends is "ERW research project, github.com/SamuelEnrique/erw" (the owner's ruling of
     7 October 2026). The digest's own sender and recipient settings are read from the environment
     (DIGEST_FROM, DIGEST_RECIPIENTS) and are allowed, as are addresses at the reserved example domains.

The later sections of this file are named where they begin. No network. Nothing here changes the environment at
import, and every test that needs a table skips on a machine without it.
"""
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONTACT = "ERW research project, github.com/SamuelEnrique/erw"

CODE_SUFFIXES = (".py", ".mjs", ".ts", ".tsx", ".js", ".sh", ".ps1", ".yml", ".yaml")
ADDRESS = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
# What makes a line a request's contact: a user agent, a From header, curl's -A, a contact default, a mailto.
CONTEXT = re.compile(
    r"user[-_ ]?agent|\bUA\b|\bcurl\b[^\n]*\s-A\s|[\"']from[\"']\s*:|\bFrom:|contact|mailto:",
    re.IGNORECASE,
)
# The digest's sender and recipients: settings read from the environment, each with its name on the line.
ALLOWED_SETTING = re.compile(r"DIGEST_FROM|DIGEST_RECIPIENTS")
# Domains that reach nobody (RFC 2606 and RFC 6761), and Resend's own test sender.
ALLOWED_DOMAIN = re.compile(r"(?:^|\.)(?:example\.(?:com|org|net)|invalid|test|example|localhost)$|^resend\.dev$",
                            re.IGNORECASE)


def tracked_code(root=ROOT):
    """The tracked code files, by git. None when git cannot say (not a checkout)."""
    try:
        out = subprocess.run(["git", "-C", root, "ls-files", "-z"], capture_output=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    names = [n for n in out.stdout.decode("utf-8", "replace").split("\0") if n]
    return [n for n in names if n.lower().endswith(CODE_SUFFIXES)]


def contact_addresses(text):
    """(line number, domain) of every e-mail address that sits in a request's contact, in one file's text.

    An address counts when its own line, or one of the two lines above it, names a user agent, a From header, a
    contact default or a mailto, unless the line names one of the digest's settings or the address is at a
    reserved domain. Only the domain is returned: a finding never repeats the address itself.
    """
    found = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        hits = ADDRESS.findall(line)
        if not hits:
            continue
        if ALLOWED_SETTING.search(line):
            continue
        window = "\n".join(lines[max(0, i - 2): i + 1])
        if not CONTEXT.search(window):
            continue
        for address in hits:
            domain = address.rsplit("@", 1)[1]
            if ALLOWED_DOMAIN.search(domain):
                continue
            found.append((i + 1, domain))
    return found


class NoPersonalAddressInAContact(unittest.TestCase):
    """Item 1: the personal contact string is gone, and cannot come back into tracked code unnoticed."""

    def test_the_scanner_finds_an_address_in_a_user_agent(self):
        # built in pieces, so that this file holds no address in a contact of its own
        someone = "some.one" + "@" + "mailhost" + ".com"
        for line in (
            'curl -sS -A "ERW research pilot %s" "$url"' % someone,
            'code=$(curl -sS -L -A "${UA:-ERW research pilot %s}" -o "$out" "$url")' % someone,
            'headers = {"User-Agent": "erw (%s)"}' % someone,
            'UA = "ERW research %s"' % someone,
            'req.add_header("From", "%s")  # From: header' % someone,
            'CONTACT = "%s"' % someone,
        ):
            self.assertEqual(contact_addresses(line), [(1, "mailhost.com")], line)

    def test_the_scanner_reads_a_user_agent_split_over_lines(self):
        someone = "some.one" + "@" + "mailhost" + ".com"
        text = 'headers = {\n    "User-Agent":\n        "erw research (%s)",\n}\n' % someone
        self.assertEqual(contact_addresses(text), [(3, "mailhost.com")])

    def test_the_scanner_allows_the_digest_settings_and_reserved_domains(self):
        sender = "onboarding" + "@" + "resend.dev"
        person = "reader" + "@" + "mailhost.com"
        for line in (
            'sender = env("DIGEST_FROM") or "ERW Energy Digest <%s>"' % sender,
            'KEYS = dict(DIGEST_RECIPIENTS="%s", DIGEST_FROM="ERW <%s>")' % (person, person),
            'self.assertEqual(call["from"], "ERW <%s>")' % ("erw" + "@" + "example.org"),
            'headers = {"User-Agent": "%s"}' % CONTACT,
            'UA = "x (%s)"' % ("a" + "@" + "b.example.invalid"),
        ):
            self.assertEqual(contact_addresses(line), [], line)

    def test_an_address_outside_a_contact_is_not_this_tests_business(self):
        self.assertEqual(contact_addresses('subscriber = "%s"' % ("reader" + "@" + "mailhost.com")), [])

    def test_the_ruled_contact_string_holds_no_address(self):
        self.assertEqual(CONTACT, "ERW research project, github.com/SamuelEnrique/erw")
        self.assertIsNone(ADDRESS.search(CONTACT))

    def test_no_tracked_code_sends_an_address_as_its_contact(self):
        names = tracked_code()
        if names is None:
            self.skipTest("git cannot list the tracked files here")
        self.assertGreater(len(names), 200, "the list of tracked code is too short to be the repository's")
        bad = []
        for name in names:
            path = os.path.join(ROOT, name)
            try:
                with open(path, encoding="utf-8", errors="replace") as f:
                    text = f.read()
            except OSError:
                continue
            for line_no, domain in contact_addresses(text):
                bad.append("%s:%d (an address at %s)" % (name, line_no, domain))
        self.assertEqual(bad, [], "an e-mail address inside a User-Agent, a From header or a contact default: "
                                  "send exactly %r" % CONTACT)


# ---------------------------------------------------------------------------------------------------------------
# 2. The daily run's failed steps (run 37633030030 of 7 October 2026, and every run from 2 or 4 October).
#    grid_network: the raw folder of the interchange connector holds the data lock's own check, whose whole answer
#    is the JSON value true; read as an EIA page it raised AttributeError. build_status: the interchange connector's
#    gap row names no day (its market is "pairs") and its table has two columns of its own, which read_series refuses.
# ---------------------------------------------------------------------------------------------------------------
import json
import tempfile
from unittest import mock


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheNetworkBuildPassesOverAnAnswerThatIsNotAPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for d in ("connectors", "derived"):
            p = os.path.join(ROOT, "warehouse", d)
            if p not in sys.path:
                sys.path.insert(0, p)
        try:
            import grid_network
        except ImportError as exc:  # a machine without pandas
            raise unittest.SkipTest("grid_network cannot be imported here: %s" % exc)
        cls.gn = grid_network

    def raw(self, files):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        run = os.path.join(tmp.name, "eia930_interchange", "20261007T142035Z")
        os.makedirs(run)
        for name, text in files.items():
            with open(os.path.join(run, name), "w", encoding="utf-8") as f:
                f.write(text)
        return tmp.name

    def test_the_lock_check_saved_beside_the_pages_does_not_stop_the_build(self):
        # the file the runner holds: 20261007T142059.123456Z_00009_erw_lock_check, four bytes
        page = {"response": {"total": 1, "data": [
            {"period": "2026-10-05T01", "fromba": "ERCO", "fromba-name": "Electric Reliability Council of Texas, Inc.",
             "toba": "SWPP", "toba-name": "Southwest Power Pool", "value": "-55"}]}}
        root = self.raw({
            "20261007T142040.000001Z_00001_data_frequency_hourly": json.dumps(page),
            "20261007T142059.000001Z_00009_erw_lock_check": "true",
            "20261007T142059.000002Z_00010_erw_lock_renew": "false",
            "20261007T142059.000003Z_00011_a_list": "[1, 2]",
            "20261007T142059.000004Z_00012_a_number": "3",
            "20261007T142059.000005Z_00013_response_true": json.dumps({"response": True}),
            "20261007T142059.000006Z_00014_data_null": json.dumps({"response": {"data": None}}),
            "20261007T142059.000007Z_00015_rows_not_rows": json.dumps({"response": {"data": [True, "x"]}}),
            "20261007T142059.000008Z_00016_not_json": "<html>busy</html>",
            "manifest.csv": "retrieved_at,status,bytes,sha256,last_modified,file,url\n",
        })
        with mock.patch.object(self.gn.ip, "RAW_DIR", root):
            names = self.gn.ba_names()
        self.assertEqual(names["SWPP"], "Southwest Power Pool")
        self.assertEqual(names["ERCO"], "Electric Reliability Council of Texas, Inc.")

    def test_the_fault_was_the_bool(self):
        # what the builder did until session 149, on the same four bytes
        with self.assertRaises(AttributeError) as c:
            json.loads("true").get("response", {})
        self.assertIn("'bool' object has no attribute 'get'", str(c.exception))


class StatusListsAGapThatNamesNoDay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for d in ("connectors", "metadata"):
            p = os.path.join(ROOT, "warehouse", d)
            if p not in sys.path:
                sys.path.insert(0, p)
        try:
            import build_status
        except ImportError as exc:
            raise unittest.SkipTest("build_status cannot be imported here: %s" % exc)
        cls.bs = build_status

    def test_a_day_is_a_calendar_day(self):
        for good in ("2026-10-06", "2024-02-29"):
            self.assertTrue(self.bs.is_day(good), good)
        for bad in ("pairs", "", "2026-10-06..2026-10-07", "2026-13-01", "2026-10-06T00", "20261006", None):
            self.assertFalse(self.bs.is_day(bad), bad)

    def test_the_interchange_gap_is_not_read_as_a_day(self):
        # the runner's file: the series columns and the table's own two, which read_series refuses
        ip = self.bs.ip
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "eia930_all_interchange.csv"), "w", encoding="utf-8", newline="\n") as f:
                f.write("# Energy Research Warehouse (ERW): a header line\n" + ",".join(ip.SERIES_COLS + ["ba", "x_to_ba"]) + "\n")
            with mock.patch.object(ip, "OUT_DIR", tmp):
                with self.assertRaises(RuntimeError):  # the refusal that failed the step, still the reader's rule
                    ip.read_series(os.path.join(tmp, "eia930_all_interchange.csv"))
                self.assertIsNone(self.bs.day_complete("eia930_all_interchange", "pairs"))
                self.assertIsNone(self.bs.day_complete("eia930_all_interchange", "2026-10-06"))

    def test_the_builder_lists_such_a_gap(self):
        text = src("warehouse", "metadata", "build_status.py")
        self.assertIn("if not is_day(g.day):", text)
        self.assertIn("listed, not re-checked", text)



if __name__ == "__main__":
    unittest.main()
