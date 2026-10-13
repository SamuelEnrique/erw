"""Session 197: the planner (scripts/planner.py), built and unarmed. What is held to, with a sample roadmap
(tests/fixtures/roadmap_sample.md) in a folder of its own, never the repository's queue:

  it refuses, and says why, when the planner is off, when the roadmap is older than 7 days, when queue/next/ holds a
    file, when the machine is at its budget of sessions for the day, when the hour is outside the start hours, when
    "Status" does not state the cutoffs, and when "This week" has no open item for the machine that was not planned;
  the hard stops: an item that names a pull, a migration, a secret, a release-gate change, a change to CLAUDE.md or a
    deletion is refused; a chain holds one to three sessions and at most one lands; the deploy cutoffs and the start
    hours are copied into every chain; a chain that fails its own checks is not written;
  when on, it drafts a valid chain file: its name passes the chain queue's own rule, its first line says it was
    planned, its first rule is the precheck, its last rule is the queue step, it has no em dash and no unfilled blank,
    the item's rulings and the roadmap's Rulings and Holds are pasted as they stand;
  --dry-run writes nothing; an item is planned once;
  the queue's closing step: with nothing waiting and the planner on, the planned chain is committed, pushed to a wip/
    branch and taken; with the planner off, which is the default, the machine idles exactly as before;
  the repository's own docs/roadmap.md is the empty template, so the planner is off here.

No request, no model call, nothing sent: every sender, git and clock is a stand-in. The environment is read, never set."""
import datetime as dt
import io
import os
import re
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import chain_queue  # noqa: E402
import planner  # noqa: E402

EM = chr(0x2014)
UTC = dt.timezone.utc
NOW = dt.datetime(2026, 10, 12, 14, 30, tzinfo=UTC)          # inside the sample's start hours (13:00 to 05:00 UTC)
SAMPLE = os.path.join(ROOT, "tests", "fixtures", "roadmap_sample.md")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Folder(unittest.TestCase):
    """A folder that looks like the repository to the planner: the sample roadmap, the real template, an empty queue."""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="erw_planner_")
        for d in ("docs", "queue/next", "queue/done", "archive/sessions", "site/content"):
            os.makedirs(os.path.join(self.root, *d.split("/")))
        self.roadmap = os.path.join(self.root, "docs", "roadmap.md")
        shutil.copy(SAMPLE, self.roadmap)
        shutil.copy(os.path.join(ROOT, "queue", "CHAIN_TEMPLATE.md"), os.path.join(self.root, "queue", "CHAIN_TEMPLATE.md"))
        for n in (193, 194):
            with open(os.path.join(self.root, "archive", "sessions", f"SESSION_{n}_REPORT.md"), "w", encoding="utf-8") as f:
                f.write(f"# Session {n} report\n")
        with open(os.path.join(self.root, "archive", "sessions", "LAST_ANSWERED"), "w", encoding="utf-8") as f:
            f.write("# a note\nlast_answered: 193\non: 2026-10-11\n")
        self.said = []

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def edit(self, old, new):
        with open(self.roadmap, encoding="utf-8") as f:
            text = f.read()
        self.assertIn(old, text)
        with open(self.roadmap, "w", encoding="utf-8", newline="\n") as f:
            f.write(text.replace(old, new))

    def run_planner(self, action="draft", dry_run=False, now=NOW, sessions=0, machine="testbox", role="code"):
        self.said = []
        code, dest = planner.run(action, machine, role, dry_run=dry_run, now=now, root=self.root, out=self.said.append, sessions=lambda m, t: sessions)
        return code, dest

    def text(self):
        return "\n".join(str(x) for x in self.said)


