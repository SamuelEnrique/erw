# The dependencies, audited, nothing upgraded (22 October 2026)

Session 586, chain 034, on samueloldlaptop (the code machine). Roadmap item 7, "Security closed". A read-only audit of the site's node packages and the warehouse's Python packages. Nothing was installed for the audit and nothing was upgraded: `requirements.txt`, `requirements-py314.txt`, `site/package.json` and `site/package-lock.json` are unchanged. Each upgrade below waits for a session the owner names.

## What was run

| Command | Where | Exit | Kept in |
|---|---|---|---|
| `npm ci` | `site/` of the session's worktree (branch `wip/586-s`, from `wip/506-combined` merged with main) | 0 (409 packages added, 410 audited) | `runs/s586_npmci.out` |
| `npm audit --omit=dev` | `site/` | 0: **found 0 vulnerabilities** | `runs/s586_npm_audit.out`, `runs/s586_npm_audit.json` |
| `npm audit` (development packages included, for the record) | `site/` | 1: 5 high, one advisory | `runs/s586_npm_audit_all.out`, `runs/s586_npm_audit_all.json` |
| `python -m pip_audit --version` | the repository's `.venv` (Python 3.14.7) | 1: not installed, so not used | |
| `python -m pip list --outdated --format=json` | the repository's `.venv` | 0: 50 packages behind PyPI | `runs/s586_pip_outdated.json` |
| `python -m pip freeze` | the repository's `.venv` | 0: 128 packages | `runs/s586_pip_freeze.txt` |

`runs/` is not in git; the counts above are what those files held on 22 October.

`pip list --outdated` names versions, not advisories. With `pip-audit` absent, the Python advisories below are those of the last `pip-audit` run, the security review of 10 October (`docs/reviews/2026-10-10-security.md`, M7), checked again against the versions installed today, plus one advisory the session knew of in a workflow pin (marked). An advisory published after 10 October on a Python package is not seen by this audit; a `pip-audit` run in a throwaway environment (the 10 October method) would see it, and is the first item for Samuel below.

## The site (node)

The production tree (`npm audit --omit=dev`, 65 production packages of 489) has **no advisory**. `next` 16.3.8 is the release the 10 October review moved to (H2).

The development tree holds one advisory, already listed on 10 October as L9 and still open:

| Package | Held | Fixed version | Reached by the ERW's code | Upgrade's size |
|---|---|---|---|---|
| `braces` (GHSA-vfj7-8cjw-p6xm, stack-exhaustion denial of service on deeply nested patterns, CVSS 7.5, range `<=3.0.3`) | 3.0.3 | none published: npm resolves the range to every published version (`braces *`) | no. The chain is `eslint-config-next` 16.3.8, `@next/eslint-plugin-next` 16.3.8, `fast-glob` 3.3.1, `micromatch` 4.0.8, `braces` 3.0.3: the linter only. No workflow runs `npm run lint` or eslint (`.github/workflows/` searched), `next build` in Next 16 does not lint, and no file under `site/app`, `site/lib`, `site/components` or `site/scripts` imports `fast-glob`, `micromatch` or `braces`. The patterns it expands are the repository's own eslint globs, never a visitor's input | npm's only offer is `npm audit fix --force`, which installs `eslint-config-next` 14.2.35: a major step **down**, out of step with `next` 16.3.8. Not advised |
| `micromatch`, `fast-glob`, `@next/eslint-plugin-next`, `eslint-config-next` | 4.0.8, 3.3.1, 16.3.8, 16.3.8 | as above (each listed only for depending on `braces`) | as above | as above |

The way out, when one exists, is an `eslint-config-next` release whose `@next/eslint-plugin-next` drops `fast-glob` 3.3.1 or a `braces` release above 3.0.3; until then the advisory stays listed and unfixed.

`motion/package-lock.json` (a second node project) was not audited: the session's part names `site/` only.

## The warehouse (Python)

### Advisories

