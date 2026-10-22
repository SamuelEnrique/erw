# Session 586 report: the dependencies, audited, nothing upgraded

22 October 2026 (UTC), on samueloldlaptop (the code machine), a session of `queue/done/034-night-22-october-code.md`, branch `wip/586-s` cut from `origin/wip/506-combined` (main already merged in). Model spend USD 0. No warehouse data written. Nothing installed or upgraded: `requirements.txt`, `requirements-py314.txt`, `site/package.json` and `site/package-lock.json` unchanged.

## Summary

- **The site's production packages: no advisory** (`npm audit --omit=dev`, 0 vulnerabilities; `next` 16.3.8).
- **The development tree: one advisory, the linter's** (`braces` 3.0.3, GHSA-vfj7-8cjw-p6xm, through `eslint-config-next` 16.3.8). No fixed version is published; npm's only fix is a forced downgrade to `eslint-config-next` 14. Unreached: no workflow lints and no site file imports the chain. Same as the 10 October review's L9.
- **Python: `pip-audit` is not installed**, so it was not used; `pip list --outdated` shows 50 packages behind PyPI. The advisories are those of the 10 October `pip-audit` run, checked against today's versions:
  - `cryptography` 46.0.7 is still installed on this machine although `requirements-py314.txt` has pinned 50.0.2 since session 312. The environment was never reinstalled from the pin.
  - `virtualenv` 20.39.1 is still held.
  - On the runner, `lxml` 5.x, `cryptography` 46.x and `setuptools` 78.x stay, because `gridstatus` 0.36.0 pins them and is still PyPI's newest.
  - Of these, only `lxml` is reached by ERW code: `pd.read_html` in two connectors, on the runner.
- **A workflow pin with a known advisory:** `requests==2.32.3` in four workflows' light installs (CVE-2024-47081, fixed in 2.32.4). It is not reached in practice. This advisory came from the session's knowledge, not from a tool run.
- The review: `docs/reviews/dependencies-2026-10-22.md` (each advisory with its version, fix, reach and size; every outdated package; eight upgrade items for Samuel).

## What was done

1. Precheck, the worktree, `npm ci` in `site/`, then the two audits and the pip reads below. Outputs went to `runs/s586_*` in the worktree, which is not in git.
2. Each advisory was traced:
   - its dependency path: `npm ls`, `pip show`;
   - the ERW's imports of each flagged package: `warehouse`, `package`, `scripts`, `site`, `tests`;
   - the workflows' install lines and Python version (3.12, `pip install -r requirements.txt`).
3. Compared `pip freeze` with `requirements-py314.txt`. One pin is not held (`cryptography`), and six raster packages are installed but unrecorded.
4. Wrote the review and this report. No code was changed, so there is no test to add.

## Checks

| Command | Exit |
|---|---|
| `.venv/Scripts/python.exe scripts/precheck.py --what "session 586"` | 0 |
| `npm ci` (site/) | 0 |
| `npm audit --omit=dev` (site/) | 0 (0 vulnerabilities) |
| `npm audit --omit=dev --json` (site/) | 0 |
| `npm audit` and `npm audit --json`, development packages included (site/) | 1 (5 high, one advisory) |
| `python -m pip_audit --version` | 1 (not installed; not used) |
| `python -m pip list --outdated --format=json` | 0 (50 packages) |
| `python -m pip freeze` | 0 (128 packages) |

Web requests: npm's registry (`npm ci`, the audits) and PyPI (`pip list --outdated`) only, as the part names. No build, no server, no browser.

## Decisions made without you

- I also ran `npm audit` once with development packages included, against the same registry, so the linter's advisory (L9) could be stated with its current versions. The part's gate is the `--omit=dev` run.
- When I could not get a current advisory list, I reused the 10 October `pip-audit` findings and checked them against today's installed versions. The review says that advisories published after 10 October are not seen.
- I listed `requests` 2.32.3 (CVE-2024-47081) from the session's own knowledge. It is marked as not coming from a tool run.
- `motion/package-lock.json` was not audited because the part names `site/` only.

## For Samuel's ruling

- Run `pip-audit` in a throwaway environment, so the Python side reads today's advisories.
- Run `pip install --no-deps -r requirements-py314.txt` on this machine to bring `cryptography` from 46.0.7 to its pin of 50.0.2.
- Move `requests` from 2.32.3 to 2.32.4 in `chain-watch.yml`, `daily-prices.yml`, `hourly-network.yml` and `roundup.yml` (CVE-2024-47081).
- Move `virtualenv` from 20.39.1 to 21.x in `requirements-py314.txt` (four advisories, a major version).
- On the runner, `lxml`, `cryptography` and `setuptools` stay held by `gridstatus` 0.36.0 until a `gridstatus` release lifts its pins.
- `braces` in the linter chain has no published fix, and the forced downgrade of `eslint-config-next` is not advised.
- Six raster packages are installed but not in `requirements-py314.txt` (`affine`, `attrs`, `imagecodecs`, `pyshp`, `rasterio`, `tifffile`): record them or remove them.
- 48 other packages are behind PyPI with no known advisory. `anthropic` 2 and `pandas` 3 are major versions.

## To finish

Nothing. Session 589 lands the chain: `docs/reviews/dependencies-2026-10-22.md` and this report are on `wip/586-s`.

## Files changed

- New: `docs/reviews/dependencies-2026-10-22.md`, `archive/sessions/SESSION_586_REPORT.md`.
