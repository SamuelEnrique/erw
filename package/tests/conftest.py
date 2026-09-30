"""Session 34: the Redivis and Supabase backend tests (test_backends.py, marker `remote`) query the network and take
about ten minutes, so the default run skips them. They run only when asked for:

    python -m pytest package/tests -m remote              # the marker selects them
    ERW_REMOTE_TESTS=1 python -m pytest package/tests     # or the environment variable, with everything else
"""

import os

import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "remote: queries the Redivis or Supabase backend over the network; skipped "
                                       "unless selected with -m remote or ERW_REMOTE_TESTS=1")


def pytest_collection_modifyitems(config, items):
    if os.environ.get("ERW_REMOTE_TESTS") == "1" or "remote" in (config.getoption("-m") or ""):
        return
    skip = pytest.mark.skip(reason="a remote backend test: run with -m remote or ERW_REMOTE_TESTS=1 (session 34)")
    for item in items:
        if "remote" in item.keywords:
            item.add_marker(skip)
