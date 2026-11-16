# Done line claims: who takes which of the 24 tools

Energy Research Warehouse (ERW). Written by session 7600 (chain 305, portable-laptop, 16 November 2026) from the table that chains 304 and 305 share (`queue/next/304-day-16-november-oldlaptop-done-line-economics.md`, `queue/done/305-night-16-november-portable-done-line-and-browser-reads.md`). It was not on origin/main, nor on any branch, when this session looked (10:35 UTC).

One row a tool. A machine reads this file after a `git fetch` and before it starts a tool, and takes no tool another machine has claimed or done. States: `claimed` (not started or in work), `done line` with the branch that holds the stack, `read: <machine>` added when the tool has been read as its reader (part C of chain 305, part B of chain 304).

| # | Tool | Machine | State |
|---:|---|---|---|
| 1 | `/contracts` | samueloldlaptop | done line (branch `wip/7501-contracts`, head `f1417cfe7`, landing row 18 of `docs/state/landing_request_oldlaptop.md`); read: samueloldlaptop |
| 2 | `/severance` with `/severance/finder` and `/severance/lease/real` | samueloldlaptop | done line (branch `wip/7502-severance`, head `0580b9670`, landing row 17 of `docs/state/landing_request_oldlaptop.md`); read: samueloldlaptop |
| 3 | `/shoulder` | samueloldlaptop | done line (branch `wip/7503-shoulder`, head `179767c18`, landing row 19 of `docs/state/landing_request_oldlaptop.md`); read: samueloldlaptop |
| 4 | `/battery/customer` | samueloldlaptop | done line (branch `wip/7504-battery-customer`, head `76261ed94`, landing row 25 of `docs/state/landing_request_oldlaptop.md`); read: samueloldlaptop |
| 5 | `/cost-of-power/battery/awards` | samueloldlaptop | done line (branch `wip/7505-battery-awards`, head `73837e331`, landing row 20 of `docs/state/landing_request_oldlaptop.md`) |
| 6 | `/impact` | samueloldlaptop | done line (branch `wip/7506-impact`, head `39fd3e028`, landing row 21 of `docs/state/landing_request_oldlaptop.md`); read: samueloldlaptop |
| 7 | `/explore/ercot-peak-premium` | samueloldlaptop | done line (branch `wip/7507-peak-premium`, head `b35e64e9a`, landing row 22 of `docs/state/landing_request_oldlaptop.md`) |
| 8 | `/explore/demand-growth` | samueloldlaptop | done line (branch `wip/7508-demand-growth`, head `66e294497`, landing row 23 of `docs/state/landing_request_oldlaptop.md`) |
| 9 | `/explore/interconnection` | samueloldlaptop | done line (branch `wip/7509-interconnection`, head `da5dfd8cb`, landing row 24 of `docs/state/landing_request_oldlaptop.md`) |
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