class ItRefuses(Folder):
    def test_when_the_planner_is_off(self):
        self.edit("- planner: on", "- planner: off")
        code, dest = self.run_planner()
        self.assertEqual((code, dest), (planner.REFUSED, None))
        self.assertEqual(self.said[0], "planner: off")
        self.assertIn("Only a person turns it on", self.text())
        self.assertEqual(os.listdir(os.path.join(self.root, "queue", "next")), [])

    def test_off_is_the_default_and_anything_but_on_is_off(self):
        for line in ("", "- planner: yes", "- planner: ON please", "- planner:"):
            shutil.copy(SAMPLE, self.roadmap)
            self.edit("- planner: on", line)
            self.assertFalse(planner.status(open(self.roadmap, encoding="utf-8").read())["on"], line)
            self.assertEqual(self.run_planner()[0], planner.REFUSED, line)

    def test_when_the_roadmap_is_older_than_seven_days(self):
        old = (NOW - dt.timedelta(days=8)).timestamp()
        os.utime(self.roadmap, (old, old))
        self.assertEqual(self.run_planner()[0], planner.REFUSED)
        self.assertIn("older than 7 days", self.text())
        fresh = (NOW - dt.timedelta(days=6, hours=23)).timestamp()
        os.utime(self.roadmap, (fresh, fresh))
        self.assertEqual(self.run_planner(action="check")[0], 0)

    def test_when_the_queue_already_holds_a_file(self):
        with open(os.path.join(self.root, "queue", "next", "195-night-of-12-october.md"), "w", encoding="utf-8") as f:
            f.write("# Chain\n\n## Session 195: x\n")
        self.assertEqual(self.run_planner()[0], planner.REFUSED)
        self.assertIn("queue/next/ already holds a file (195-night-of-12-october.md)", self.text())

    def test_when_the_machine_is_at_its_budget(self):
        self.assertEqual(self.run_planner(sessions=3)[0], planner.REFUSED)
        self.assertIn("the budget is reached: testbox has 3 sessions for 2026-10-12 UTC, and the budget is 3 a day per machine", self.text())
        self.assertEqual(self.run_planner(sessions=4)[0], planner.REFUSED)
        self.assertEqual(self.run_planner(action="check", sessions=2)[0], 0)

    def test_outside_the_start_hours(self):
        for hour, ok in ((13, True), (23, True), (0, True), (5, True), (6, False), (9, False), (12, False)):
            code, _ = self.run_planner(action="check", now=NOW.replace(hour=hour, minute=0))
            self.assertEqual(code == 0, ok, hour)
        self.run_planner(now=NOW.replace(hour=9, minute=15))
        self.assertIn("it is 09:15 UTC: a session may start from 13:00 to 05:00 UTC", self.text())

    def test_when_status_does_not_state_a_stop(self):
        for line, words in (("- budget: 3 sessions a day per machine", "does not state the budget"), ("- latest start: 05:00 UTC", "does not state the latest hour"),
                            ("- earliest start: 13:00 UTC", "does not state the earliest hour"), ("- deploy cutoffs: 22:30 to 23:45 UTC; 16:45 to 17:30 UTC", "does not state the deploy cutoffs")):
            shutil.copy(SAMPLE, self.roadmap)
            self.edit(line, "")
            self.assertEqual(self.run_planner()[0], planner.REFUSED, line)
            self.assertIn(words, self.text())
        shutil.copy(SAMPLE, self.roadmap)
        self.edit("- deploy cutoffs: 22:30 to 23:45 UTC; 16:45 to 17:30 UTC", "- deploy cutoffs: after lunch")
        self.assertEqual(self.run_planner()[0], planner.REFUSED)
        self.assertIn("a deploy cutoff cannot be read", self.text())

    def test_when_this_week_has_no_open_item_for_the_machine(self):
        self.edit("3. [ ] The battery page", "3. [x] The battery page")
        self.edit("4. [ ] The generator page", "4. [x] The generator page")
        self.assertEqual(self.run_planner()[0], planner.REFUSED)
        self.assertIn('"This week" has no open item for testbox (code)', self.text())
        # the data machine has its own open item, and a machine with no role is refused
        self.assertEqual(self.run_planner(action="check", role="data")[0], 0)
        self.assertEqual(self.run_planner(role=None)[0], planner.REFUSED)
        self.assertIn("the machine's role is not known", self.text())


