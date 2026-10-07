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


if __name__ == "__main__":
    unittest.main()
