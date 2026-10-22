# Session 730 report: large-load tariffs

22 October 2026, from 15:33 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-730` on `wip/730-allgrids` (cut from `wip/729-allgrids`). Chain `queue/done/062-day-23-october-code-allgrids-2.md`, session 730. Model spend USD 0. No warehouse data written; no request.

## Read these first

- **None there.** `utility_large_load_tariffs` has not landed. Its connector (`warehouse/connectors/openei_large_load_tariffs.py`, chain 043's session 670) exists but has never run: the data machine holds no `OPENEI_API_KEY`. So the gaps file's row on large-load tariffs stays as it is.
- **The fallback, as the chain file asks: the column's functions, written against the connector's documented shape, tested, not wired.**
  - `siting_page.tariffs_file` (builder): each utility's rates, newest first. It would write `site/data/siting/tariffs.json`; it is not called.
  - `tariffFor` (lib/siting.ts): the newest rate whose minimum demand the load meets.
  - `tariffParts` (lib/siting.ts): the energy charge as written, plus the demand charge and the fixed charge spread over the MWh the load draws in a 730-hour month. This is the four-peak charge's rule; a load running half the hours pays twice per MWh.
- **The parts are kept apart.** A bundled rate's energy charge is a retail price, not a wires charge, so which parts the transmission column adds is a decision for the session that wires it, with the table in hand.
- `tests/test_session730.py` checks the builder on a seven-row fixture in the connector's shape, the rate chosen for a 10 MW and a 100 MW load, the spread, and that nothing is wired.

## What to review

1. `site/lib/siting.ts`, `tariffFor` and `tariffParts`, and `warehouse/derived/siting_page.py`, `tariffs_file`.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `warehouse/metadata/coverage.csv` on main | | no `utility_large_load_tariffs` |
| `tests.test_session730` | 0 | 3 OK |

## The landing

With 722 to 729 (the landing below, in this session's branch, once done).

## Decisions made without you

1. **The newest rate open to the load**, not the cheapest: the tab ranks nothing by a score.
2. **Parts apart, not one figure**, until the table is in hand.

## For Samuel's ruling

- The data machine's tariff table waits on an `OPENEI_API_KEY` (the NREL developer network's key) in its `.env`: one step for you, as chain 043's session 670 said.

## Files

- Changed: `warehouse/derived/siting_page.py` (`tariffs_file`), `site/lib/siting.ts` (`TariffRate`, `tariffFor`, `tariffParts`).
- New: `tests/test_session730.py`, this report.