class TheHardStops(Folder):
    def test_what_a_planned_chain_never_names(self):
        base = {"words": []}
        for words, what in (("pull the PJM queue reports", "a pull"), ("download the tariff files", "a pull"), ("add migration 031 for the new table", "a migration"),
                            ("rotate the API key", "a secret"), ("read the token from .env", "a secret"), ("make /storage live", "a release-gate change"),
                            ("edit site/lib/release.ts", "a release-gate change"), ("remove REVIEW_FREEZE", "a release-gate change"), ("add a rule to CLAUDE.md", "a change to CLAUDE.md or to a permission file"),
                            ("allow it in .claude/settings.json", "a change to CLAUDE.md or to a permission file"), ("delete the old branch", "a deletion"), ("drop the table of 2019", "a deletion")):
            found = [w for w, _ in planner.never(dict(base, words=[words]))]
            self.assertIn(what, found, words)
        for words in ("the battery page says which strategy its headline is", "the face check at two widths, the Method note, and the landing", "the page stays in review"):
            self.assertEqual(planner.never(dict(base, words=[words])), [], words)

    def test_an_item_that_names_one_is_refused_not_skipped(self):
        self.edit("   - session: write the sentence and its test, on a local build", "   - session: pull the operator's monthly report, then write the sentence")
        self.assertEqual(self.run_planner()[0], planner.REFUSED)
        self.assertIn('names a pull ("pull")', self.text())
        self.assertEqual(os.listdir(os.path.join(self.root, "queue", "next")), [])    # the next item is not taken in its place

    def test_one_to_three_sessions_and_an_item_that_says_where_and_done(self):
        self.edit("   - session: write the sentence and its test, on a local build", "   - session: one\n   - session: two\n   - session: three")
        self.assertEqual(self.run_planner()[0], planner.REFUSED)
        self.assertIn("asks for 4 sessions: a planned chain holds one to 3", self.text())
        shutil.copy(SAMPLE, self.roadmap)
        self.edit("   - where: /cost-of-power/battery\n", "")
        self.assertEqual(self.run_planner()[0], planner.REFUSED)
        self.assertIn("does not say where", self.text())

    def test_a_chain_that_fails_its_own_checks_is_named(self):
        self.run_planner()
        name = os.listdir(os.path.join(self.root, "queue", "next"))[0]
        good = open(os.path.join(self.root, "queue", "next", name), encoding="utf-8").read()
        cut = [(22 * 60 + 30, 23 * 60 + 45), (16 * 60 + 45, 17 * 60 + 30)]
        self.assertEqual(planner.problems_of(name, good, cut), [])
        bad = planner.problems_of
        self.assertIn("an em dash", bad(name, good + EM, cut))
        self.assertIn("more than one session lands", bad(name, good + "\n- **Landing: this session lands**, again.\n", cut))
        self.assertTrue(any("sessions: a planned chain holds one to 3" in p for p in bad(name, good + "\n## Session 301: a\n\n## Session 302: b\n", cut)))
        self.assertTrue(any("was not filled" in p for p in bad(name, good.replace("USD 0.", "USD <total>.", 1), cut)))
        self.assertIn("the first rule is not the precheck", bad(name, good.replace("1. **Precheck first.**", "1. **Start.**"), cut))
        self.assertIn("the last rule is not the queue step", bad(name, good.replace("python scripts/chain_queue.py next", "stop"), cut))
        self.assertIn("the deploy cutoff 22:30 to 23:45 UTC is not in the chain", bad(name, good.replace("22:30 to 23:45 UTC", "late"), cut))
        self.assertTrue(any("does not say that it approves no pull" in p for p in bad(name, good.replace("**Pulls:** none.", "**Pulls:** some."), cut)))
        self.assertTrue(any("is not NNN-planned-<slug>.md" in p for p in bad("199-code-x.md", good, cut)))
        self.assertTrue(any("is not NNN-planned-<slug>.md" in p for p in bad("planned.md", good, cut)))


