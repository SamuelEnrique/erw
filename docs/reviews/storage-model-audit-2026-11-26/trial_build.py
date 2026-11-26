"""Session 10212 (storage audit): the page's three derived tables rebuilt by their own builders in a trial folder.

    python trial_build.py <worktree root> <trial dir>

Every output (CSVs, logs, registry, status) goes under the trial folder (iso_prices.set_out_dir): nothing is written to
warehouse/output, so no data lock is needed. The builders are the worktree's, unchanged.
"""
import os
import sys

root, trial = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
sys.path.insert(0, os.path.join(root, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(root, "warehouse", "derived"))
import iso_prices as ip  # noqa: E402

ip.set_out_dir(trial)
import storage_capacity  # noqa: E402
import storage_daily_cycle  # noqa: E402
import storage_buildout  # noqa: E402

print("storage_capacity", storage_capacity.main())
print("storage_daily_cycle", storage_daily_cycle.main())
print("storage_buildout", storage_buildout.main(["--inputs-dir", trial, "--out-dir", trial]))