| Package | Held | Fixed version | Reached by the ERW's code | Upgrade's size |
|---|---|---|---|---|
| `cryptography` (PYSEC-2026-3552, -3553, -3554, GHSA-537c-gmf6-5ccf; from the 10 October run) | **46.0.7 in this machine's `.venv`**, although `requirements-py314.txt` has pinned 50.0.2 since session 312: the environment was never reinstalled from the pin. On the runner (Python 3.12, `pip install -r requirements.txt`), 46.x, held by `gridstatus==0.36.0` (`cryptography<47`) | 48.0.1 to 50.0.0 (the review's words); PyPI's newest is 50.0.2 | no file of the ERW imports it (`warehouse`, `package`, `scripts`, `site`, `tests` searched). It is installed for `gridstatus` and `pdfminer.six` (`pip show`); pdfminer reaches it only to decrypt an encrypted PDF, and the advisories concern certificate-chain checks and PKCS7 decryption, which neither the ERW nor pdfminer's PDF reading calls. The PDFs read are CAISO's and CARB's (`warehouse/connectors/caiso_emergencies.py`, `carbon_auctions.py`) | major (46 to 50). On this machine a reinstall from the existing pin (`pip install --no-deps -r requirements-py314.txt`) closes it with no file changed; on the runner it waits for a `gridstatus` release that lifts `cryptography<47` (0.36.0 is still PyPI's newest today: `pip list --outdated` does not list it) |
| `lxml` (PYSEC-2026-87, entity resolution in the default parsers; from the 10 October run) | 6.1.3 on this machine (closed); 5.x on the runner, held by `gridstatus` (`lxml~=5.3`) | 6.1.0 | on the runner, yes: `pd.read_html` in `warehouse/connectors/boem_leases.py` (line 52) and `carbon_auctions.py` (line 148) parses with lxml. The pages are BOEM's and CARB's own, fetched over HTTPS from the publishers the ERW names; a hostile document would need one of them to serve it | major (5 to 6), blocked on the runner by `gridstatus` |
| `setuptools` (PYSEC-2026-3447; from the 10 October run) | 84.0.0 on this machine (closed); 78.x on the runner, held by `gridstatus` (`setuptools<79`) | 83.0.0 | no: an installation tool, run at install time only | major (78 to 84), blocked on the runner by `gridstatus` |
| `virtualenv` (PYSEC-2026-4011 to -4014; from the 10 October run) | 20.39.1 (here and in `requirements-py314.txt`), installed for `gridstatus` | 21.7.13; PyPI's newest is 21.14.12 | no: no file imports it, and no ERW command creates an environment with it | major (20 to 21) |
| `requests` (CVE-2024-47081 / GHSA-9hjg-9r4m-mvj7, `.netrc` credentials sent to the wrong host for a crafted URL; known to the session, not from a tool run today) | 2.32.3, pinned by the light installs of `.github/workflows/chain-watch.yml` (line 60), `daily-prices.yml` (137), `hourly-network.yml` (37) and `roundup.yml` (90); this machine and `requirements-py314.txt` hold 2.34.2 | 2.32.4 | not in practice: those steps call GitHub's and Supabase's addresses written in the repository, and a GitHub runner has no `.netrc` | patch (2.32.3 to 2.32.4); a change to four workflow files, so a code session's |

### Every package behind PyPI (`pip list --outdated`, this machine's `.venv`)

"In requirements.txt" says whether the file names the package itself; the rest come in as dependencies. A calendar-versioned package (a version that is a date) is marked "date release", not minor. `pandas` 3 is outside `requirements.txt`'s own range (`<3`).

| Package | Held | Newest | Size | In requirements.txt |
|---|---|---|---|---|
| anthropic | 1.8.0 | 2.1.0 | major | yes |
| certifi | 2026.7.22 | 2026.10.19 | date release | no |
| charset-normalizer | 3.5.1 | 3.5.2 | patch | no |
| cryptography | 46.0.7 | 50.0.2 | major (advisory, above) | no |
| distlib | 0.4.3 | 0.4.4 | patch | no |
| filelock | 3.32.7 | 4.2.4 | major | no |
| fonttools | 4.66.0 | 4.67.0 | minor | no |
| httpcore2 | 2.13.1 | 2.16.0 | minor | no |
| httpx2 | 2.13.1 | 2.16.0 | minor | no |
| imagecodecs | 2026.8.16 | 2026.10.10 | date release | no |
| iniconfig | 2.3.0 | 2.3.1 | patch | no |
| multidict | 7.0.0 | 7.1.0 | minor | no |
| narwhals | 2.26.0 | 2.27.1 | minor | no |
| numpy | 2.3.5 | 2.5.4 | minor (held at 2.3.5 on purpose: Smart App Control blocked 2.5.3, `requirements-py314.txt`) | no |
| pandas | 2.3.3 | 3.0.6 | major (outside `<3`) | yes |
| pillow | 12.3.0 | 13.0.0 | major | no |
| pip | 26.2.1 | 26.2.2 | patch | no |
| platformdirs | 4.11.12 | 4.13.5 | minor | no |
| plotly | 6.9.0 | 7.1.0 | major | no |
| pluggy | 1.6.0 | 1.7.0 | minor | no |
| polars | 1.44.2 | 2.0.0 | major | no |
| polars-runtime-32 | 1.44.2 | 2.0.0 | major | no |
| postgrest | 2.32.0 | 2.33.0 | minor | no |
| pyarrow | 25.0.1 | 26.0.0 | major | no |
| pycparser | 3.0 | 3.11 | minor | no |
| pydantic | 2.13.5 | 2.14.1 | minor | no |
| pydantic_core | 2.46.5 | 2.50.1 | minor | no |
| pypdfium2 | 5.13.0 | 5.14.0 | minor | no |
| python-dateutil | 2.9.0.post0 | 3.0.0 | major | no |
| python-dotenv | 1.2.3 | 1.2.4 | patch | yes |
| pytz | 2026.4 | 2026.5 | date release | no |
| realtime | 2.32.0 | 2.33.0 | minor | no |
| redivis | 0.20.15 | 0.21.1 | minor (0.x: may break) | yes |
| rpds-py | 2026.6.3 | 2026.9.1 | date release | no |
| setuptools | 84.0.0 | 84.2.1 | minor | no |
| shapely | 2.1.2 | 2.2.0 | minor | no |
| soupsieve | 2.10 | 3.0.3 | major | no |
| storage3 | 2.32.0 | 2.33.0 | minor | no |
| supabase | 2.32.0 | 2.33.0 | minor | yes |
| supabase-auth | 2.32.0 | 2.33.0 | minor | no |
| supabase-functions | 2.32.0 | 2.33.0 | minor | no |
| tifffile | 2026.9.20 | 2026.10.15 | date release | no |
| toolz | 1.1.0 | 1.2.0 | minor | no |
| truststore | 0.10.4 | 0.10.5 | patch | no |
| tzdata | 2026.4 | 2026.5 | date release | no |
| urllib3-future | 2.25.901 | 2.25.903 | patch | no |
| virtualenv | 20.39.1 | 21.14.12 | major (advisory, above) | no |
| websockets | 15.0.1 | 17.3 | major | no |
| xmltodict | 0.15.1 | 1.0.4 | major | no |
| zipp | 3.23.1 | 4.1.2 | major | no |

### This machine against its pin file

`pip freeze` against `requirements-py314.txt` (the exact environment the file promises): one pin is not what is installed, `cryptography` (pinned 50.0.2, installed 46.0.7). Six installed packages are not in the file: `affine` 3.0.1, `attrs` 26.1.0, `imagecodecs` 2026.8.16, `pyshp` 3.1.6, `rasterio` 1.5.2, `tifffile` 2026.9.20 (a raster stack some session installed and the file never recorded).

## The upgrades, for Samuel's ruling (none done)

1. A `pip-audit` run in a throwaway environment (the 10 October method), so the Python side reads today's advisories and not 10 October's; it installs `pip-audit` in that environment only.
2. On this machine, `pip install --no-deps -r requirements-py314.txt` to bring `cryptography` to its pin, 50.0.2 (closes four advisories here; no file changes).
3. `requests` 2.32.3 to 2.32.4 in the four workflows' light installs (CVE-2024-47081; patch).
4. `virtualenv` 20.39.1 to 21.x in `requirements-py314.txt` (four advisories; major; installed only for `gridstatus`).
5. On the runner, `lxml`, `cryptography` and `setuptools` stay where `gridstatus` 0.36.0 holds them until a `gridstatus` release lifts its pins (unchanged since 10 October, M7).
6. `braces` and its chain (the linter only, L9): no fix published; npm's forced fix is a major downgrade of `eslint-config-next` and is not advised.
7. Whether the six unrecorded raster packages go into `requirements-py314.txt` or out of the environment.
8. The 48 other packages behind PyPI, none with a known advisory: `anthropic` 2 and `pandas` 3 are majors the code would need a session for; the rest when a session the owner names takes them.
