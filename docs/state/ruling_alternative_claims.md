# Ruling alternative claims (17 November 2026)

For the chain that builds, tool by tool, the other choice of each line of `docs/reviews/ruling-impact-<tool>-2026-11-17.md` whose change is 1 percent or more, or that adds or removes a figure. Each other choice is built on its own branch `wip/alt-<tool>-<n>` from origin/main, with a test that pins the figure under the other choice and a screenshot at 1280 under `docs/reviews/ruling-alternatives/`; the record is `docs/reviews/ruling-alternatives-<tool>-2026-11-17.md`. No branch asks to land and no default on main changes. A machine claims a tool here, commits and pushes the claim alone; a tool already claimed is skipped by every other machine. Tools are taken from the bottom of `docs/state/ruling_impact_claims.md` up.

| Tool | Machine | Session | State | File |
|---|---|---|---|---|
| /cost-of-power/battery | portable-laptop | 7620 | done | docs/reviews/ruling-alternatives-battery-2026-11-17.md |
| /cost-of-power/seller | portable-laptop | 7621 | claimed | docs/reviews/ruling-alternatives-seller-2026-11-17.md |
| /contracts | samueloldlaptop | 7700 | claimed | docs/reviews/ruling-alternatives-contracts-2026-11-17.md |
