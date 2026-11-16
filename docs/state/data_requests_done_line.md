# Data requests: the done line of the 24 tools (chains 304 and 305)

Energy Research Warehouse (ERW). Written by session 7600 (chain 305, portable-laptop, 16 November 2026). The laptops write no warehouse table and run no builder under the data lock. Each row below is something only the data machine does. The data machine marks a row done with its commit.

A data fault found by a laptop while it takes a tool to the done line is one row here, marked requested, and one row marked `data machine` in that tool's faults file (`docs/reviews/<tool>-faults-2026-11-16.md`).

| # | Requested (UTC) | Session | Table or file | What, exactly | Source | State |
|---:|---|---|---|---|---|---|
| 1 | 2026-11-16 | 7600 (chain 305, portable-laptop) | `docs/state/done_line_claims.md` | For chain 301's section 'If goals 1 to 4 are done and no new file waits': take the tools marked lab-desktop in docs/state/done_line_claims.md, in that order, and no tool marked for a laptop (the laptops' replication folders are on wip branches and reach main only when landed). Asked by Samuel through Claude in chat, 16 November 2026. | `queue/done/305-night-16-november-portable-done-line-and-browser-reads.md`, session 7600's section | requested |
