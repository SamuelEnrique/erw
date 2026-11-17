# Done line claims: who takes which of the 24 tools

Energy Research Warehouse (ERW). Written by session 7600 (chain 305, portable-laptop, 16 November 2026) from the table that chains 304 and 305 share (`queue/next/304-day-16-november-oldlaptop-done-line-economics.md`, `queue/done/305-night-16-november-portable-done-line-and-browser-reads.md`). It was not on origin/main, nor on any branch, when this session looked (10:35 UTC).

One row a tool. A machine reads this file after a `git fetch` and before it starts a tool, and takes no tool another machine has claimed or done. States: `claimed` (not started or in work), `done line` with the branch that holds the stack, `read: <machine>` added when the tool has been read as its reader (part C of chain 305, part B of chain 304).

| # | Tool | Machine | State |
|---:|---|---|---|
| 1 | `/contracts` | samueloldlaptop | done line (branch `wip/7501-contracts`, head `f1417cfe7`, landing row 18 of `docs/state/landing_request_oldlaptop.md`); read: samueloldlaptop |
| 2 | `/severance` with `/severance/finder` and `/severance/lease/real` | samueloldlaptop | done line (branch `wip/7502-severance`, head `0580b9670`, landing row 17 of `docs/state/landing_request_oldlaptop.md`); read: samueloldlaptop |
| 3 | `/shoulder` | samueloldlaptop | done line (branch `wip/7503-shoulder`, head `179767c18`, landing row 19 of `docs/state/landing_request_oldlaptop.md`); read: samueloldlaptop |
| 4 | `/battery/customer` | samueloldlaptop | done line (branch `wip/7504-battery-customer`, head `76261ed94`, landing row 25 of `docs/state/landing_request_oldlaptop.md`); read: samueloldlaptop |
| 5 | `/cost-of-power/battery/awards` | samueloldlaptop | done line (branch `wip/7505-battery-awards`, head `74992ec65`, landing row 20 of `docs/state/landing_request_oldlaptop.md`); read: samueloldlaptop |
| 6 | `/impact` | samueloldlaptop | done line (branch `wip/7506-impact`, head `39fd3e028`, landing row 21 of `docs/state/landing_request_oldlaptop.md`); read: samueloldlaptop |
| 7 | `/explore/ercot-peak-premium` | samueloldlaptop | done line (branch `wip/7507-peak-premium`, head `a6184f8d2`, landing row 22 of `docs/state/landing_request_oldlaptop.md`); read: samueloldlaptop |
| 8 | `/explore/demand-growth` | samueloldlaptop | done line (branch `wip/7508-demand-growth`, head `39dc57835`, landing row 23 of `docs/state/landing_request_oldlaptop.md`); read: samueloldlaptop |
| 9 | `/explore/interconnection` | samueloldlaptop | done line (branch `wip/7509-interconnection`, head `aead62928`, landing row 24 of `docs/state/landing_request_oldlaptop.md`); read: samueloldlaptop |
| 10 | `/map` | portable-laptop | done line (branch `wip/7601-map`, head `884c94071`, landing row 37 of `docs/state/landing_request_portable.md`); read: samueloldlaptop (session 7537, branch `wip/7537-map-read`, head `aa6158f2a`, landing row 35 of `docs/state/landing_request_oldlaptop.md`) |
| 11 | `/events` and its nine event pages | samueloldlaptop | done line (branch `wip/7531-events-b`, head `984d91a4b`, landing row 29 of `docs/state/landing_request_oldlaptop.md`); read: samueloldlaptop (session 7549, on the same branch, head `1ee8233fc`) |
| 12 | `/grid/caiso/alerts` | samueloldlaptop | done line (branch `wip/7532-caiso-alerts`, head `ac362d6f6`, landing row 30 of `docs/state/landing_request_oldlaptop.md`); read: samueloldlaptop (session 7546, on the same branch, head `79c26b05d`) |
| 13 | `/learn/bill` | samueloldlaptop | done line (branch `wip/7533-learn-bill`, head `09eafa96e`, landing row 31 of `docs/state/landing_request_oldlaptop.md`); read: samueloldlaptop (session 7547, on the same branch, head `2d5c874f6`) |
| 14 | `/learn/problems` | samueloldlaptop | done line (branch `wip/7534-learn-problems-b`, head `430032463`, landing row 32 of `docs/state/landing_request_oldlaptop.md`); read: samueloldlaptop (session 7548, on the same branch, head `1f79d1450`) |
| 15 | `/play/battery` | samueloldlaptop | done line (branch `wip/7535-play-battery`, head `544328a5b`, landing row 33 of `docs/state/landing_request_oldlaptop.md`); read: samueloldlaptop (session 7551, on the same branch, head `0fb8d3d3d`) |
| 16 | `/play/ev` | samueloldlaptop | done line (branch `wip/7536-play-ev`, head `95943ca8e`, landing row 34 of `docs/state/landing_request_oldlaptop.md`); read: samueloldlaptop (session 7550, on the same branch, head `3c5bbabaf`) |
| 17 | `/board` | lab-desktop | done line (branch `wip/c301-later`, head `a4dc611c3` or later: the replication, the faults, the cross-checks, the decisions block, the sign-off; the pack `docs/reviews/desktop-tools-signature-pack-2026-11-16.md`; lands with chain 301's gate h); read: samueloldlaptop (session 7538, branch `wip/7538-board-read`, head `9486d422c`, landing row 36 of `docs/state/landing_request_oldlaptop.md`) |
| 18 | `/prices` | lab-desktop | done line (branch `wip/c301-later`, head `a4dc611c3` or later: the replication, the faults, the cross-checks, the decisions block, the sign-off; the pack `docs/reviews/desktop-tools-signature-pack-2026-11-16.md`; lands with chain 301's gate h); read: samueloldlaptop (session 7539, branch `wip/7539-prices-read`, head `51d8cac91`, landing row 37 of `docs/state/landing_request_oldlaptop.md`) |
| 19 | `/prices/compare` | lab-desktop | done line (branch `wip/c301-later`, head `a4dc611c3` or later: the replication, the faults, the cross-checks, the decisions block, the sign-off; the pack `docs/reviews/desktop-tools-signature-pack-2026-11-16.md`; lands with chain 301's gate h); read: samueloldlaptop (session 7540, branch `wip/7540-compare-read`, head `028b48e1d`, landing row 38 of `docs/state/landing_request_oldlaptop.md`) |
| 20 | `/supply` | lab-desktop | done line (branch `wip/c301-later`, head `a4dc611c3` or later: the replication, the faults, the cross-checks, the decisions block, the sign-off; the pack `docs/reviews/desktop-tools-signature-pack-2026-11-16.md`; lands with chain 301's gate h); read: samueloldlaptop (session 7541, branch `wip/7541-supply-read-b`, head `af5deaca7`, landing row 39 of `docs/state/landing_request_oldlaptop.md`) |
| 21 | `/storage` | lab-desktop | done line (branch `wip/c301-later`, head `a4dc611c3` or later: the replication, the faults, the cross-checks, the decisions block, the sign-off; the pack `docs/reviews/desktop-tools-signature-pack-2026-11-16.md`; lands with chain 301's gate h); read: samueloldlaptop (session 7542, branch `wip/7542-storage-read`, head `e8ffc18ff`, landing row 40 of `docs/state/landing_request_oldlaptop.md`) |
| 22 | `/demand` | lab-desktop | done line (branch `wip/c301-later`, head `a4dc611c3` or later: the replication, the faults, the cross-checks, the decisions block, the sign-off; the pack `docs/reviews/desktop-tools-signature-pack-2026-11-16.md`; lands with chain 301's gate h); read: samueloldlaptop (session 7543, branch `wip/7543-demand-read`, head `8ec599dec`, landing row 41 of `docs/state/landing_request_oldlaptop.md`) |
| 23 | `/curtailment` | lab-desktop | done line (branch `wip/c301-later`, head `a4dc611c3` or later: the replication, the faults, the cross-checks, the decisions block, the sign-off; the pack `docs/reviews/desktop-tools-signature-pack-2026-11-16.md`; lands with chain 301's gate h); read: samueloldlaptop (session 7544, branch `wip/7544-curtailment-read`, head `a291b1b16`, landing row 42 of `docs/state/landing_request_oldlaptop.md`) |
| 24 | `/queues` | lab-desktop | done line (branch `wip/c301-later`, head `a4dc611c3` or later: the replication, the faults, the cross-checks, the decisions block, the sign-off; the pack `docs/reviews/desktop-tools-signature-pack-2026-11-16.md`; lands with chain 301's gate h); read: samueloldlaptop (session 7545, branch `wip/7545-queues-read`, head `3d443cf6a`, landing row 43 of `docs/state/landing_request_oldlaptop.md`) |

Not in the split: `/ask` and `/thesis` (they need the key), the Digest and the Roundup (paused this week), the pages that are not tools (`/about`, `/data`, `/terms`, `/privacy`, `/subscribe`, `/tour`, `/home/v2`, `/in-review`, the draft reports).

The ten tools already at the done line before this file (battery, generator, datacenter cost, Automated Analysis, Grid, the datacenter tracker, the deal tracker, companies, the policy monitor, attention) are not rows here, except the six below.

## The six tools of the first ten with no read (added by session 7560, samueloldlaptop, 17 November 2026 UTC)

Asked by Samuel: the reader's read, in chain 304's part B form, for the six tools of the first ten that had no `docs/reviews/<tool>-read-2026-11-16.md` on any branch (checked on all 568 remote branches at 03:40 UTC on 17 November: battery, generator, datacenter cost and the policy monitor have reads; these six do not). All six reads go on branch `wip/7560-six-reads`, one session a tool.

| # | Tool | At the done line | State |
|---:|---|---|---|
| 25 | `/datacenters` (the datacenter tracker) | chain 303, `docs/reviews/trackers-signature-pack-2026-11-16.md` | read: samueloldlaptop, claimed (session 7560) |
| 26 | `/deals` (the deal tracker) | chain 303, the same pack | read: samueloldlaptop, claimed (session 7561) |
| 27 | `/companies` | chain 303's portable run | read: samueloldlaptop, claimed (session 7562) |
| 28 | `/attention` | chain 303's portable run | read: samueloldlaptop, claimed (session 7563) |
| 29 | `/research` (Automated Analysis) | the five tools' pack, `docs/reviews/five-tools-signature-pack-2026-11-14.md` | read: samueloldlaptop, claimed (session 7564) |
| 30 | `/grid` | the five tools' pack | read: samueloldlaptop, claimed (session 7565) |