class ItDrafts(Folder):
    def draft(self):
        code, dest = self.run_planner()
        self.assertEqual(code, 0, self.text())
        with open(dest, encoding="utf-8") as f:
            return os.path.basename(dest), f.read()

    def test_a_valid_chain_file(self):
        name, text = self.draft()
        self.assertEqual(name, "195-planned-the-battery-page-says-which-strategy-its.md")    # the next free session number, then "planned"
        self.assertTrue(chain_queue.NAME_RE.match(name) and not chain_queue.TASK_RE.match(name))
        self.assertEqual(chain_queue.waiting(self.root), ([name], []))                         # the chain queue takes it
        first = text.split("\n")[0]
        self.assertTrue(first.startswith("PLANNED by scripts/planner.py from docs/roadmap.md as of 2026-10-12 14:30 UTC"), first)
        self.assertNotIn(EM, text)
        rules = re.findall(r"(?m)^(\d+)\. (.+)$", text[text.index("## Rules for every session of this chain"):text.index("## What the owner has ruled")])
        self.assertEqual([int(n) for n, _ in rules], list(range(1, len(rules) + 1)))
        self.assertTrue(rules[0][1].startswith("**Precheck first.**") and 'python scripts/precheck.py --what "session <N>"' in rules[0][1])
        self.assertTrue(rules[-1][1].startswith("**Last step of the last session: the queue.**") and "python scripts/chain_queue.py next" in rules[-1][1])
        # every rule of the template is there, in its words, but for the three the planner fills
        template = planner.template_rules(src("queue", "CHAIN_TEMPLATE.md"))
        self.assertEqual(len(rules), len(template))
        kept = 0
        for (_, got), want in zip(rules, template):
            if "<Any rule of this chain alone" in want or want.startswith("**Pulls:**") or "USD <total>" in want:
                continue
            self.assertEqual(got, want)
            kept += 1
        self.assertEqual(kept, len(template) - 3)
        self.assertIsNone(re.search(r"<(?!N>)[A-Za-z][^>\n]*>", text))                         # no blank of the template is left

    def test_the_stops_of_status_are_in_the_chain(self):
        _, text = self.draft()
        self.assertIn("No session starts outside the start hours, from 13:00 to 05:00 UTC", text)
        self.assertIn("No landing in a deploy cutoff (22:30 to 23:45 UTC; 16:45 to 17:30 UTC)", text)
        self.assertIn("**Pulls:** none. This chain approves no pull.", text)
        self.assertIn("Total for the chain: USD 0.", text)
        self.assertIn("no pull, no migration, no secret, no change to `site/lib/release.ts` or to any release gate, no change to `CLAUDE.md` or to a permission file, and no deletion", text)

    def test_the_roadmaps_words_are_pasted_as_they_stand(self):
        _, text = self.draft()
        self.assertIn("Roadmap item: 3. The battery page says which strategy its headline is", text)
        for words in ("- Ruling already made: the sentence states the strategy and the window; it recommends nothing (Samuel, 11 October 2026)", "- Ruling already made: the page stays in review",
                      "- 11 October 2026: a page states what the reader can decide with; it recommends nothing.", "- 11 October 2026: every page stays in review until Samuel says otherwise.",
                      "- video/ and the Roundup workflow.", "- The scanner's thresholds.",
                      "- Done means, in the roadmap's words: check-battery-face.mjs passes on a local build and on production, and the face check at 1280 and 390 px reads the sentence from the page"):
            self.assertIn(words, text, words)
        self.assertNotIn("Ben", text)                                                          # the input and the review log are read by people only
        self.assertNotIn("The sample was written", text)
        self.assertIn("The last report whose rulings the owner has answered: session 193", text)
        self.assertIn("1 report after it on this branch: SESSION_194_REPORT.md", text)

    def test_two_sessions_numbered_from_the_next_free_one_and_one_landing(self):
        _, text = self.draft()
        self.assertEqual(re.findall(r"(?m)^## Session (\d+): (.+)$", text), [("195", "write the sentence and its test, on a local build"), ("196", "the face check at two widths, the Method note, and the landing")])
        self.assertEqual(text.count("**Landing: this session lands**"), 1)
        self.assertLess(text.index("## Session 196"), text.index("**Landing: this session lands**"))    # the last session's
        self.assertIn("Branch `wip/195-", text)
        self.assertIn("Branch `task/196-", text)
        self.assertIn("This session does not land: it leaves its work on its `wip/` branch", text)
        self.assertEqual(text.count("Model spend cap USD 0. Pulls: none."), 2)

    def test_a_cap_named_by_the_item_and_a_table_that_does_not_land(self):
        self.edit("   - rulings: the page stays in review", "   - rulings: the page stays in review\n   - cap: USD 3")
        _, text = self.draft()
        self.assertIn("Total for the chain: USD 3.", text)
        self.assertEqual(text.count("Model spend cap USD 1.5. Pulls: none."), 2)
        self.said = []
        code, dest = planner.run("draft", "databox", "data", now=NOW, root=os.path.join(self.root), out=self.said.append, sessions=lambda m, t: 0)
        self.assertEqual(code, planner.REFUSED)                                                # the queue now holds the first chain
        os.remove(os.path.join(self.root, "queue", "next", os.listdir(os.path.join(self.root, "queue", "next"))[0]))
        code, dest = planner.run("draft", "databox", "data", now=NOW, root=self.root, out=self.said.append, sessions=lambda m, t: 0)
        self.assertEqual(code, 0, "\n".join(self.said))
        data = open(dest, encoding="utf-8").read()
        self.assertIn("Roadmap item: 2. The storage table gains its September rows", data)
        self.assertNotIn("**Landing: this session lands**", data)                              # a table is not a page: nothing lands
        self.assertIn("**This session does not land.**", data)

    def test_dry_run_prints_the_file_and_writes_nothing(self):
        code, dest = self.run_planner(dry_run=True)
        self.assertEqual((code, dest), (0, None))
        self.assertEqual(os.listdir(os.path.join(self.root, "queue", "next")), [])
        self.assertIn("would write queue/next/195-planned-the-battery-page-says-which-strategy-its.md:", self.text())
        self.assertIn("PLANNED by scripts/planner.py from docs/roadmap.md as of ", self.text())

    def test_an_item_is_planned_once(self):
        name, _ = self.draft()
        shutil.move(os.path.join(self.root, "queue", "next", name), os.path.join(self.root, "queue", "done", name))    # the chain was taken
        code, dest = self.run_planner()
        self.assertEqual(code, 0, self.text())
        second = open(dest, encoding="utf-8").read()
        self.assertIn("Roadmap item: 4. The generator page lists its hubs by region", second)
        self.assertEqual(re.findall(r"(?m)^## Session (\d+)", second), ["197"])               # after the first chain's 195 and 196
        shutil.move(dest, os.path.join(self.root, "queue", "done", os.path.basename(dest)))
        self.assertEqual(self.run_planner()[0], planner.REFUSED)
        self.assertIn("that was not planned before: 2 open, each already in a planned chain", self.text())


