# Done line claims: who takes which of the 24 tools

Energy Research Warehouse (ERW). Written by session 7600 (chain 305, portable-laptop, 16 November 2026) from the table that chains 304 and 305 share (`queue/next/304-day-16-november-oldlaptop-done-line-economics.md`, `queue/done/305-night-16-november-portable-done-line-and-browser-reads.md`). It was not on origin/main, nor on any branch, when this session looked (10:35 UTC).

One row a tool. A machine reads this file after a `git fetch` and before it starts a tool, and takes no tool another machine has claimed or done. States: `claimed` (not started or in work), `done line` with the branch that holds the stack, `read: <machine>` added when the tool has been read as its reader (part C of chain 305, part B of chain 304).

| # | Tool | Machine | State |
|---:|---|---|---|
| 1 | `/contracts` | samueloldlaptop | done line (branch `wip/7501-contracts`, head `118e668fa`, landing row row 18 of `docs/state/landing_request_oldlaptop.md`) |
| 2 | `/severance` with `/severance/finder` and `/severance/lease/real` | samueloldlaptop | done line (branch `wip/7502-severance`, head `c247ad4e1`, landing row row 17 of `docs/state/landing_request_oldlaptop.md`) |
| 3 | `/shoulder` | samueloldlaptop | done line (branch `wip/7503-shoulder`, head `7820907a4`, landing row row 19 of `docs/state/landing_request_oldlaptop.md`) |
| 4 | `/battery/customer` | samueloldlaptop | claimed |
| 5 | `/cost-of-power/battery/awards` | samueloldlaptop | claimed |
| 6 | `/impact` | samueloldlaptop | claimed |
| 7 | `/explore/ercot-peak-premium` | samueloldlaptop | claimed |
| 8 | `/explore/demand-growth` | samueloldlaptop | claimed |
| 9 | `/explore/interconnection` | samueloldlaptop | claimed |
| 10 | `/map` | portable-laptop | claimed |
| 11 | `/events` and its nine event pages | portable-laptop | claimed |
| 12 | `/grid/caiso/alerts` | portable-laptop | claimed |
| 13 | `/learn/bill` | portable-laptop | claimed |
| 14 | `/learn/problems` | portable-laptop | claimed |
| 15 | `/play/battery` | portable-laptop | claimed |
| 16 | `/play/ev` | portable-laptop | claimed |
| 17 | `/board` | lab-desktop | claimed |
| 18 | `/prices` | lab-desktop | claimed |
| 19 | `/prices/compare` | lab-desktop | claimed |
| 20 | `/supply` | lab-desktop | claimed |
| 21 | `/storage` | lab-desktop | claimed |
| 22 | `/demand` | lab-desktop | claimed |
| 23 | `/curtailment` | lab-desktop | claimed |
| 24 | `/queues` | lab-desktop | claimed |

Not in the split: `/ask` and `/thesis` (they need the key), the Digest and the Roundup (paused this week), the pages that are not tools (`/about`, `/data`, `/terms`, `/privacy`, `/subscribe`, `/tour`, `/home/v2`, `/in-review`, the draft reports).

The ten tools already at the done line before this file (battery, generator, datacenter cost, Automated Analysis, Grid, the datacenter tracker, the deal tracker, companies, the policy monitor, attention) are not rows here.
