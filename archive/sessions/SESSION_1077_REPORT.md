# Session 1077 report: the package's install and README, read again

23 October 2026, about 09:45 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-1064` on `wip/1064-allgrids`. Chain `queue/done/073-evening-23-october-code-allgrids-packages-3.md`, session 1077. Model spend USD 0. No request; nothing uploaded. Outside the repository: `%TEMP%\erw1077` (the wheel, a venv).

- **The wheel, rebuilt offline from this branch's `package/`** (`pip wheel --no-deps --no-index --no-build-isolation`): `erw_energy-0.1.0-py3-none-any.whl`, installed with `--no-index --no-deps` in a clean venv.
- **From the clean venv** (`ERW_DATA_DIR` on the main checkout's tables, pandas lent through `PYTHONPATH`, as 1035 did): session 1002's five-table test answers (346 tables listed), and the README's example runs as written (`runs/s1035_readme.py`: every call answers, 0 requests).
- **Session 1056's new errors from the installed wheel**: `erw.fetch("eia_fuel_spot_prices", start="2026-13-45")` raises `erw.ERWBadWindow` with its sentence.
- `package/tools/build_tables.py --check`: 346 shipped, 346 in the record, 0 differ.


## The landing

Lands with the next landing of this chain.

## Checks

| Check | Exit | Result |
|---|---|---|
| `build_tables.py --check` | 0 | 346 and 346 |
| `pip wheel` | 0 | the wheel |
| `venv`, `pip install --no-index --no-deps` | 0, 0 | |
| `runs/s1002_five.py` from the clean venv | 0 | five tables answer |
| `runs/s1035_readme.py` from the clean venv | 0 | 0 requests |

## Decisions made without you

- None.

## For Samuel's ruling

- None new (the PyPI upload is packages-open item 4).
