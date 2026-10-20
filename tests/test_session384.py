"""Session 384: the data lock released when the daily run's console closes. The run of 20 October ended at 18:06 UTC
with 0xC000013A and held the lock two hours: a console close ends the process before `finally` runs, so lock.py run
registers a console handler that releases the lock on a close, a sign-out or a shutdown."""

import os
import sys
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import lock  # noqa: E402


class FakeKernel:
    def __init__(self):
        self.handlers = []

    def SetConsoleCtrlHandler(self, handler, add):
        self.handlers.append((handler, add))
        return 1


class OnClose(unittest.TestCase):
    def test_a_close_runs_it_once_and_lets_windows_go_on(self):
        k, ran = FakeKernel(), []
        done = lock.on_console_close(lambda: ran.append(1), kernel32=k)
        (handler, add), = k.handlers
        self.assertTrue(add)
        self.assertFalse(handler(0))   # Ctrl+C: Python's own KeyboardInterrupt, then run()'s finally
        self.assertEqual(ran, [])
        self.assertFalse(handler(2))   # the console closed
        self.assertFalse(handler(6))   # and then the shutdown: not twice
        self.assertEqual(ran, [1])
        self.assertTrue(done.is_set())

    def test_sign_out_and_shutdown_count(self):
        for ev in (5, 6):
            k, ran = FakeKernel(), []
            lock.on_console_close(lambda: ran.append(ev), kernel32=k)
            k.handlers[0][0](ev)
            self.assertEqual(ran, [ev])

    def test_a_failed_release_is_said_not_raised(self):
        k = FakeKernel()

        def boom():
            raise RuntimeError("no network")
        done = lock.on_console_close(boom, kernel32=k)
        self.assertFalse(k.handlers[0][0](2))
        self.assertTrue(done.is_set())


class Run(unittest.TestCase):
    def test_released_once_whichever_way_it_ends(self):
        released = []
        with mock.patch.object(lock, "acquire", return_value="tok"), \
             mock.patch.object(lock, "release", side_effect=lambda t: released.append(t)), \
             mock.patch.object(lock.subprocess, "call", return_value=0), \
             mock.patch.object(lock, "on_console_close", return_value=lock.threading.Event()):
            self.assertEqual(lock.run("t", ["x"]), 0)
        self.assertEqual(released, ["tok"])
        done = lock.threading.Event()
        done.set()  # the handler already released it as the console closed
        released.clear()
        with mock.patch.object(lock, "acquire", return_value="tok"), \
             mock.patch.object(lock, "release", side_effect=lambda t: released.append(t)), \
             mock.patch.object(lock.subprocess, "call", return_value=0), \
             mock.patch.object(lock, "on_console_close", return_value=done):
            lock.run("t", ["x"])
        self.assertEqual(released, [])

    def test_off_windows_nothing_is_registered(self):
        with mock.patch.object(lock.os, "name", "posix"):
            self.assertFalse(lock.on_console_close(lambda: None).is_set())


if __name__ == "__main__":
    unittest.main()
