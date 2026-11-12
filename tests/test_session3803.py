"""Session 3803 (chain 215): the data machine's push goes on when the catalogue is the one file its rebase cannot merge.

On 12 November 2026 chain 215's landing reached main between the data machine's sync and its push; both had rewritten
package/llms.txt's header, so `git pull --rebase` stopped on that file and the day's page files stayed on the machine.
warehouse/run_data_machine.sh now writes the catalogue again from the merged metadata (scripts/build_llms.py) when it is
the one unmerged file, and goes on; any other conflict still stops the push.

The test runs the script's own lines (from `git pull --rebase` to the block's end) in a scratch repository with a real
conflict, a stand-in build_llms.py writing the file. Needs git and bash; no network, no warehouse table, no model.
"""
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.join(ROOT, "warehouse", "run_data_machine.sh")
BASH = shutil.which("bash")
GIT = shutil.which("git")


def snippet():
    with open(RUN, encoding="utf-8") as f:
        t = f.read()
    a = t.index("git pull --rebase --quiet origin main\n")
    b = t.index('  echo "main moved in a way the commit could not follow')
    block = t[a:b] + '  echo "STOPPED"\nfi\necho "rc=$rc"\n'
    return block


def git(cwd, *args):
    return subprocess.run([GIT, "-c", "user.email=t@t", "-c", "user.name=t", *args], cwd=cwd, capture_output=True, text=True)


@unittest.skipIf(not BASH or not GIT, "bash or git is not here")
class TheCatalogueConflict(unittest.TestCase):
    def repos(self, other_file):
        d = tempfile.mkdtemp()
        origin, a, b = (os.path.join(d, x) for x in ("origin.git", "a", "b"))
        git(d, "init", "--bare", "-b", "main", origin)
        git(d, "clone", origin, a)
        os.makedirs(os.path.join(a, "package"))
        os.makedirs(os.path.join(a, "scripts"))
        for p, s in (("package/llms.txt", "Generated: 1\nrows\n"), ("other.txt", "one\n"),
                     ("scripts/build_llms.py", "open('package/llms.txt','w').write('Generated: merged\\nrows\\n')\n")):
            with open(os.path.join(a, p), "w", encoding="utf-8", newline="\n") as f:
                f.write(s)
        git(a, "add", "-A")
        git(a, "commit", "-m", "base")
        git(a, "push", "origin", "main")
        git(d, "clone", origin, b)
        # main moves: the catalogue's header (and, in the second case, another file too)
        with open(os.path.join(a, "package", "llms.txt"), "w", encoding="utf-8", newline="\n") as f:
            f.write("Generated: 2\nrows\n")
        if other_file:
            with open(os.path.join(a, "other.txt"), "w", encoding="utf-8", newline="\n") as f:
                f.write("two\n")
        git(a, "commit", "-am", "landing")
        git(a, "push", "origin", "main")
        # the machine's commit
        with open(os.path.join(b, "package", "llms.txt"), "w", encoding="utf-8", newline="\n") as f:
            f.write("Generated: 3\nrows\n")
        if other_file:
            with open(os.path.join(b, "other.txt"), "w", encoding="utf-8", newline="\n") as f:
                f.write("three\n")
        git(b, "commit", "-am", "page files")
        return b

    def run_block(self, cwd):
        env = dict(os.environ, PYTHON=shutil.which("python") or "python",
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        return subprocess.run([BASH, "-c", snippet()], cwd=cwd, capture_output=True, text=True, env=env)

    def test_the_catalogue_alone_is_written_again_and_the_rebase_goes_on(self):
        b = self.repos(other_file=False)
        p = self.run_block(b)
        self.assertIn("rc=0", p.stdout, p.stdout + p.stderr)
        self.assertNotIn("STOPPED", p.stdout)
        log = git(b, "log", "--format=%s").stdout.split()
        self.assertEqual(log[:3], ["page", "files", "landing"])
        with open(os.path.join(b, "package", "llms.txt"), encoding="utf-8") as f:
            self.assertEqual(f.read(), "Generated: merged\nrows\n")

    def test_another_conflict_still_stops_the_push(self):
        b = self.repos(other_file=True)
        p = self.run_block(b)
        self.assertIn("STOPPED", p.stdout, p.stdout + p.stderr)
        self.assertNotIn("rc=0", p.stdout)


if __name__ == "__main__":
    unittest.main()
