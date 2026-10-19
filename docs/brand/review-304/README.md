# Session 304: the tracker and the contracts page, the rulings of 14 October

Screenshots in the internal view at 1280 and 390 px, quantized to 32 colors, 19 October 2026, each page in its default
state. "Before" is production serving session 302 (session 303's chart was not landed when these were taken); "after"
is the local build of branch `wip/304-replication`. Taken with `runs/chain_oct19/capture300.mjs`, which also kept each
page's checked numbers and visible text under `runs/chain_oct19/s304/` (not in git).

| File | Address | What it shows |
|---|---|---|
| `*_datacenters_*.png` | `/datacenters` | ERCOT's large-load section: under the three headline figures, the new line saying ERCOT paused approvals to energize on 3 August 2026, cited to the Batch Zero deck to TAC of 26 August 2026 (ruling 4) |
| `*_contracts_*.png` | `/contracts` | the contracts of the newest quarter; no execution date lies after today, so no row reads "as filed" on 19 October (ruling 5: the words appear beside a date after today) |

Not kept here, for their size: `/policy` (1.5 MB a shot at 1280, 1.7 MB at 390; no action's date lies after today, so no "as filed" shows on 19 October either) and `/internal/findings` (3 to 4 MB a shot: 48 drafts). Their shots are under `runs/chain_oct19/s304/` on the code machine. What to look at on `/internal/findings`, after: every verdict line reads "Verdict of 13 October 2026" or "Verdict of 14 October 2026"; the four drafts of 14 October marked drop read "dismissed"; the eight others read "no verdict yet" with what the verification read them as.

Every checked number on the tracker is the same before and after (150 keys).
