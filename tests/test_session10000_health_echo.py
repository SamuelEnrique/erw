"""Session 10000 (chain 701): warehouse/health.py echoes a child's output without dying on a character the console's
encoding lacks. On 22 and 26 November 2026 the data machine's live set load died partway: its child wrote a cp1252 byte,
health.py read it as the replacement character, and the echo to the cp1252 console raised UnicodeEncodeError. No table
is read."""
import importlib.util
import io
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPLACEMENT = chr(0xFFFD)
EN_DASH = chr(0x2013)
ARROW = chr(0x2192)


def load():
    spec = importlib.util.spec_from_file_location("health_t", os.path.join(ROOT, "warehouse", "health.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def console():
    return io.TextIOWrapper(io.BytesIO(), encoding="cp1252", newline=chr(10))


class TheEchoNeverKillsTheRun(unittest.TestCase):
    def setUp(self):
        self.m = load()

    def test_a_character_the_console_lacks_is_replaced(self):
        out = console()
        self.m.echo(f"match    a table {REPLACEMENT} and {EN_DASH} written" + chr(10), out)
        out.flush()
        self.assertEqual(out.buffer.getvalue().decode("cp1252"), f"match    a table ? and {EN_DASH} written" + chr(10))

    def test_the_child_writes_utf8_and_the_line_survives(self):
        saved = sys.stdout
        sys.stdout = console()
        try:
            code, tail, _ = self.m.attempt([sys.executable, "-c", "print('IEA ' + chr(0x2013) + ' a source'); print(chr(0x2192) + ' next')"])
        finally:
            sys.stdout.flush()
            sys.stdout = saved
        self.assertEqual(code, 0)
        self.assertEqual(tail, [f"IEA {EN_DASH} a source", f"{ARROW} next"])   # read whole: no replacement from a cp1252 byte

    def test_the_child_is_told_its_encoding(self):
        with open(os.path.join(ROOT, "warehouse", "health.py"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn('"PYTHONIOENCODING": "utf-8"', s)
        self.assertNotIn("        sys.stdout.write(line)" + chr(10), s)


if __name__ == "__main__":
    unittest.main()