class TheQueueStep(Folder):
    """scripts/chain_queue.py, `next`, with nothing waiting."""

    def take(self, **kw):
        said, calls = [], {"rec": 0, "send": 0, "off": 0, "git": []}

        def git(*args, root=None):
            calls["git"].append(args)
            return ""

        def plan(who, root, dry_run, out):
            return chain_queue.plan(who, root, dry_run, out, git=git, role="code", now=NOW)        # the sample's start hours, not the clock's (session 201)

        def mover(name, who, root):
            shutil.move(os.path.join(root, "queue", "next", name), os.path.join(root, "queue", "done", name))
            return f"queue/done/{name}"

        code = chain_queue.take(root=self.root, who="testbox", now=NOW, out=said.append, mover=mover, planner=kw.get("planner", plan),
                                rec=lambda *a, **k: calls.__setitem__("rec", calls["rec"] + 1) or True,
                                send=lambda *a, **k: calls.__setitem__("send", calls["send"] + 1) or 1,
                                off=lambda: calls.__setitem__("off", calls["off"] + 1) or "off duty", dry_run=kw.get("dry_run", False))
        return code, said, calls

    def test_with_the_planner_off_the_machine_idles_as_before(self):
        self.edit("- planner: on", "- planner: off")
        code, said, calls = self.take()
        self.assertEqual(code, chain_queue.IDLE_EXIT)
        self.assertEqual((calls["rec"], calls["send"], calls["off"], calls["git"]), (1, 1, 1, []))
        self.assertEqual(os.listdir(os.path.join(self.root, "queue", "next")), [])

    def test_with_no_roadmap_at_all_it_idles_as_before(self):
        os.remove(self.roadmap)
        code, _, calls = self.take()
        self.assertEqual((code, calls["git"]), (chain_queue.IDLE_EXIT, []))

    def test_with_the_planner_on_the_planned_chain_is_committed_pushed_and_taken(self):
        stamp = planner.sessions_today
        planner.sessions_today = lambda *a, **k: 0          # a folder that is not a repository has no history to count
        try:
            code, said, calls = self.take()
        finally:
            planner.sessions_today = stamp
        self.assertEqual(code, 0, "\n".join(str(s) for s in said))
        name = os.listdir(os.path.join(self.root, "queue", "done"))[0]
        self.assertRegex(name, r"^195-planned-")
        self.assertEqual([a[0] for a in calls["git"]], ["add", "commit", "push"])
        self.assertEqual(calls["git"][1][-1], f"queue/next/{name}")                            # the commit holds the planned file alone
        self.assertEqual(calls["git"][2], ("push", "origin", f"HEAD:refs/heads/wip/{name[:-3]}"))   # a wip/ branch: no deploy
        self.assertTrue(str(said[-1]).endswith(os.path.join("queue", "done", name)))           # the path, on the last line
        self.assertEqual((calls["rec"], calls["send"], calls["off"]), (0, 0, 0))               # not idle

    def test_when_the_planner_refuses_the_machine_idles(self):
        self.edit("- budget: 3 sessions a day per machine", "- budget: 0 sessions a day per machine")
        code, said, calls = self.take()
        self.assertEqual(code, chain_queue.IDLE_EXIT)
        self.assertIn("the budget is reached", "\n".join(str(s) for s in said))
        self.assertEqual((calls["rec"], calls["send"], calls["off"], calls["git"]), (1, 1, 1, []))

    def test_a_planner_that_breaks_does_not_break_the_queue(self):
        def broken(*a):
            raise RuntimeError("no")
        err, sys.stderr = sys.stderr, io.StringIO()
        try:
            code, _, calls = self.take(planner=broken)
        finally:
            sys.stderr = err
        self.assertEqual((code, calls["off"]), (chain_queue.IDLE_EXIT, 1))

    def test_dry_run_says_what_the_planner_would_do_and_writes_nothing(self):
        code, said, calls = self.take(dry_run=True)
        self.assertEqual(code, chain_queue.IDLE_EXIT)
        self.assertEqual(calls["git"], [])
        self.assertEqual(os.listdir(os.path.join(self.root, "queue", "next")), [])
        self.assertIn("the planner is on (docs/roadmap.md)", "\n".join(str(s) for s in said))


