"""Session 185: the two PowerShell scripts that register and remove the data machine's daily run.

The register script (scripts/register_data_machine_daily.ps1) names one task, runs the command of docs/machines.md
under the data lock, holds no secret, refuses to register a run that would count ERCOT's rows from zero (no
warehouse/raw/ercot_zone_prices/manifest.csv) unless it is registered switched off, and makes a push that needs a
sign-in fail at once. The unregister script is safe when the task is absent and does not stop a run that holds the
lock. No test registers anything and none reaches the network: the one test that starts PowerShell runs -DryRun
against a made-up checkout whose role is "code", which the script refuses before anything else.
"""

import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REGISTER = os.path.join(ROOT, "scripts", "register_data_machine_daily.ps1")
UNREGISTER = os.path.join(ROOT, "scripts", "unregister_data_machine_daily.ps1")
RUN = os.path.join(ROOT, "warehouse", "run_data_machine.sh")
BASH = "C:\\Program Files\\Git\\bin\\bash.exe"


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def code(text):
    """The script without its comment lines."""
    return "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))


class TestTheRegisterScript(unittest.TestCase):
    def setUp(self):
        self.text = read(REGISTER)
        self.code = code(self.text)

    def test_it_names_one_task_and_replaces_it(self):
        self.assertIn('$TaskName = "ERW data machine daily"', self.code)
        self.assertEqual(self.code.count("Register-ScheduledTask"), 1)
        self.assertIn("-Force", self.code.split("Register-ScheduledTask", 1)[1].splitlines()[0])

    def test_it_runs_the_documented_command_under_the_lock(self):
        for part in ("warehouse/lock.py run --task 'data machine daily' --wait 60 -- bash warehouse/run_data_machine.sh",
                     ">> runs/data_machine_daily.out 2>&1", ".venv/Scripts/python.exe"):
            self.assertIn(part, self.code)
        self.assertTrue(os.path.exists(RUN))
        self.assertIn("warehouse/lock.py run --task \"data machine daily\" --wait 60 -- bash warehouse/run_data_machine.sh", read(RUN))

    def test_a_push_that_needs_a_sign_in_cannot_wait_under_the_lock(self):
        self.assertIn("GCM_INTERACTIVE=never GIT_TERMINAL_PROMPT=0 .venv/Scripts/python.exe warehouse/lock.py run", self.code)

    def test_it_refuses_a_run_that_would_count_from_zero(self):
        self.assertIn('"warehouse\\raw\\ercot_zone_prices\\manifest.csv"', self.code)
        self.assertIn("if (-not $counted -and -not $Disabled)", self.code)
        refusal = self.code.split("if (-not $counted -and -not $Disabled)", 1)[1].split("}", 1)[0]
        self.assertIn("NOT REGISTERED", refusal)
        self.assertIn("exit 1", refusal)
        self.assertLess(self.code.index("if (-not $counted -and -not $Disabled)"), self.code.index("Register-ScheduledTask"))
        self.assertIn("$settings.Enabled = $false", self.code)

    def test_it_refuses_a_machine_that_is_not_the_data_machine(self):
        self.assertIn("role", self.code)
        self.assertIn("this machine's role is not data", self.code)
        for t in ("ercot_all_hub_prices_history", "ercot_zone_prices_history", "iso_zone_prices_history"):
            self.assertIn(t, self.code)

    def test_the_dry_run_ends_before_anything_is_registered(self):
        self.assertLess(self.code.index("if ($DryRun)"), self.code.index("Register-ScheduledTask"))

    def test_its_root_is_the_checkout_it_is_in_and_no_persons_path(self):
        self.assertIn("[string]$Root = (Split-Path -Parent $PSScriptRoot)", self.code)
        self.assertNotIn("C:\\Users\\lossa", self.code)

    def test_it_holds_no_secret_and_reads_no_key(self):
        for word in ("SUPABASE", "GH_TOKEN", "API_KEY", "REDIVIS_API_TOKEN", ".env\"", "Get-Content"):
            self.assertNotIn(word, self.code)

    def test_no_startup_trigger_no_elevation_no_late_start(self):
        self.assertIn("-LogonType Interactive -RunLevel Limited", self.code)
        for word in ("-AtStartup", "S4U", "Highest", "-StartWhenAvailable", "-WakeToRun"):
            self.assertNotIn(word, self.code)
        self.assertIn("-MultipleInstances IgnoreNew", self.code)
        self.assertIn("-ExecutionTimeLimit (New-TimeSpan -Hours 6)", self.code)

    def test_a_dry_run_on_a_machine_whose_role_is_code_registers_nothing(self):
        if os.name != "nt" or not shutil.which("powershell") or not os.path.exists(BASH):
            self.skipTest("Windows PowerShell and Git Bash are not here")
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, ".venv", "Scripts"))
            os.makedirs(os.path.join(d, "warehouse"))
            # a stand-in for python.exe that answers lock.py role as a code machine does
            fake = os.path.join(d, ".venv", "Scripts", "python.exe")
            shutil.copy(os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "cmd.exe"), fake)
            open(os.path.join(d, "warehouse", "run_data_machine.sh"), "w").close()
            open(os.path.join(d, "warehouse", "lock.py"), "w").close()
            r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", REGISTER, "-Root", d, "-DryRun"],
                               capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("NOT REGISTERED: this machine's role is not data", r.stdout)
        self.assertNotIn("REGISTERED: 1 task", r.stdout)


class TestTheUnregisterScript(unittest.TestCase):
    def setUp(self):
        self.code = code(read(UNREGISTER))

    def test_it_is_safe_when_the_task_is_absent(self):
        self.assertIn("nothing to remove", self.code)
        self.assertLess(self.code.index("nothing to remove"), self.code.index("Unregister-ScheduledTask"))

    def test_it_does_not_stop_a_run_that_holds_the_lock(self):
        self.assertNotIn("Stop-ScheduledTask", self.code)
        running = self.code.split('if ($task.State -eq "Running")', 1)[1].split("}", 1)[0]
        self.assertIn("exit 1", running)

    def test_it_removes_nothing_but_the_task(self):
        for word in ("Remove-Item", "del ", "rmdir"):
            self.assertNotIn(word, self.code)


class TestTheText(unittest.TestCase):
    def test_no_em_dash_in_this_sessions_files(self):
        for p in (REGISTER, UNREGISTER, os.path.abspath(__file__)):
            self.assertNotIn(chr(0x2014), read(p), p)
            self.assertNotIn(chr(0x2013), read(p), p)


if __name__ == "__main__":
    unittest.main()