class TheRepositorysOwn(unittest.TestCase):
    def test_the_roadmap_keeps_its_six_headings_and_the_planner_can_read_it(self):
        # Session 201 filled the template of session 197 with Samuel's roadmap; session 209 added the seventh heading, Backlog. A person turns the planner on and
        # off and rewrites the items, so neither is pinned here: only what the planner needs to read the file.
        text = src("docs", "roadmap.md")
        self.assertEqual(tuple(planner.sections(text)), planner.SECTIONS)
        for name, lines in planner.sections(text).items():
            body = [x for x in lines if x.strip()]
            self.assertTrue(body and body[0].startswith("What goes here"), name)               # each still opens with the line that says what goes there
        self.assertNotIn(EM, text)
        s = planner.status(text)
        self.assertIsInstance(planner.items(text), list)
        said = []
        code, dest = planner.run("check", "samueloldlaptop", "code", now=NOW, out=said.append, sessions=lambda m, t: 0)
        self.assertIn(code, (0, planner.REFUSED))
        self.assertIsNone(dest)                                                                # a check writes nothing
        self.assertEqual(said[0], "planner: on" if s["on"] else "planner: off")

    def test_the_sample_is_not_the_roadmap(self):
        self.assertTrue(planner.status(src("tests", "fixtures", "roadmap_sample.md"))["on"])
        self.assertIn("not the roadmap", src("tests", "fixtures", "roadmap_sample.md").split("\n")[0])

    def test_no_model_call_and_no_request(self):
        code = re.sub(r'(?s)""".*?"""', "", src("scripts", "planner.py"))
        for word in ("anthropic", "requests", "urllib", "http", "openai", "claude -p", "subprocess.run([\"claude"):
            self.assertNotIn(word, code, word)
        self.assertEqual(re.findall(r'subprocess\.run\(\[("[a-z]+")', code), ['"git"'])          # git, to read history; nothing else is run

    def test_the_template_and_the_documents_say_it(self):
        last = planner.template_rules(src("queue", "CHAIN_TEMPLATE.md"))[-1]
        self.assertIn("With `planner: on` in `docs/roadmap.md` (it is off unless a person turned it on), the same command first runs `python scripts/planner.py draft`", last)
        self.assertIn("### The planner", src("docs", "machines.md"))
        self.assertLess(src("docs", "machines.md").index("## Continuous work"), src("docs", "machines.md").index("### The planner"))
        self.assertIn("## The planner (session 197)", src("queue", "README.md"))
        self.assertIn("python scripts/planner.py check", src("queue", "README.md"))

    def test_no_em_dash_in_what_the_session_wrote(self):
        for f in ("scripts/planner.py", "scripts/chain_queue.py", "queue/CHAIN_TEMPLATE.md", "queue/README.md", "docs/roadmap.md", "docs/machines.md",
                  "tests/fixtures/roadmap_sample.md", "tests/test_planner.py", "archive/sessions/SESSION_197_REPORT.md"):
            if os.path.exists(os.path.join(ROOT, *f.split("/"))):
                self.assertNotIn(EM, src(*f.split("/")), f)


if __name__ == "__main__":
    unittest.main()
